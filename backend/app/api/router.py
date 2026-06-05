from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from typing import List

from app.database.session import get_db
from app.database.models import User, Voucher, Campaign, ClaimRecord, ClaimStatusEnum,  CampaignStatusEnum
from app.schemas.voucher import (
    claimVoucherRequest,
    claimVoucherResponse,
    checkclaimVoucherResponse,
    CampaignResponse,
    CampaignListResponse,
    VoucherResponse,
    VoucherListResponse,
    ErrorResponse,
    HealthCheckResponse,
)
from app.core.redis_client import redis_client
from app.core.kafka_client import kafka_client
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["Voucher"])

# Health Check Endpoint
@router.get("/health", response_model = HealthCheckResponse, tags =["System"])
async def health_check(db: Session = Depends(get_db)):
    db_status = "connected" if db.execute("SELECT 1") else "disconnected"
    redis_status = "connected" if redis_client.ping() else "disconnected"
    kafka_status = "connected" # Simplified check

    return HealthCheckResponse(
        status = "OK",
        database = db_status,
        redis = redis_status,
        kafka = kafka_status,
    )


#====================
# Campaign Endpoints
#====================

@router.get("/campaigns", response_model = CampaignListResponse)
async def get_campaigns(
    db: Session = Depends(get_db),
    status: str = Query(None, description = "Lọc theo trạng thái: SCHEDULED, ACTIVE, ENDED")
    ):

    # Lấy danh sách campaign từ DB
    query = db.query(Campaign)

    if status:
        query = query.filter(Campaign.status == status)

    campaigns = query.all()

    return CampaignListResponse(
        data = [CampaignResponse.model_validate(c) for c in campaigns],
        total = len(campaigns)
    )


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign)
    campaign = campaign.filter(Campaign.id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return CampaignResponse.model_validate(campaign)

#====================
# Voucher Endpoints
#====================

@router.get("/campaigns/{campaign_id}/vouchers", response_model = VoucherListResponse)
async def get_vouchers(campaign_id: int, db: Session =Depends(get_db)):
        campaign = db.query(Campaign)
        campaign = campaign.filter(Campaign.id == campaign_id).first()

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
    
        vouchers = db.query(Voucher)
        vouchers = vouchers.filter(Voucher.campaign_id == campaign_id).all()

        voucher_responses = []

        for v in vouchers:
            res = VoucherResponse.model_validate(v)
            res.calculate_remaining()
            voucher_responses.append(res)

        return VoucherListResponse(
            data = voucher_responses,
            total = len(voucher_responses)
        )

@router.get("/vouchers/{voucher_id}", response_model = VoucherResponse)
async def get_voucher(voucher_id: int, db: Session = Depends(get_db)):
    voucher = db.query(Voucher)
    voucher = voucher.filter(Voucher.id == voucher_id).first()

    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    res = VoucherResponse.model_validate(voucher)
    res.calculate_remaining()
    return res

#====================
# Claim Voucher Endpoint
#====================

@router.post("/vouchers/claim", response_model = claimVoucherResponse)
async def claim_voucher(
    request: claimVoucherRequest,
    db: Session = Depends(get_db)
    ):

    """
    Claim Voucher - Thu thập voucher người dùng

    Quy trình
    1. Kiểm tra voucher tồn tại
    2. Kiểm tra user tồn tại
    3. Kiểm tra user đã claim voucher này chưa (unique constraint)
    4. Chạy Lua script trên Redis (check + trừ kho atomic)
    5. Nếu success → push event vào Kafka
    6. Trả về response nhanh chóng (~50ms)
    """

    # Step 1
    voucher = db.query(Voucher)
    voucher = voucher.filter(Voucher.id == request.voucher_id).first()

    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    # Step 2
    user = db.query(User)
    user = user.filter(User.id == request.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Step 3
    existing_claim = db.query(ClaimRecord).filter(
        ClaimRecord.user_id == request.user_id,
        ClaimRecord.voucher_id == request.voucher_id
    ).first()

    if existing_claim:
        raise HTTPException(
            status_code = 400,
            detail = "Bạn đã claim voucher này rồi"
        )
    
    # Step 4.1
    redis_key_inventory = f"voucher:{request.voucher_id}.inventory"
    redis_key_lock = f"voucher:{request.user_id}.lock"

    if not redis_client.exists(redis_key_inventory):
        redis_client.set_inventory(request.voucher_id, voucher.calculate_remaning)

    try:
        redis_client.load_lua_script(
            "claim_voucher",
            "/app/scripts/claim_voucher.lua"
        )
    except:
        pass
    
    redis_client.execute_lua_script(
        "claim_voucher",
        keys = [redis_key_inventory, redis_key_lock],
        args = [settings.CLAIM_COOLDOWN_SECONDS]
    )

    # Step 4.2

    
