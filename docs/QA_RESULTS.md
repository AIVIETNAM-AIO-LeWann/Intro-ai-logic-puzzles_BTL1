# Kết quả rà soát ngày 25/10/2026

## Phạm vi phát hành

Đọc đầy đủ hai trang đề BTL1, đối chiếu luật với trang Pipes/Light Up gốc và rà toàn bộ mã nguồn. Giữ lựa chọn hai bài toán và DFS/Greedy; bổ sung input JSON/CLI, bộ đo mở rộng, báo cáo, slide và đóng gói.

## Sửa lỗi và củng cố

- Light Up: điều kiện đích tự kiểm tra đèn nhìn nhau, không phụ thuộc việc analyze đã được gọi trước đó.
- Search: kiểm tra ngân sách hữu hạn/không âm; không chiếm hay dừng phiên tracemalloc của công cụ khác; frontier_peak bằng 0 khi gốc bị loại ngay.
- API: kiểm tra định danh màn và thuật toán nhất quán, kể cả bảng đã giải; trả lỗi đọc được cho Origin sai cú pháp, JSON quá sâu/sai mã hóa; kiểm tra giải phóng slot tìm kiếm khi lỗi.
- Giao diện: điều hướng ô bằng mũi tên/Home/End, thao tác ngược bằng Shift + Enter, aria-pressed cho tab game; giải thích ống mờ chưa gán; không bật lại chúc mừng khi khôi phục màn đã hoàn thành.
- Light Up: ô đen/ô số giữ nguyên độ đậm, không bị opacity của button disabled làm giảm tương phản.
- Thêm CLI không cần web, input tự tạo có kiểm tra cấu trúc và ví dụ vô nghiệm.
- Benchmark có warm-up, 7 mẫu/tổ hợp, đo bộ nhớ riêng, JSON/CSV, nguyên input và SHA-256 để tái lập.

## Bằng chứng chạy trong phiên này

- **47 test Python qua**, gồm test HTTP server thật, WSGI, oracle độc lập, liệt kê nghiệm bảng nhỏ, 48 kịch bản sửa nước sai và 36 tổ hợp thuật toán/input mở rộng ngoài 8 màn.
- **800 đối chiếu luật JavaScript/Python qua**; kiểm tra lịch sử, clock, hoạt ảnh, hủy/timeout, phản hồi lỗi/cũ và khôi phục dữ liệu lưu qua DOM giả lập.
- **Chromium thật qua:** 16 demo (8 màn x 2 thuật toán), tiến/lùi trạng thái, xem nghiệm mà không ghi bảng người chơi; điều hướng/giữ focus bằng bàn phím; sửa đèn cạnh số 0; áp dụng gợi ý tới thắng; lưu và khôi phục; không lặp hộp thoại thắng.
- Kiểm tra 1440, 768, 390 và 320 px cho cả hai game và demo: không tràn ngang; có thể cuộn tới các nút cuối hộp thoại. Không có lỗi console/uncaught exception trong kịch bản chạy.
- Ảnh giao diện thật đã xem lại; ảnh chọn làm tài liệu ở docs/images. Bộ ảnh kiểm tra đầy đủ nằm trong tmp/browser và không đưa vào gói nộp.
- **Benchmark 26 input x 2 thuật toán x 7 mẫu = 364 lượt thời gian**, tất cả solved và nghiệm hợp lệ. **52 lượt bộ nhớ** đều solved và kiểm tra nghiệm qua. Dữ liệu ở results/benchmark.json và results/benchmark.csv.
- Báo cáo PDF 10 trang được render và xem từng trang. PowerPoint 12 slide có 3 bảng và 2 biểu đồ native; kiểm tra cấu trúc, hình học, font, workbook nhúng và nhập lại bằng Artifact Tool. Slide PDF là bản render từ các ảnh slide đã xem lại.
- Kiểm tra cú pháp Python/JavaScript và git diff --check qua.
- Gói ZIP được kiểm tra CRC và mã băm từng tệp, không có .git/tmp/cache. Sau giải nén, chạy lại 47 test Python, 800 đối chiếu JavaScript và CLI ví dụ đều qua. Mã băm nguồn đang lưu khớp bản dùng để benchmark; 52 dòng CSV khớp dữ liệu JSON.

## Giới hạn xác minh

