# Phụ lục thực nghiệm

Nguồn: results/benchmark.json và results/benchmark.csv.

Python 3.12.14; Windows-11-10.0.26200-SP0. 7 lần đo thời gian mỗi tổ hợp; một lần đo bộ nhớ riêng.

ms = median thời gian search; KiB = peak cấp phát Python trong search, không phải RSS. N = trạng thái đã xét, gồm đích.

Ngân sách: 4.0 giây/lượt thường; 30.0 giây/lượt đo bộ nhớ; 100000 trạng thái/lượt.

Nếu một tổ hợp chưa hoàn thành mọi lượt, bảng ghi rõ trạng thái; không diễn giải median của lượt bị giới hạn như thời gian giải thành công.

## Pipes

| Input | DFS ms | Greedy ms | DFS KiB | Greedy KiB | DFS N | Greedy N |
| --- | --- | --- | --- | --- | --- | --- |
| pipes-3 | 0.253 | 0.265 | 9.84 | 9.73 | 10 | 10 |
| pipes-4 | 0.735 | 0.754 | 20.76 | 20.80 | 17 | 17 |
| pipes-5 | 1.885 | 1.864 | 46.08 | 46.16 | 28 | 28 |
| pipes-6 | 3.631 | 3.853 | 84.48 | 84.52 | 37 | 37 |
| pipes-4-seed-101 | 0.648 | 0.674 | 21.57 | 21.61 | 17 | 17 |
| pipes-4-seed-102 | 0.650 | 0.668 | 21.89 | 21.93 | 17 | 17 |
| pipes-4-seed-103 | 0.657 | 0.683 | 22.31 | 22.35 | 17 | 17 |
| pipes-6-seed-101 | 3.018 | 3.096 | 83.05 | 83.09 | 37 | 37 |
| pipes-6-seed-102 | 2.952 | 3.087 | 83.20 | 83.23 | 37 | 37 |
| pipes-6-seed-103 | 3.023 | 3.306 | 83.45 | 83.48 | 37 | 37 |
| pipes-8-seed-101 | 10.332 | 10.561 | 195.39 | 195.45 | 67 | 67 |
| pipes-8-seed-102 | 9.514 | 11.190 | 209.72 | 209.76 | 65 | 65 |
| pipes-8-seed-103 | 12.033 | 13.000 | 213.34 | 210.48 | 67 | 69 |

## Light Up

| Input | DFS ms | Greedy ms | DFS KiB | Greedy KiB | DFS N | Greedy N |
| --- | --- | --- | --- | --- | --- | --- |
| lightup-3 | 0.064 | 0.087 | 4.74 | 6.23 | 7 | 9 |
| lightup-5 | 0.625 | 0.780 | 14.82 | 18.55 | 32 | 35 |
| lightup-6 | 0.447 | 0.713 | 12.41 | 14.36 | 20 | 26 |
| lightup-7 | 1.629 | 4.711 | 35.10 | 61.02 | 51 | 142 |
| lightup-4-seed-101 | 0.152 | 0.184 | 5.39 | 5.62 | 9 | 9 |
| lightup-4-seed-102 | 0.162 | 0.161 | 7.34 | 8.69 | 14 | 11 |
| lightup-4-seed-103 | 0.119 | 0.142 | 5.24 | 5.49 | 7 | 7 |
| lightup-6-seed-101 | 0.686 | 0.608 | 19.15 | 19.86 | 29 | 23 |
| lightup-6-seed-102 | 0.683 | 0.802 | 15.56 | 18.84 | 31 | 29 |
| lightup-6-seed-103 | 1.397 | 0.620 | 21.94 | 17.55 | 56 | 22 |
| lightup-8-seed-101 | 2.197 | 2.221 | 21.59 | 26.36 | 52 | 44 |
| lightup-8-seed-102 | 47.455 | 2.577 | 366.38 | 38.19 | 1584 | 68 |
| lightup-8-seed-103 | 1.881 | 1.744 | 31.78 | 31.41 | 53 | 43 |

## Dấu vết tái lập

Thời điểm UTC: 2026-10-25T13:38:49.795438+00:00.

SHA-256 input: a71abd6a65c3bed8f523a15c4636f54ed6f1db8fd242bcbbe5383c709d5fe3d7.

SHA-256 nguồn benchmark/logic_lab: 099ca1fab095061fcedca7bcf604be403df7764d23fc073f5c9b8385587ca78b.

JSON lưu nguyên input, từng thời gian, thống kê từng lượt, trạng thái kiểm tra nghiệm và thông tin môi trường. Để chạy lại nguyên bộ input đã lưu, xuất trường inputs ra một tệp JSON rồi truyền --input cho benchmark.py.
