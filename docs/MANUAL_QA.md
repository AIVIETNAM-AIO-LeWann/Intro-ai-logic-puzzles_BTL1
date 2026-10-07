# Checklist kiểm tra giao diện

Đây là checklist để chạy trên trình duyệt thật. Không xem danh sách này là xác nhận đã kiểm tra trực quan: phiên phát triển chưa có trình duyệt kết nối với công cụ điều khiển.

## Pipes

1. Chạy `python app.py`, mở URL local; thấy sidebar, bảng Pipes và khu vực gợi ý.
2. Nhấn ô rồi chuột phải: hướng xoay đúng hai chiều, chấm đã chỉnh xuất hiện.
3. Hoàn tác khôi phục cả hướng và dấu đã chỉnh. Làm lại trả đúng trạng thái.
4. Bấm Gợi ý trên bảng mới, xem ô được đánh dấu và chỉ thay đổi khi bấm Áp dụng.
5. Xoay một ống ở biên cho chĩa ra ngoài, xin gợi ý: nhận đề xuất sửa rõ ràng.
6. Áp dụng nhiều gợi ý đến khi hoàn thành. Thử cả bốn màn.
7. Đặt lại bảng, hoàn tác việc đặt lại; tiến độ được khôi phục.

## Light Up

1. Chọn màn 3×3. Đặt đèn góc trên trái và dưới phải: bảng được xác nhận hoàn thành.
2. Đặt lại; thử góc trên phải và dưới trái: đáp án khác vẫn được chấp nhận.
3. Đặt đèn cạnh ô số 0: ô có lỗi được phản hồi; gợi ý đề nghị bỏ đèn.
4. Đặt hai đèn cùng hàng không có vật cản: thấy xung đột.
5. Đánh dấu × ở cả bốn góc màn 3×3: gợi ý đề nghị bỏ một dấu ×.
6. Nút “Đánh dấu” hoạt động trên màn hình cảm ứng mà không cần chuột phải.

## Demo và lưu tiến độ

- Giải xong cả Pipes và Light Up: hộp thoại Hoàn thành hiện sau khi API xác nhận, đúng nước đi/thời gian; dấu tick trên danh sách màn được lưu.
- Đóng hộp thoại hoặc nhấn Escape, đổi thuật toán: không bật lại thông báo cho cùng bảng. Hoàn tác về bảng chưa xong rồi giải lại: thông báo xuất hiện lại.
- Nút màn tiếp theo chuyển đúng màn. Ở màn cuối, ưu tiên màn cùng game còn thiếu rồi chuyển game còn chưa xong; khi vượt hết, ẩn nút tiếp và báo đã hoàn thành toàn bộ.
- Reload một bảng đã giải vẫn xác nhận lại với Python và cho xem kết quả; kết quả xác nhận chậm của bảng cũ không mở hộp thoại trên bảng mới.

1. Chọn DFS rồi Greedy; mở demo, chạy từng bước, tự chạy, kéo thanh, xem lời giải.
2. Đóng demo rồi kiểm tra bảng người chơi không bị thay đổi.
3. Đổi màn trong lúc chờ gợi ý: kết quả cũ không áp dụng lên màn mới.
4. Reload trang: khôi phục màn và bảng đang chơi. Hoàn tác cũ không được lưu qua reload.
5. Dừng Python, xin gợi ý: giao diện báo lỗi kết nối thay vì treo vô hạn.
6. Thử chiều rộng 390 px, 768 px và 1366 px. Không có thanh cuộn ngang hoặc nút bị che.
7. Dùng Tab/Enter để chơi, Escape đóng hộp thoại; trạng thái focus dễ nhìn.

## Kiểm thử tự động đã có

`python -m unittest discover -s tests -v` kiểm tra luật bằng oracle độc lập, cả hai solver trên 8 màn, bảo toàn nước đi, sửa mâu thuẫn, ngân sách, đầu vào API và WSGI.
