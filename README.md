**English** · [中文](#zh)

<a id="en"></a>

# spice-chip-modeling — Turn device datasheets into ngspice models with AI

Hand your vendor datasheet (PDF) to an AI assistant. It reads the device behavior, builds a **native ngspice** model, runs simulations to verify it, and gives you back a model file you can `include` directly, plus a short write-up.

This is a **skill** (a packaged instruction set), not a standalone application, and it has no GUI. Once installed you simply ask in plain language — no commands to memorize.

> **Prerequisite**: an AI assistant that supports skills (for example Claude Code, DSH or Codex), plus the device's datasheet.

---

## What it does

- **Build models**: resistors/capacitors/inductors, transformers, crystals, diodes, BJTs, MOSFETs, op-amps, comparators, voltage references, LDOs, DC-DC converters, drivers, current sensors, logic gates, analog switches, ADCs/DACs, optocouplers, and more — each family has its own modeling recipe.
- **Review models**: check whether an existing model has obvious problems and whether its parameters match the datasheet.
- **Validate models**: simulate real operating conditions — open/closed loop, large-signal behavior, protection, startup, temperature — instead of declaring "pass" from a single DC operating point.
- **Prepare the simulation engine**: if ngspice is not installed, it downloads the current official stable release into a private directory of its own.

## What it does not do

- It is **not a security sandbox**. Simulation runs native ngspice, and `.control` blocks can read and write files and invoke external programs. **Only simulate circuits and models you trust.**
- It does **not guarantee a complete reproduction of a real device.** It aims to match the datasheet-supported behavior as closely as possible, but real device behavior cannot be fully reproduced. Review important designs against the datasheet yourself.
- It provides **no manufacturer certification** and does not replace an official vendor model. Generated model files carry an AI-generated notice; that is intentional, so please do not delete it and pass the model off as an official one.
- It does **not modify your ngspice installation** or your global `.spiceinit` (every run uses an isolated startup configuration).

---

## Installation

### Step 1: what you need

| Requirement | Notes |
|---|---|
| Python **3.8 or newer** | The scripts use only the standard library — **no Python packages to install**. On Windows, tick "Add to PATH" when installing Python. |
| ngspice | **Optional.** The skill downloads an official stable release into a private directory when no engine is available. |
| 7-Zip | Only needed on Windows for that automatic download. Without it, run `pip install py7zr`. |
| Datasheet PDF | Prefer the manufacturer's original, and note the document number and revision. |

### Step 2: put the skill into your skills directory

A skill is just a folder. Place it in your AI assistant's skills directory, and **name the folder `spice-chip-modeling`** (matching the skill name inside the package — the safest choice).

**Windows (PowerShell)**

```powershell
# Option A: clone from GitHub (recommended; easy to update later)
git clone https://github.com/easyeda/spice-model-skill.git "$env:USERPROFILE\.claude\skills\spice-chip-modeling"
```

```powershell
# Option B: you already have the folder — copy it
Copy-Item -Recurse "D:\your\path\spice-model-skill" "$env:USERPROFILE\.claude\skills\spice-chip-modeling"
```

The result should look like this:

```text
C:\Users\<your-name>\.claude\skills\spice-chip-modeling\
├── SKILL.md          ← skill entry point, required
├── references\       ← modeling, validation and syntax references
├── scripts\          ← Python helper scripts
├── assets\           ← templates
└── agents\           ← configuration for other tools
```

**macOS / Linux**

```bash
git clone https://github.com/easyeda/spice-model-skill.git ~/.claude/skills/spice-chip-modeling
```

> The skills directory name differs between tools (some use `~/.config/<tool>/skills`). The rule is the same: **one folder per skill, and the folder must contain `SKILL.md`.**

### Step 3: confirm the installation

1. Restart your AI client; for a web UI, refresh the page or simply **start a new session** (skills load when a session starts).
2. Ask:

   ```text
   Which skills can you use right now?
   ```

3. Seeing `spice-chip-modeling` in the answer means it loaded.

If it does not appear, check three things: `SKILL.md` is in the folder root, the folder is in the correct skills directory, and you started a new session.

### (Optional) other tools

`agents/openai.yaml` holds the display metadata used by Codex-style tools (skill name, short description, default prompt). Other tools read the `SKILL.md` header directly and need no extra configuration.

---

## Usage

After installation, **just chat**. State three things:

1. **Which device**: manufacturer + full part number + package/pin count (e.g. "TI LM358, SOIC-8").
2. **The datasheet**: a PDF path or link (the manufacturer's original is best).
3. **How you intend to use it**: supply voltage, load, temperature range, and the metrics you care about (e.g. "5 V supply, driving a 600 Ω load, care about slew rate and output swing").

### Example prompts

```text
Build an ngspice model from D:\datasheets\1N4148.pdf.
Use: freewheeling diode in a 5 V switching circuit; care about forward drop and junction capacitance.
```

```text
Build an op-amp model for the LM358 from the curves in its datasheet.
Requirements: ±5 V supply, reproduce bandwidth and slew rate, include output short-circuit protection.
```

```text
Generate a model for this LDO (datasheet attached).
Focus the validation on load steps, dropout, current limit, and stability with 1 uF to 100 uF output capacitors.
```

```text
Here is an existing .lib model — review it against the datasheet. Don't change it, just write a report.
```

Tips:

- State the boundaries explicitly — "review only, don't modify" or "design only, no validation" — and it will stay inside them.
- One device per request works best; for batches, list the parts and acceptance criteria up front.
- Scanned datasheets are fine, but clearer text and curves give more reliable parameter extraction.

### What the workflow looks like

1. **Read the sources**: confirm the part, package, pin order and document revision, and map every material specification to its datasheet page or curve.
2. **Design the architecture**: turn each behavior to reproduce into equations, states and ports, then pick the matching family recipe.
3. **Implement**: write the model in native ngspice syntax (`.lib` / `.mod`).
4. **Validate**: run calibration points, independent behavior, application cases (closed loop, large-signal, protection, startup, temperature) and numerical robustness checks. A failure gets a cause diagnosis and a rerun of the affected checks.
5. **Deliver and clean up**: give you only the model files plus one write-up, and remove the intermediates.

### What you get

A folder with, typically, just two things:

- **The model file** (`.lib` / `.mod`, plus any necessary includes, lookup tables or module files), with an AI-generated notice in its header.
- **One Markdown write-up**: part identity and pin order, how to include it, dependencies and the engine version used, which behaviors and conditions are reproduced, error or bounds, known assumptions and limits, and a verification summary.

By default it does **not** hand you piles of testbenches, logs, fitting data and plots. If you want the full evidence chain, ask for it explicitly.

---

## Optional self-check

To catch environment problems before a real modeling job, run a minimal voltage-divider example. Create an empty directory (a scratch workspace you can delete afterwards) and put these two files in it.

`divider.inc`:

```text
V1 in 0 2
R1 in out 1k
R2 out 0 1k
```

`case.json`:

```json
{
  "schema_version": "ngspice-run/2",
  "entry": "divider.inc",
  "analysis": {"type": "op"},
  "vectors": [{"name": "out", "expression": "v(out)"}],
  "metrics": [{
    "id": "divider", "column": "out", "operation": "scalar",
    "expected": 1, "atol": 0.000001, "rtol": 0,
    "unit": "V", "source": "DERIVED: 2 V times 1 kohm / 2 kohm",
    "tolerance_basis": "Numerical allowance for the ideal divider equation"
  }]
}
```

First prepare the engine (this step downloads ngspice when it is missing). Run it from the skill directory, or spell out the script path — below assumes the skill is installed at `C:\Users\<your-name>\.claude\skills\spice-chip-modeling`:

```text
python "C:\Users\<your-name>\.claude\skills\spice-chip-modeling\scripts\provisioning.py" --cache .tools\ngspice
```

It prints a JSON document: `path` is the usable ngspice executable, and `action` says whether an existing installation was reused (`reused`) or a new one was installed (`installed`). `--cache` is where the engine is kept — here inside the scratch directory as `.tools\ngspice`.

Then run the analysis (execute this from the directory containing `case.json`; pass the `path` value to `--engine`; `--output` must be a directory that **does not exist yet**):

```text
python "C:\Users\<your-name>\.claude\skills\spice-chip-modeling\scripts\run_analysis.py" --manifest case.json --engine <value of path> --output run1
```

If `result.json` reports `PASS` with `out ≈ 1 V`, then Python, the engine and the runner are all wired up correctly.

---

## Command line (advanced, optional)

You do not need these day to day — the AI calls them for you. Use them to reproduce results yourself; `scripts\` below means the `scripts\` folder in the skill directory:

| Script | Purpose |
|---|---|
| `scripts/provisioning.py --cache <dir> [--engine <path>]` | Find a usable ngspice, or download the official stable release into a private directory. `--engine` points at an existing install. |
| `scripts/run_analysis.py --manifest <case.json> --engine <ngspice> --output <new-dir>` | Run one declared analysis, check the exported data, and report `PASS` / `FAIL` / `REVIEW_REQUIRED` and so on. |
| `scripts/workspace.py create --parent <dir>` | Create a scratch directory carrying an ownership marker. |
| `scripts/workspace.py publish --workspace <dir> --token <token> --destination <new-dir> --file <file> [...]` | Copy only the selected delivery files out (the destination must not exist). |
| `scripts/workspace.py cleanup --workspace <dir> --token <token>` | Remove the scratch directory it created itself; it never touches your other folders. |

A `case.json` can declare `op` / `dc` / `ac` / `tran` / `noise` analyses, the vectors to export, the criteria (expected values or bounds) and a timeout. Expected values must come from the datasheet or an independent derivation, never from the model's own output. See `references/execution/runner.md` for the full syntax.

---

## FAQ

**`python` is not recognized**
Python was installed on Windows without "Add to PATH". Reinstall with that option ticked, or use the `py` launcher instead.

**No ngspice found / the download fails**
Install ngspice manually and point `--engine` at it, or set the `NGSPICE_EXECUTABLE` environment variable. Behind a restricted network, download it from the [official ngspice page](https://ngspice.sourceforge.io/download.html) and unpack it yourself.

**No output at all on Windows**
Some Windows builds ship `ngspice.exe` as a GUI-subsystem program that produces no captured output in batch mode. Use `ngspice_con.exe` from the same directory instead.

**Error: the output directory already exists**
That is deliberate: every run writes to a brand-new directory so stale results cannot masquerade as fresh ones. Pick a new directory name, or delete the old one.

**What does `REVIEW_REQUIRED` mean?**
The simulation completed and the criteria passed, but the engine emitted numerical warnings (for example a gmin or source-stepping rescue). A human needs to confirm those warnings did not affect the result; it is not an automatic pass.

**What does `EXECUTED` mean?**
Every declared export was produced, but the case declared no electrical criteria, so it only proves the run completed — not that the model is correct.

**Will it modify my files?**
The skill works inside a scratch directory and copies only selected files out at delivery, refusing destinations that already exist. Keep your own copy of the original datasheet.

**Can I delete the AI-generated notice in the model file?**
Better not. It tells downstream users that the model was generated by AI from the datasheet and does not guarantee a complete reproduction of the real device. Removing it invites people to mistake the model for an official vendor model.

**How do I update it?**
`git pull` inside the skills directory; for a copy-based install, copy the new version over the old one.

---

## Directory layout

```text
SKILL.md                    Skill entry point: workflow, boundaries, acceptance rules
references/
  sources/evidence.md       How to read a datasheet (facts / derivations / assumptions kept apart)
  modeling/architecture.md  Behavior → equations / states / ports
  recipes/                  Per-family modeling recipes (passives, discretes, op-amps, switching, interfaces…)
  mechanisms/               Charge, noise, temperature/electrothermal topics
  syntax/ngspice.md         Native syntax essentials
  execution/                Engine provisioning, runner, capability limits, probe decks
  verification/             Validation contract, numerical diagnosis
  delivery/                 Deliverables and temporary-file lifecycle rules
  maintenance/              Rule placement
scripts/                    Python helpers (engine provisioning, running, result checks, workspace)
assets/                     Write-up and construction-record templates
agents/openai.yaml          Display metadata for other AI tools
```

---

## Version and notes

- Skill version: **v1.1.2**
- Author: **EasyEDA**
- License: **Apache-2.0** — see [LICENSE](LICENSE)
- Dependencies: Python 3.8+ (standard library only), ngspice (obtainable automatically); on Windows the automatic download additionally needs 7-Zip or `py7zr`.
- The generated models are **engineering approximations built by AI from public technical sources**, intended for simulation analysis. They are not manufacturer certification and do not replace the guaranteed values in the datasheet. Verify critical specifications yourself before production use.

---
---

<a id="zh"></a>

# spice-chip-modeling — 用 AI 把芯片 datasheet 变成 ngspice 模型

[↑ English](#en)

把厂商 datasheet（PDF）交给 AI 助手，它会读懂器件行为、搭建 **原生 ngspice** 模型，并跑仿真验证，最后交给你一个可以直接 `include` 的模型文件加一份说明。

这是一个 **skill（技能包）**：它本身不是软件，也不提供图形界面。装好之后，你在 AI 助手里用日常语言提要求即可，不需要记命令。

> **使用前提**：你有一个支持 skill 的 AI 助手（例如 Claude Code、DSH、Codex 等），并且能提供器件的 datasheet。

---

## 它能做什么

- **建模型**：电阻/电容/电感、变压器、晶振、二极管、三极管、MOSFET、运放、比较器、基准源、LDO、DC-DC、驱动器、电流传感器、逻辑门、模拟开关、ADC/DAC、光耦等，按器件类别套用对应的建模套路。
- **审模型**：检查你手上的现成模型有没有明显问题、参数是否对得上 datasheet。
- **验证模型**：用真实工作条件跑仿真，检查开环/闭环、大信号、保护、启动、温度等行为，而不是只跑一个直流工作点就说"通过"。
- **自动准备仿真引擎**：电脑上没装 ngspice 时，会自己下载官方稳定版到一个独立目录，不污染你的系统。

## 它不做什么

- 不做安全沙箱。仿真时运行的是原生 ngspice，`.control` 里的指令可以读写文件、调用外部程序。**只仿真你自己信任的电路和模型。**
- 不保证"完全还原真实器件"。它追求在 datasheet 支持范围内尽量贴合，但真实器件行为无法被完全复现，重要设计请对照 datasheet 复核。
- 不提供厂商认证或替代器件厂的官方模型。生成的模型文件头会带一段 AI 生成声明，这是有意的，请不要删掉后当作官方模型使用。
- 不改你的 ngspice 安装，也不改你的全局 `.spiceinit`（每次运行都用独立的启动配置）。

---

## 安装

### 第 1 步：准备工作

| 需要 | 说明 |
|---|---|
| Python **3.8 或更新** | 脚本本身只用标准库，**不需要装任何 Python 包**。Windows 上装 Python 时记得勾选 "Add to PATH"。 |
| ngspice | **可以不装**。skill 会在缺少引擎时自动下载官方稳定版到私有目录。 |
| 7-Zip | 仅 Windows 自动下载时需要。没装 7-Zip 的话可以先执行 `pip install py7zr`。 |
| datasheet PDF | 尽量用厂商官网原版，并记下文档编号和版本。 |

### 第 2 步：把技能包放进 skills 目录

技能就是一个文件夹。把它放到你的 AI 助手的 skills 目录里，**文件夹名建议用 `spice-chip-modeling`**（和包内的技能名一致，最稳妥）。

**Windows（PowerShell）**

```powershell
# 方式 A：从 GitHub 克隆（推荐，方便以后更新）
git clone https://github.com/easyeda/spice-model-skill.git "$env:USERPROFILE\.claude\skills\spice-chip-modeling"
```

```powershell
# 方式 B：已经有这个文件夹了，直接复制过去
Copy-Item -Recurse "D:\你的路径\spice-model-skill" "$env:USERPROFILE\.claude\skills\spice-chip-modeling"
```

装完应该长这样：

```text
C:\Users\<你的用户名>\.claude\skills\spice-chip-modeling\
├── SKILL.md          ← 技能入口，必须有
├── references\       ← 建模、验证、语法等参考文档
├── scripts\          ← Python 助手脚本
├── assets\           ← 模板
└── agents\           ← 其他工具的配置
```

**macOS / Linux**

```bash
git clone https://github.com/easyeda/spice-model-skill.git ~/.claude/skills/spice-chip-modeling
```

> 不同的 AI 工具 skills 目录名可能不同（例如有些工具用 `~/.config/<工具名>/skills`）。规则是一样的：**一个技能一个文件夹，文件夹里要有 `SKILL.md`**。

### 第 3 步：确认装好了

1. 重启你的 AI 助手客户端；Web 界面刷新页面，或者直接**开一个新会话**（技能在会话开始时加载）。
2. 问它一句：

   ```text
   你现在能用哪些技能？
   ```

3. 看到 `spice-chip-modeling` 就说明装载成功。

如果没看到，检查三件事：`SKILL.md` 是否在文件夹根目录、文件夹是否放对了 skills 目录、是否开了新会话。

### （可选）其他工具

`agents/openai.yaml` 里是给 Codex 类工具用的展示信息（技能名、简介、默认提示词）。其他工具一般直接读 `SKILL.md` 的头部信息，无需额外配置。

---

## 怎么用

装好之后就**只用聊天**，把下面三样说清楚即可：

1. **哪个器件**：厂商 + 完整型号 + 封装/引脚数（例如 "TI 的 LM358，SOIC-8"）。
2. **datasheet**：给出 PDF 路径或链接（能给原版最好）。
3. **你打算怎么用**：工作电压、负载、温度范围、你关心的指标（例如 "5V 供电、驱动 600Ω 负载、关心压摆率和输出摆幅"）。

### 示例说法

```text
帮我把 D:\datasheets\1N4148.pdf 做成 ngspice 模型。
用途：5V 开关电路里的续流二极管，关心正向压降和结电容。
```

```text
用 datasheet 里的曲线给我建一个 LM358 的运放模型，
要求：±5V 供电、能反映带宽和压摆率、输出短路保护要有。
```

```text
这个 LDO（datasheet 在附件里）帮我生成模型，
重点验证：负载阶跃、压差、限流、以及 1uF~100uF 输出电容下的稳定性。
```

```text
这是个现成的 .lib 模型，帮我审一下它和 datasheet 对得上吗？不用改，只出报告。
```

小技巧：

- 说清楚**"只审不改"**或**"只设计不验证"**这类边界，它就不会多做多余的事。
- 一次可以只做一个器件；要批量做，先说清清单和验收标准。
- datasheet 是扫描件也没关系，但文字/曲线越清晰，参数提取越可靠。

### 它会按什么流程干活

1. **读源料**：确认型号、封装、引脚顺序、文档版本，把每个关键指标对应到 datasheet 的页码/曲线。
2. **设计架构**：把要复现的行为拆成方程、状态和端口，再选对应的器件建模套路。
3. **实现**：用原生 ngspice 语法写成模型（`.lib` / `.mod`）。
4. **验证**：跑标定点、独立行为、应用场景（闭环、大信号、保护、启动、温度）和数值稳定性检查。某条不过就定位原因改，改完重跑受影响的检查。
5. **交付 + 清理**：只给你需要的模型文件和一份说明，中间文件清掉。

### 你会拿到什么

一个文件夹，里面通常只有两样东西：

- **模型文件**（`.lib` / `.mod`，必要时带 include 的子文件、表格数据、模块文件），文件头有 AI 生成声明。
- **一份 Markdown 说明**：型号与引脚顺序、怎么 include、依赖和所需的引擎版本、能复现哪些行为及其条件、误差或边界、已知假设和限制、验证摘要。

默认**不会**给你一堆测试台、日志、拟合数据和截图。如果你想要完整的过程证据，可以明确要求保留。

---

## 想先确认环境能用？（可选自检）

不想等建模时才暴露环境问题，可以先跑一个"分压电路"最小例子。新建一个空目录（当作临时工作区，跑完可以直接删），在该目录里放下面两个文件。

`divider.inc`：

```text
V1 in 0 2
R1 in out 1k
R2 out 0 1k
```

`case.json`：

```json
{
  "schema_version": "ngspice-run/2",
  "entry": "divider.inc",
  "analysis": {"type": "op"},
  "vectors": [{"name": "out", "expression": "v(out)"}],
  "metrics": [{
    "id": "divider", "column": "out", "operation": "scalar",
    "expected": 1, "atol": 0.000001, "rtol": 0,
    "unit": "V", "source": "DERIVED: 2 V times 1 kohm / 2 kohm",
    "tolerance_basis": "Numerical allowance for the ideal divider equation"
  }]
}
```

先准备引擎（没有 ngspice 时这一步会下载）。注意要在**技能目录**下执行，或者把脚本路径写全 —— 下面假设技能装在 `C:\Users\<你的用户名>\.claude\skills\spice-chip-modeling`：

```text
python "C:\Users\<你的用户名>\.claude\skills\spice-chip-modeling\scripts\provisioning.py" --cache .tools\ngspice
```

它会输出一段 JSON：`path` 就是可用的 ngspice 可执行文件路径，`action` 说明是复用了已有安装（`reused`）还是新装（`installed`）。`--cache` 是引擎的存放目录，这里放进当前临时目录的 `.tools\ngspice`。

再跑分析（回到放着 `case.json` 的目录执行；`--engine` 填上面的 `path` 的值；`--output` 必须是一个**还不存在**的目录）：

```text
python "C:\Users\<你的用户名>\.claude\skills\spice-chip-modeling\scripts\run_analysis.py" --manifest case.json --engine <path 的值> --output run1
```

看到 `result.json` 里状态为 `PASS`、`out ≈ 1 V`，说明 Python、引擎、运行器整条链路是通的。

---

## 命令行用法（进阶，可选）

日常不用碰这些命令，AI 会自动调用。想自己复现结果时，下面命令里的 `scripts\` 指技能目录下的 `scripts\`：

| 脚本 | 用途 |
|---|---|
| `scripts/provisioning.py --cache <目录> [--engine <路径>]` | 找可用的 ngspice；没有就下载官方稳定版到私有目录。`--engine` 指定你已有的。 |
| `scripts/run_analysis.py --manifest <case.json> --engine <ngspice> --output <新目录>` | 跑一个声明的分析，核对导出数据并给出 `PASS` / `FAIL` / `REVIEW_REQUIRED` 等状态。 |
| `scripts/workspace.py create --parent <目录>` | 建一个带归属标记的临时工作目录。 |
| `scripts/workspace.py publish --workspace <目录> --token <令牌> --destination <新目录> --file <文件> [...]` | 只把选定的交付文件复制出去（目标目录必须不存在）。 |
| `scripts/workspace.py cleanup --workspace <目录> --token <令牌>` | 清理它自己建的临时目录，不会碰你的其他文件夹。 |

`case.json` 里可以声明 `op` / `dc` / `ac` / `tran` / `noise` 分析、要导出的向量、判据（期望值或上下限）以及超时。判据的期望值应当来自 datasheet 或独立推导，不能来自模型自己的输出。更细的写法见 `references/execution/runner.md`。

---

## 常见问题

**提示找不到 `python`**
Windows 装 Python 时没勾 "Add to PATH"。重装并勾选，或改用 `py` 命令。

**提示没有 ngspice / 下载失败**
先手动装一个 ngspice，然后用 `--engine` 指向它，或设置环境变量 `NGSPICE_EXECUTABLE`。网络受限时，从 [ngspice 官网](https://ngspice.sourceforge.io/download.html) 下载后解压即可。

**Windows 上跑完没有输出**
某些 Windows 版本的 `ngspice.exe` 是窗口程序，批处理下拿不到输出。改用同一目录里的 `ngspice_con.exe`。

**报错"输出目录已存在"**
这是故意的：每次都写到全新的目录，避免旧结果冒充新结果。换个新目录名，或者先删掉旧的。

**状态是 `REVIEW_REQUIRED` 是什么意思**
仿真跑完了、判据也过了，但引擎报过数值警告（例如 gmin 或源步进救场）。需要人工看一眼这些警告是否影响了结果，不能直接当通过。

**提示 `EXECUTED` 是什么意思**
声明要导出的数据都拿到了，但这个用例没有声明电气判据，所以只算"跑通"，不算"合格"。

**能改我的文件吗**
skill 在工作目录里干活，交付时只复制选中的文件，而且拒绝覆盖已存在的目录。原始 datasheet 建议你自己留一份原版。

**模型文件头的 AI 声明能删吗**
不建议。它是为了让使用者知道这模型是 AI 依据 datasheet 生成的、不保证完全复现真实器件。删掉会让下游误以为是厂商官方模型。

**装完想升级**
进到 skills 目录里 `git pull` 就行；用复制方式安装的，重新复制覆盖一次。

---

## 目录结构

```text
SKILL.md                    技能入口：工作流、边界、验收原则
references/
  sources/evidence.md       怎么读 datasheet（事实 / 推导 / 假设要分开）
  modeling/architecture.md  行为 → 方程 / 状态 / 端口
  recipes/                  各类器件的建模套路（无源、分立、运放、开关、接口…）
  mechanisms/               电荷、噪声、温度/电热等专项
  syntax/ngspice.md         原生语法要点
  execution/                引擎获取、运行器、能力边界、探针电路
  verification/             验证契约、数值诊断
  delivery/                 交付物与临时文件清理规则
  maintenance/              规则归位
scripts/                    Python 助手（引擎获取、运行、结果核对、工作区）
assets/                     说明文档与构建记录模板
agents/openai.yaml          其他 AI 工具的展示配置
```

---

## 版本与说明

- 技能版本：**v1.1.2**
- 作者：**EasyEDA**
- 许可：**Apache-2.0**，详见 [LICENSE](LICENSE)
- 依赖：Python 3.8+（仅标准库）、ngspice（可自动获取）；Windows 自动下载时另需 7-Zip 或 `py7zr`。
- 生成的模型是 **AI 依据公开技术资料构建的工程近似**，用于仿真分析；不构成厂商认证，也不替代 datasheet 中的保证值。正式使用前请自行复核关键指标。
