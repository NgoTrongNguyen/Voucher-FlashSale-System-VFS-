from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


# Enums
class claimStatusEnum(str, Enum):
    PENDING = "PENDING"
    CLAIMED = "CLAIMED"
    FAILED = "FAILED"
    PROCESSING = "PROCESSING"


# Voucher Request Models
class claimVoucherRequest(BaseModel):
    user_id: int = Field(..., gt = 0, description= "ID của User")
    voucher_id: int = Field(..., gt = 0, description= "ID của Voucher")
    
    class config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "voucher": 1
            }
        }


#=============================
# Response Models
#=============================

# Voucher Response Models
class claimVoucherResponse(BaseModel):
    # Responses khi claim voucher
    status: str = Field(..., description="PROCESSING")
    message: str = Field(..., description="Mô tả trạng thái")
    request_id: str = Field(..., description="ID của request, dùng để tra cứu sau này")

    class config:
        json_schema_extra = {
            "example": {
                "status": "PROCESSING",
                "message": "Yêu cầu đang được xử lý",
                "request_id": "req_abc123xyz"
            }
        }

    class config:
        json_schema_extra = {
            "example": {
                "status": "PROCESSING",
                "message": "Yêu cầu đang được xử lý",
                "request_id": "req_abc123xyz"
            }
        }
class checkclaimVoucherResponse(BaseModel):
    status: str = Field(..., description="PROCESSING")
    message: str = Field(..., description="Mô tả trạng thái")
    voucher_id: Optional[dict] = Field(None, description="Thông tin voucher nếu claim thành công")

    
    class config:
        json_schema_extra = {
            "example": {
                "status": "SUCCESS",
                "message": "Yêu cầu đang được xử lý",
                "voucher_id": {
                    "id": 1,
                    "code": "VOUCHER123",
                    "discount_type": "PERCENTAGE",
                    "discount_value": 20.0,
                }
            }
        }

# Error Response Model
class ErrorResponse(BaseModel):
    status: str = "ERROR"
    message: str = Field(..., description ="Mô tả lỗi")
    detail: Optional[str] = None

    class config:
        json_schema_extra = {
            "example": { 
                "status": "ERROR",
                "message": "Hết voucher",
                "detail": "Không còn voucher nào để claim",
            }
        }

# Health Check Response Model
class HealthCheckResponse(BaseModel):
    status: str = "OK",
    database: str = Field(..., description="DB status"),
    redis: str = Field(..., description="Redis status"),
    kafka: str = Field(..., description="Kafka status")

    class config:
        json_schema_extra = {
            "example": {
                "status": "OK",
                "database": "connected",
                "redis": "connected",
                "kafka": "connected"
            }
        }

#=============================
# Schemas
#=============================

# Campaign Schema
class CampaignResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    status: str

    class config:
        from_attributes = True

class CampaignListResponse(BaseModel):
    data: list[CampaignResponse]
    total: int = Field(..., description="Tổng số campaign")

# Voucher Schema
class VoucherResponse(BaseModel):
    id: int
    code: str
    description: Optional[str] = None
    discount_type: str
    discount_value: float
    quantity_total: int
    quantity_claimed: int
    quantity_remaining: Optional[int] = None
    min_order_value: float
    created_at: datetime

    class config:
        from_attributes = True

    def calculate_remaining(self):
        self.quantity_remaining = self.quantity_total - self.quantity_claimed

class VoucherListResponse(BaseModel):
    data: list[VoucherResponse]
    total: int = Field(..., description="Tổng số voucher")
