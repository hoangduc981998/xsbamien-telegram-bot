# 🎰 XS Ba Miền - Bot Telegram Tra Cứu Xổ Số 3 Miền

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)
![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-21.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Bot Telegram tra cứu kết quả xổ số nhanh chóng, chính xác cho cả 3 miền Bắc - Trung - Nam**

[Demo](#-demo) • [Tính Năng](#-tính-năng) • [Cài Đặt](#-cài-đặt) • [Sử Dụng](#-sử-dụng) • [Đóng Góp](#-đóng-góp)

</div>

---

## 📖 Giới Thiệu

**XS Ba Miền Bot** là bot Telegram giúp tra cứu kết quả xổ số cực nhanh, hỗ trợ đầy đủ:
- 🔴 **Miền Bắc** (1 tỉnh)
- 🟠 **Miền Trung** (14 tỉnh)  
- 🟢 **Miền Nam** (21 tỉnh)

### ✨ Điểm Nổi Bật
- ⚡ **Phản hồi cực nhanh** - Dưới 2 giây
- 🎨 **Giao diện đẹp** - Inline keyboards chuyên nghiệp
- 📊 **Thống kê chi tiết** - Lô 2 số, 3 số, đầu-đuôi, lô gan
- 🔔 **Nhắc nhở tự động** - Thông báo khi có kết quả mới
- 🌐 **Open Source** - Miễn phí, phục vụ cộng đồng

---

## 🎯 Tính Năng

### 🎰 Tra Cứu Kết Quả
- ✅ Kết quả hôm nay theo miền
- ✅ Kết quả theo tỉnh/thành cụ thể
- ✅ Lịch sử 30 kỳ gần nhất
- ✅ Hiển thị đẹp mắt với bảng Unicode

### 📊 Thống Kê & Phân Tích
- 📈 Thống kê lô 2 số (00-99)
- 📈 Thống kê lô 3 số (000-999)
- 📈 Phân tích đầu-đuôi
- 📈 Tính lô gan (số lâu chưa về)

### 🔔 Thông Báo Thông Minh
- ⏰ Nhắc trước giờ quay (15 phút)
- 🎊 Thông báo kết quả ngay khi có
- 🎯 Đăng ký theo tỉnh yêu thích

### 📅 Lịch Quay Thưởng
- 🟢 **Miền Nam**: 16:15 - 16:45
- 🟠 **Miền Trung**: 17:15 - 17:45
- 🔴 **Miền Bắc**: 18:15 - 18:30

---

## 🚀 Cài Đặt

### Yêu Cầu
- Python 3.12+
- Telegram Bot Token ([Tạo bot](https://t.me/BotFather))
- Redis (tùy chọn, cho production)

### Cài Đặt Nhanh

#### 1️⃣ Clone Repository
```bash
git clone https://github.com/hoangduc981998/xsbamien-telegram-bot.git
cd xsbamien-telegram-bot
```

#### 2️⃣ Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

#### 3️⃣ Cấu Hình
```bash
cp .env.example .env
nano .env  # Thêm TELEGRAM_BOT_TOKEN
```

#### 4️⃣ Chạy Bot
```bash
python -m app.main
```

### 🐳 Chạy Với Docker

```bash
docker-compose up -d
```

---

## 💡 Sử Dụng

### Lệnh Cơ Bản

| Lệnh | Mô Tả |
|------|-------|
| `/start` | Khởi động bot, hiện menu chính |
| `/help` | Xem hướng dẫn chi tiết |
| `/mb` | Kết quả Miền Bắc hôm nay |
| `/mt` | Kết quả Miền Trung hôm nay |
| `/mn` | Kết quả Miền Nam hôm nay |

### Tra Cứu Nhanh

```
/latest TPHCM          # Kỳ mới nhất TP.HCM
/province DANA         # Kết quả Đà Nẵng
/stats MIBA 2digit     # Thống kê lô 2 số Miền Bắc
```

### Đăng Ký Nhắc Nhở

```
/subscribe TPHCM       # Nhận thông báo TP.HCM
/unsubscribe TPHCM     # Hủy nhận thông báo
/mysubs                # Xem danh sách đã đăng ký
```

---

## 🏗️ Kiến Trúc

```
┌─────────────┐
│  Telegram   │
│   Users     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│     Bot Layer (PTB v21)         │
│  • Command Handlers             │
│  • Callback Handlers            │
│  • Error Handlers               │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│      Service Layer              │
│  • Mu88Client (API)             │
│  • Cache (Redis/SQLite)         │
│  • Stats Service                │
│  • Scheduler (APScheduler)      │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│       Data Layer                │
│  • API mu88.live                │
│  • Redis Cache                  │
│  • SQLite (fallback)            │
└─────────────────────────────────┘
```

---

## 🗂️ Cấu Trúc Dự Án

```
xsbamien-telegram-bot/
├── app/
│   ├── main.py              # Entry point
│   ├── config.py            # Cấu hình toàn cục
│   │
│   ├── ui/                  # UI/UX Layer
│   │   ├── keyboards.py     # Inline keyboards
│   │   ├── messages.py      # Message templates
│   │   └── formatters.py    # Format kết quả
│   │
│   ├── handlers/            # Request Handlers
│   │   ├── commands.py      # Command handlers
│   │   ├── callbacks.py     # Callback handlers
│   │   └── errors.py        # Error handlers
│   │
│   ├── services/            # Business Logic
│   │   ├── mu88_client.py   # API client
│   │   ├── cache.py         # Cache layer
│   │   ├── stats.py         # Thống kê
│   │   └── subscription.py  # Đăng ký nhắc
│   │
│   └── models/              # Data Models
│       └── lottery.py       # Pydantic models
│
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker build
└── docker-compose.yml       # Docker orchestration
```

---

## 📊 Danh Sách Tỉnh/Thành

### 🔴 Miền Bắc (1)
- `MIBA` - Miền Bắc

### 🟢 Miền Nam (21)
`TPHCM`, `BALI`, `BETR`, `ANGI`, `BIDU`, `BIPH`, `BITH`, `CAMA`, `CATH`, `DALAT`, `DONA`, `DOTH`, `HAGI`, `KIGI`, `LOAN`, `SOTR`, `TANI`, `TIGI`, `TRVI`, `VILO`, `VUTA`

### 🟠 Miền Trung (14)
`DANA`, `BIDI`, `DALAK`, `DANO`, `GILA`, `KHHO`, `KOTU`, `NITH`, `PHYE`, `QUBI`, `QUNA`, `QUNG`, `QUTR`, `THTH`

---

## 🛠️ Tech Stack

- **Language**: Python 3.12
- **Bot Framework**: [python-telegram-bot](https://python-telegram-bot.org/) v21
- **HTTP Client**: httpx
- **Cache**: Redis / SQLite
- **Scheduler**: APScheduler
- **Validation**: Pydantic
- **Metrics**: Prometheus
- **Container**: Docker

---

## 🗓️ Roadmap

### ✅ Phase 1 - MVP (Hoàn Thành)
- [x] Cấu trúc dự án
- [x] UI/UX với inline keyboards
- [x] Commands cơ bản
- [x] Mock data demo

### 🚧 Phase 2 - Core Features (Đang Phát Triển)
- [ ] Tích hợp API mu88.live
- [ ] Cache layer (Redis)
- [ ] Thống kê cơ bản
- [ ] Lịch quay thưởng

### 📋 Phase 3 - Advanced Features
- [ ] Subscription system
- [ ] APScheduler jobs
- [ ] Metrics & monitoring
- [ ] Admin dashboard

### 🎨 Phase 4 - Polish
- [ ] i18n (Tiếng Việt/English)
- [ ] Export ảnh kết quả
- [ ] Grafana dashboard
- [ ] Load testing

---

## 🤝 Đóng Góp

Mọi đóng góp đều được hoan nghênh! 

### Cách Đóng Góp
1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

### Quy Tắc Code
- Tuân thủ PEP 8
- Comment bằng tiếng Việt
- Viết docstring đầy đủ
- Test trước khi commit

---

## 📝 License

Dự án này được phân phối dưới giấy phép MIT. Xem file `LICENSE` để biết thêm chi tiết.

---

## 👨‍💻 Tác Giả

**Hoàng Đức**
- GitHub: [@hoangduc981998](https://github.com/hoangduc981998)
- Telegram: [Coming Soon]

---

## 🙏 Lời Cảm Ơn

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Amazing bot framework
- [mu88.live](https://mu88.live) - API data source
- Cộng đồng Python Việt Nam

---

## 📞 Liên Hệ & Hỗ Trợ

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/hoangduc981998/xsbamien-telegram-bot/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/hoangduc981998/xsbamien-telegram-bot/discussions)
- 📧 **Email**: [Coming Soon]

---

<div align="center">

**⭐ Nếu dự án hữu ích, hãy cho một ngôi sao! ⭐**

Made with ❤️ for Vietnamese Lottery Community

</div>