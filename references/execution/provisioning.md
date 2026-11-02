# Native engine selection and provisioning

Reuse the user's engine or a suitable existing native installation. Record actual version/build once and check relevant required capabilities (XSPICE modules, OSDI ABI, solver support) through the intended analysis. Version alone is not capability qualification. Do not replace a suitable installation because another is newer, or silently change engines during a verification series.

If no usable engine exists, autonomously obtain the latest **stable official** release for the OS/architecture into a private engine directory. Use the [official page](https://ngspice.sourceforge.io/download.html) and its SourceForge release folder. Do not select nightly/experimental builds by the largest numeric filename. Respect an explicit version choice. Required capability/reproducibility can justify a different build; state why.

[provisioning.py](../../scripts/provisioning.py) implements reuse and official discovery/download:

```text
python scripts/provisioning.py --cache /project/.tools/ngspice --candidate /known/ngspice
python scripts/provisioning.py --cache /project/.tools/ngspice --engine /user/selected/ngspice
```

It checks explicit selection, environment NGSPICE_EXECUTABLE, provided candidates, PATH and private cache before network. Windows x64 uses the advertised stable 7z package and py7zr or installed 7-Zip. It validates archive signature and paths. If the release URL returns HTML or a download error, it retries once through the official SourceForge mirror route; non-archive content is never installed. Unix-like systems use official source and an existing compiler/make toolchain for a private console build with XSPICE/CIDER. Sourced extra flags use `--configure-arg=...`. It is not a universal toolchain installer.

When build/extraction dependencies are absent, obtain trusted platform tools within authorized setup scope and retry. A macOS/Linux package manager can supply dependencies or a suitable engine; compare fresh-install versions with official stable because distribution packages may lag. If permissions/network/toolchain prevent setup, state the missing prerequisite and keep execution pending. Do not invent successful installation or call an older fallback latest.

Record actual executable banner, source/build, modules and nondefault startup/solver configuration in working state. The final MD needs a concise runtime statement, not an inventory. Private-cache installation.json and local download hashes are not model deliverables or vendor digital signatures.

Configure needed native startup commands; do not universally disable OSDI or load unrelated modules. Reuse applicable semantic checks for unchanged builds. Missing compiled features are build gaps; evaluate relevant [native alternatives](capabilities.md) before claiming an engine ceiling.
