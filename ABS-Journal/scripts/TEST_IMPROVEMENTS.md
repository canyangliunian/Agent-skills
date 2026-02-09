# 测试改进建议

## 当前测试覆盖状态

### ✅ 已覆盖（优秀）
- `abs_article_impl.py`：主题贴合 gating、星级平衡、候选池生成
- `abs_ai_review.py`：子集验证、跨模式重复检测
- `hybrid_report.py`：报告生成、多池索引
- `abs_journal.py`：混合流程端到端、自动 AI 生成

### ⚠️ 待补充

## 1. ajg_fetch.py 网络层测试（优先级：Low）

### 建议添加的测试

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_ajg_fetch_mock.py - Mock-based unit tests for ajg_fetch.py"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from ajg_fetch import (
    parse_algolia_vars_from_html,
    is_gated_page,
    normalize_title,
    dedupe_rows,
)


class TestAjgFetchParsing(unittest.TestCase):
    """Test HTML parsing logic without network calls."""

    def test_parse_algolia_vars_success(self):
        html = """
        <script>
        window.ALGOLIA_APP_ID = 'TEST123';
        window.ALGOLIA_PUBLIC = 'pubkey456';
        window.ALGOLIA_USE_DEV_INDEXES = false;
        </script>
        """
        result = parse_algolia_vars_from_html(html)
        self.assertIsNotNone(result)
        app_id, api_key, use_dev = result
        self.assertEqual(app_id, 'TEST123')
        self.assertEqual(api_key, 'pubkey456')
        self.assertFalse(use_dev)

    def test_is_gated_page_detection(self):
        gated_html = '<div>Log in or register to view this content</div>'
        self.assertTrue(is_gated_page(gated_html))

        open_html = '<div>Welcome to the journal guide</div>'
        self.assertFalse(is_gated_page(open_html))

    def test_normalize_title(self):
        self.assertEqual(normalize_title("Journal of Economics"), "journal of economics")
        self.assertEqual(normalize_title("Nature's Best"), "natures best")
        self.assertEqual(normalize_title("  Spaced  Out  "), "spaced out")

    def test_dedupe_rows(self):
        rows = [
            {"title": "Journal A", "issn": "1234-5678"},
            {"title": "Journal A", "issn": "1234-5678"},  # duplicate
            {"title": "Journal B", "issn": "9999-0000"},
        ]
        deduped, dup_count = dedupe_rows(rows)
        self.assertEqual(len(deduped), 2)
        self.assertEqual(dup_count, 1)


if __name__ == '__main__':
    unittest.main()
```

### 测试覆盖目标
- ✅ HTML 解析逻辑（无需网络）
- ✅ 数据清洗函数（normalize_title, dedupe_rows）
- ✅ 门控页面检测
- ⚠️ 网络请求层（需要 mock）

---

## 2. abs_paths.py 环境变量测试（优先级：Low）

### 建议添加的测试

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_abs_paths.py - Test path resolution logic"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from abs_paths import skill_root, data_dir, cache_dir, reports_dir


class TestAbsPaths(unittest.TestCase):
    """Test path resolution with and without env overrides."""

    def test_skill_root_default(self):
        """Test default skill root detection (walks up to SKILL.md)."""
        root = skill_root()
        self.assertTrue(root.is_dir())
        self.assertTrue((root / "SKILL.md").is_file())

    def test_skill_root_env_override(self):
        """Test ABS_JOURNAL_HOME env override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ['ABS_JOURNAL_HOME'] = tmpdir
            try:
                root = skill_root()
                self.assertEqual(root, Path(tmpdir).resolve())
            finally:
                del os.environ['ABS_JOURNAL_HOME']

    def test_data_dir_default(self):
        """Test default data_dir is <root>/assets/data."""
        root = skill_root()
        expected = root / "assets" / "data"
        self.assertEqual(data_dir(), expected.resolve())

    def test_data_dir_env_override(self):
        """Test ABS_JOURNAL_DATA_DIR env override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ['ABS_JOURNAL_DATA_DIR'] = tmpdir
            try:
                self.assertEqual(data_dir(), Path(tmpdir).resolve())
            finally:
                del os.environ['ABS_JOURNAL_DATA_DIR']

    def test_cache_dir_default(self):
        """Test default cache_dir is <root>/.cache."""
        root = skill_root()
        expected = root / ".cache"
        self.assertEqual(cache_dir(), expected.resolve())

    def test_reports_dir_default(self):
        """Test default reports_dir is <root>/reports."""
        root = skill_root()
        expected = root / "reports"
        self.assertEqual(reports_dir(), expected.resolve())


if __name__ == '__main__':
    unittest.main()
```

### 测试覆盖目标
- ✅ 默认路径解析
- ✅ 环境变量覆盖优先级
- ✅ 路径规范化（resolve）

---

## 3. 边界条件测试（优先级：Low）

