# 🧩 Mạch — Logic Lab

Bài tập lớn Nhập môn AI: giải **Pipes** và **Light Up (Akari)** bằng **DFS** và **Greedy Best-First Search**, với giao diện web để chơi và xem thuật toán từng bước.

**Python 3.10+ · HTML / CSS / JavaScript · 2 game · 8 màn chơi**

## 🚀 Clone và chạy

Cần **Git** và **Python 3.10 trở lên**. Chạy local không cần cài thêm thư viện.

```bash
git clone https://github.com/AIVIETNAM-AIO-LeWann/Intro-ai-logic-puzzles_BTL1.git
cd Intro-ai-logic-puzzles_BTL1
python app.py
```

Mở **http://127.0.0.1:8765** trên trình duyệt. Giữ terminal đang chạy; nhấn `Ctrl+C` để dừng.

- **Windows:** nếu không nhận `python`, thử `py -3 app.py`.
- **macOS / Linux:** dùng `python3 app.py`.
- **Cổng bị trùng:** chạy `python app.py --port 8766`, mở `http://127.0.0.1:8766`.

> Chạy qua Python, không mở trực tiếp `index.html` hoặc dùng Live Server. Sau khi cập nhật code, khởi động lại server và tải lại trang bằng `Ctrl+F5`.

## ✨ Tính năng

- Mỗi game có **4 màn**, hỗ trợ hoàn tác, làm lại và lưu tiến độ trên trình duyệt.
- **Gợi ý theo bảng hiện tại**; đề xuất sửa khi các lựa chọn không còn lời giải.
- Hoạt ảnh hướng dẫn xoay ống và thông báo hoàn thành kèm thời gian, số nước đi.
- Chọn **DFS / Greedy**, xem từng trạng thái tìm kiếm hoặc chạy demo tự động.
- Đo thời gian và bộ nhớ bằng công cụ benchmark riêng.

## 🎮 Cách chơi

| | Pipes | Light Up |
|---|---|---|
| Mục tiêu | Nối tất cả ống thành một mạng, không đầu hở hoặc vòng kín | Chiếu sáng mọi ô trắng, thỏa các ô số, không để đèn chiếu vào nhau |
| Nhấn trái | Xoay ống theo chiều kim đồng hồ | Đặt / bỏ đèn |
| Nhấn phải | Xoay ngược chiều kim đồng hồ | Đặt / bỏ dấu × (không đặt đèn) |

Gợi ý giữ hướng các ô Pipes đã chỉnh (có chấm nhỏ), hoặc giữ đèn và dấu × của Light Up. Máy chỉ thay đổi bảng khi bạn bấm **Áp dụng**. Luật chi tiết nằm trong nút **Cách chơi** trên giao diện.

## 📂 Cấu trúc chính

```text
├── app.py                 # Chạy ứng dụng local
├── logic_lab/
│   ├── games/
│   │   ├── pipes.py       # Logic Pipes
│   │   └── lightup.py     # Logic Light Up
│   ├── search.py          # DFS và Greedy dùng chung
│   ├── levels.py          # Dữ liệu màn chơi
│   └── service.py         # Kiểm tra, giải và gợi ý
├── web/                   # Giao diện
├── tests/                 # Kiểm thử
├── benchmark.py           # Đo hiệu năng
├── results/               # Kết quả đo
├── docs/                  # Tài liệu chi tiết
└── render.yaml            # Cấu hình triển khai Render
```

## 🧪 Kiểm thử

```bash
python -m unittest discover -s tests -v
python benchmark.py --repeat 5 --output results/benchmark.json
```

Nếu có Node.js, kiểm tra thêm giao diện: `node tests/check_frontend.mjs`.

Benchmark đo thời gian và bộ nhớ trong hai lượt riêng. `peak_python_kib` là peak cấp phát Python, không phải tổng RAM của tiến trình.

## 📖 Tài liệu

- [Thiết kế thuật toán và cơ chế gợi ý](docs/DESIGN.md)
- [Checklist kiểm tra giao diện](docs/MANUAL_QA.md)
- Luật tham khảo: [Pipes](https://www.puzzle-pipes.com/) · [Light Up](https://www.puzzle-light-up.com/)

Các màn được tạo riêng và có thể có nhiều lời giải. Đây là bản baseline; báo cáo và slide nộp bài sẽ được bổ sung sau.
