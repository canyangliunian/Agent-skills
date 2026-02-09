# 投稿期刊推荐（混合流程：脚本候选池 → AI 二次筛选）

## 可追溯信息

- 候选池形态：easy/medium/hard 多池（嵌入于 AI 输出 JSON；用于离线 auto_ai 复现与校验）
- Easy：AJG CSV=/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/ABS-Journal/assets/data/ajg_2024_journals_core_custom.csv；星级过滤=1,2；规模=160
- Medium：AJG CSV=/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/ABS-Journal/assets/data/ajg_2024_journals_core_custom.csv；星级过滤=2,3；规模=160
- Hard：AJG CSV=/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/ABS-Journal/assets/data/ajg_2024_journals_core_custom.csv；星级过滤=4,4*；规模=56

## 论文信息

- 标题：test

## 推荐清单（固定列）

### Easy Top10

| 序号 | 期刊名 | ABS星级 | Field |
|---:|---|---:|---|
| 1 | Agricultural and Resource Economics Review | 1 | ECON |
| 2 | Applied Health Economics and Heath Policy | 1 | ECON |
| 3 | Behavioural Public Policy | 1 | ECON |
| 4 | China Agricultural Economic Review | 1 | ECON |
| 5 | Constitutional Political Economy | 1 | ECON |
| 6 | Economia Agraria y Recursos Naturales – Agricultural and Resource Economics | 1 | ECON |
| 7 | Economic Analysis and Policy | 1 | ECON |
| 8 | Economics of Energy and Environmental Policy | 1 | ECON |
| 9 | Ekonomicheskaya Politika / Economic Policy | 1 | ECON |
| 10 | Environmental Economics and Policy Studies | 1 | ECON |

### Medium Top10

| 序号 | 期刊名 | ABS星级 | Field |
|---:|---|---:|---|
| 1 | Agricultural Economics (United Kingdom) | 2 | ECON |
| 2 | Annals of Public and Cooperative Economics | 2 | ECON |
| 3 | Applied Economic Perspectives and Policy | 2 | ECON |
| 4 | Australian Journal of Agricultural and Resource Economics | 2 | ECON |
| 5 | B.E. Journal of Economic Analysis and Policy | 2 | ECON |
| 6 | Canadian Journal of Agricultural Economics | 2 | ECON |
| 7 | Contemporary Economic Policy | 2 | ECON |
| 8 | Contributions to Political Economy | 2 | ECON |
| 9 | European Journal of Political Economy | 2 | ECON |
| 10 | History of Political Economy | 2 | ECON |

### Hard Top10

| 序号 | 期刊名 | ABS星级 | Field |
|---:|---|---:|---|
| 1 | Biometrika | 4 | ECON |
| 2 | International Economic Review | 4 | ECON |
| 3 | RAND Journal of Economics | 4 | ECON |
| 4 | Journal of Economic Theory | 4 | ECON |
| 5 | Quantitative Economics | 4 | ECON |
| 6 | Theoretical Economics | 4 | ECON |
| 7 | Annals of Statistics | 4* | ECON |
| 8 | Econometric Theory | 4 | ECON |
| 9 | Risk Analysis | 4 | SOC SCI |
| 10 | Journal of International Economics | 4 | ECON |

## 说明

- `Field` 来自候选池（AJG CSV 的 Field 列），用于快速定位期刊所属领域。
- 本流程不自动联网查询审稿周期/版面费/投稿偏好等信息。
