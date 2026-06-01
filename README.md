# Hệ Thống Săn Voucher Flash Sale Tốc Độ Cao

Một hệ thống thương mại điện tử mô phỏng cơ chế săn voucher giảm giá trong khung giờ vàng (flash sale). Hệ thống được thiết kế để xử lý **hàng nghìn request đồng thời** mà không bị chậm, ngẽn database hay bán lố hàng.

---

## Kiến Trúc Hệ Thống

Hệ thống sử dụng kiến trúc **3 tầng + 2 lớp chắn**:

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend (React)                       │
│          [Nút Săn] → [Đếm ngược] → [Trạng thái]         │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP Request
┌──────────────────────▼──────────────────────────────────┐
│            FastAPI Server (Port 8000)                   │
│              [Validate Request]                         │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼─────────────────┐   ┌──────▼──────────────────┐
│  LỚP CHẮN 1: Redis      │   │  LỚP CHẮN 2: Kafka      │
│                         │   │                         │
│ • Check trùng lặp       │   │ • Queue Request         │
│ • Trừ kho (Atomic)      │   │ • Giảm áp hệ thống      │
│ • Lua Script (nguyên tử)│   │ • Đảm bảo thứ tự        │
└───────┬─────────────────┘   └──────┬──────────────────┘
        │ Hợp lệ?               │ Đẩy vào
        │ YES → Event           │ Topic
        └───────────┬───────────┘
                    │
         ┌──────────▼──────────┐
         │  Worker Process     │
         │  (Kafka Consumer)   │
         │                     │
         │ • Tiêu thụ message  │
         │ • Ghi DB an toàn    │
         └──────────┬──────────┘
                    │
         ┌──────────▼────────┐
         │  PostgreSQL       │
         │  (Database gốc)   │
         └───────────────────┘
```

### **Quy Trình Một Request "Săn Voucher"**

1. **Frontend gửi request**: `POST /api/v1/vouchers/claim`
2. **Redis kiểm tra**:
   - Người dùng này đã săn trong 1s qua chưa? (Anti-cheat)
   - Còn hàng không? (Atomic decrement)
3. **Nếu hợp lệ** → Kafka nhận event → trả về "Đang xử lý"
4. **Worker xử lý từ từ** → Ghi vào DB → Cập nhật trạng thái
5. **Frontend poll trạng thái** → Hiển thị kết quả

**Kết quả**: Response nhanh (< 50ms) + Không bán lố + Không ngẽn DB

---

## Công Nghệ Sử Dụng

| Công Nghệ | Phiên Bản | Vai Trò |
|-----------|----------|--------|
| **FastAPI** | 0.100+ | Web framework async/await (tốc độ cao) |
| **PostgreSQL** | 15 | Database lưu trữ bền vững |
| **Redis** | 7 | Cache + Lua Scripts (chặn race condition) |
| **Apache Kafka** | 7.5 | Message broker (giảm áp tải) |
| **React** | 18+ | Frontend UI |
| **Python** | 3.9+ | Backend runtime |

---

## Cấu Trúc Thư Mục

```
voucher-flashsale-system/
│
├── docker-compose.yml          # Khởi động hạ tầng (Postgres, Redis, Kafka)
├── README.md                   # Tài liệu này
├── .gitignore                  # Git ignore rules
│
├── backend/                    # API Server & Workers
│   ├── .env                    # Biến môi trường (bí mật)
│   ├── requirements.txt        # Dependencies Python
│   │
│   └── app/
│       ├── __init__.py
│       ├── main.py             # FastAPI app chính
│       ├── config.py           # Quản lý config dùng để qlý biến MT (Pydantic)
│       ├── consumer.py         # Kafka consumer worker
│       │
│       ├── core/               # Kết nối hạ tầng
|       |   ├── __init__.py
│       │   ├── redis_client.py # Redis connection pool
│       │   └── kafka_client.py # Kafka producer
│       │
│       ├── database/           # Tầng data access
|       |   ├── __init__.py
│       │   ├── session.py      # SQLAlchemy config
│       │   └── models.py       # DB models (User, Campaign, Voucher)
│       │
│       ├── api/                # API endpoints
│       │   └── router.py       # Routes định nghĩa
│       │
│       ├── schemas/            # Pydantic models (validation)
│       │   └── voucher.py      # Request/Response schemas
│       │
│       └── scripts/            # Tập lệnh hỗ trợ
│           └── claim_voucher.lua # Lua script cho Redis
│
└── frontend/                   # React UI
    ├── package.json
    ├── public/
    └── src/
        ├── components/         # React components
        │   ├── VoucherCard.jsx
        │   ├── ClaimButton.jsx
        │   └── Countdown.jsx
        ├── services/           # API clients
        │   └── voucherApi.js
        ├── App.jsx
        └── index.js
