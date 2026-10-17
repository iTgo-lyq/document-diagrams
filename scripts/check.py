#!/usr/bin/env python3
"""Check submodule pins and portable local references without network access."""
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
UPSTREAMS = {
    "diagram-design": (
        "https://github.com/cathrynlavery/diagram-design.git",
        "skills/diagram-design/SKILL.md",
    ),
    "svg-diagram": ("https://github.com/bybit-exchange/svg-diagram.git", "SKILL.md"),
}


def git(*args, cwd=ROOT):
    return subprocess.check_output(
        ["git", *args], cwd=cwd, text=True, stderr=subprocess.PIPE
    ).strip()


def main():
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
                errors.append(f"{relative}: unexpected upstream URL {registered}")
            index = git("ls-files", "--stage", "--", relative).split()
            if len(index) < 4 or index[0] != "160000" or index[2] != "0":
                errors.append(f"{relative}: missing or conflicted gitlink in index")
            elif git("rev-parse", "HEAD", cwd=path) != index[1]:
                errors.append(f"{relative}: checkout differs from staged gitlink; stage an intentional update before checking")
            if git("status", "--porcelain", cwd=path):
                errors.append(f"{relative}: upstream checkout has local changes")
            for required in (entry, "LICENSE"):
                if not (path / required).is_file():
                    errors.append(f"{relative}: missing {required}")
        except subprocess.CalledProcessError as exc:
            errors.append(f"{relative}: {exc.stderr.strip()}")

    documents = sorted(ROOT.glob("*.md"))
    for directory in ("references", "evals"):
        documents.extend(sorted((ROOT / directory).rglob("*.md")))
    for document in documents:
        for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", document.read_text()):
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            relative = Path(unquote(parsed.path))
            if relative.is_absolute():
                errors.append(f"{document.relative_to(ROOT)}: nonportable absolute link {target}")
            elif not (document.parent / relative).exists():
                errors.append(f"{document.relative_to(ROOT)}: broken local link {target}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: 2 pinned, clean submodules; local links in {len(documents)} documents resolve.")
    print("This checks package integrity, not diagram correctness or visual quality.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
