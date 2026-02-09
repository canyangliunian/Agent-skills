# 投稿期刊推荐（混合流程：脚本候选池 → AI 二次筛选）

## 可追溯信息

- 候选池形态：easy/medium/hard 多池（嵌入于 AI 输出 JSON；用于离线 auto_ai 复现与校验）
- Easy：AJG CSV=/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/ABS-Journal/assets/data/ajg_2024_journals_core_custom.csv；星级过滤=1,2；规模=100
- Medium：AJG CSV=/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/ABS-Journal/assets/data/ajg_2024_journals_core_custom.csv；星级过滤=2,3；规模=100
- Hard：AJG CSV=/Users/lingguiwang/Documents/Coding/LLM/Agent-skills/ABS-Journal/assets/data/ajg_2024_journals_core_custom.csv；星级过滤=4,4*；规模=56

## 论文信息

- 标题：Information, beliefs and support for retaliatory tariffs on US agricultural products: evidence from a randomised controlled trial in China
- 摘要：The US–China trade war has profoundly reshaped global agricultural markets, yet the consequences of protectionist measures for domestic public attitudes—particularly within collectivist societies like China—have been underexplored. This study investigates how Chinese citizens perceive retaliatory tariffs on US agricultural products and explores how awareness of economic self-interest shapes their support for such policies.

## 推荐清单（固定列）

### Easy Top10

| 序号 | 期刊名 | ABS星级 | Field |
|---:|---|---:|---|
| 1 | Journal of International Trade and Economic Development | 1 | ECON |
| 2 | Agricultural and Resource Economics Review | 1 | ECON |
| 3 | China Agricultural Economic Review | 1 | ECON |
| 4 | Economia Agraria y Recursos Naturales – Agricultural and Resource Economics | 1 | ECON |
| 5 | Journal of Agricultural & Applied Economics | 1 | ECON |
| 6 | Journal of Agricultural and Food Industrial Organization | 1 | ECON |
| 7 | Studies in Agricultural Economics | 1 | ECON |
| 8 | Applied Health Economics and Heath Policy | 1 | ECON |
| 9 | Behavioural Public Policy | 1 | ECON |
| 10 | Economic Analysis and Policy | 1 | ECON |

### Medium Top10

| 序号 | 期刊名 | ABS星级 | Field |
|---:|---|---:|---|
| 1 | Agricultural Economics (United Kingdom) | 2 | ECON |
| 2 | Australian Journal of Agricultural and Resource Economics | 2 | ECON |
| 3 | Canadian Journal of Agricultural Economics | 2 | ECON |
| 4 | Journal of Agricultural and Resource Economics | 2 | ECON |
| 5 | Journal of Industry, Competition and Trade | 2 | ECON |
| 6 | Public Money and Management | 2 | PUB SEC |
| 7 | Public Administration and Development | 2 | PUB SEC |
| 8 | Annals of Public and Cooperative Economics | 2 | ECON |
| 9 | Applied Economic Perspectives and Policy | 2 | ECON |
| 10 | B.E. Journal of Economic Analysis and Policy | 2 | ECON |

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
| 10 | Public Administration Review | 4* | PUB SEC |

## 说明

- `Field` 来自候选池（AJG CSV 的 Field 列），用于快速定位期刊所属领域。
- 本流程不自动联网查询审稿周期/版面费/投稿偏好等信息。
