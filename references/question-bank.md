# 花生习题内置题库

## 收录范围

2026 年 11 月 6 日按用户请求导入“花生习题”目录中的 10 份 DOCX，保存题本、配套解析和来源文件。

| 模块 | 参数 | 题数 | 套数 | 每套题数 | 已标记待核对 |
| --- | --- | --- | --- | --- | --- |
| 片段阅读 | `pianduan` | 600 | 30 | 20 | 1 |
| 数量关系 | `shuliang` | 600 | 60 | 10 | 63 |
| 逻辑判断 | `luoji` | 600 | 30 | 20 | 2 |
| 资料分析 | `ziliao` | 600 | 30 | 20 | 302 |
| 合计 | | 2400 | 150 | | 368 |

资料分析保存 120 篇共用材料，每篇关联原套的 5 道题，并保留表格行列。片段阅读上下册分别对应第 1 至 15 套、第 16 至 30 套。

## 按需取题

先确定 skill 的实际目录。以下 `<skill目录>` 均指包含 `SKILL.md` 的目录，脚本使用自身路径定位题库。Python 仅使用标准库，支持从其他工作目录运行。Windows 可使用环境提供的 Python 可执行文件。

```bash
python "<skill目录>/scripts/question_bank.py" --stats
python "<skill目录>/scripts/question_bank.py" --module pianduan --count 5 --seed 20261106
python "<skill目录>/scripts/question_bank.py" --module shuliang --set 3 --count 10
python "<skill目录>/scripts/question_bank.py" --module luoji --tag 加强 --count 5 --seed 42
python "<skill目录>/scripts/question_bank.py" --module ziliao --tag 增长量 --count 5 --seed 42
python "<skill目录>/scripts/question_bank.py" --module shuliang --keyword 工程 --count 5
python "<skill目录>/scripts/question_bank.py" --module ziliao --set 1 --numbers 1-5 --count 5
python "<skill目录>/scripts/question_bank.py" --id HS13-PIANDUAN-01-01 --with-answer
python "<skill目录>/scripts/question_bank.py" --module ziliao --set 1 --count 20 --include-review
python "<skill目录>/scripts/question_bank.py" --module shuliang --list-tags
```

- `--module` 接受上表参数或对应中文模块名。
- `--set` 表示原书练习套号，需要同时提供模块。
- `--numbers` 接受 `1,3,5-8` 形式的原套题号。
- `--id` 可接收多个稳定题号，精确查询会返回待核对记录及其质量提示。
- `--keyword` 搜索题干、选项、题型标签和共用材料。`--tag` 匹配原解析中的题型标签。
- `--count` 默认 5。提供 `--seed` 时随机抽取，省略时按题库顺序返回。
- `--with-answer` 加载答案、原文解析、题型、难度和资料分析的材料批注。练习阶段默认隐藏这些字段。
- `--include-review` 纳入待核对记录，适用于核查原套缺项或用户要求查看指定整套。

输出为 JSON。`matched` 是符合检索条件的总数，`eligible` 是应用质量筛选后的数量，`returned` 是本次返回数量，`excluded_review` 是排除的待核对数量，`shortage` 表示本次题数缺口。按返回值说明实际题量。

稳定题号采用 `HS13-模块大写-两位套号-两位题号`，例如 `HS13-SHULIANG-03-02`。批改、错题复练与连续练习沿用此 ID，并保留选项顺序。资料分析题的 `material_id` 对应输出 `materials` 中的共用材料，展示时将材料与题目一并提供。默认隐藏解析与材料批注，防止提前泄露答案。读取解析后，只展示本次讲解对应的内容，材料批注可能涉及同篇其他题的答案。

## 来源和数据结构

`assets/question-bank/` 中包含以下文件。

- `pianduan.jsonl`、`shuliang.jsonl`、`luoji.jsonl`、`ziliao.jsonl` 每行保存一道题及其配套解析。
- `materials.jsonl` 保存共用材料、表格、材料批注与来源定位。
- `manifest.json` 保存统计、源文件 SHA-256、清理记录和答案冲突记录。
- `sources/` 保存用户提供的 10 份原始 DOCX 副本。

题目记录保存 `id`、`module`、`set`、`number`、`stem`、`options`、`material_id`、`tags`、`difficulty`、`answer`、`answer_origin`、`analysis`、`quality_flags`、`question_source` 和 `analysis_source`。来源中的 `file` 相对于 `assets/question-bank/`，`body_block_start` 与 `body_block_end_inclusive` 为 `word/document.xml` 正文直接子节点的零基索引，末端含在范围内。`start_part` 和 `end_part` 标明同一原始段落拆开的逻辑片段。题号定位优先使用原套号与题号。

解析可能保留原书对题干、选项的批注。练习题干采用题本版本，答案与解析采用对应解析版本。抽题后结合所需模块的方法论讲解即可，按需查询可控制加载量。

## 待核对记录

源 DOCX 中存在引用图形但缺少对应图片的情况，还存在少量选项、公式转换异常。入库时保留全部 2,400 道题，并为发现的问题添加标记。默认抽题范围为其余 2,032 道。标记项会重叠，字段含义如下。

| 标记 | 含义 |
| --- | --- |
| `visual_reference_without_embedded_figure` | 题目或共用材料引用图形，源文件未包含可提取的图形，需核对原图 |
| `missing_options` | 选项数量不足或选项内容为空 |
| `answer_option_missing` | 参考答案对应的选项缺失 |
| `ocr_math_artifact` | 公式含明显转换残留或替换字符 |
| `question_analysis_option_mismatch` | 题本与解析的选项文本存在待核对差异 |
| `source_answer_conflict` | 同篇总答案与逐题答案不同 |

已发现资料分析第 18 套第 13 题的全篇答案与逐题答案不一致，两个版本均保留在来源记录中。数量第 6 套第 7 题缺少参考答案标签，其解析明确写出 D，`answer_origin` 记录为 `explicit_solution_conclusion`。此题同时带有缺图提示。

对缺图、缺选项或材料不足的题，先检查原始文件或用户补充的完整题图，再确定能否作答。可识别的公式残留可与解析逐项核对。存在答案冲突时独立验算并说明来源差异。

入库已清理 141 处相同的宣传尾注、1 处 OCR 指令残留及重复横线，原始文件完整保存。片段阅读解析上册在首套之前夹有无关公司公告，题目索引从实际套题标题开始。原书的题目整体评价、平均正确率和示例测试结果按教材背景处理，学习记录使用当前用户的实际作答。
