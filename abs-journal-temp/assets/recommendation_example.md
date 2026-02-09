# 期刊推荐输出示例

本文档展示 `abs-journal` 技能的典型输出格式。

---

## 输出格式说明

推荐报告分为三个难度等级，每个等级包含 10 本期刊（默认）：

- **Easy 模式**：较容易投稿的期刊（ABS 1-2星）
- **Medium 模式**：中等难度的期刊（ABS 2-3星）
- **Hard 模式**：高难度的期刊（ABS 4-4*星）

每条推荐包含以下信息：
- **序号**：推荐顺序
- **期刊名**：期刊全称
- **ABS星级**：ABS 评级（1, 2, 3, 4, 4*）
- **Field**：期刊所属领域（如 ECON, FINANCE）
- **推荐理由**：AI 根据论文内容生成的匹配度说明

---

## 示例输出

### Easy 模式推荐（较容易投稿）

| 序号 | 期刊名 | ABS星级 | Field | 推荐理由 |
|------|--------|---------|-------|----------|
| 1 | Applied Economics Letters | 2 | ECON | 该期刊专注于应用经济学的简短研究，适合发表实证分析和政策建议，与您的研究主题高度相关 |
| 2 | Economic Issues | 1 | ECON | 面向经济学教学和政策讨论的期刊，接受理论与实证结合的研究，投稿门槛较低 |
| 3 | Journal of Economic Studies | 2 | ECON | 涵盖广泛的经济学主题，包括宏观、微观和发展经济学，适合多样化的研究方向 |
| 4 | International Journal of Finance & Economics | 2 | FINANCE | 关注金融与经济学交叉领域，适合金融市场、货币政策等主题的研究 |
| 5 | Applied Economics | 2 | ECON | 强调应用经济学研究，接受实证分析和政策评估，审稿周期相对较短 |
| 6 | Economics Letters | 2 | ECON | 发表简短的经济学研究，适合快速传播创新性发现和方法 |
| 7 | Journal of Policy Modeling | 2 | ECON | 专注于政策建模和评估，适合政策导向的经济学研究 |
| 8 | Economic Modelling | 2 | ECON | 强调经济模型的构建和应用，适合理论与实证结合的研究 |
| 9 | Journal of International Money and Finance | 2 | FINANCE | 关注国际金融和货币经济学，适合跨国比较和国际金融市场研究 |
| 10 | World Development | 2 | ECON | 专注于发展经济学，适合发展中国家的经济问题研究 |

---

### Medium 模式推荐（中等难度）

| 序号 | 期刊名 | ABS星级 | Field | 推荐理由 |
|------|--------|---------|-------|----------|
| 1 | Journal of Economic Behavior & Organization | 3 | ECON | 关注行为经济学和实验经济学，适合微观层面的决策行为研究 |
| 2 | European Economic Review | 3 | ECON | 欧洲顶级经济学期刊，涵盖宏观、微观和国际经济学，影响力较高 |
| 3 | Journal of Development Economics | 3 | ECON | 发展经济学领域的权威期刊，适合贫困、不平等和经济增长等主题 |
| 4 | Journal of Public Economics | 3 | PUB SEC | 公共经济学顶级期刊，关注税收、公共支出和社会福利政策 |
| 5 | Journal of International Economics | 3 | ECON | 国际经济学权威期刊，适合贸易、汇率和国际金融研究 |
| 6 | Journal of Monetary Economics | 3 | ECON | 货币经济学顶级期刊，关注货币政策、通货膨胀和金融稳定 |
| 7 | Journal of Financial Economics | 3 | FINANCE | 金融学顶级期刊，适合公司金融、资产定价和金融市场研究 |
| 8 | Review of Economics and Statistics | 3 | ECON | 强调实证方法和数据分析，适合计量经济学和应用研究 |
| 9 | Economic Journal | 3 | ECON | 英国皇家经济学会旗舰期刊，涵盖广泛的经济学主题 |
| 10 | Journal of Labor Economics | 3 | ECON | 劳动经济学权威期刊，适合就业、工资和人力资本研究 |

---

### Hard 模式推荐（高难度）

| 序号 | 期刊名 | ABS星级 | Field | 推荐理由 |
|------|--------|---------|-------|----------|
| 1 | American Economic Review | 4* | ECON | 经济学顶级期刊之一，发表突破性研究，影响力极高 |
| 2 | Econometrica | 4* | ECON | 理论经济学和计量经济学的顶级期刊，强调方法创新 |
| 3 | Journal of Political Economy | 4* | ECON | 芝加哥大学旗舰期刊，涵盖宏观、微观和政治经济学 |
| 4 | Quarterly Journal of Economics | 4* | ECON | 哈佛大学旗舰期刊，发表高质量的理论和实证研究 |
| 5 | Review of Economic Studies | 4* | ECON | 欧洲顶级经济学期刊，强调理论严谨性和实证创新 |
| 6 | Journal of Finance | 4* | FINANCE | 金融学顶级期刊，发表资产定价、公司金融和金融市场研究 |
| 7 | Review of Financial Studies | 4 | FINANCE | 金融学权威期刊，适合金融理论和实证研究 |
| 8 | Journal of Financial and Quantitative Analysis | 4 | FINANCE | 强调定量方法在金融研究中的应用 |
| 9 | Management Science | 4 | ECON | 跨学科期刊，涵盖经济学、管理学和运筹学 |
| 10 | Journal of Economic Theory | 4 | ECON | 理论经济学顶级期刊，适合博弈论、微观理论等研究 |

---

## 使用说明

1. **根据论文质量选择难度**：
   - 如果是初次投稿或论文创新性一般，建议从 Easy 模式开始
   - 如果论文有较强的理论或实证贡献，可以尝试 Medium 模式
   - 如果论文有重大突破或方法创新，可以挑战 Hard 模式

2. **参考推荐理由**：
   - AI 生成的推荐理由说明了期刊与论文的匹配度
   - 可以根据推荐理由判断期刊是否适合您的研究

3. **查看 Field 信息**：
   - Field 列显示期刊所属领域，帮助您快速定位相关期刊
   - 可以优先考虑与您研究领域匹配的期刊

4. **结合 ABS 星级**：
   - ABS 星级反映期刊的学术影响力和认可度
   - 可以根据目标学校或机构的要求选择合适星级的期刊

---

## 生成此报告的命令

```bash
python3 scripts/abs_journal.py \
  recommend \
  --title "您的论文标题" \
  --abstract "您的论文摘要（可选）" \
  --mode medium \
  --topk 10 \
  --hybrid \
  --auto_ai \
  --ai_report_md "reports/ai_report.md"
```

---

**注意**：以上示例为演示用途，实际推荐结果会根据您的论文内容和当前数据库动态生成。
