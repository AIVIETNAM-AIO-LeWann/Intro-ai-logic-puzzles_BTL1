# Thiết kế tìm kiếm và gợi ý

## Luồng dữ liệu

```text
Người chơi thao tác
  → app.js cập nhật bảng, lịch sử và lưu trình duyệt
  → board.js vẽ bảng + kiểm tra nhẹ để phản hồi tức thì
  → nếu có dấu hiệu hoàn thành, Python /api/check xác nhận

Người chơi bấm Gợi ý
  → POST /api/hint: level + state + algorithm
  → service tạo bài toán với lựa chọn hiện tại làm ràng buộc
  → search chạy DFS hoặc Greedy
  → có nghiệm: trả một hành động khác bảng hiện tại
  → vô nghiệm: chạy bài gốc rồi đề xuất sửa một lựa chọn
  → hết ngân sách: báo chưa biết, không coi là vô nghiệm
  → người chơi bấm Áp dụng hoặc tự thao tác
```

Mỗi yêu cầu gợi ý dùng bản chụp trạng thái. Nếu người chơi thay đổi bảng trong lúc chờ, giao diện bỏ kết quả cũ để tránh gợi ý sai ngữ cảnh. Máy không chạy full search sau mỗi lần click.

## Pipes

Mảnh ống dùng bitmask: trên = 1, phải = 2, dưới = 4, trái = 8. Ví dụ 6 = phải + dưới. Phép xoay là quay vòng bốn bit. Ống thẳng có hai hướng phân biệt, ống chữ thập có một; không sinh bản sao đối xứng.

Bảng chơi luôn có hướng cho mọi ô. **Trạng thái tìm kiếm là phép gán hướng cuối cùng từng phần**, dùng 0 để chỉ ô chưa gán. Hướng hiện tại của ô chưa được người chơi chỉnh chỉ dùng để hiển thị, không bị ép vào lời giải. Hướng của ô đã chỉnh là ràng buộc cố định.

- Trạng thái đầu: các ô người chơi chỉnh được gán, các ô còn lại chưa gán.
- Một hành động trong search: gán một hướng hợp lệ cho ô chưa gán đầu tiên theo thứ tự hàng/cột.
- Cắt nhánh chung: đầu ống chĩa ngoài, không tương thích với ô đã gán, miền giá trị rỗng, chu trình đã hình thành hoặc đồ thị cạnh còn khả thi không thể liên thông.
- Đích: mọi ô đã gán, mọi đầu nối khớp, một thành phần liên thông và không chu trình.
- Heuristic Greedy: `h = Σ [1 + 0.25 × (|D_i| − 1)]` trên các ô chưa gán; `D_i` là miền hướng còn lại sau kiểm tra cục bộ. Ưu tiên trạng thái còn ít ô chưa gán và ít khả năng lựa chọn.

Đây là heuristic xếp hạng, không phải cận dưới chi phí cho A*. Search không tối ưu số lần xoay. Một hành động search gán hướng có thể tương ứng 1–3 lần xoay 90° trên giao diện. Nút “Áp dụng” đặt hướng được đề xuất trong một thao tác giao diện.

## Light Up

Chỉ ô trắng là biến. Mỗi biến nhận `-1` (chưa quyết định), `0` (không có đèn), `1` (có đèn). Tính trước tập ô nhìn thấy từ từng ô trắng, gồm chính ô đó.

- Trạng thái đầu: đèn người chơi = 1, dấu × = 0, ô còn lại = -1.
- Hành động: chọn ô chưa quyết định đầu tiên theo hàng/cột, thử 0 rồi 1; không thử 1 khi vị trí không thể đặt đèn hợp lệ.
- Cắt nhánh chung: đèn nhìn nhau; vượt số quanh ô đen; không còn đủ vị trí đặt đèn để đạt một ô số; một ô chưa sáng không còn ứng viên nào chiếu tới được.
- Đích: mọi ô trắng sáng và các ô số chính xác. Những biến chưa quyết định còn lại có thể xem là không đặt đèn.
- Heuristic Greedy: `h = số ô trắng chưa sáng + tổng số đèn còn thiếu quanh các ô số`.

Vì một bóng đèn có thể thỏa nhiều mục tiêu, đây không phải heuristic admissible về số đèn cần thêm. Ta dùng **Greedy**, không gọi nó là A*.

