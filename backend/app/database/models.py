from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Index, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()



# --- Helpers
def utc_now():
    return datetime.now(timezone.utc)



# --- Enums
class UserStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"

class CampaignStatusEnum(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"

class ClaimStatusEnum(str, enum.Enum):
    # Claim voucher status
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"



# --- Tables
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.ACTIVE)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    claim_records = relationship("ClaimRecord", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(CampaignStatusEnum), default=CampaignStatusEnum.SCHEDULED, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    vouchers = relationship("Voucher", back_populates="campaign", cascade="all, delete-orphan")
    
    # TODO: Can xem lai Index
    __table_args__ = (
        Index('idx_campaign_time', 'start_time', 'end_time'),
        Index('idx_campaign_status', 'status'),
    )
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name={self.name})>"


class Voucher(Base):
    __tablename__ = "vouchers"

    # TODO: Co the khong can foreign key, ngam hieu campaign_id choc den table campaign la duoc
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    discount_type = Column(String(20), default="FIXED")
    discount_value = Column(Float, nullable=False)
    quantity_total = Column(Integer, nullable=False)
    quantity_claimed = Column(Integer, default=0)
    min_order_value = Column(Float, default=0)
    max_uses_per_user = Column(Integer, default=1)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    campaign = relationship("Campaign", back_populates="vouchers")
    claim_records = relationship("ClaimRecord", back_populates="voucher", cascade="all, delete-orphan")

    @property
    def quantity_remaining(self):
        return self.quantity_total - self.quantity_claimed
    
    __table_args__ = (
        Index('idx_voucher_campaign', 'campaign_id'),
        Index('idx_voucher_code', 'code'),
    )

    def __repr__(self):
        return f"<Voucher(id={self.id}, code={self.code}, remaining={self.quantity_remaining})>"


class ClaimRecord(Base):
    __tablename__ = "claim_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    voucher_id = Column(Integer, ForeignKey('vouchers.id'), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), nullable=False, index=True)
    request_id = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(Enum(ClaimStatusEnum), default=ClaimStatusEnum.PENDING, index=True)
    failure_reason = Column(String(500), nullable=True)
    claimed_at = Column(DateTime, default=utc_now, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="claim_records")
    voucher = relationship("Voucher", back_populates="claim_records")
    campaign = relationship("Campaign")

    __table_args__ = (
        UniqueConstraint('user_id', 'voucher_id', name='unique_user_voucher_claim'),
        Index('idx_claim_user', 'user_id'),
        Index('idx_claim_voucher', 'voucher_id'),
        Index('idx_claim_campaign', 'campaign_id'),
        Index('idx_claim_status', 'status'),
        Index('idx_claim_time', 'claimed_at'),
    )

    def __repr__(self):
        return f"<ClaimRecord(id={self.id}, user_id={self.user_id}, voucher_id={self.voucher_id})>"


