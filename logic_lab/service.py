"""Game API and honest, progress-aware hints."""
from .levels import BY_ID
from .games.pipes import Pipes, rotate
from .games.lightup import LightUp
from .search import search


def integer_list(value, label, max_length=200):
    if not isinstance(value, list) or len(value) > max_length or any(type(x) is not int for x in value):
        raise ValueError(f"{label} phải là danh sách vị trí hợp lệ.")
    return value


def context(data):
    if not isinstance(data, dict) or data.get("level") not in BY_ID:
        raise ValueError("Màn chơi không tồn tại.")
    level = BY_ID[data["level"]]
    state = data.get("state", {})
    if not isinstance(state, dict):
        raise ValueError("Trạng thái không hợp lệ.")
    if level["game"] == "pipes":
        tiles = integer_list(state.get("tiles", level["tiles"]), "Hướng ống")
        fixed = integer_list(state.get("fixed", []), "Ô đã chỉnh")
        puzzle = Pipes(level, tiles, fixed)
        state = {"tiles": tiles, "fixed": sorted(set(fixed))}
    else:
        bulbs = integer_list(state.get("bulbs", []), "Đèn")
        crosses = integer_list(state.get("crosses", []), "Dấu X")
        puzzle = LightUp(level, bulbs, crosses)
        state = {"bulbs": sorted(set(bulbs)), "crosses": sorted(set(crosses))}
    return level, state, puzzle


def check(data):
    level, state, puzzle = context(data)
    return puzzle.check(state["tiles"]) if level["game"] == "pipes" else puzzle.check(state["bulbs"], state["crosses"])


def solve(data, trace=False):
    _, _, puzzle = context(data)
    return search(puzzle, algorithm=data.get("algorithm", "greedy"),
                  timeout=5.0, max_nodes=100000, trace_limit=350 if trace else 0)


def hint(data):
    level, state, puzzle = context(data)
    algorithm = data.get("algorithm", "greedy")
    if check(data)["solved"]:
        return {"status": "complete", "message": "Bạn đã giải đúng màn này. Mọi điều kiện đều được thỏa!"}
    result = search(puzzle, algorithm, timeout=4.0, max_nodes=80000)
    if result["status"] == "limit":
        return {**result, "message": "Máy đã chạm giới hạn tìm kiếm. Chưa thể kết luận các nước đi của bạn sai. Hãy thử thuật toán còn lại hoặc hoàn tác một bước."}
    repair = result["status"] == "unsat"
    original_metrics = result["metrics"]
    if repair:
        clean = Pipes(level) if level["game"] == "pipes" else LightUp(level)
        result = search(clean, algorithm, timeout=4.0, max_nodes=80000)
        if result["status"] != "solved":
            return {"status": "repair_limit", "metrics": original_metrics,
                    "message": "Các lựa chọn hiện tại không thể hoàn thành. Máy chưa tìm được phương án sửa trong giới hạn; bạn có thể hoàn tác hoặc bỏ một dấu đã đặt."}
    solution = result["solution"]
    if level["game"] == "pipes":
        candidates = state["fixed"] if repair else range(len(state["tiles"]))
        cell = next(i for i in candidates if state["tiles"][i] != solution["tiles"][i])
        value, turns = state["tiles"][cell], 0
        while value != solution["tiles"][cell]:
            value = rotate(value)
            turns += 1
        action = {"kind": "rotate", "cell": cell, "value": value, "turns": turns}
        detail = f"Xoay ô hàng {cell // level['cols'] + 1}, cột {cell % level['cols'] + 1} thêm {turns * 90}° theo chiều kim đồng hồ."
    else:
        target = set(solution["bulbs"])
        wrong_bulbs = set(state["bulbs"]) - target
        wrong_crosses = set(state["crosses"]) & target
        if repair and wrong_bulbs:
            cell = min(wrong_bulbs)
            action = {"kind": "remove_bulb", "cell": cell}
            verb = "Bỏ đèn ở"
        elif repair and wrong_crosses:
            cell = min(wrong_crosses)
            action = {"kind": "remove_cross", "cell": cell}
            verb = "Bỏ dấu X ở"
        else:
            cell = min(target - set(state["bulbs"]))
            action = {"kind": "add_bulb", "cell": cell}
            verb = "Đặt một đèn tại"
        detail = f"{verb} ô hàng {cell // level['cols'] + 1}, cột {cell % level['cols'] + 1}."
    return {"status": "repair" if repair else "hint", "action": action,
            "message": detail,
            "explanation": ("Không có lời giải giữ nguyên toàn bộ lựa chọn hiện tại. Đây là một bước sửa theo một lời giải hợp lệ; có thể cần sửa thêm. Máy không tự thay đổi bảng và không khẳng định đây là cách sửa ít bước nhất."
                            if repair else "Máy đã tìm được một lời giải hoàn chỉnh giữ nguyên các lựa chọn của bạn. Đây là một bước trong lời giải đó; có thể tồn tại cách giải khác."),
            "metrics": result["metrics"], "diagnosis_metrics": original_metrics if repair else None}
