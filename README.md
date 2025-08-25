# A股今日看点（三次自动分析）

本仓库提供脚本化流程，自动在早盘、午盘与收盘三个时间窗口生成 A 股市场分析，并以 CSV 与 Markdown 形式归档。

## 环境准备
- Python 3.10+
- 配置环境变量 `OPENAI_API_KEY` 以调用 OpenAI 接口
- 准备行情/资讯数据源，写入 `context.md`

## 目录结构
- `prompts/`：提示词模板。
- `logs/YYYYMM/`：按月归档的 Markdown 日志。
- `tri_daily.csv`：三段摘要的索引表。
- `schema.json`：单次记录的 JSON Schema。
- `runner.py`：生成入口脚本。
- `scheduler_stub.py`：调度示例。

## CSV 规范
表头：`date,slot,one_liner,md_path,sources_json`。
- `date`：交易日（YYYY-MM-DD）。
- `slot`：`morning`、`noon` 或 `close`。
- `one_liner`：不超过 80 字的单行摘要。
- `md_path`：对应 Markdown 文件路径。
- `sources_json`：引用来源的字符串数组（JSON 格式）。

## 日志归档
所有 Markdown 结果写入 `logs/YYYYMM/`，文件名遵循 `YYYYMMDD_{slot}.md`。

## 使用方法
1. 将当日行情整理为 `context.md`（或通过 `--context` 指定路径）。
2. 执行 `python runner.py --slot morning|noon|close` 生成对应时间段的分析；若省略 `--slot`，脚本会按当前时间推断。
3. 成功运行后，可在 `logs/YYYYMM/` 及 `tri_daily.csv` 查看结果。
4. 可参考 `scheduler_stub.py` 在 crontab 或 systemd 中定时触发。

## 贡献指南
欢迎提交 Pull Request，请在提交前确保代码通过基本语法检查：
```
python -m py_compile runner.py scheduler_stub.py
```

