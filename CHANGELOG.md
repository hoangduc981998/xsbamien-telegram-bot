# CHANGELOG

## [2.0.0] - 2025-10-18

### ✨ Added
- **Smart Notification System**: Tự động gửi thông báo khi có kết quả mới
- **Prize Validation**: Kiểm tra đủ 27 giải (MB) / 18 giải (MT/MN) mới gửi
- **Optimized Scheduler**: Chỉ check trong khung giờ cụ thể (tiết kiệm 83% API)
- **Notification Log**: Đánh dấu đã gửi, tránh spam users
- **Subscription Management**: `/subscriptions` command

### 🔧 Changed
- Scheduler: Từ check mỗi 10 phút → Check trong khung giờ (16:20-18:45)
- Database: Thêm `notification_log` table

### 📊 Performance
- API calls giảm từ 144/day → 24/day (83%)
- Zero duplicate notifications
- Auto-detect new results

## [1.0.0] - 2025-10-17

### ✨ Initial Release
- Xem kết quả xổ số MB/MT/MN
- Thống kê Lô 2 số, Lô 3 số
- Phân tích Đầu/Đuôi lô
- Database integration với SQLite
