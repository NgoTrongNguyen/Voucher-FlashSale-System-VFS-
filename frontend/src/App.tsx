import { useEffect, useMemo, useState } from 'react';
import { getCampaigns } from './services/voucherService';
import type { CampaignResponse, ErrorResponse } from './types/api';

const formatDate = (value: string) => new Date(value).toLocaleString(undefined, {
  year: 'numeric',
  month: 'short',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
});

function App() {
  const [campaigns, setCampaigns] = useState<CampaignResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    getCampaigns('ACTIVE')
      .then((data) => {
        setCampaigns(data.data);
      })
      .catch((err: ErrorResponse) => {
        setError(err.message || 'Không thể tải campaign');
      })
      .finally(() => setIsLoading(false));
  }, []);

  const emptyMessage = useMemo(() => {
    if (isLoading) return null;
    if (error) return null;
    return campaigns.length === 0 ? 'Không có chiến dịch flash sale nào đang hoạt động.' : null;
  }, [campaigns, error, isLoading]);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8 rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur">
          <h1 className="text-3xl font-semibold text-slate-900">Voucher Flash Sale</h1>
          <p className="mt-2 text-slate-600">Tải danh sách campaign trực tiếp từ backend và chuẩn bị các tính năng claim voucher.</p>
        </header>

        <section className="grid gap-6 md:grid-cols-2">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-900">Campaign đang hoạt động</h2>
                <p className="mt-1 text-sm text-slate-500">Danh sách được lấy từ API /api/v1/campaigns</p>
              </div>
            </div>

            {isLoading ? (
              <div className="rounded-2xl bg-slate-100 p-6 text-slate-700">Đang tải dữ liệu...</div>
            ) : error ? (
              <div className="rounded-2xl bg-rose-50 p-6 text-rose-700">Lỗi: {error}</div>
            ) : emptyMessage ? (
              <div className="rounded-2xl bg-slate-100 p-6 text-slate-700">{emptyMessage}</div>
            ) : (
              <div className="space-y-4">
                {campaigns.map((campaign) => (
                  <article key={campaign.id} className="rounded-3xl border border-slate-200 bg-slate-50 p-4 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h3 className="text-lg font-semibold text-slate-900">{campaign.name}</h3>
                        <p className="mt-1 text-sm text-slate-600">{campaign.description ?? 'Không có mô tả.'}</p>
                      </div>
                      <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.16em] text-emerald-800">{campaign.status}</span>
                    </div>
                    <dl className="mt-4 grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                      <div>
                        <dt className="font-medium">Bắt đầu</dt>
                        <dd>{formatDate(campaign.start_time)}</dd>
                      </div>
                      <div>
                        <dt className="font-medium">Kết thúc</dt>
                        <dd>{formatDate(campaign.end_time)}</dd>
                      </div>
                    </dl>
                  </article>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-xl font-semibold text-slate-900">Kết nối backend</h2>
            <p className="mt-2 text-sm text-slate-600">Sử dụng cấu hình API để gọi các endpoint hiện có.</p>
            <div className="mt-6 space-y-3 text-sm text-slate-700">
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="font-medium text-slate-900">Base URL</p>
                <p className="mt-1 text-slate-600">{import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}</p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4">
                <p className="font-medium text-slate-900">Endpoints</p>
                <ul className="mt-2 space-y-1 text-slate-600">
                  <li>GET /api/v1/campaigns</li>
                  <li>GET /api/v1/campaigns/{'{campaign_id}'}/vouchers</li>
                  <li>POST /api/v1/vouchers/claim</li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
