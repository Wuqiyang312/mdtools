import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_md_path(temp_dir):
    md_path = Path(temp_dir) / "sample.md"
    content = """# 测试文档

这是**粗体**和*斜体*测试。

## 列表测试

- 项目 1
- 项目 2
- 项目 3

## 代码块

```python
print("Hello World")
```

## 表格

| 姓名 | 年龄 | 城市 |
|------|------|------|
| 张三 | 25   | 北京 |
| 李四 | 30   | 上海 |
"""
    md_path.write_text(content, encoding="utf-8")
    return str(md_path)


@pytest.fixture
def sample_pdf_path():
    import sys
    from pathlib import Path
    project_root = Path(__file__).parent.parent
    return str(project_root / "tests" / "fixtures" / "sample.pdf")
