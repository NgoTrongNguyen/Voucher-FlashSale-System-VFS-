Hệ Thống Săn Voucher Giảm Giá Tốc Độ Cao (Flash Sale System)
Dự án cá nhân mô phỏng hệ thống săn voucher khung giờ vàng trên các sàn Thương mại Điện tử (TMĐT). Hệ thống được thiết kế theo kiến trúc phân tầng (Layered Architecture), giải quyết bài toán tải cao (High-Concurrency), chống nghẽn Cơ sở dữ liệu (Database) và ngăn chặn tình trạng bán lố (Overselling) bằng cách kết hợp FastAPI (Python), Redis (Lua Script) và Kafka.

📌 Kiến Trúc Hệ Thống (Architecture Overview)
Hệ thống sử dụng cơ chế xử lý bất đồng bộ (Asynchronous) và phân tách luồng dữ liệu (Decoupling) để tối ưu hiệu năng:

Lá chắn vòng ngoài (Redis): Khi người dùng nhấn "Săn", hệ thống không ghi trực tiếp vào DB mà chạy một đoạn mã Lua Script trực tiếp trên RAM của Redis để kiểm tra điều kiện trùng lặp (Anti-cheat) và trừ số lượng kho (quantity) một cách nguyên tử (Atomic).

Hàng đợi giảm áp (Kafka): Nếu Redis xác nhận hợp lệ, một sự kiện (Event) được đẩy vào Kafka Topic. Backend lập tức trả về phản hồi "Đang xử lý" cho giao diện Web (Frontend) trong vài mili-giây.

Xử lý ngầm (Worker/Consumer): Một tiến trình Worker chạy độc lập sẽ tiêu thụ (Consume) các tin nhắn từ Kafka và thực hiện ghi dữ liệu trúng thưởng một cách an toàn, tuần tự vào Database chính.

📂 Cấu Trúc Thư Mục Dự Án (Project Structure)

voucher-flashsale-system/       # Thư mục gốc dự án
│
├── docker-compose.yml          # Cấu hình môi trường chứa hạ tầng (Postgres, Kafka, Redis)
├── .gitignore                  # Chặn các file rác, môi trường ảo lên Git
├── README.md                   # Tài liệu hướng dẫn hệ thống
│
├── frontend/                   # 🖥️ Giao diện Web Client
│   ├── package.json            
│   ├── src/                    
│   │   ├── components/         # Giao diện nút bấm, thẻ hiển thị voucher, đồng hồ đếm ngược
│   │   ├── services/           # Trình gọi API kết nối sang Backend (Axios / Fetch)
│   │   └── App.js              
│   └── public/
│
└── backend/                    # ⚙️ Logic xử lý Backend Server
    ├── .env                    # Quản lý các biến môi trường bí mật
    ├── requirements.txt        # Danh sách thư viện Python cần cài đặt
    └── app/                    
        ├── __init__.py
        ├── config.py           # Đọc và quản lý cấu hình hệ thống bằng Pydantic
        ├── main.py             # FastAPI App chính (Cấu hình CORS, Lifespan Event)
        ├── consumer.py         # Worker xử lý ngầm (Kafka Consumer) ghi nhận vào DB
        │
        ├── core/               # Quản lý các kết nối hạ tầng hệ thống
        │   ├── __init__.py
        │   ├── redis_client.py # Connection Pool của Redis và trình chạy Lua Script
        │   └── kafka_client.py # Khởi tạo và quản lý Kafka Producer
        │
        ├── database/           # Tầng quản lý dữ liệu lưu trữ bền vững
        │   ├── __init__.py
        │   ├── session.py      # Cấu hình nạp session ORM kết nối tới DB gốc
        │   └── models.py       # Định nghĩa các thực thể bảng (User, Campaign, Voucher)
        │
        ├── scripts/            # Chứa các tập lệnh kịch bản mở rộng
        │   └── claim_voucher.lua # Lua Script kiểm tra chặn trùng & trừ kho trên RAM
        │
        ├── schemas/            # Định nghĩa định dạng dữ liệu truyền tải
        │   ├── __init__.py
        │   └── voucher.py      # Pydantic Model kiểm định dữ liệu Request/Response
        │
        └── api/                # Nơi định nghĩa phân luồng điều hướng API
            ├── __init__.py
            └── router.py       # Định nghĩa các endpoints cụ thể (/api/v1/...)



🚀 Hướng Dẫn Cài Đặt & Chạy Dự Án
1. Chuẩn bị môi trường hạ tầng
Đảm bảo máy tính của bạn đã được cài đặt Docker và Docker Compose. Tại thư mục gốc của dự án, khởi động toàn bộ hạ tầng (PostgreSQL, Kafka, Zookeeper, Redis) bằng lệnh:

Bash
docker compose up -d
2. Cài đặt và Chạy Backend
Di chuyển vào thư mục backend, tạo môi trường ảo Python và tiến hành cài đặt thư viện:

Bash
cd backend
python -m venv venv
source venv/bin/activate  # Trên Windows dùng: venv\Scripts\activate
pip install -r requirements.txt
Cấu hình file .env nằm trong thư mục backend/ với các thông số phù hợp (mẫu cấu hình có sẵn trong file hướng dẫn cụ thể). Sau đó:

Chạy API Server:

Bash
uvicorn app.main:app --reload --port 8000
Chạy Worker lưu DB (Mở một Terminal mới):

Bash
python -m app.consumer
3. Cài đặt và Chạy Frontend
Di chuyển vào thư mục frontend, tiến hành cài đặt các gói phụ thuộc và khởi chạy giao diện:

Bash
cd ../frontend
npm install
npm start
Giao diện ứng dụng sẽ được chạy tại địa chỉ: http://localhost:3000

🛠️ Công Nghệ Sử Dụng (Tech Stack)
Frontend: React.js / Vue.js, TailwindCSS (Tối ưu hóa giao diện và tăng tốc độ hiển thị).

Backend Framework: FastAPI (Tận dụng cơ chế async/await xử lý bất đồng bộ, tốc độ tiệm cận NodeJS và Go).

Caching & In-Memory Logic: Redis (Sử dụng cấu hình Connection Pool + Lua Script loại bỏ triệt để hiện tượng Race Condition khi luồng request đâm vào cùng lúc).

Message Broker: Apache Kafka (Phân tách luồng xử lý nặng, đảm bảo thứ tự tin nhắn theo phân vùng Partition Key dựa trên mã định danh User).

Database: PostgreSQL / MySQL (Lưu trữ trạng thái hóa đơn, thông tin Voucher chính thức một cách toàn vẹn).