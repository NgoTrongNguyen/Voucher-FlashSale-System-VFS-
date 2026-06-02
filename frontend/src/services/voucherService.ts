import type {
  CampaignListResponse,
  CampaignResponse,
  VoucherListResponse,
  VoucherResponse,
  ClaimVoucherRequest,
  ClaimVoucherResponse,
  ClaimStatusResponse,
  HealthCheckResponse,
  CampaignStatus,
} from '../types/api';
import { apiClient } from './api';

const API_PREFIX = '/api/v1';

export const getCampaigns = async (status?: CampaignStatus): Promise<CampaignListResponse> => {
  const response = await apiClient.get<CampaignListResponse>(`${API_PREFIX}/campaigns`, {
    params: status ? { status } : undefined,
  });
  return response.data;
};

export const getCampaign = async (campaignId: number): Promise<CampaignResponse> => {
  const response = await apiClient.get<CampaignResponse>(`${API_PREFIX}/campaigns/${campaignId}`);
  return response.data;
};

export const getVouchers = async (campaignId: number): Promise<VoucherListResponse> => {
  const response = await apiClient.get<VoucherListResponse>(`${API_PREFIX}/campaigns/${campaignId}/vouchers`);
  return response.data;
};

export const getVoucher = async (voucherId: number): Promise<VoucherResponse> => {
  const response = await apiClient.get<VoucherResponse>(`${API_PREFIX}/vouchers/${voucherId}`);
  return response.data;
};

export const claimVoucher = async (
  payload: ClaimVoucherRequest
): Promise<ClaimVoucherResponse> => {
  const response = await apiClient.post<ClaimVoucherResponse>(`${API_PREFIX}/vouchers/claim`, payload);
  return response.data;
};

export const getClaimStatus = async (requestId: string): Promise<ClaimStatusResponse> => {
  const response = await apiClient.get<ClaimStatusResponse>(`${API_PREFIX}/vouchers/claim/${requestId}`);
  return response.data;
};

export const getHealthCheck = async (): Promise<HealthCheckResponse> => {
  const response = await apiClient.get<HealthCheckResponse>(`${API_PREFIX}/health`);
  return response.data;
};
