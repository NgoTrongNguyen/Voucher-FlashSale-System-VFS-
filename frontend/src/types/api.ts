export type CampaignStatus = 'SCHEDULED' | 'ACTIVE' | 'ENDED';
export type DiscountType = 'FIXED' | 'PERCENTAGE';
export type ClaimResponseStatus = 'PROCESSING' | 'SUCCESS' | 'FAILED';

export interface ClaimVoucherRequest {
  user_id: number;
  voucher_id: number;
}

export interface ClaimVoucherResponse {
  status: string;
  message: string;
  request_id: string;
}

export interface ClaimStatusResponse {
  status: ClaimResponseStatus;
  message: string;
  voucher?: {
    id: number;
    code: string;
    discount_type: DiscountType;
    discount_value: number;
  } | null;
}

export interface ErrorResponse {
  status?: string;
  message: string;
  detail?: string | null;
}

export interface HealthCheckResponse {
  status: string;
  database: string;
  redis: string;
  kafka: string;
}

export interface CampaignResponse {
  id: number;
  name: string;
  description?: string | null;
  start_time: string;
  end_time: string;
  status: CampaignStatus;
}

export interface CampaignListResponse {
  data: CampaignResponse[];
  total: number;
}

export interface VoucherResponse {
  id: number;
  code: string;
  description?: string | null;
  discount_type: DiscountType;
  discount_value: number;
  quantity_total: number;
  quantity_claimed: number;
  quantity_remaining?: number | null;
  min_order_value: number;
  created_at: string;
}

export interface VoucherListResponse {
  data: VoucherResponse[];
  total: number;
}
