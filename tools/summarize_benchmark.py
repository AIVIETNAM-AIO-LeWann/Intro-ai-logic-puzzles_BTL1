"""Build the report appendix from raw measurements; no copied/manual numbers."""
import argparse
import json
from pathlib import Path


def benchmark_markdown(data):
    lines = ["# Phụ lục thực nghiệm", "", "Nguồn: results/benchmark.json và results/benchmark.csv.", "",
             f"Python {data['python']}; {data['platform']}. {data['repeat']} lần đo thời gian mỗi tổ hợp; một lần đo bộ nhớ riêng.", "",
             "ms = median thời gian search; KiB = peak cấp phát Python trong search, không phải RSS. N = trạng thái đã xét, gồm đích.", "",
             f"Ngân sách: {data['limits']['timeout_seconds']} giây/lượt thường; {data['limits']['memory_timeout_seconds']} giây/lượt đo bộ nhớ; {data['limits']['max_nodes']} trạng thái/lượt.", "",
             "Nếu một tổ hợp chưa hoàn thành mọi lượt, bảng ghi rõ trạng thái; không diễn giải median của lượt bị giới hạn như thời gian giải thành công.", ""]
    records = {(r["level"], r["algorithm"]): r for r in data["results"]}
    for game in ("pipes", "lightup"):
        lines.extend([f"## {'Pipes' if game == 'pipes' else 'Light Up'}", "",
                      "| Input | DFS ms | Greedy ms | DFS KiB | Greedy KiB | DFS N | Greedy N |",
                      "| --- | --- | --- | --- | --- | --- | --- |"])
        for level in data["inputs"]:
            if level["game"] != game:
                continue
            dfs, greedy = (records[(level["id"], a)] for a in ("dfs", "greedy"))
            lines.append(f"| {level['id']} | {dfs['median_ms']:.3f} | {greedy['median_ms']:.3f} | "
                         f"{dfs['peak_python_kib']:.2f} | {greedy['peak_python_kib']:.2f} | {dfs['expanded']} | {greedy['expanded']} |")
            for record in (dfs, greedy):
                if record["solved_runs"] != data["repeat"] or record["memory_status"] != "solved":
                    lines.extend(["", f"Trạng thái {level['id']}/{record['algorithm']}: "
                                  f"{record['solved_runs']}/{data['repeat']} solved; các lượt: {record['statuses']}; "
                                  f"bộ nhớ: {record['memory_status']}.", ""])
        lines.append("")
    lines.extend(["## Dấu vết tái lập", "", f"Thời điểm UTC: {data['created_utc']}.", "",
                  f"SHA-256 input: {data['inputs_sha256']}.", "",
                  f"SHA-256 nguồn benchmark/logic_lab: {data['source_sha256']}.", "",
                  "JSON lưu nguyên input, từng thời gian, thống kê từng lượt, trạng thái kiểm tra nghiệm và thông tin môi trường. "
                  "Để chạy lại nguyên bộ input đã lưu, xuất trường inputs ra một tệp JSON rồi truyền --input cho benchmark.py.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="results/benchmark.json")
    parser.add_argument("--output", default="docs/BENCHMARK.md")
    args = parser.parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(benchmark_markdown(data), encoding="utf-8")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
