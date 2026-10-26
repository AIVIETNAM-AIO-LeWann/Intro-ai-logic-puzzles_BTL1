# Nội dung thuyết trình

## 1. Mạch - Logic Lab

Giới thiệu hai bài toán và hai chính sách tìm kiếm. Python 3 xử lý toàn bộ search và luật; giao diện chỉ hỗ trợ tương tác. Không tuyên bố tối ưu số nước đi.

Nguồn: docs/REPORT.md; results/benchmark.json

## 2. Pipes: một mạng, không vòng kín

Mỗi ô là một đỉnh của đồ thị. Chỉ tạo cạnh khi hai đầu nối khớp. Nghiệm là cây bao trùm các ô, đồng thời không có đầu hở hoặc nối ra ngoài biên. Ứng dụng chọn bản không nối xuyên biên.

Nguồn: https://www.puzzle-pipes.com/ (25/10/2026); logic_lab/games/pipes.py; docs/images/pipes.png

## 3. Light Up: phủ sáng và thỏa ô số

Đèn chỉ đặt trên ô trắng. Ô đen chặn tia sáng, ô số yêu cầu số đèn kề cạnh chính xác. Hai tia sáng có thể giao nhau nhưng hai đèn không được nhìn nhau. Dấu X không chặn ánh sáng.

Nguồn: https://www.puzzle-light-up.com/ (25/10/2026); logic_lab/games/lightup.py; docs/images/lightup.png

## 4. DFS và Greedy dùng chung mô hình

Phân biệt chính sách lấy node khỏi frontier. Hai bên có cùng trạng thái đầu, thứ tự chọn biến, thứ tự giá trị và cắt nhánh. DFS không sắp xếp theo heuristic. Có ngân sách nên limit là chưa biết; chỉ duyệt hết frontier mới chứng minh unsat.

Nguồn: docs/REPORT.md; results/benchmark.json

## 5. Pipes: gán hướng cuối cùng

Tuple gồm hướng đã gán hoặc 0 cho chưa gán. Các hướng đối xứng được loại trùng. Một bước search gán một ô, có thể tương đương nhiều lần xoay trên UI. Điểm h xếp hạng theo số biến chưa gán và kích thước miền; không là cận tối ưu thao tác.

Nguồn: docs/REPORT.md; results/benchmark.json

## 6. Light Up: quyết định có đặt đèn

Chỉ ô trắng là biến -1/0/1. Tiền xử lý tập nhìn thấy. Thử không đèn trước, có đèn sau nếu còn hợp lệ. Đích có thể đạt khi còn biến -1, hiểu là không đặt thêm đèn. Một bóng đèn thỏa nhiều mục tiêu nên h có thể đếm chồng.

Nguồn: docs/REPORT.md; results/benchmark.json

## 7. Demo là lịch sử xét trạng thái

Demo phát tối đa 350 trạng thái lấy ra khỏi frontier. Đây không phải đường nghiệm: trạng thái liền nhau có thể là nhánh khác nhau. Nghiệm cuối nằm ở nút riêng. Bảng người chơi không đổi khi xem demo; ống mờ là hướng minh họa chưa được gán.

Nguồn: web/app.js; logic_lab/search.py; docs/images/demo.png

## 8. Thực nghiệm có dữ liệu tái lập

26 input gồm 8 màn chơi và 18 input: hai game x kích thước 4,6,8 x seed 101,102,103. Mỗi tổ hợp warm-up rồi 7 mẫu thời gian, lấy median; memory chạy riêng sau gc.collect. Cả 364 lượt time và 52 lượt memory solved và được check. Đo search không gồm khởi tạo/HTTP/UI/trace. Các khác biệt rất nhỏ có thể là nhiễu.

Nguồn: docs/REPORT.md; results/benchmark.json

## 9. Pipes: cắt nhánh chi phối kết quả

Bảng hiển thị bốn màn tương tác và một input 8x8, không thay cho bảng toàn bộ trong phụ lục báo cáo. Trên 13 input Pipes, DFS xét 453 trạng thái, Greedy 455. Nhiều miền chỉ còn một giá trị nên heuristic ít đổi thứ tự. Tổng median từng input DFS 49.331 ms, Greedy 53.001 ms. Không suy rộng từ chênh lệch nhỏ.

Nguồn: docs/REPORT.md; results/benchmark.json

## 10. Light Up: lợi ích tùy cấu trúc input

Bảng trích toàn bộ bốn màn tương tác và ba input 8x8. Bảng 13 input đầy đủ nằm trong phụ lục. Seed 102 là trường hợp Greedy có lợi rõ; lightup-7 là phản ví dụ. Peak cấp phát bao gồm cấu trúc được tạo trong search và không đồng nhất frontier_peak.

Nguồn: docs/REPORT.md; results/benchmark.json

## 11. Heuristic có thể giúp hoặc gây lệch hướng

Biểu đồ số trạng thái xét, hai thang trục độc lập: không so độ cao cột giữa hai biểu đồ. Lightup-7: DFS 51, Greedy142; seed102: DFS1584, Greedy68. Heuristic không biết toàn bộ tương tác ràng buộc tương lai nên giảm h cục bộ không đảm bảo ít node hơn.

Nguồn: docs/REPORT.md; results/benchmark.json

## 12. Kiểm chứng và demo trực tiếp

Chạy python app.py. Demo 1: Pipes chọn DFS, xem vài trạng thái và nghiệm cuối. Demo 2: LightUp3 đặt đèn cạnh số0, xin gợi ý sửa, áp dụng rồi giải tiếp. Kết thúc bằng so sánh hai case heuristic. 47 unit tests và 800 so luật, Chromium thực tế; không khẳng định không còn lỗi. Chưa kiểm Safari/Firefox hay cảm ứng vật lý. Thông tin nhóm cần bổ sung trước nộp.

Nguồn: tests/; docs/QA_RESULTS.md; https://www.puzzle-pipes.com/; https://www.puzzle-light-up.com/
