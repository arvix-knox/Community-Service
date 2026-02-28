"""Runtime bootstrap helpers."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def add_local_venv_site_packages(project_root: Path | None = None) -> None:
    """Add local venv site-packages to sys.path when available."""
    if project_root is None:
        project_root = Path(__file__).resolve().parents[2]

    candidates: list[Path] = []
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if virtual_env:
        candidates.append(Path(virtual_env))

    candidates.extend(
        [
            project_root / ".venv",
            project_root / "venv",
        ]
    )

    py_version = f"python{sys.version_info.major}.{sys.version_info.minor}"

    for venv_dir in candidates:
        linux_site = venv_dir / "lib" / py_version / "site-packages"
        windows_site = venv_dir / "Lib" / "site-packages"
        for site_dir in (linux_site, windows_site):
            if site_dir.exists():
                site_path = str(site_dir)
                if site_path in sys.path:
                    sys.path.remove(site_path)
                sys.path.insert(0, site_path)
                return