Kết quả trên chỉ áp dụng cho các kịch bản và môi trường đã chạy: Python 3.12.14, Node 24, Chromium trên Windows 11. Ma trận Python 3.10/3.12/3.13 trong CI vẫn được giữ, nhưng không ghi nhận như đã chạy toàn bộ ngay trong phiên này. Chưa xác minh Safari, Firefox, cảm ứng vật lý hoặc Microsoft PowerPoint native. Không khẳng định phần mềm không còn lỗi hoặc solver tối ưu số nước đi. Benchmark đo peak Python trong search, không phải RSS và không gồm UI/HTTP/khởi tạo.

Thông tin tên nhóm/thành viên/MSSV/lớp chưa được cung cấp; cần điền theo thực tế trước khi nộp. Không tự tạo thông tin cá nhân hay phân công.

---

# Lịch sử rà soát ngày 08/10/2026

Nhánh: `fix/gameplay-qa`. Phạm vi: chơi Pipes/Light Up, gợi ý, demo, hoàn thành, hoàn tác, lưu trạng thái, lỗi kết nối và khả năng thao tác giao diện.

## Lỗi đã xử lý

| Tình huống | Thay đổi |
|---|---|
| Bấm lại màn/tab game đang chọn làm mất lịch sử hoàn tác | Giữ nguyên phiên chơi |
| Hoàn tác làm đồng hồ lùi; chơi lại tự đếm thời gian dù chưa đi nước nào | Tách lượt chơi và thời gian, chỉ khởi động sau nước đầu tiên |
| Chờ gợi ý rồi đổi bảng/thuật toán | Hủy chờ và ngăn phản hồi cũ ghi đè |
| Đóng/mở demo khi kết quả cũ chưa về | Mỗi lần mở có yêu cầu riêng, không nhận nhầm kết quả |
| Kết nối treo hoặc phản hồi không phải JSON | Hạn chờ 15 giây, thông báo lỗi đọc được, mở lại nút thao tác |
| Xác nhận thắng trả về sau khi chơi lại cùng đáp án | Kiểm tra phiên bản bảng, chỉ xác nhận lượt hiện tại |
| Mất kết nối lúc thắng, chưa nhận được tick | Có nút xác nhận lại, giữ bảng đã giải |
| Nút màn tiếp theo dẫn tới màn đã hoàn thành | Ưu tiên các màn còn thiếu |
| Số liệu lần giải trước còn hiển thị khi chuyển màn | Xóa số liệu cũ khi chuyển |

Đã chỉnh CSS để hộp thoại cuộn trên màn thấp, tăng vùng bấm, tăng cỡ chữ phần hướng dẫn/thống kê, xếp các thẻ thành một cột trên điện thoại và giữ focus trong ô. Bổ sung nhãn hộp thoại, trạng thái công cụ Light Up cho trình đọc màn hình. Các thay đổi bố cục này **chưa được xác nhận trực quan**.

## Bằng chứng kiểm thử

- `python -m unittest discover -s tests -q`: 29 test qua.
- Trong đó, 48 kịch bản tạo nước sai có seed cố định: 8 màn × 2 thuật toán × 3 mẫu. Demo không sửa bảng; liên tiếp áp dụng gợi ý sửa và gợi ý tiếp đều hoàn thành.
- HTTP server thật trên cổng local tạm: tải trang/tài nguyên, 16 tổ hợp màn/thuật toán, kiểm tra đáp án và gợi ý trên bảng hoàn thành.
- `node tests/check_frontend.mjs`: cú pháp, 800 đối chiếu luật Python/JavaScript, xoay ống/giảm chuyển động, lịch sử, đồng hồ, timeout/hủy yêu cầu, phản hồi đến sai thứ tự, xác nhận thắng và khôi phục dữ liệu lưu lỗi đều qua.
- `python benchmark.py --repeat 3 --output tmp/qa-benchmark.json`: 16 tổ hợp đều giải được trong cả lượt đo thời gian và bộ nhớ. Đây là kiểm tra chức năng benchmark; chưa phải bộ số liệu phân tích hiệu năng cho báo cáo.
- Bộ kiểm thử mới chạy cùng lệnh CI hiện có; không cần thêm thư viện.

## Giới hạn

Phiên này không có trình duyệt kết nối để thao tác thật hoặc chụp ảnh. Kiểm thử JavaScript dùng DOM giả lập; chưa xác nhận font, khoảng cách, hoạt ảnh nhìn bằng mắt, cảm ứng, focus native của hộp thoại và bố cục trên các trình duyệt. Tiếp tục dùng [MANUAL_QA.md](MANUAL_QA.md) cho phần đó. Kết quả trên không phải cam kết ứng dụng không còn lỗi.
