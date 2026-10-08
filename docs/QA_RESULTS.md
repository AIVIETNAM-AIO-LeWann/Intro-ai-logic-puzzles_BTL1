# Kết quả rà soát ngày 08/10/2026

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