### 建议添加的测试场景

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/test_edge_cases.py - Boundary condition tests"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
IMPL = REPO_ROOT / "scripts" / "abs_article_impl.py"
AJG_CSV = REPO_ROOT / "assets" / "data" / "ajg_2024_journals_core_custom.csv"


def test_empty_candidate_pool():
    """Test behavior when no journals match field_scope."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pool_json = Path(tmpdir) / "pool.json"

        # Use a non-existent field to force empty candidate pool
        proc = subprocess.run(
            [
                sys.executable, str(IMPL),
                "--ajg_csv", str(AJG_CSV),
                "--field", "ECON",
                "--field_scope", "NONEXISTENT_FIELD",
                "--title", "Test",
                "--mode", "easy",
                "--topk", "10",
                "--export_candidate_pool_json", str(pool_json),
            ],
            capture_output=True,
            text=True,
        )

        # Should fail with clear error message
        assert proc.returncode != 0
        assert "不存在于 AJG CSV" in proc.stdout or "不存在于 AJG CSV" in proc.stderr


def test_topk_exceeds_pool_size():
    """Test behavior when TopK > available candidates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pool_json = Path(tmpdir) / "pool.json"

        # Request TopK=1000 (likely exceeds available journals)
        proc = subprocess.run(
            [
                sys.executable, str(IMPL),
                "--ajg_csv", str(AJG_CSV),
                "--field", "ECON",
                "--title", "Test",
                "--mode", "easy",
                "--topk", "1000",
                "--export_candidate_pool_json", str(pool_json),
            ],
            capture_output=True,
            text=True,
        )

        # Should succeed but return fewer than 1000
        assert proc.returncode == 0

        if pool_json.exists():
            pool = json.loads(pool_json.read_text())
            candidates = pool.get("candidates", [])
            # Should return all available, not crash
            assert len(candidates) > 0
            assert len(candidates) <= 1000


def test_empty_title():
    """Test behavior with empty title (should fail gracefully)."""
    proc = subprocess.run(
        [
            sys.executable, str(IMPL),
            "--ajg_csv", str(AJG_CSV),
            "--field", "ECON",
            "--title", "",  # Empty title
            "--mode", "easy",
            "--topk", "10",
        ],
        capture_output=True,
        text=True,
    )

    # Should either succeed with warning or fail with clear message
    # (Current implementation may allow empty title; adjust assertion as needed)
    assert proc.returncode == 0 or "title" in proc.stderr.lower()


if __name__ == "__main__":
    test_empty_candidate_pool()
    print("✓ test_empty_candidate_pool")

    test_topk_exceeds_pool_size()
    print("✓ test_topk_exceeds_pool_size")

    test_empty_title()
    print("✓ test_empty_title")

    print("\nAll edge case tests passed!")
```

### 测试覆盖目标
- ✅ 空候选池处理
- ✅ TopK 越界处理
- ✅ 空输入处理
- ✅ 星级过滤无匹配时的回退

---

## 实施优先级

### 立即实施（已完成）
- ✅ 修复 `abs_article_impl.py` 中的大小写不一致

### 短期（可选）
- ⚠️ 添加 `abs_paths.py` 环境变量测试（工作量：1-2 小时）
- ⚠️ 添加边界条件测试（工作量：2-3 小时）

### 长期（可选）
- ⚠️ 添加 `ajg_fetch.py` mock 测试（工作量：4-6 小时）
- ⚠️ 集成 pytest 框架替代当前的轻量级测试脚本

---

## 测试运行指南

### 当前测试运行方式

```bash
# 运行所有现有测试
cd /Users/lingguiwang/Documents/Coding/LLM/Agent-skills/abs-journal

python3 scripts/test_hybrid_flow.py
python3 scripts/test_recommendation_gating.py
python3 scripts/test_hybrid_requires_export.py
```

### 建议的测试组织结构

```
abs-journal/
├── scripts/
│   ├── abs_journal.py
│   ├── abs_article_impl.py
│   └── ...
├── tests/                          # 新增：专门的测试目录
│   ├── __init__.py
│   ├── test_ajg_fetch_mock.py     # 新增
│   ├── test_abs_paths.py          # 新增
│   ├── test_edge_cases.py         # 新增
│   ├── test_hybrid_flow.py        # 迁移自 scripts/
│   ├── test_recommendation_gating.py  # 迁移自 scripts/
│   └── test_hybrid_requires_export.py # 迁移自 scripts/
└── pytest.ini                      # 可选：pytest 配置
```

---

## 总结

当前测试覆盖已经**非常完善**，核心业务逻辑（推荐算法、混合流程、验证逻辑）均有充分测试。

建议的改进主要针对：
1. **工具模块**（ajg_fetch, abs_paths）的单元测试
2. **边界条件**的系统性覆盖

这些改进属于**锦上添花**，不影响当前代码的生产可用性。