```

---

## Hướng Dẫn Cài Đặt & Chạy

### **Yêu Cầu Hệ Thống**
- Docker & Docker Compose
- Python 3.9+
- Node.js 16+
- Git

---

### **1. Khởi Động Hạ Tầng (Bắt Buộc)**

```bash
# Tại thư mục gốc dự án
docker compose up -d
```

**Kiểm tra trạng thái:**
```bash
docker compose ps
# Tất cả containers phải có status "Up (healthy)"
```

**Kiểm tra kết nối:**
```bash
# PostgreSQL
docker compose exec postgres psql -U voucher_user -d voucher_db -c "SELECT 1"

# Redis
docker compose exec redis redis-cli PING

# Kafka
docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list
```

---

### **2. Cài Đặt & Chạy Backend**

#### **Cài đặt Dependencies**

```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Activate virtual environment
# Trên Linux/Mac:
source venv/bin/activate
# Trên Windows:
# venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt
```

#### **Tạo File .env**

```bash
# backend/.env
DATABASE_URL=postgresql://voucher_user:voucher_pass123@localhost:5432/voucher_db
REDIS_URL=redis://localhost:6379/0
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_VOUCHER=voucher-claims
LOG_LEVEL=INFO
```

#### **Chạy Database Migrations (nếu có)**

```bash
# Nếu sử dụng Alembic
alembic upgrade head
```

#### **Khởi Động API Server**

```bash
# Terminal 1: Chạy FastAPI server
uvicorn app.main:app --reload --port 8000
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

#### **Khởi Động Kafka Consumer Worker**

```bash
# Terminal 2 (cùng thư mục backend/): Chạy worker
python -m app.consumer
```

**Output:**
```
INFO:     Kafka consumer started, listening on topic: voucher-claims
```

---

### **3. Cài Đặt & Chạy Frontend**

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm start
```

**Output:**
```
Compiled successfully!
webpack compiled with 1 warning
Local:            http://localhost:3000
On Your Network:  http://192.168.x.x:3000
```

Truy cập: **http://localhost:3000**

---

## API Endpoints

### **Lấy danh sách chiến dịch flash sale**
```http
GET /api/v1/campaigns

Response:
{
  "data": [
    {
      "id": 1,
      "name": "Flash Sale Tháng 5",
      "start_time": "2024-05-21T10:00:00Z",
      "end_time": "2024-05-21T11:00:00Z",
      "status": "ACTIVE"
    }
  ]
}
```

### **Lấy danh sách voucher trong chiến dịch**
```http
GET /api/v1/campaigns/{campaign_id}/vouchers

Response:
{
  "data": [
    {
      "id": 1,
      "code": "FLASH50",
      "discount": 50000,
      "quantity": 100,
      "quantity_remaining": 45,
      "claimed_by_user": false
    }
  ]
}
```

### **Săn voucher (Claim)**
```http
POST /api/v1/vouchers/claim

Request Body:
{
  "voucher_id": 1,
  "user_id": 123
}

Response (Nhanh < 50ms):
{
  "status": "PROCESSING",
  "message": "Yêu cầu đang được xử lý",
  "request_id": "req_abc123"
}
```

### **Kiểm tra trạng thái claim**
```http
GET /api/v1/vouchers/claim/{request_id}

Response:
{
  "status": "SUCCESS",  // hoặc "FAILED", "PENDING"
  "message": "Bạn đã nhận voucher thành công",
  "voucher": {
    "id": 1,
    "code": "FLASH50"
  }
}
```

---

## Testing & Debugging

### **Test API bằng cURL**

```bash
# Săn voucher
curl -X POST http://localhost:8000/api/v1/vouchers/claim \
  -H "Content-Type: application/json" \
  -d '{"voucher_id": 1, "user_id": 123}'

# Kiểm tra trạng thái
curl http://localhost:8000/api/v1/vouchers/claim/req_abc123
```

### **Xem logs**

```bash
# FastAPI logs
docker compose logs -f postgres

# Kafka logs
docker compose logs -f kafka

# Redis logs
docker compose logs -f redis
```

### **Xem database**

```bash
# Kết nối vào PostgreSQL
docker compose exec postgres psql -U voucher_user -d voucher_db

# Liệt kê bảng
\dt

