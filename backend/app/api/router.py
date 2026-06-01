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