## DFS và Greedy dùng chung phần nào?

Cùng trạng thái đầu, thứ tự chọn biến, thứ tự sinh nhánh và quy tắc loại trạng thái vi phạm. Không dùng MRV hoặc heuristic để sắp xếp nhánh trong DFS.

- DFS dùng stack, đi sâu trước. Bộ cắt nhánh chỉ loại lựa chọn không thể hoàn thành.
- Greedy dùng heap theo `h`. Nếu bằng điểm, dùng thứ tự đưa vào hàng đợi làm tie-break.
- Dùng thứ tự gán biến cố định nên không tạo nhiều đường dẫn tới cùng một phép gán. Không cần tập visited khổng lồ cho các hoán vị đặt đèn hoặc chuỗi xoay vòng.
- Không thuật toán nào ở đây được cam kết tìm nghiệm tối ưu theo số thao tác giao diện.
- Mọi miền đều hữu hạn. Nếu không giới hạn tài nguyên, duyệt hết frontier mới cho kết luận vô nghiệm. Bản web có giới hạn nên có thể trả `limit`.

## Khi người chơi đi sai

Hệ thống phân biệt:

| Kết quả | Ý nghĩa | Phản hồi |
|---|---|---|
| `hint` | Tồn tại lời giải giữ lựa chọn hiện tại | Gợi ý một bước và đánh dấu ô |
| `repair` | Đã chứng minh không có nghiệm giữ mọi lựa chọn | Tìm một nghiệm bài gốc, đề xuất sửa một lựa chọn không khớp |
| `limit` | Search chưa xong | Không gọi là đi sai; cho thử lại hoặc đổi thuật toán |
| `repair_limit` | Đã chứng minh nhánh hiện tại vô nghiệm nhưng chưa tìm xong phương án sửa | Đề nghị hoàn tác, không bịa nước sửa |
| `complete` | Bảng hiện tại hợp lệ | Báo hoàn thành |

Gợi ý sửa hiện tại chưa tối ưu số nước cần sửa, cũng không khẳng định một ô gợi ý là sai trong mọi nghiệm. Nó chỉ chỉ ra một thay đổi theo một lời giải hợp lệ tìm được. Nếu nhiều lựa chọn mâu thuẫn, một bước sửa có thể chưa đủ. Hệ thống phải giải lại khi xin gợi ý tiếp theo.

## Demo và thống kê

Demo lưu tối đa 350 trạng thái được lấy ra khỏi frontier, trước khi kiểm tra đích. Đây là **lịch sử xét trạng thái**, không phải đường đi lời giải. Các trạng thái kề nhau có thể thuộc hai nhánh khác nhau. Nếu cắt trace, giao diện nói rõ và vẫn có nút xem bảng lời giải cuối. Demo không tự ghi lên bảng người chơi.

`expanded` trong phiên bản này đếm số trạng thái lấy ra để xét, **bao gồm trạng thái đích**; tên hiển thị là “trạng thái đã xét”. `generated` tính cả gốc và các trạng thái con bị loại. `frontier_peak` là số node chờ xét lớn nhất, không phải đơn vị bộ nhớ. Đo RAM trong benchmark dùng `tracemalloc`, không chạy trong HTTP đa luồng.

## API

- `GET /api/levels`: dữ liệu màn công khai, loại `_witness`.
- `POST /api/check`: kiểm tra bảng theo luật.
- `POST /api/hint`: một gợi ý hoặc phương án sửa.
- `POST /api/solve`: lời giải và trace cho demo.

Ví dụ:

```json
{
  "level": "lightup-3",
  "algorithm": "greedy",
  "state": {"bulbs": [0], "crosses": []}
}
```

Chỉ số ô = `hàng * số_cột + cột`, bắt đầu từ 0. Pipes dùng `state.tiles` và `state.fixed`.

## Hướng phát triển tiếp

- Gợi ý sửa ít lựa chọn nhất bằng bài toán tối ưu có trọng số.
- Cho người chơi ghim/bỏ ghim ô Pipes thay vì coi mọi ô đã chỉnh là ràng buộc.
- Thêm input lớn và phân loại độ khó bằng số đo thực tế.
- Xuất bộ benchmark lớn, báo cáo và slide thuyết trình từ kết quả đã kiểm chứng.
