"""Create and clean a task-owned scratch directory; copy only selected delivery files.

This helper does not certify a model. Load and validate final paths with ngspice
before cleanup. Never use it to clean pre-existing user or shared-engine folders.
"""
from __future__ import annotations
import argparse
import json
import os
import secrets
import shutil
import tempfile
from pathlib import Path, PurePosixPath

MARKER = ".ngspice-task-owner.json"


def linked(path):
    return path.is_symlink() or getattr(path, "is_junction", lambda: False)()


def create(parent: Path):
    parent = parent.resolve(strict=True)
    path = Path(tempfile.mkdtemp(prefix="ngspice-task-", dir=parent))
    token = secrets.token_hex(24)
    record = {"schema": "ngspice-task/1", "root": str(path), "token": token}
    (path / MARKER).write_text(json.dumps(record), encoding="utf-8")
    return record


def owned(root: Path, token: str):
    if linked(root):
        raise ValueError("Workspace root must not be a link or junction")
    root = root.resolve(strict=True)
    if not root.name.startswith("ngspice-task-"):
        raise ValueError("Not a generated task workspace")
    marker = root / MARKER
    if linked(marker):
        raise ValueError("Ownership marker must not be a link")
    record = json.loads(marker.read_text(encoding="utf-8"))
    if (record.get("schema") != "ngspice-task/1" or record.get("root") != str(root)
            or not secrets.compare_digest(str(record.get("token", "")), token)):
        raise ValueError("Workspace ownership mismatch")
    for path in root.rglob("*"):
        if linked(path):
            raise ValueError(f"Workspace contains a link/junction; review before cleanup: {path}")
    return root


def relative_file(name: str):
    path = PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or ".." in path.parts or ":" in str(path) or not path.parts:
        raise ValueError(f"Unsafe delivery path: {name}")
    if path.name == MARKER:
        raise ValueError("Workspace ownership marker is not a model dependency")
    return Path(*path.parts)


def publish(root: Path, token: str, destination: Path, files: list[str], description: str | None = None):
    root = owned(root, token)
    destination = destination.absolute()
    parent = destination.parent.resolve()
    destination = parent / destination.name
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Delivery destination already exists; no user files overwritten")
    if destination == root or root in destination.parents:
        raise ValueError("Delivery must be outside the disposable workspace")
    paths = [relative_file(name) for name in files]
    if len(set(paths)) != len(paths):
        raise ValueError("Duplicate delivery paths")
    markdown = [p for p in paths if p.suffix.lower() == ".md"]
    if description is None:
        if len(markdown) != 1:
            raise ValueError("Identify one primary Markdown explanation with --description")
    elif relative_file(description) not in markdown:
        raise ValueError("The primary Markdown explanation must be among selected files")
    if len(paths) < 2:
        raise ValueError("Select the model and all its necessary use-time dependencies")
    for path in paths:
        source = (root / path).resolve(strict=True)
        if root not in source.parents or not source.is_file():
            raise ValueError(f"Not an owned regular delivery file: {path}")
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".ngspice-delivery-", dir=parent) as name:
        stage = Path(name)
        for path in paths:
            target = stage / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / path, target)
        if destination.exists():
            raise FileExistsError(destination)
        os.rename(stage, destination)
    return {"destination": str(destination), "files": [p.as_posix() for p in paths],
            "next": "Run the final-path load/behavior check, then clean the owned workspace"}


def cleanup(root: Path, token: str):
    root = owned(root, token)
    # The absolute root and every link boundary have been checked above.
    shutil.rmtree(root)
    return {"removed": str(root)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("create")
    new.add_argument("--parent", type=Path, required=True)
    for name in ("publish", "cleanup"):
        sub = commands.add_parser(name)
        sub.add_argument("--workspace", type=Path, required=True)
        sub.add_argument("--token", required=True)
        if name == "publish":
            sub.add_argument("--destination", type=Path, required=True)
            sub.add_argument("--file", action="append", required=True)
            sub.add_argument("--description", help="Primary MD when required licenses also use .md")
    args = parser.parse_args()
    try:
        if args.command == "create":
            result = create(args.parent)
        elif args.command == "publish":
            result = publish(args.workspace, args.token, args.destination, args.file, args.description)
        else:
            result = cleanup(args.workspace, args.token)
        print(json.dumps(result, indent=2))
    except Exception as error:
        parser.exit(1, f"Workspace operation failed: {error}\n")


if __name__ == "__main__":
    main()
