"""Read the bundled Huasheng question bank using only the Python standard library."""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
import sys


BANK = Path(__file__).resolve().parents[1] / "assets" / "question-bank"
MODULES = {
    "pianduan": "片段阅读",
    "shuliang": "数量关系",
    "luoji": "逻辑判断",
    "ziliao": "资料分析",
}


def read_jsonl(path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def number_list(value):
    numbers = set()
    try:
        for part in value.split(","):
            bounds = [int(item) for item in part.split("-")]
            if len(bounds) == 1:
                numbers.add(bounds[0])
            elif len(bounds) == 2 and bounds[0] <= bounds[1]:
                numbers.update(range(bounds[0], bounds[1] + 1))
            else:
                raise ValueError
        if not numbers or min(numbers) < 1 or max(numbers) > 20:
            raise ValueError
    except ValueError as error:
        raise argparse.ArgumentTypeError("题号格式为 1,3,5-8，取值为 1 至 20") from error
    return numbers


def module_key(value):
    for key, label in MODULES.items():
        if value in (key, label):
            return key
    raise argparse.ArgumentTypeError("模块可选 pianduan、shuliang、luoji、ziliao 或对应中文名")


def positive_integer(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("请输入正整数")
    return number


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="花生习题内置题库，默认隐藏答案并排除待核对题")
    parser.add_argument("--module", type=module_key)
    parser.add_argument("--set", type=positive_integer, dest="set_number")
    parser.add_argument("--numbers", type=number_list)
    parser.add_argument("--id", nargs="+", help="一个或多个稳定题号，精确取题包含质量提示")
    parser.add_argument("--keyword", help="检索题干、选项、题型和共用材料")
    parser.add_argument("--tag", help="匹配原解析中的题型标签")
    parser.add_argument("--count", type=positive_integer, default=5)
    parser.add_argument("--seed", type=int, help="提供种子后随机抽题，可复现")
    parser.add_argument("--with-answer", action="store_true")
    parser.add_argument("--include-review", action="store_true", help="包含缺图、缺选项或格式存疑的题")
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--list-tags", action="store_true")
    args = parser.parse_args()
    if args.set_number and not args.module:
        parser.error("--set 需要同时指定 --module")
    if args.module and args.set_number:
        maximum = 60 if args.module == "shuliang" else 30
        if args.set_number > maximum:
            parser.error(f"该模块最多 {maximum} 套")
    if args.module == "shuliang" and args.numbers and max(args.numbers) > 10:
        parser.error("数量关系每套为 1 至 10 题")
    if args.stats:
        manifest = json.loads((BANK / "manifest.json").read_text(encoding="utf-8"))
        emit({key: manifest[key] for key in ("total_questions", "total_materials", "modules", "quality_flags")})
        return
    modules = [args.module] if args.module else list(MODULES)
    records = [record for module in modules for record in read_jsonl(BANK / f"{module}.jsonl")]
    materials = {item["id"]: item for item in read_jsonl(BANK / "materials.jsonl")}
    if args.id:
        missing = sorted(set(args.id) - {record["id"] for record in records})
        if missing:
            parser.error("未找到题号 " + ", ".join(missing))
    matched = []
    for record in records:
        if args.id and record["id"] not in args.id:
            continue
        if args.set_number and record["set"] != args.set_number:
            continue
        if args.numbers and record["number"] not in args.numbers:
            continue
        if args.tag and not any(args.tag.casefold() in tag.casefold() for tag in record["tags"]):
            continue
        material = materials.get(record["material_id"])
        searchable = "\n".join([record["stem"], *record["options"].values(), *record["tags"],
                                 material["text"] if material else ""])
        if args.keyword and args.keyword.casefold() not in searchable.casefold():
            continue
        matched.append(record)
    if args.list_tags:
        emit(dict(sorted(Counter(tag for record in matched for tag in record["tags"]).items())))
        return
    eligible = [record for record in matched if args.include_review or args.id or not record["quality_flags"]]
    requested = len(args.id) if args.id else args.count
    size = min(requested, len(eligible))
    selected = random.Random(args.seed).sample(eligible, size) if args.seed is not None else eligible[:size]
    questions = []
    selected_materials = {}
    for record in selected:
        question = {key: record[key] for key in ("id", "module", "set", "number", "stem", "options",
                                                 "material_id", "quality_flags", "question_source")}
        # Source labels and difficulty remain hidden in practice mode because some reveal the method.
        if args.with_answer:
            question.update({key: record[key] for key in ("answer", "answer_origin", "analysis", "tags",
                                                          "difficulty", "analysis_source")})
        questions.append(question)
        material_id = record["material_id"]
        if material_id:
            material = materials[material_id]
            selected_materials[material_id] = {key: value for key, value in material.items()
                                               if args.with_answer or key not in ("analysis_context", "analysis_source")}
    emit(dict(requested=requested, matched=len(matched), eligible=len(eligible), returned=len(selected),
              excluded_review=len(matched) - len(eligible),
              shortage=max(0, requested - len(selected)), questions=questions,
              materials=list(selected_materials.values())))


if __name__ == "__main__":
    main()
