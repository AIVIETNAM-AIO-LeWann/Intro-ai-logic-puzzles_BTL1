# Phân công nhóm 5 người

Bản hiện tại là baseline để nhóm đọc, kiểm chứng và phát triển. Có ứng dụng chơi được, hai solver, gợi ý theo trạng thái, test và công cụ benchmark. Chưa coi đây là bộ nộp hoàn chỉnh: cần review thuật toán, dữ liệu đa dạng, thực nghiệm, báo cáo, slide và kiểm tra giao diện thật.

Thay TV2–TV5 bằng tên thành viên sau khi nhóm thống nhất. Mỗi người chịu trách nhiệm cả sản phẩm lẫn phần giải thích khi thuyết trình.

## 1. Bạn — tích hợp, gợi ý và demo

**Phụ trách:** `web/`, `logic_lab/service.py`, `logic_lab/http_api.py`, `app.py`, `wsgi.py`, cấu hình triển khai.

- Hướng dẫn nhóm chạy baseline và giữ phiên bản ổn định trên nhánh main.
- Kiểm tra giao diện trên máy tính và điện thoại theo `docs/MANUAL_QA.md`.
- Hoàn thiện phản hồi khi gợi ý thành công, cần sửa hoặc hết ngân sách; không hiển thị kết quả từ bảng cũ sau khi người chơi đổi bảng.
- Review và ghép PR của các thành viên. Thay đổi `search.py` cần thống nhất với cả hai người phụ trách thuật toán.
- Chuẩn bị bản demo local và bản Render nếu nhóm chọn triển khai; đóng gói bản cuối sau khi mọi phần đạt yêu cầu.
- Viết phần kiến trúc ứng dụng, gợi ý và giới hạn; trình bày demo.

**Hoàn thành khi:** chạy sạch từ clone mới; cả hai game chơi được; gợi ý và hoàn tác đúng; demo không sửa bảng người chơi; không có lỗi chặn luồng thao tác chính.

## 2. TV2 — Pipes và thuật toán của Pipes

**Phụ trách:** `logic_lab/games/pipes.py`, `tests/test_pipes.py` (tạo mới), `docs/report/pipes.md` (tạo mới).

- Đọc và giải thích được bitmask, phép xoay, trạng thái gán hướng từng phần, goal test và sinh nhánh.
- Kiểm tra DFS có dùng heuristic để chọn nhánh không; giải thích tác dụng của các phép cắt nhánh dùng chung.
- Review tính đúng của kiểm tra đầu hở, biên, chu trình và liên thông. Thêm test đối chiếu vét cạn trên bảng nhỏ.
- Đánh giá heuristic hiện tại; đề xuất cải tiến nếu có bằng chứng, giữ baseline để so sánh. Không bắt buộc đổi thuật toán chỉ để tạo khác biệt.
- Gửi đề xuất màn/nhóm tình huống Pipes cho TV4; không tự thay bộ dữ liệu chung mà chưa thống nhất.
- Viết phần Pipes trong báo cáo: luật, mô hình, giả mã, heuristic, ví dụ và giới hạn. Chuẩn bị 2–3 slide nội dung cho TV5.

**Hoàn thành khi:** lời giải qua bộ kiểm tra độc lập; test cho các lỗi nêu trên; giải thích rõ một hành động search khác một lần click xoay như thế nào; có nội dung báo cáo và ví dụ truy vết.

## 3. TV3 — Light Up và thuật toán của Light Up

**Phụ trách:** `logic_lab/games/lightup.py`, `tests/test_lightup.py` (tạo mới), `docs/report/lightup.md` (tạo mới).

- Kiểm tra ánh sáng bị chặn bởi ô đen, đèn nhìn nhau, số đèn kề cạnh và ô số 0.
- Giải thích trạng thái -1/0/1, cách giữ đèn/dấu × của người chơi và điều kiện cắt nhánh.
- Test các bảng có nhiều nghiệm, không có nghiệm và ràng buộc người chơi sai. Đối chiếu solver với vét cạn trên bảng nhỏ.
- Đánh giá heuristic ô chưa sáng + thiếu đèn; giải thích vì sao dùng cho Greedy và không tự gọi nó là heuristic admissible cho A*.
- Gửi các nhóm tình huống Light Up cho TV4. Nếu cải tiến, giữ phiên bản baseline hoặc cấu hình tái lập được để đối chiếu.
- Viết phần Light Up trong báo cáo và chuẩn bị 2–3 slide nội dung cho TV5.

**Hoàn thành khi:** test phủ đủ luật; gợi ý giữ được lựa chọn đúng và chấp nhận nghiệm khác; trình bày được một nhánh thành công và một nhánh bị loại.

## 4. TV4 — dữ liệu, thực nghiệm và phân tích

**Phụ trách:** `logic_lab/levels.py`, `benchmark.py`, `results/`, `docs/report/experiments.md` (tạo mới).

- Tách bộ màn chơi nhanh khỏi bộ benchmark nếu số lượng tăng; ghi nguồn hoặc cách tạo, seed, kích thước và đặc điểm từng input.
- Mục tiêu ban đầu: tối thiểu 10 input cho mỗi game, trải trên ít nhất 3 kích thước, tăng thêm nếu thời gian cho phép. Đây là mục tiêu nội bộ, không phải yêu cầu số lượng của đề.
- Phối hợp TV2/TV3 để xác nhận input và lời giải. Không khẳng định nghiệm duy nhất nếu chưa kiểm chứng.
- Đo DFS và Greedy trên cùng input, cùng giới hạn, cùng thứ tự sinh nhánh/cắt nhánh; lặp ít nhất 5 lần để lấy trung vị thời gian.
- Ghi Python, hệ điều hành, CPU/RAM và phiên bản commit. Lưu dữ liệu thô, trạng thái solved/unsat/limit, số trạng thái xét và peak frontier.
- Đo bộ nhớ riêng; nêu rõ tracemalloc chỉ đo cấp phát Python, không phải toàn bộ RAM/RSS. Không trộn thời gian ghi trace, HTTP hoặc hoạt ảnh với thời gian solver.
- Làm bảng và biểu đồ, giải thích khi Greedy chậm hơn DFS; không bỏ những kết quả bất lợi hay coi timeout là vô nghiệm.

