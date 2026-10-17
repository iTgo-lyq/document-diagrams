#!/usr/bin/env python3
"""Validate an installable skill without Git; optionally audit source pins."""
import argparse
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "document-diagrams"
UPSTREAMS = {
    "diagram-design": (
        "https://github.com/cathrynlavery/diagram-design.git",
        "skills/diagram-design/SKILL.md",
    ),
    "svg-diagram": ("https://github.com/bybit-exchange/svg-diagram.git", "SKILL.md"),
}
SOURCE_TERMS = re.compile(
    r"submodule|diagram-design|svg-diagram|bybit|cathryn|上游(?:项目|仓库|技能)",
    re.IGNORECASE,
)
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".svg", ".html", ".css", ".txt", ".py", ".js"}
LINK = re.compile(r"\[[^\]]*\]\(([^\s)]+)\)")
RUNTIME_PATH = re.compile(r"(?<![\w/])(?:scripts/[\w-]+\.py|assets/[\w-]+\.svg|references/[\w-]+\.md)")


def check_links(document, boundary, allow_external=False):
    errors = []
    for target in LINK.findall(document.read_text(encoding="utf-8")):
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            if not allow_external:
                errors.append(f"{document.relative_to(boundary)}: external reference {target}")
            continue
        if not parsed.path:
            continue
        relative = Path(unquote(parsed.path))
        resolved = (document.parent / relative).resolve()
        if relative.is_absolute() or not resolved.is_relative_to(boundary):
            errors.append(f"{document.relative_to(boundary)}: reference leaves package: {target}")
        elif not resolved.exists():
            errors.append(f"{document.relative_to(boundary)}: missing reference {target}")
    return errors


def check_package(directory):
    directory = Path(directory).resolve()
    errors = []
    for required in ("SKILL.md", "LICENSE", "agents/openai.yaml"):
        if not (directory / required).is_file():
            errors.append(f"missing {required}")
    if not directory.is_dir():
        return errors

    for path in sorted(directory.rglob("*")):
        relative = path.relative_to(directory)
        if path.is_symlink():
            errors.append(f"{relative}: symbolic links are not part of the package")
            continue
        if relative.parts[0] not in {"SKILL.md", "LICENSE", "agents", "references", "assets", "scripts"}:
            errors.append(f"{relative}: outside the installable file layout")
        if any(part in {".git", "upstream", "vendor", "node_modules", "__pycache__"} for part in relative.parts):
            errors.append(f"{relative}: development dependency included in package")
        if path.is_dir():
            continue
        if not path.is_file():
            errors.append(f"{relative}: unsupported file type")
            continue
        if path.name == "SKILL.md" and relative != Path("SKILL.md"):
            errors.append(f"{relative}: nested skill entrypoint")
        if path.name.lower() == "readme.md":
            errors.append(f"{relative}: README belongs in the repository, not the installed skill")
        if path.suffix.lower() in {".html", ".htm", ".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            errors.append(f"{relative}: output resources must stay within SVG scope")
        if path.suffix in TEXT_SUFFIXES:
            content = path.read_text(encoding="utf-8")
            if SOURCE_TERMS.search(content):
                errors.append(f"{relative}: source attribution belongs in the repository README.md")
        if path.suffix == ".md":
            errors.extend(check_links(path, directory))
            for target in RUNTIME_PATH.findall(path.read_text(encoding="utf-8")):
                if not (directory / target).is_file():
                    errors.append(f"{relative}: missing runtime resource {target}")
    return errors


def git(*args, cwd=ROOT):
    return subprocess.check_output(
        ["git", *args], cwd=cwd, text=True, stderr=subprocess.PIPE
    ).strip()


def check_source():
    errors = []
    for name, (url, entry) in UPSTREAMS.items():
        relative = f"upstream/{name}"
        path = ROOT / relative
        if not (path / ".git").exists():
            errors.append(f"{relative}: uninitialized; run git submodule update --init --recursive")
            continue
        try:
            registered = git("config", "--file", ".gitmodules", "--get", f"submodule.{relative}.url")
            if registered != url:
                errors.append(f"{relative}: unexpected URL {registered}")
            index = git("ls-files", "--stage", "--", relative).split()
            if len(index) < 4 or index[0] != "160000" or index[2] != "0":
                errors.append(f"{relative}: missing or conflicted gitlink")
            elif git("rev-parse", "HEAD", cwd=path) != index[1]:
                errors.append(f"{relative}: checkout differs from staged gitlink")
            if git("status", "--porcelain", cwd=path):
                errors.append(f"{relative}: checkout has local changes")
            for required in (entry, "LICENSE"):
                if not (path / required).is_file():
                    errors.append(f"{relative}: missing {required}")
        except subprocess.CalledProcessError as exc:
            errors.append(f"{relative}: {exc.stderr.strip()}")
    for document in [ROOT / "README.md", *sorted((ROOT / "evals").rglob("*.md"))]:
        errors.extend(check_links(document, ROOT, allow_external=True))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=SKILL)
    parser.add_argument("--source", action="store_true", help="also validate this repository's source pins")
    args = parser.parse_args()
    errors = check_package(args.skill_dir)
    if args.source:
        errors.extend(check_source())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: self-contained skill; package boundaries and local references checked.")
    if args.source:
        print("OK: source submodules are pinned and clean; repository links resolve.")
    print("This checks installation integrity, not diagram correctness or visual quality.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
