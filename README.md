# Mạch — Logic Lab

Ứng dụng chơi **Pipes** và **Light Up (Akari)**, kèm gợi ý theo trạng thái người chơi và demo tìm kiếm **DFS / Greedy Best-First Search**. Phần thuật toán viết bằng Python 3. Giao diện HTML/CSS/JavaScript chạy trực tiếp trong trình duyệt.

> Baseline cho nhóm BTL1: đọc [phân công 5 người](docs/TEAM_PLAN.md) và [thiết kế thuật toán](docs/DESIGN.md) trước khi nhận việc.

## Clone và chạy

Yêu cầu **Git**, **Python 3.10 trở lên** và trình duyệt hiện đại. Chạy local không cần cài thư viện, Node.js, database hay API key.

### Windows — PowerShell / terminal VS Code

```powershell
git clone https://github.com/AIVIETNAM-AIO-LeWann/Intro-ai-logic-puzzles_BTL1.git
cd Intro-ai-logic-puzzles_BTL1
python --version
python app.py
```

Mở **http://127.0.0.1:8765**. Giữ terminal đang chạy, bấm `Ctrl+C` để dừng.

Nếu Windows không nhận `python`, thử `py -3 --version` và `py -3 app.py`. Nếu chưa cài Python, tải từ [python.org](https://www.python.org/downloads/), bật **Add Python to PATH** và mở lại terminal. Kiểm tra phiên bản thực tế ít nhất là 3.10.

### macOS / Linux

```bash
git clone https://github.com/AIVIETNAM-AIO-LeWann/Intro-ai-logic-puzzles_BTL1.git
cd Intro-ai-logic-puzzles_BTL1
python3 --version
python3 app.py
```

Trong các lệnh còn lại, thay `python` bằng `python3` nếu cần. Nếu tải ZIP thay vì clone, giải nén rồi mở terminal tại thư mục chứa `app.py`.

Nếu cổng đã được dùng:

```powershell
python app.py --port 8766
```

Khi đổi cổng, mở **http://127.0.0.1:8766**. Không mở trực tiếp `web/index.html` hoặc dùng VS Code Live Server: giao diện cần API Python để lấy màn chơi và xin gợi ý.

### Chạy thử lần đầu

1. Chọn **Light Up → Hai đốm sáng**. Đặt đèn ở góc trên trái rồi bấm **Gợi ý một bước**: máy đề xuất đèn ở góc dưới phải.
2. Bấm **Áp dụng** để hoàn thành; thử hoàn tác.
3. Chọn **Pipes**, xin gợi ý và xem hoạt ảnh hướng ống trước khi áp dụng.
4. Chọn DFS hoặc Greedy, mở **Xem máy tìm lời giải** để xem các trạng thái đã xét.

### Lỗi thường gặp

| Hiện tượng | Cách xử lý |
|---|---|
| Không nhận lệnh `git` | Cài Git rồi mở lại terminal |
| Không tìm thấy `app.py` | Chuyển vào thư mục clone, nơi có file `app.py` |
| Lỗi cú pháp Python | Kiểm tra `python --version`, cần phiên bản 3.10+ |
| Cổng 8765 bị chiếm | Dừng server cũ hoặc dùng `--port 8766` |
| Không tải trang/màn chơi | Giữ Python đang chạy; mở đúng URL và cổng in trong terminal |
| Sửa code chưa thấy thay đổi | Khởi động lại Python nếu sửa backend; Ctrl+F5 nếu sửa giao diện |
| Muốn xóa toàn bộ tiến độ | Xóa dữ liệu trang local trong trình duyệt; tiến độ không lưu trên GitHub |

## Có gì trong bản này?

- Hai khu vực game riêng, mỗi game 4 màn. Pipes: 3×3, 4×4, 5×5, 6×6. Light Up: 3×3, 5×5, 6×6, 7×7.
- Chơi trực tiếp, hoàn tác/làm lại, đặt lại bảng, đếm nước đi và thời gian.
- Khi Python xác nhận giải đúng, hiện hộp thoại **Hoàn thành!** kèm số nước đi, thời gian và nút sang màn tiếp theo. Có thể đóng để xem lại bảng. Chơi lại màn đã vượt vẫn có thông báo chiến thắng.
- Light Up phản hồi vùng sáng, đèn xung đột và số đèn quanh ô đen ngay khi chơi.
- Xin một gợi ý, xem giải thích rồi tự chọn áp dụng. Không tự sửa nước đi của người chơi.
- Khi lựa chọn hiện tại vô nghiệm, đề xuất một bước sửa. Hết ngân sách tìm kiếm được báo riêng.
- Chọn DFS hoặc Greedy, xem từng trạng thái đã xét hoặc tự chạy demo.
- Lưu bảng hiện tại và màn đã hoàn thành trong localStorage của trình duyệt. Không có tài khoản, không đồng bộ giữa các máy. Lịch sử hoàn tác chỉ giữ trong phiên đang mở.
- Benchmark thời gian và peak bộ nhớ Python bằng lệnh riêng, không trộn với thời gian giao diện.

## Điều khiển

| Thao tác | Pipes | Light Up |
|---|---|---|
| Nhấn trái | Xoay 90° theo chiều kim đồng hồ | Đặt/bỏ đèn hoặc dấu × theo công cụ đang chọn |
| Nhấn phải | Xoay 90° ngược chiều kim đồng hồ | Đặt/bỏ dấu × |
| Nút trên màn hình | Hoàn tác, làm lại, đặt lại bảng | Có thêm chọn Đèn / Đánh dấu cho màn hình cảm ứng |
| Phím tắt | Ctrl/Cmd+Z, Ctrl+Y, Ctrl/Cmd+Shift+Z | Tương tự; B chọn đèn, X chọn dấu × |

**Pipes:** các ô bạn đã xoay có chấm nhỏ. Gợi ý coi hướng hiện tại của các ô này là ràng buộc cần giữ. Máy vẫn cho bạn xoay tiếp hoặc hoàn tác. Đây là quy ước tương tác của ứng dụng, không phải luật bổ sung của puzzle.

**Light Up:** dấu × nghĩa là bạn quyết định không đặt đèn ở ô đó. Dấu này không chặn ánh sáng. Gợi ý giữ cả đèn lẫn dấu ×.

## Cấu trúc code

Phân công nhóm 5 người, tiêu chí hoàn thành và quy trình PR: [docs/TEAM_PLAN.md](docs/TEAM_PLAN.md).

```text
Intro-ai-logic-puzzles_BTL1/
├── app.py                       # HTTP server local, bind 127.0.0.1
├── wsgi.py                      # Adapter production cho Gunicorn
├── benchmark.py                 # Chạy phép đo độc lập với web
├── logic_lab/
│   ├── games/
│   │   ├── pipes.py             # Luật, trạng thái, sinh nhánh, heuristic Pipes
│   │   └── lightup.py           # Luật, trạng thái, sinh nhánh, heuristic Akari
│   ├── search.py                # DFS, Greedy, trace, ngân sách, thống kê
│   ├── levels.py                # Màn tự tạo có seed, không lấy đáp án từ web
│   ├── service.py               # Check, solve, hint và đề xuất sửa
│   └── http_api.py              # Routing dùng chung local/production
├── web/
│   ├── index.html               # Cấu trúc giao diện tiếng Việt
│   ├── style.css                # Giao diện responsive
│   ├── app.js                   # Chơi, lịch sử, localStorage, gợi ý, demo
│   ├── board.js                 # Vẽ bảng và phản hồi tức thì
│   ├── api.js                   # Gọi API Python
│   ├── pipe-hint.js             # Hoạt ảnh gợi ý hướng ống
│   └── pipe-hint.css            # Kiểu hiển thị gợi ý Pipes
├── tests/                      # Kiểm thử luật, solver, gợi ý, HTTP/WSGI
├── docs/                       # Giải thích thiết kế và checklist chơi thử
├── results/benchmark.json       # Số liệu chạy thực tế, có thông tin môi trường
├── render.yaml                 # Blueprint Render
└── .github/workflows/tests.yml  # CI cho Python 3.10 / 3.12 / 3.13
```

Đọc [thiết kế và thuật toán](docs/DESIGN.md) để hiểu rõ search state khác với bảng đang hiển thị như thế nào.

## Kiểm thử và đo đạc

```powershell
python -m unittest discover -s tests -v
python benchmark.py --repeat 5 --output results/benchmark.json
```

Test đối chiếu solver với bộ vét cạn độc lập trên các bảng nhỏ, không chỉ kiểm tra lại cùng một hàm. Các trường hợp gồm giữ nước đi đúng, đáp án khác, đèn/dấu × sai, Pipes có vòng kín, hết ngân sách và API production.

Benchmark đo thời gian và bộ nhớ trong hai lượt riêng để `tracemalloc` không làm tăng số thời gian báo cáo. `peak_python_kib` là peak cấp phát Python trong quá trình search, **không phải tổng RAM/RSS của tiến trình**; không gồm dựng puzzle, HTTP, trace hoặc vẽ giao diện. Dữ liệu demo nhỏ nên chênh lệch thời gian dễ bị nhiễu. Greedy không được bảo đảm nhanh hơn DFS.

Checklist giao diện: [docs/MANUAL_QA.md](docs/MANUAL_QA.md).

Nếu máy có Node.js, chạy thêm `node tests/check_frontend.mjs` để kiểm tra cú pháp JS và đối chiếu 800 trạng thái giữa logic phản hồi giao diện với Python. CI chạy bước này tự động. Đây không phải kiểm thử bố cục hoặc thao tác trên trình duyệt thật.

## Triển khai Render

Giao diện này dùng Python backend riêng, không dùng Streamlit. Render chạy ứng dụng qua **Gunicorn + WSGI**.

1. Push dự án lên GitHub với `app.py` và `render.yaml` ở gốc repo.
2. Trên Render chọn **New → Blueprint**, kết nối repo và dùng `render.yaml`.
3. Hoặc tạo **Web Service**, chọn Python và cấu hình:

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn wsgi:application --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 30
Health Check: /api/levels
```

Nếu repo chứa nhiều dự án, đặt Root Directory là `intro_ai_btl1` trước khi dùng các lệnh này. Không triển khai backend lên GitHub Pages vì dịch vụ đó không chạy Python server. Cấu hình Render đã chuẩn bị nhưng chưa triển khai trực tuyến. Khi host công khai, tiến trình chỉ cho tối đa hai tác vụ search đồng thời và mỗi lượt search có ngân sách hữu hạn. Bản này phù hợp demo lớp học, chưa có chống lạm dụng theo người dùng.

Tài liệu nền tảng: [Render Python/Gunicorn](https://render.com/docs/deploy-flask), [Blueprint reference](https://render.com/docs/blueprint-spec).

## Nguồn luật và giới hạn

- [Pipes](https://www.puzzle-pipes.com/): bản không nối xuyên biên, một mạng, không chu trình.
- [Light Up](https://www.puzzle-light-up.com/): phủ sáng, không đèn nhìn nhau, thỏa ô số.
- Màn do chương trình tạo từ seed cố định; có lời giải xây dựng được, **không khẳng định mỗi màn có duy nhất một đáp án**. Máy chấm theo luật, không so với đáp án mẫu.
- Nhãn màn chỉ là lộ trình học theo kích thước, chưa là kết quả hiệu chuẩn độ khó.
- Bộ dữ liệu hiện tại phục vụ chơi và demo. Cần bổ sung input đa dạng hơn trước khi đưa ra kết luận thực nghiệm rộng trong báo cáo BTL.
- Báo cáo nộp bài và slide nhóm chưa nằm trong bản ứng dụng này.
