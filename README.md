# textbook-chapter-writing

**中文** | [English](#english)

中文教材章节编写 skill：目录框架为唯一大纲 → 并行权威调研 → 教材语体撰写 → 全数据配引用 → 来源本地存档 → 带引用 / 无引用双版本 docx 交付。
A Coding Agent skill for writing Chinese textbook chapters: fixed TOC as the sole outline → parallel authoritative research → textbook-style writing → citation for every fact → local source archiving → dual-version docx delivery.

> **⚠️ PS（请务必阅读）：警惕使用 AI 工具进行学术内容创作。** 本 skill 仅为教材编写流程的辅助工具与经验沉淀，不构成任何学术成果的生产捷径。AI 生成内容可能存在事实错误、口径偏差与版权风险，全部内容、数据与引用必须由作者本人逐条核验、改写并对最终文本承担全部责任。请勿将 AI 输出未经核实直接作为学术成果提交。

---

## 中文

一套教材章节编写工作流：以**目录框架为唯一大纲**，复刻样章排版风格，按节并行调研权威来源，以教材语体撰写概念论述与案例，为每一处数据事实配「文内 [N] + 文尾参考文章」引用，将全部引用来源下载清洗为本地纯文本存档，最终同时交付**带引用版**与**无引用提交版**两个 docx。

### 实战成果

本 Skill 已在真实教材编写项目中全程跑通，支撑完成**《数字经济概论》**与**《数字经济与数字化转型》**两本教材的章节撰写。以《数字经济与数字化转型》第十一章为例，单次交付：概念论述 2 节 + 案例 8 个，约 1.8 万字，89 条引用全部双向核验通过，89 份来源全部本地存档并可逐条回查。

### 设计思路

- **人定框架、AI 交付、人来验收**：目录框架由编写者给定，Agent 负责调研、撰写、配引、存档、排版与自检，人只做理解确认与最终验收；验收满意的流程随即固化为 Skill。
- **经验在积累，而非流失**：SKILL.md 里每条规则都是真实项目踩坑后的教训——37 份「头文错配」的复用存档、两次因未确认理解而返工、尾注编号被 Word 静默退回罗马数字……全部写明原因与对策，这是 Skill 与口头交代最本质的区别。
- **引用工程化**：引用不是写完再补的点缀，而是从撰写打点、下载存档、编号重排、双向核验到链接终检的一条流水线，每一步都有对应脚本。
- **双版本交付**：带引用版留档核验、无引用版对外提交，一行命令派生，永不手工删引用。

### 硬性约束（也是亮点）

- **目录框架即唯一大纲**：框架列了什么就写什么，不多写不少写——只列了案例的节绝不自行补写概念小节；未列任何内容的节按教材常规写概念论述。对框架理解有疑义时，先书面汇报理解、经确认后再动笔。
- **每个数据必有引用，找不到权威出处宁可不写**：来源优先级为 gov.cn 各部门 > 新华社/人民网/央视 > 官方机构（信通院/CNNIC/赛迪）> 公司官网 > 权威财经媒体；自媒体与券商研报数字慎用，口径差异必须在文中注明（「据 XX 测算」）。
- **引用形态零脆弱性**：文内 [N] + 文尾「参考文章」为纯文本，**无任何 Word 域机制**——永不丢失、经 Word/WPS 再保存不变形、编号想怎么排怎么排（真实尾注方案因 OOXML 机制太脆弱已弃用，仅留档参考）。
- **双向核验 + 覆盖核查**：文中↔文尾一一对应、首次出现序列严格 1..N、孤儿条目必删；并反向扫描「该有引用而没有」的段落——双向核验管不了这一维，本项目两处整段零引用都靠这步才暴露。
- **来源全量本地存档**：每条引用对应一份清洗后的纯文本 txt（GBK 老站自动转码、两级页脚规则、JS 空壳预警），并用「关键事实词」逐份校验命中、核验首行 URL 与正文一致。
- **交付前链接终检**：全部 URL 并发测试，识别软 404 / JS 空壳 / CDN 与 WAF 造成的假阴性；确认死链按「官方原始页 > 官方镜像 > 权威转载」换源，文档条目、存档首行、引用清单三处同步更新。
- **开工前必问，信息不齐不动笔**：面向对象（决定内容侧重）、目录框架与样章、内容要求、引用要求、交付物五项收齐，并书面汇报「哪节写什么、哪节不写什么、面向谁、侧重什么」经确认后才进入撰写。

### 日常使用：一句话 Prompt

在 Coding Agent（Kimi Code / Claude Code 等）中打开本文件夹，输入：

> 按 textbook-chapter-writing 的流程，帮我撰写教材《XXX》第 X 章，目录框架和样章在 XXX.docx

Agent 会先向你确认「面向对象 / 目录框架 / 内容要求 / 引用要求 / 交付物」五项信息，确认后按 [SKILL.md](SKILL.md) 自动执行完整流水线：解析样章风格 → 按节并行调研 → 撰写 → 来源下载存档 → 生成 docx → 引用重排与双向核验 → 链接终检 → 模拟专家评审 → 交付双版本。无需记忆任何命令。

也可将本文件夹放入你的 Agent skills 目录，「写教材章节 / 教材编写 / 书稿扩写 / 案例集撰写」类请求即可自动触发本 Skill。

### 交付物

| 层级 | 交付物 | 说明 |
|---|---|---|
| **最终** | 带引用版章节 docx | 复刻样章排版（样式、字号、案例体例、思考题形式）；文内 [N] + 文尾「参考文章」，留档核验用 |
| **最终** | 无引用提交版 docx | 由带引用版一键派生（`renumber_refs.py --strip`），全文无残留 [N]、无「参考文章」字样，对外提交用 |
| 中间 | 参考资料存档 `N.txt` | 每条引用来源的纯文本清洗版，首行注明原始 URL，关键事实词全部命中 |
| 中间 | 引用清单 | 编号 ↔ 引文 ↔ 本地文件对照表 |
| 沉淀 | SKILL.md 更新 | 每次项目的新教训写回 Skill，下次不再踩坑 |

### 随附脚本（scripts/）

| 脚本 | 用途 | 用法 |
|---|---|---|
| `probe_style.py` | 提取样章样式/字号/字体/案例标题格式 | `python probe_style.py 样章.docx 锚定文字…` |
| `download_clean.py` | 按「编号 TAB URL」清单下载来源并清洗为纯文本（GBK 转码、两级页脚规则、JS 空壳预警） | `python download_clean.py urls.tsv 输出目录` |
| `check_archives.py` | 存档核验：关键事实词命中、首行 URL 一致、过薄预警 | `python check_archives.py 存档目录 urls.tsv` |
| `build_gbt.py` | 以样章为模板生成章节 docx（**标准形式**：文内 [N] + 文尾参考文章，无域机制） | 与同目录 `content.py`（BLOCKS+ENDNOTES）配合，改头部常量后运行 |
| `build_docx.py` | ~~真实 Word 尾注版~~（已弃用，仅留档参考：OOXML 尾注机制脆弱） | 同上 |
| `build_inline.py` | 文内括号注版（仅当明确要求括号注时备选） | 同上 |
| `renumber_refs.py` | 引用按首次出现顺序重排、删孤儿条目、双向核验、派生无引用版、无引用段落遗漏扫描 | `python renumber_refs.py 章节.docx [-o 输出.docx]`；`--strip 无引用版.docx`；`--check-missing` |
| `check_links.py` | 交付前链接终检：并发测试全部引用 URL，识别软 404 / JS 空壳 / 疑似误报 | `python check_links.py 章节.docx` |

### 快速开始

```bash
pip install python-docx lxml
```

1. 准备本章**目录框架**与**参照样章** docx（样章仅作排版模板）
2. 在 Coding Agent 中打开本文件夹，用上面的一句话 Prompt 发起任务
3. 回答 Agent 的开工前五项确认（面向对象 / 框架 / 内容 / 引用 / 交付物）
4. 流水线跑完后，在 Word/WPS 中打开带引用版复查排版（需安装样章同款字体），确认后取无引用版提交

### 目录结构

```
├── SKILL.md          # 完整工作流文档（开工前必问、最高原则、验证清单、踩坑速查）
├── scripts/          # 八个可复用脚本（样式提取 / 下载清洗 / 存档核验 / 三种生成 / 重排核验 / 链接终检）
└── README.md
```

> ⚠️ 再次提醒：警惕使用 AI 工具进行学术内容创作。请遵守所在机构与出版方关于 AI 工具使用的规定，由作者本人对最终文本的事实、观点与引用负全部责任。

---

## English

A complete workflow for writing Chinese textbook chapters: the **given table of contents is the sole outline**; the sample chapter's layout is replicated; authoritative sources are researched in parallel per section; concepts and cases are written in textbook style; every fact and figure gets a citation in the "in-text [N] + end-of-chapter reference list" format; all cited sources are downloaded and cleaned into local plain-text archives; and two docx files — **with citations** (for archiving) and **without citations** (for submission) — are delivered together.

### Proven in Real Projects

This skill has been battle-tested in real textbook projects, supporting chapters of two published-book projects: ***Introduction to the Digital Economy* (《数字经济概论》)** and ***Digital Economy and Digital Transformation* (《数字经济与数字化转型》)**. For Chapter 11 of the latter, a single delivery covered 2 concept sections + 8 cases, ~18,000 Chinese characters, with 89 citations passing bidirectional verification and 89 sources archived locally for traceability.

### Design Philosophy

- **Human sets the outline, AI delivers, human accepts**: the author provides the TOC; the agent researches, writes, cites, archives, typesets, and self-checks; humans only confirm understanding and give final acceptance — and any workflow that passes is codified into a Skill.
- **Experience compounds instead of leaking**: every rule in SKILL.md is a lesson from a real pitfall — 37 reused archives with mismatched headers, two rework rounds caused by unconfirmed understanding, endnote numbering silently reverted to Roman numerals by Word — each documented with cause and remedy. That is the essential difference between a Skill and verbal instructions.
- **Citation engineering**: citations are not an afterthought but a pipeline — marking while writing, downloading & archiving, renumbering, bidirectional verification, and a final link check, each step backed by a script.
- **Dual-version delivery**: the cited version for archiving/verification, the citation-free version for submission — derived with one command, never by hand.

### Hard Constraints (a.k.a. Highlights)

- **The TOC is the sole outline**: write exactly what the outline lists — no more, no less. Sections listing only cases get cases only; sections listing nothing get full concept exposition. Any ambiguity is reported in writing and confirmed before writing.
- **Every fact needs a citation; unverifiable "circulating numbers" are dropped**: source priority is gov.cn ministries > Xinhua/People's Daily/CCTV > official institutions (CAICT/CNNIC/CCID) > company official sites > authoritative financial media; self-media and broker-report numbers are used with caution, and caliber differences must be noted in text.
- **Zero-fragility citation format**: in-text [N] + end-of-chapter reference list as plain text — **no Word field machinery at all**, so citations never break or deform when re-saved in Word/WPS (the real-endnote approach was deprecated for OOXML fragility and is kept for reference only).
- **Bidirectional verification + coverage audit**: text↔list one-to-one mapping, first-appearance sequence strictly 1..N, orphan entries deleted; plus a reverse scan for "paragraphs that should have citations but don't" — the dimension bidirectional checks cannot cover.
- **Full local archiving of sources**: every citation gets a cleaned plain-text txt (auto GBK transcoding for legacy government sites, two-level footer rules, JS-shell warnings), verified by keyword hits and header-URL consistency.
- **Final link check before delivery**: all URLs tested concurrently, detecting soft 404s, JS shells, and false negatives caused by CDN/WAF; confirmed dead links are replaced in the order "official original > official mirror > authoritative republication", with the document entry, archive header, and citation list updated together.
- **No writing before requirements are complete**: five items must be collected and confirmed up front — target audience (which determines content emphasis), TOC & sample chapter, content requirements, citation requirements, deliverables — with a written statement of understanding ("which sections cover what, for whom, with what emphasis").

### Daily Use: One Prompt

Open this folder in a Coding Agent (Kimi Code, Claude Code, etc.) and type:

> Follow the textbook-chapter-writing workflow to write Chapter X of the textbook "XXX"; the TOC and sample chapter are in XXX.docx（按 textbook-chapter-writing 流程撰写教材某章）

The agent first confirms five items with you (audience / TOC / content / citation / deliverables), then follows [SKILL.md](SKILL.md) to run the full pipeline: probe sample style → parallel research per section → write → download & archive sources → build docx → renumber & bidirectionally verify citations → final link check → mock expert review → deliver both versions. No commands to memorize.

You can also drop this folder into your agent's skills directory so that requests like "write a textbook chapter / expand a manuscript / write a case collection" trigger this skill automatically.

### Deliverables

| Level | Deliverable | Notes |
|---|---|---|
| **Final** | Cited chapter docx | Replicates the sample chapter's layout (styles, fonts, case format, review questions); in-text [N] + end-of-chapter reference list, for archiving & verification |
| **Final** | Citation-free submission docx | Derived with one command (`renumber_refs.py --strip`); no residual [N] or reference section, ready for submission |
| Intermediate | Source archives `N.txt` | Cleaned plain text of each cited source, original URL in the header line, keyword hits verified |
| Intermediate | Citation list | Number ↔ citation ↔ local file mapping |
| Accumulated | SKILL.md updates | New lessons from each project written back into the Skill |

### Bundled Scripts (scripts/)

| Script | Purpose | Usage |
|---|---|---|
| `probe_style.py` | Extract sample-chapter styles/font sizes/case-title format | `python probe_style.py sample.docx anchors…` |
| `download_clean.py` | Download sources from a "number TAB URL" list and clean to plain text (GBK transcoding, two-level footer rules, JS-shell warning) | `python download_clean.py urls.tsv outdir` |
| `check_archives.py` | Archive verification: keyword hits, header-URL consistency, thin-content warning | `python check_archives.py archive_dir urls.tsv` |
| `build_gbt.py` | Build chapter docx from the sample template (**standard form**: in-text [N] + end-of-chapter list, no field machinery) | Works with `content.py` (BLOCKS+ENDNOTES) in the same dir; edit the header constants and run |
| `build_docx.py` | ~~Real Word endnotes~~ (deprecated, kept for reference: fragile OOXML endnote machinery) | Same as above |
| `build_inline.py` | In-text parenthetical citations (only when explicitly requested) | Same as above |
| `renumber_refs.py` | Renumber citations by first appearance, delete orphans, bidirectional verification, derive citation-free version, missing-citation scan | `python renumber_refs.py chapter.docx [-o out.docx]`; `--strip clean.docx`; `--check-missing` |
| `check_links.py` | Final link check: concurrently test all cited URLs, detect soft 404 / JS shell / suspected false positives | `python check_links.py chapter.docx` |

### Quick Start

```bash
pip install python-docx lxml
```

1. Prepare the chapter **TOC** and a **sample chapter** docx (used as the layout template only)
2. Open this folder in a Coding Agent and start the task with the one-line prompt above
3. Answer the agent's five pre-flight questions (audience / TOC / content / citation / deliverables)
4. When the pipeline finishes, open the cited version in Word/WPS to review the layout (requires the same fonts as the sample chapter), then submit the citation-free version

### Layout

```
├── SKILL.md          # Full workflow documentation (pre-flight questions, top principles, verification checklist, pitfall guide)
├── scripts/          # Eight reusable scripts (style probing / download & cleaning / archive check / three builders / renumbering & verification / link check)
└── README.md
```

> ⚠️ Reminder: be cautious about using AI tools for academic content creation. Comply with your institution's and publisher's policies on AI assistance; the author bears full responsibility for the facts, views, and citations in the final text.

---

## License / 许可证

Released under the [MIT License](LICENSE). 本项目以 MIT 许可证开源，可自由使用、修改与再分发，保留版权声明即可。

Copyright (c) 2026 Ruiyang Li (PhD Student, Renmin University of China)
