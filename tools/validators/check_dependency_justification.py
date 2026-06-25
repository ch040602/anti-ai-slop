from __future__ import annotations

import re
from pathlib import Path

try:
    from .common import Finding, read_text, relpath, run_cli
except ImportError:
    from common import Finding, read_text, relpath, run_cli


MANIFESTS = ["requirements.txt", "pyproject.toml", "package.json", "pnpm-lock.yaml", "package-lock.json"]


def mentioned_in_catalog(root: Path, name: str) -> bool:
    catalog = root / "docs/references/resource-catalog.yaml"
    return catalog.exists() and name.lower() in read_text(catalog).lower()


def python_imports(path: Path) -> set[str]:
    text = read_text(path)
    imports = set(re.findall(r"^\s*(?:import|from)\s+([a-zA-Z_][\w]*)", text, re.MULTILINE))
    stdlib_like = {
        "__future__", "argparse", "ast", "collections", "csv", "dataclasses", "datetime", "fnmatch",
        "importlib", "json", "os", "pathlib", "re", "shutil", "subprocess", "sys", "tempfile",
        "textwrap", "typing", "unittest",
    }
    return {item for item in imports if item not in stdlib_like and not item.startswith("tools")}


def check(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for manifest in MANIFESTS:
        path = root / manifest
        if path.exists() and not mentioned_in_catalog(root, manifest.split(".")[0]):
            findings.append(Finding("MEDIUM", "dependency-justification", relpath(path, root), "Dependency manifest exists but catalog justification is not explicit.", "Add dependency rationale to docs/references/resource-catalog.yaml."))
    for path in list((root / "tools").rglob("*.py")) + list((root / "tests").rglob("*.py")) if (root / "tools").exists() else []:
        for dep in sorted(python_imports(path)):
            if dep in {"common"}:
                continue
            findings.append(Finding("HIGH", "dependency-justification", relpath(path, root), f"Non-stdlib import `{dep}` found.", "Use stdlib or record dependency justification in the plan and resource catalog."))
    return findings


if __name__ == "__main__":
    raise SystemExit(run_cli(check, "Dependency Justification Check"))
