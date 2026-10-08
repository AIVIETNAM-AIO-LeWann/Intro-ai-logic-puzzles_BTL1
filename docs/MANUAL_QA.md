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

- Đóng thông báo chiến thắng bằng nút × góc trên phải: bảng và dấu hoàn thành được giữ, hộp thoại không tự bật lại khi chỉ đổi thuật toán.
- Xoay Pipes ra ngoài biên hoặc đặt đèn cạnh ô số 0 rồi mở demo: chế độ giữ nước hiện tại báo mâu thuẫn và vẫn hiển thị bảng. Chọn “Cho phép sửa nước đã đi”: có trace/lời giải và các nút phát hoạt động; đóng demo không làm mất nước đi người chơi.
- Chuyển qua lại hai chế độ demo với DFS và Greedy. Mỗi lần đổi dừng phát cũ, đặt lại thanh trượt và hiển thị đúng phạm vi đang giải.

- Giải xong cả Pipes và Light Up: hộp thoại Hoàn thành hiện sau khi API xác nhận, đúng nước đi/thời gian; dấu tick trên danh sách màn được lưu.
- Đóng hộp thoại hoặc nhấn Escape, đổi thuật toán: không bật lại thông báo cho cùng bảng. Hoàn tác về bảng chưa xong rồi giải lại: thông báo xuất hiện lại.
- Nút màn tiếp theo chuyển đúng màn. Ở màn cuối, ưu tiên màn cùng game còn thiếu rồi chuyển game còn chưa xong; khi vượt hết, ẩn nút tiếp và báo đã hoàn thành toàn bộ.
- Reload một bảng đã giải vẫn xác nhận lại với Python và cho xem kết quả; kết quả xác nhận chậm của bảng cũ không mở hộp thoại trên bảng mới.

1. Chọn DFS rồi Greedy; mở demo, chạy từng bước, tự chạy, kéo thanh, xem lời giải.
   Với Pipes, các ô đổi hướng phải xoay từ hình trước sang hình sau. Thử cả bước lùi, kéo thanh nhanh và nút xem bảng lời giải; đóng/mở demo không dùng lại hướng của màn trước. Ô chưa gán vẫn mờ. Bật giảm chuyển động của hệ điều hành thì bảng đổi hướng ngay, không xoay.
2. Đóng demo rồi kiểm tra bảng người chơi không bị thay đổi.
3. Đổi màn trong lúc chờ gợi ý: kết quả cũ không áp dụng lên màn mới.
4. Reload trang: khôi phục màn và bảng đang chơi. Hoàn tác cũ không được lưu qua reload.
5. Dừng Python, xin gợi ý: giao diện báo lỗi kết nối thay vì treo vô hạn.
6. Thử chiều rộng 390 px, 768 px và 1366 px. Không có thanh cuộn ngang hoặc nút bị che.
7. Dùng Tab/Enter để chơi, Escape đóng hộp thoại; trạng thái focus dễ nhìn.

## Tình huống hồi quy cần thử trên trình duyệt

- Bấm lại tên màn đang chơi và tab game đang chọn: lịch sử hoàn tác vẫn còn.
- Xin gợi ý rồi đi tiếp hoặc đổi thuật toán ngay: kết quả cũ không đè thông báo mới; nút gợi ý dùng được tiếp.
- Mở demo, đóng khi đang tải, mở lại ngay: chỉ phiên mới cập nhật bảng demo.
- Chơi lại rồi chờ: đồng hồ giữ 00:00 tới nước đầu tiên. Hoàn tác/tiến lại nước thường không làm thời gian lùi. Mở luật hoặc demo thì thời gian chơi tạm dừng.
- Dừng server ngay trước nước thắng, chờ phản hồi lỗi: thấy “Xác nhận hoàn thành lại”. Bật server, bấm nút đó: tick và thông báo thắng hiện đúng, bảng không mất.
- Chơi màn kế tiếp sau khi đã hoàn thành một số màn không theo thứ tự: bỏ qua màn đã xong.
- Thử 320 px, 390 px, chế độ ngang điện thoại và zoom 200%: hộp thoại cuộn được, nút đóng và các hành động không bị che. Kiểm tra cả bảng 6×6 và phần demo.
- Dùng Tab tới từng ô: đường viền focus nằm trong ô, không bị bảng cắt mất. Light Up thông báo đúng công cụ Đèn/Đánh dấu đang chọn.

## Chạy kiểm thử tự động

`python -m unittest discover -s tests -v` kiểm tra luật bằng oracle độc lập, cả hai solver trên 8 màn, bảo toàn nước đi, sửa mâu thuẫn, ngân sách, đầu vào API và WSGI.

`node tests/check_frontend.mjs` đối chiếu luật, kiểm tra hoạt ảnh và các luồng thao tác bằng DOM giả lập. Không thay thế việc kiểm tra bố cục/cảm ứng trên trình duyệt thật. Kết quả đợt rà soát được ghi trong [QA_RESULTS.md](QA_RESULTS.md).