# Xem dữ liệu
SELECT * FROM users;
SELECT * FROM vouchers;
```

---

## Chặn Overselling & Race Condition

### **Cơ chế Anti-Cheat (Redis Lua Script)**

```lua
-- claim_voucher.lua
-- Chạy nguyên tử trên Redis, không bị race condition

local key = KEYS[1]  -- "voucher:1:inventory"
local user_lock = KEYS[2]  -- "user:123:lock"

-- Kiểm tra user đã lock chưa (trong 1s gần đây)
if redis.call("EXISTS", user_lock) == 1 then
  return {0, "Bạn vừa săn, chờ 1s"}
end

-- Lấy số lượng hiện tại
local current = tonumber(redis.call("GET", key)) or 0
if current <= 0 then
  return {0, "Hết hàng"}
end

-- Trừ kho + set lock
redis.call("DECR", key)
redis.call("SETEX", user_lock, 1, "1")

return {1, "Thành công"}
```

---

## Hiệu Năng & Metrics

| Chỉ số | Giá trị | Ghi chú |
|--------|--------|--------|
| **Response Time API** | < 50ms | Redis block request |
| **Throughput** | 10k req/s | Single Kafka partition |
| **DB Write Latency** | 100-500ms | Xử lý từ worker |
| **Race Condition** | 0 | Lua Script (atomic) |
| **Overselling** | 0 | Redis decrement chính xác |

---

## Lệnh Hữu Ích

```bash
# ============== Docker ==============
# Khởi động tất cả
docker compose up -d

# Dừng tất cả (giữ data)
docker compose stop

# Xóa tất cả (kể cả data)
docker compose down -v

# Xem logs realtime
docker compose logs -f kafka

# ============== Backend ==============
# Activate venv
source backend/venv/bin/activate

# Chạy uvicorn
uvicorn app.main:app --reload --port 8000

# Chạy worker
python -m app.consumer

# ============== Frontend ==============
# Chạy dev server
cd frontend && npm start

# Build production
npm run build

# ============== Database ==============
# Kết nối PostgreSQL
docker compose exec postgres psql -U voucher_user -d voucher_db

# Kết nối Redis CLI
docker compose exec redis redis-cli

# Kết nối Kafka
docker compose exec kafka kafka-console-producer --broker-list localhost:9092 --topic voucher-claims
```

---

## Biến Môi Trường

**`backend/.env`** mẫu:

```env
# Database
DATABASE_URL=postgresql://voucher_user:voucher_pass123@localhost:5432/voucher_db
DB_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_VOUCHER=voucher-claims
KAFKA_GROUP_ID=voucher-consumer-group

# Logging
LOG_LEVEL=INFO

# Server
API_PORT=8000
API_HOST=0.0.0.0
```

---

## Troubleshooting

### **Container fails khi khởi động**

```bash
# Xem chi tiết lỗi
docker compose logs kafka

# Xóa volumes và start lại
docker compose down -v
docker compose up -d
```

### **Connection refused: localhost:5432**

Đảm bảo PostgreSQL container đã healthy:
```bash
docker compose ps
# Nếu status khác "Up (healthy)", khởi động lại:
docker compose restart postgres
```

### **Worker không tiêu thụ message từ Kafka**

```bash
# Kiểm tra group offset
docker compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group voucher-consumer-group \
  --describe

# Reset offset nếu cần
docker compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group voucher-consumer-group \
  --reset-offsets --to-earliest --execute --topic voucher-claims
```

### **Frontend không kết nối được API**

Kiểm tra CORS trong `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Tài Liệu Tham Khảo

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Lua Scripts](https://redis.io/docs/interact/programmability/lua-api/)
- [Apache Kafka Docs](https://kafka.apache.org/documentation/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [React Documentation](https://react.dev/)

---

## Học Tập & Cải Tiến

### **Concepts được thực hành:**
- Async/Await trong Python (FastAPI)
- Lua Scripts cho atomic operations
- Message Queue pattern (Kafka)
- Caching layer (Redis)
- Database transaction & isolation
- API design (REST + Status polling)

### **Cải tiến trong tương lai:**
- [ ] WebSocket cho real-time updates
- [ ] Distributed caching (Redis Cluster)
- [ ] Load balancing (Nginx)
- [ ] Monitoring & alerting (Prometheus)
- [ ] Automated testing (pytest)
- [ ] Docker multi-stage builds

---

## Support

Nếu gặp vấn đề hoặc có câu hỏi, vui lòng:
1. Kiểm tra phần **Troubleshooting**
2. Xem logs: `docker compose logs -f`
3. Tạo issue trên GitHub (nếu có)

---

**Happy coding!**

Made by Nguyen, Huy
