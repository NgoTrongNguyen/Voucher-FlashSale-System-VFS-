import axios, { AxiosError } from 'axios';
import type { ErrorResponse } from '../types/api';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

interface ApiErrorPayload {
  status?: string;
  message: string;
  detail?: string | null;
}

export const extractApiError = (error: unknown): ApiErrorPayload => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ErrorResponse>;
    if (axiosError.response?.data) {
      const payload = axiosError.response.data;
      return {
        status: payload.status,
        message: payload.message ?? axiosError.message,
        detail: payload.detail,
      };
    }

    return {
      message: axiosError.message || 'Unknown API error',
      detail: axiosError.code ?? null,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message,
    };
  }

  return {
    message: 'An unknown error occurred.',
  };
};

apiClient.interceptors.request.use((config) => {
  const accessToken = localStorage.getItem('auth_token');
  if (accessToken && config.headers) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const payload = extractApiError(error);
    return Promise.reject(payload);
  }
);
