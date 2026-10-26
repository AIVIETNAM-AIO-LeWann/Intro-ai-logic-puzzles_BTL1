# Chuẩn bị nộp BTL1

Mã nguồn, benchmark, báo cáo và slide kỹ thuật đã có trong dự án. Gói `output/BTL1_submission.zip` có thư mục `BTL1/`, kèm `Bao_cao.pdf`, `Slides.pptx`, `Slides.pdf`, mã nguồn và dữ liệu thực nghiệm. `MANIFEST.sha256` trong ZIP ghi mã băm từng tệp.

## Thông tin nhóm

Trước khi nộp, điền tên nhóm, họ tên, MSSV, lớp và phân công thực tế vào báo cáo/slide. Dự án không tự suy đoán thông tin cá nhân hoặc công việc của từng thành viên. Dùng hạn nộp và lịch trình bày do giảng viên/LMS thông báo; đề hiện chỉ ghi sẽ thông báo sau.

Nếu sửa nội dung, xuất lại tài liệu tương ứng, rồi chạy `python tools/package_submission.py` để cập nhật ZIP. Không nộp thư mục `tmp`, `.git`, môi trường ảo, khóa/token hoặc nhật ký máy cá nhân.

## Chạy trên máy người chấm

1. Giải nén ZIP, mở terminal trong `BTL1/`.
2. Chạy `python app.py`, mở `http://127.0.0.1:8765`.
3. Nếu cổng bận: `python app.py --port 8766`. Nếu Windows không có lệnh python: thử `py -3 app.py`.
   PowerShell có thể chạy `.\start.ps1` để tự tìm Python đã cài/runtime Codex.
4. Chạy kiểm thử bằng `python -m unittest discover -s tests -v`.
5. Tái lập số liệu: `python benchmark.py --repeat 7 --suite extended --output results/benchmark.json`.

Ứng dụng, CLI, unit test và benchmark dùng Python 3.10+ với thư viện chuẩn; không cần internet. Gunicorn trong requirements.txt chỉ dùng khi triển khai Linux. Kiểm tra JavaScript bổ sung cần Node.js; kiểm tra trình duyệt cần Playwright/Chromium và là công cụ phát triển tùy chọn.

## Kịch bản trình bày khoảng 10-12 phút

1. **Luật và trạng thái (3 phút):** giải thích cây của Pipes, chiếu sáng/ô số của Light Up; chỉ ra sự khác nhau giữa trạng thái chơi và phép gán từng phần.
2. **Thuật toán (3 phút):** DFS stack so với Greedy heap theo h; cùng thứ tự biến và cắt nhánh. Trình bày cả hai công thức heuristic và giới hạn không tối ưu.
3. **Demo (3 phút):** mở Pipes, chọn DFS, tiến/lùi vài trạng thái rồi xem nghiệm. Đổi Greedy. Chuyển Light Up 3x3, đặt đèn ở hàng 1 cột 2 cạnh số 0; xin gợi ý, đọc lý do sửa, áp dụng rồi giải tiếp. Demo không ghi đè bảng chơi.
4. **Thực nghiệm và giới hạn (2 phút):** so lightup-7 với lightup-8-seed-102. Phân biệt thời gian search với thời gian chơi, peak Python với RSS, `limit` với `unsat`, trace xét trạng thái với đường nghiệm.

## Câu hỏi cần nắm

- **DFS có còn là tìm kiếm mù khi dùng cắt nhánh?** Có: các ràng buộc chỉ loại trạng thái không thể hoàn thành; DFS không dùng h để xếp thứ tự mở rộng. Cả hai thuật toán được so trên cùng quy tắc cắt nhánh.
- **Tại sao không gọi là A*?** Heap chỉ dùng h, không dùng g + h và không có bảo đảm tối ưu theo chi phí thao tác.
- **Làm sao biết cắt nhánh đúng?** Mỗi điều kiện là điều kiện cần của mọi nghiệm hậu duệ; báo cáo giải thích từng trường hợp và test so với liệt kê nghiệm độc lập trên bảng nhỏ.
- **Tại sao Greedy đôi khi chậm hơn?** h chỉ đo tiến triển cục bộ và có thể đếm chồng; thứ tự h thấp có thể gặp nhiều nhánh bế tắc hơn thứ tự cố định của DFS.
- **Có đọc đáp án lưu sẵn không?** Không. Nghiệm chứng kiến phục vụ kiểm tra bộ sinh; search không đọc và API không gửi trường _witness.
- **Có thể nhiều nghiệm không?** Có. Bộ kiểm tra đánh giá luật thay vì đối chiếu một đáp án.
- **Đo bộ nhớ gì?** Peak cấp phát Python được tracemalloc ghi nhận trong search; loại trừ tiền xử lý, không phải RSS hay RAM của trình duyệt.
- **Hết thời gian có vô nghiệm không?** Không; chỉ khi hết frontier sau duyệt đầy đủ mới kết luận vô nghiệm.
