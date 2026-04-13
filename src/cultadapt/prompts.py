from __future__ import annotations

from pathlib import Path


def load_template(path: str | Path) -> str:
    with Path(path).open("r", encoding="utf-8") as f:
        return f.read()


def render_template(template: str, **kwargs: str) -> str:
    return template.format(**kwargs)