**Hoàn thành khi:** có lệnh tái lập, dữ liệu thô và bảng tổng hợp; mỗi kết luận gắn với số liệu; TV2/TV3 review diễn giải thuật toán.

## 5. TV5 — kiểm thử độc lập, báo cáo và slide

**Phụ trách:** `docs/MANUAL_QA.md`, `docs/QA_RESULTS.md` (tạo mới), `docs/report/` phần chung, `report/` và `slides/` khi xuất bản cuối.

- Đọc đề và lập bảng đối chiếu yêu cầu với sản phẩm: 2 game, mỗi game 2 thuật toán, Python, trực quan, thời gian/bộ nhớ, báo cáo, slide, ZIP.
- Chơi thử độc lập trên trình duyệt; ghi thiết bị, thao tác tái hiện, kết quả mong đợi/thực tế và ảnh khi có lỗi. Mở issue thay vì âm thầm sửa file của người khác.
- Review khả năng cài/chạy từ clone mới theo README; phân biệt test logic đã pass với UI đã được quan sát thật.
- Lập sườn báo cáo sớm; biên tập phần Pipes của TV2, Light Up của TV3, thực nghiệm của TV4 và kiến trúc của bạn. Mỗi tác giả tự xác nhận nội dung kỹ thuật mình gửi.
- Hoàn thiện slide, dẫn nguồn, tên/MSSV, bảng phân công và kịch bản thuyết trình. Không tự bịa phần giải thích hoặc số đo để lấp chỗ thiếu.
- Kiểm tra ZIP có source, báo cáo, slide và hướng dẫn chạy; chạy thử bản giải nén trước khi bàn giao.

**Hoàn thành khi:** checklist đề đủ, lỗi quan trọng được xử lý hoặc ghi rõ, số liệu trong báo cáo khớp file benchmark, mọi thành viên có phần thuyết trình và bản nộp mở được.

## Mốc làm việc đề xuất

Chưa có hạn nộp chính thức trong đề đã đọc, nên các mốc sau tính từ ngày nhóm bắt đầu và có thể điều chỉnh.

| Mốc | Sản phẩm cần có |
|---|---|
| Ngày 1 | Cả 5 người chạy được baseline; chia nhánh; từng người báo lại cách hoạt động phần mình |
| Ngày 2–3 | Review luật/thuật toán, thêm test; bộ input nháp; sườn báo cáo; danh sách lỗi UI |
| Ngày 4–5 | Merge sửa lỗi đã review; chốt phiên bản thuật toán; chạy benchmark chính thức |
| Ngày 6 | Báo cáo và slide nháp đầy đủ; đối chiếu số liệu; tổng duyệt demo |
| Ngày 7 | Sửa lỗi cuối, kiểm tra bản giải nén, chốt release và phân công nộp |

Không chạy benchmark chính thức rồi tiếp tục sửa thuật toán mà vẫn dùng kết quả cũ. Nếu thay đổi có ảnh hưởng, TV4 chạy lại phần liên quan.

## Quy trình Git cho nhóm

1. `main` là bản ổn định. Mỗi nhiệm vụ làm trên nhánh riêng: `feat/pipes-review`, `feat/lightup-review`, `feat/benchmark`, `docs/report-qa`, `feat/ui-hints`.
2. Mở issue có mục tiêu, file dự kiến và điều kiện xong trước khi sửa lớn.
3. Mỗi PR tập trung một việc, ghi thay đổi và cách kiểm tra. Có ít nhất một người khác đọc trước khi bạn merge.
4. Chạy `python -m unittest discover -s tests -v`. Nếu có Node, thêm `node tests/check_frontend.mjs`; GitHub CI cũng chạy cả hai.
5. TV2/TV3 tạo file test riêng thay vì cùng sửa `tests/test_logic.py`. TV4 sở hữu `levels.py`; người khác gửi case hoặc PR nhỏ.
6. `search.py` là lõi dùng chung: thảo luận giao diện hàm, quy ước đếm và ngân sách với bạn, TV2, TV3 trước khi sửa.
7. Không commit `.venv`, `__pycache__`, secret hoặc file tạm. Chỉ lưu kết quả benchmark có chủ đích; cập nhật thông tin phiên bản khi đo.

## Issue có thể tạo ngay

- [Bạn] Kiểm tra và hoàn thiện UI/hint trên desktop và mobile.
- [TV2] Review Pipes, bổ sung test và viết phần mô hình/thuật toán.
- [TV3] Review Light Up, bổ sung test và viết phần mô hình/thuật toán.
- [TV4] Xây bộ input tái lập và so sánh DFS/Greedy bằng dữ liệu thực tế.
- [TV5] Checklist nghiệm thu, tổng hợp báo cáo/slide và chạy thử bản nộp.

Sau khi có tên thành viên, gán người phụ trách trên GitHub; tài liệu này chưa tự gửi tin hay tạo issue cho ai.
