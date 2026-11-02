"""Reuse a native engine, or obtain the current official stable release privately.

Standard library except optional py7zr / 7-Zip for the official Windows archive.
Discovery is not a capability qualification; run the needed circuit afterwards.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import ssl
import subprocess
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

DOWNLOAD_PAGE = "https://ngspice.sourceforge.io/download.html"
FILES_ROOT = "https://sourceforge.net/projects/ngspice/files/ng-spice-rework/"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(v for k, v in attrs if k == "href" and v)


def stable_release(html: str, system: str, machine: str) -> dict:
    """Use the official stable-folder anchor, never nightly/experimental numbers."""
    parser = Links()
    parser.feed(html)
    versions = [int(m.group(1)) for url in parser.links
                if (m := re.fullmatch(re.escape(FILES_ROOT) + r"(\d+)/?", url))]
    if not versions:
        raise ValueError("Official stable release folder not found; review the download page")
    version = max(versions)
    if system == "Windows":
        if machine.lower() not in {"amd64", "x86_64"}:
            raise ValueError("Select an official build appropriate to this Windows architecture")
        filename = f"ngspice-{version}_64.7z"
    else:
        filename = f"ngspice-{version}.tar.gz"
    # A known official-page defect links a current filename under the previous
    # folder. Require the filename to be advertised, but use the stable folder.
    if not any(urllib.parse.urlparse(url).path.rstrip("/").endswith("/" + filename)
               for url in parser.links if url.startswith(FILES_ROOT)):
        raise ValueError(f"Official page does not advertise {filename}; review packaging changes")
    return {"version": version, "filename": filename,
            "url": FILES_ROOT + f"{version}/{filename}/download",
            "discovery_url": DOWNLOAD_PAGE}


def fetch(url: str, destination: Path | None = None, limit=512 * 1024 * 1024):
    # Do not inherit SSLKEYLOGFILE into a library-created TLS context.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_default_certs()
    request = urllib.request.Request(url, headers={"User-Agent": "ngspice-native-skill/1.1.2"})
    with urllib.request.urlopen(request, context=context, timeout=60) as response:
        if urllib.parse.urlparse(response.geturl()).scheme != "https":
            raise ValueError("Refusing a non-HTTPS download redirect")
        total = 0
        chunks = []
        stream = destination.open("xb") if destination else None
        try:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > limit:
                    raise ValueError("Download exceeds the configured size limit")
                if stream:
                    stream.write(chunk)
                else:
                    chunks.append(chunk)
        finally:
            if stream:
                stream.close()
    return b"".join(chunks) if destination is None else destination


def safe_name(name: str) -> str:
    name = name.replace("\\", "/")
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or ":" in name:
        raise ValueError(f"Unsafe archive member: {name!r}")
    return name


def download_release(release: dict, destination: Path):
    """One official-page attempt, then the official mirror route if HTML/errors occur."""
    if destination.exists():
        raise FileExistsError(destination)
    mirror = ("https://downloads.sourceforge.net/project/ngspice/ng-spice-rework/"
              f"{release['version']}/{release['filename']}")
    failures = []
    for url in (release['url'], mirror):
        try:
            fetch(url, destination)
            with destination.open('rb') as stream:
                head = stream.read(8)
            if not head.startswith((b'7z\xbc\xaf\x27\x1c', b'PK\x03\x04', b'\x1f\x8b')):
                raise ValueError('Official download returned non-archive content')
            return url
        except (OSError, ValueError) as error:
            failures.append(f'{url}: {error}')
            # This function created this exact temporary file; never a user input.
            destination.unlink(missing_ok=True)
    raise RuntimeError('Official release download failed: ' + '; '.join(failures))


def run(command, cwd=None, timeout=60):
    completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if completed.returncode:
        raise RuntimeError(f"Command failed ({completed.returncode}): {command[0]}\n"
                           + completed.stdout[-3000:] + completed.stderr[-3000:])
    return completed.stdout + completed.stderr


def extract(archive: Path, destination: Path):
    with archive.open("rb") as stream:
        head = stream.read(8)
    destination.mkdir()
    if head.startswith(b"PK\x03\x04"):
        with zipfile.ZipFile(archive) as src:
            for item in src.infolist():
                safe_name(item.filename)
                if (item.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Archive symbolic links are not accepted")
            src.extractall(destination)
    elif head.startswith(b"\x1f\x8b"):
        with tarfile.open(archive, "r:gz") as src:
            for item in src.getmembers():
                safe_name(item.name)
                if not (item.isfile() or item.isdir()):
                    raise ValueError("Archive links and special files require explicit review")
            src.extractall(destination, filter="data")
    elif head.startswith(b"7z\xbc\xaf\x27\x1c"):
        try:
            import py7zr
        except ImportError:
            executable = shutil.which("7z") or shutil.which("7zz")
            if not executable:
                standard = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "7-Zip/7z.exe"
                executable = str(standard) if standard.is_file() else None
            if not executable:
                raise RuntimeError("Install a trusted 7-Zip extractor or py7zr, then retry; no engine installed")
            listing = run([executable, "l", "-slt", "-ba", str(archive)])
            for line in listing.splitlines():
                if line.startswith("Path = "):
                    safe_name(line[7:])
                if line.startswith(("Symbolic Link = ", "Hard Link = ")):
                    raise ValueError("Archive links require explicit review")
            run([executable, "x", "-y", "-o" + str(destination), str(archive)])
        else:
            with py7zr.SevenZipFile(archive) as src:
                for item in src.list():
                    safe_name(item.filename)
                    if getattr(item, "is_symlink", False):
                        raise ValueError("Archive symbolic links are not accepted")
                src.extractall(destination)
    else:
        raise ValueError("Download is not a supported archive (HTML responses are not packages)")
    for path in destination.rglob("*"):
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError("Extracted link/junction requires explicit review")


def identity(engine: Path) -> dict:
    engine = engine.resolve(strict=True)
    # Some native Windows builds do not route -v output to captured stdout.
    # A bounded batch version command with an explicit log gives actual build data.
    with tempfile.TemporaryDirectory(prefix="ngspice-identify-") as name:
        root = Path(name)
        (root / "spinit").write_text("", encoding="utf-8")
        (root / "version.cir").write_text(
            "* Identify native build\n.control\nversion -f\nquit\n.endc\n.end\n", encoding="utf-8")
        env = os.environ.copy()
        env["SPICE_SCRIPTS"] = str(root)
        completed = subprocess.run(
            [str(engine), "-n", "-b", "-o", str(root / "version.log"), str(root / "version.cir")],
            cwd=root, env=env, capture_output=True, timeout=20,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        banner = (completed.stdout + completed.stderr).decode("utf-8", errors="replace")
        if (root / "version.log").is_file():
            banner += (root / "version.log").read_text(encoding="utf-8", errors="replace")
        if completed.returncode:
            raise ValueError("Native engine version command failed: " + banner[-2000:])
    if not re.search(r"ngspice[-\s]+\d", banner, re.I):
        raise ValueError("Executable did not identify itself as ngspice")
    return {"path": str(engine), "banner": banner.strip(),
            "sha256": hashlib.sha256(engine.read_bytes()).hexdigest()}


def ensure_engine(cache: Path, explicit: Path | None = None, candidates=(),
                  configure_args=(), build_timeout=1800) -> dict:
    """Reuse before network. An invalid explicit selection must not silently fall back."""
    if explicit:
        return {"action": "reused-explicit", **identity(explicit)}
    choices = list(candidates)
    if os.environ.get("NGSPICE_EXECUTABLE"):
        choices.insert(0, Path(os.environ["NGSPICE_EXECUTABLE"]))
    on_path = shutil.which("ngspice")
    if on_path:
        choices.append(Path(on_path))
    if cache.exists():
        choices.extend(sorted(cache.glob("ngspice-*/**/ngspice.exe"), reverse=True)
                       if os.name == "nt" else sorted(cache.glob("ngspice-*/install/bin/ngspice"), reverse=True))
    invalid = []
    for choice in choices:
        try:
            return {"action": "reused", **identity(Path(choice))}
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
            invalid.append(f"{choice}: {error}")
    release = stable_release(fetch(DOWNLOAD_PAGE, limit=4 * 1024 * 1024).decode("utf-8"),
                             platform.system(), platform.machine())
    cache = cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    final = cache / f"ngspice-{release['version']}-{platform.system().lower()}-{platform.machine().lower()}"
    if final.exists():
        raise FileExistsError(f"Private install exists but no usable engine found: {final}")
    with tempfile.TemporaryDirectory(prefix=".ngspice-install-", dir=cache) as name:
        stage = Path(name)
        archive = stage / release["filename"]
        download_url = download_release(release, archive)
        archive_hash = hashlib.sha256(archive.read_bytes()).hexdigest()
        unpacked = stage / "distribution"
        extract(archive, unpacked)
        if platform.system() == "Windows":
            engines = list(unpacked.rglob("ngspice.exe"))
            if len(engines) != 1:
                raise ValueError("Expected exactly one native console ngspice.exe; review distribution")
            engine = engines[0]
            relative = engine.relative_to(unpacked)
            details = identity(engine)
            if not re.search(r"ngspice[-\s]+" + str(release["version"]) + r"\b", details["banner"], re.I):
                raise ValueError("Downloaded engine version differs from the discovered stable release")
            os.rename(unpacked, final)
        else:
            sources = [p.parent for p in unpacked.glob("*/configure")]
            if len(sources) != 1:
                raise ValueError("Cannot identify the official source tree")
            # The prefix is the final private directory: installed paths remain valid.
            # DESTDIR staging is intentionally avoided for platform-specific libpaths.
            build = sources[0]
            run(["sh", "configure", "--prefix=" + str(final / "install"),
                 "--with-x=no", "--with-readline=no", "--enable-xspice", "--enable-cider",
                 *configure_args], cwd=build, timeout=build_timeout)
            run(["make", "-j2"], cwd=build, timeout=build_timeout)
            run(["make", "install"], cwd=build, timeout=build_timeout)
            relative = Path("install/bin/ngspice")
            details = identity(final / relative)
            if not re.search(r"ngspice[-\s]+" + str(release["version"]) + r"\b", details["banner"], re.I):
                raise ValueError("Built engine version differs from the discovered stable release")
        details["path"] = str(final / relative)
        record = {"action": "installed", **details, "source": release,
                  "download_url": download_url,
                  "archive_sha256": archive_hash, "configure_args": list(configure_args),
                  "skipped_invalid_candidates": invalid}
        (final / "installation.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", type=Path)
    parser.add_argument("--candidate", action="append", type=Path, default=[])
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--configure-arg", action="append", default=[])
    args = parser.parse_args()
    try:
        print(json.dumps(ensure_engine(args.cache, args.engine, args.candidate, args.configure_arg), indent=2))
    except Exception as error:
        parser.exit(1, f"Engine provisioning failed: {error}\n")


if __name__ == "__main__":
    main()
