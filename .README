[User] ---> [API Gateway / Backend]
                  |
                  v (Kiểm tra & Trừ số lượng cực nhanh)
            [Redis] 
                  |
                  v (Đẩy coupon trúng thưởng vào hàng đợi)
            [Kafka Producer] ---> [Kafka Topic]
                                       |
                                       v (Xử lý ngầm, lưu DB)
                                [Kafka Consumer] ---> [Database chính]


voucher-flashsale-system/       # Thư mục gốc dự án
│
├── docker-compose.yml          # Chạy chung cho cả Database, Kafka, Redis
├── .gitignore                  # Chặn các file rác, venv, .env đẩy lên GitHub
├── README.md                   # Hướng dẫn chạy dự án (Cách cài đặt, test)
│
├── frontend/                   # Toàn bộ code giao diện Web
│   ├── package.json            # Định nghĩa thư viện (nếu dùng React/Vue/Next.js)
│   ├── src/                    # Mã nguồn giao diện
│   │   ├── components/         # Các nút bấm, khung hiển thị (VoucherCard, Timer)
│   │   ├── services/           # Nơi viết code gọi API sang Backend (Axios/Fetch)
│   │   └── App.js              # File giao diện chính
│   └── public/
│
└── backend/                    # Toàn bộ phần logic bạn đã thiết kế ở câu trước
    ├── .env                    # Lưu cấu hình bí mật (Database URL, Kafka Host, Redis Host)
    ├── requirements.txt        # Danh sách các thư viện Python cần cài đặt
    ├── app/
    │   ├── __init__.py
    │   ├── main.py             # FastAPI Server
    │   ├── consumer.py         # Kafka Worker
    │   ├── core/               # Kết nối Redis, Kafka
    │   ├── database/           # Models, Session DB chính
    │   ├── scripts/            # Lua script
    │   ├── schemas/            # Pydantic schemas
    │   └── api/                # Router định nghĩa URL API

# Cấu trúc riêng cho phần Backend/App

backend/
│                           
├── app/                  # Thư mục chứa toàn bộ mã nguồn của ứng dụng
│   ├── __init__.py
│   ├── config.py         # Đọc dữ liệu từ file .env bằng Pydantic BaseSettings
│   ├── main.py           # File chạy chính của FastAPI (Khởi tạo App, Routes)
│   ├── consumer.py       # Worker chạy ngầm để lắng nghe Kafka và ghi vào DB
│   │
│   ├── core/             # Nơi quản lý các kết nối hệ thống (Lá chắn bên ngoài)
│   │   ├── __init__.py
│   │   ├── redis_client.py   # Quản lý Connection Pool của Redis và các hàm Lua Script
│   │   └── kafka_client.py   # Quản lý Kafka Producer (Kết nối, ngắt kết nối, bắn message)
│   │
│   ├── database/         # Nơi quản lý Database chính (Ví dụ: PostgreSQL/MySQL)
│   │   ├── __init__.py
│   │   ├── session.py        # Khởi tạo kết nối SQLAlchemy/Tortoise ORM
│   │   └── models.py         # Định nghĩa các bảng trong DB (User, Voucher, Campaign)
│   │
│   ├── scripts/          # Nơi lưu trữ các đoạn code Lua viết riêng cho sạch
│   │   └── claim_voucher.lua # Đoạn Lua Script trừ kho và check trùng user
│   │
│   ├── schemas/          # Định nghĩa kiểu dữ liệu Input/Output (Pydantic Models)
│   │   ├── __init__.py
│   │   └── voucher.py    # Schema cho Request/Response lúc săn voucher
│   │
│   └── api/              # Nơi định nghĩa các API Endpoints (Routes)
│       ├── __init__.py
│       └── router.py     # Định nghĩa URL /api/v1/campaigns/...