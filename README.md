# 🧩 Mạch — Logic Lab

Bài tập lớn Nhập môn AI: giải **Pipes** và **Light Up (Akari)** bằng **DFS** và **Greedy Best-First Search**, với giao diện web để chơi và xem thuật toán từng bước.

**Python 3.10+ · HTML / CSS / JavaScript · 2 game · 8 màn chơi**

Bản hoàn thiện có solver, CLI đọc input JSON, kiểm thử tự động, benchmark **26 input**, báo cáo kỹ thuật và slide thuyết trình.

## 🚀 Clone và chạy

Cần **Git** và **Python 3.10 trở lên**. Chạy local không cần cài thêm thư viện.

```bash
git clone https://github.com/AIVIETNAM-AIO-LeWann/Intro-ai-logic-puzzles_BTL1.git
cd Intro-ai-logic-puzzles_BTL1
python app.py
```

Mở **http://127.0.0.1:8765** trên trình duyệt. Giữ terminal đang chạy; nhấn `Ctrl+C` để dừng.

- **Windows:** nếu không nhận `python`, thử `py -3 app.py`.
- **PowerShell:** chạy `.\start.ps1` (hoặc `.\start.ps1 -Port 8766`); script tự tìm Python đã cài hoặc runtime đi kèm Codex, bỏ qua alias Microsoft Store không chạy được.
- **macOS / Linux:** dùng `python3 app.py`.
- **Cổng bị trùng:** chạy `python app.py --port 8766`, mở `http://127.0.0.1:8766`.

> Chạy qua Python, không mở trực tiếp `index.html` hoặc dùng Live Server. Sau khi cập nhật code, khởi động lại server và tải lại trang bằng `Ctrl+F5`.

## ✨ Tính năng

- Mỗi game có **4 màn**, hỗ trợ hoàn tác, làm lại và lưu tiến độ trên trình duyệt.
- **Gợi ý theo bảng hiện tại**; đề xuất sửa khi các lựa chọn không còn lời giải.
- Hoạt ảnh hướng dẫn xoay ống và thông báo hoàn thành kèm thời gian, số nước đi.
- Chọn **DFS / Greedy**, xem từng trạng thái tìm kiếm hoặc chạy demo tự động.
- Đo thời gian và bộ nhớ bằng công cụ benchmark riêng.
- Chạy solver độc lập từ terminal với màn có sẵn hoặc input JSON tự tạo.
- Điều khiển bảng bằng phím mũi tên; Shift + Enter xoay ngược / đánh dấu ×.

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
├── inputs/                # Ví dụ JSON có nghiệm và vô nghiệm
├── tools/                 # Tạo phụ lục, báo cáo, slide và gói nộp
├── results/               # Kết quả đo
├── docs/                  # Tài liệu chi tiết
├── output/                # PDF báo cáo, PowerPoint và gói ZIP
└── render.yaml            # Cấu hình triển khai Render
```

## 🧪 Kiểm thử

```bash
python -m unittest discover -s tests -v
python benchmark.py --repeat 7 --suite extended --output results/benchmark.json
```

Nếu có Node.js, kiểm tra thêm giao diện: `node tests/check_frontend.mjs`.

Nếu Python không nằm trong PATH, đặt biến môi trường `PYTHON` thành đường dẫn trình thông dịch để các kiểm tra Node gọi đúng Python.

Kiểm tra trình duyệt thật là tùy chọn: cài Playwright (`npm install --no-save playwright`, `npx playwright install chromium`), rồi chạy `node tests/check_browser.mjs`. Có thể đặt `PLAYWRIGHT_MODULE` để dùng Playwright có sẵn, `CHROMIUM_EXECUTABLE` để chọn Chromium và `BROWSER_OUTPUT` để đổi thư mục ảnh (mặc định `tmp/browser`). Các kiểm tra này không cần cho việc chạy ứng dụng.

Benchmark đo thời gian và bộ nhớ trong hai lượt riêng, có warm-up và lưu từng mẫu. `peak_python_kib` là peak cấp phát Python **trong search**, không phải tổng RAM của tiến trình; không gồm khởi tạo bài toán, UI, HTTP hoặc trace. JSON lưu input, mã băm và thông tin môi trường; CSV mở được bằng bảng tính. `--suite playable` đo 8 màn, `--suite extended` đo 26 input. Dùng `--input inputs/examples.json` để đo bộ riêng. `limit` luôn là chưa biết, không phải vô nghiệm.

## Giải từ terminal

```bash
python -m logic_lab --level pipes-5 --algorithm dfs --trace 20
python -m logic_lab --input inputs/examples.json --algorithm greedy --output results/custom.json
python -m logic_lab --list --output inputs/playable.json
```

Input gồm `id`, `game`, `rows`, `cols` và `tiles` (Pipes, bitmask 1/2/4/8) hoặc `board` (Light Up, ký tự `.#01234`). Tệp nhận một bài hoặc danh sách bài, không cần đáp án. CLI xuất JSON; mã thoát 0 khi đã kết luận `solved`/`unsat`, 2 khi có `limit` hoặc lỗi tham số. Xem [ví dụ](inputs/examples.json).

## Báo cáo và thuyết trình

- [Báo cáo PDF](output/pdf/BTL1_Bao_cao.pdf) · [Nguồn báo cáo](docs/REPORT.md)
- [PowerPoint](output/presentation/BTL1_Thuyet_trinh.pptx) · [Slide PDF](output/presentation/BTL1_Thuyet_trinh.pdf)
- [Bảng thực nghiệm đầy đủ](docs/BENCHMARK.md) · [Dữ liệu CSV](results/benchmark.csv)
- [Gói nộp](output/BTL1_submission.zip) · [Hướng dẫn chuẩn bị nộp và demo](docs/SUBMISSION.md)

Sau khi đo lại, chạy `python tools/summarize_benchmark.py` để cập nhật phụ lục. Tạo PDF bằng `python tools/build_report.py` (cần ReportLab và font Unicode); PowerPoint có thể chỉnh trực tiếp hoặc dựng lại bằng `tools/build_slides.mjs` trong môi trường Codex có Artifact Tool. Các thư viện tạo tài liệu là tùy chọn và không thuộc yêu cầu chạy bài. Đóng gói bằng `python tools/package_submission.py`.

## 📖 Tài liệu

- [Thiết kế thuật toán và cơ chế gợi ý](docs/DESIGN.md)
- [Checklist kiểm tra giao diện](docs/MANUAL_QA.md)
- [Kết quả kiểm thử đã thực hiện](docs/QA_RESULTS.md)
- Luật tham khảo: [Pipes](https://www.puzzle-pipes.com/) · [Light Up](https://www.puzzle-light-up.com/)

Các màn được tạo riêng và có thể có nhiều lời giải. Báo cáo công bố cả trường hợp DFS tốt hơn Greedy và ngược lại; không khẳng định tối ưu số thao tác. Trước khi nộp LMS, bổ sung tên nhóm, thành viên, MSSV và lớp vào tài liệu theo thông tin thực tế.
