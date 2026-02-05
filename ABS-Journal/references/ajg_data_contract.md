## Purpose

本文件描述 ABS-Journal skill 的本地数据契约：AJG 抓取脚本产物、文件命名、以及离线校验方式。

## Output Files (Expected)

抓取脚本（`scripts/ajg_fetch.py`）写入 `--outdir` 后，期望至少存在：

- `ajg_<year>_journals_raw.jsonl`
- `ajg_<year>_meta.json`
- `ajg_<year>_journals_core_custom.csv`

其中 `<year>` 为脚本自动发现的最新年份（例如 2024）。

## Offline Verification

不联网校验（推荐）：

```bash
python3 /Users/lingguiwang/.agents/skills/abs-journal/scripts/ajg_verify_outputs.py \
  --outdir /Users/lingguiwang/.agents/skills/abs-journal/assets/data
```

## Notes

- 推荐脚本默认读取本地 CSV；本文件不规定推荐算法细节，只规定输入数据文件的最小可用性。
