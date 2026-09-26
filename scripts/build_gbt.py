# -*- coding: utf-8 -*-
"""
build_gbt.py — 以样章为模板生成教材章节 docx（标准形式：文内[N] + 文尾"参考文章"）

引用形式（本项目最终交付形态，尾注/脚注方案已弃用）：
  正文引用标记直接写成纯文本 [n]（无任何 Word 域机制，永不丢失、经 Word/WPS 再保存不变形）；
  文末追加"参考文章"节，每行一条 "[N] 单位：链接"。

与 content.py 配合（写法同 build_docx.py 头部注释）：
  BLOCKS   = [(段落类型, 文本), ...]；正文中用 ⟦n⟧ 标引用位（撰写时按首次出现顺序编号）
  ENDNOTES = {n: "单位：链接"}
用法：
  1) 改头部 SRC/OUT 常量（或用 argv: python build_gbt.py 样章.docx 输出.docx）
  2) 把 content.py 放在本脚本同目录，运行 python build_gbt.py
  3) 生成后必做（见 SKILL.md §6/§7）：
       python renumber_refs.py 输出.docx                 # 重排+双向核验
       python renumber_refs.py 输出.docx --strip 无引用提交版.docx   # 标准配套交付物
"""
import copy, re, shutil, sys
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import qn, nsdecls

sys.path.insert(0, '.')
from content import BLOCKS, ENDNOTES

SRC = '../第一章  数字经济概述.docx'   # 样章（排版模板）
OUT = '../第十一章 数字经济新兴业态与数字治理.docx'
CASE_ICON_ANCHOR = '小米智能家居'      # 样章中案例标题图标所在段的锚定文字
if len(sys.argv) >= 3:
    SRC, OUT = sys.argv[1], sys.argv[2]

shutil.copy(SRC, OUT)
doc = Document(OUT)
body = doc.element.body

icon_run = None
for p in doc.paragraphs:
    if p.text.strip().startswith(CASE_ICON_ANCHOR):
        for r in p._element.findall(qn('w:r')):
            if r.find(qn('w:drawing')) is not None:
                icon_run = copy.deepcopy(r)
                break
    if icon_run is not None:
        break
assert icon_run is not None, f'样章中未找到案例图标（锚定文字: {CASE_ICON_ANCHOR}）'

sectPr = body.find(qn('w:sectPr'))
for child in list(body):
    body.remove(child)

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

PPR_BASE = ('<w:keepNext w:val="0"/><w:keepLines w:val="0"/><w:pageBreakBefore w:val="0"/>'
            '<w:widowControl/><w:kinsoku/><w:wordWrap/><w:overflowPunct/><w:topLinePunct w:val="0"/>'
            '<w:autoSpaceDE/><w:autoSpaceDN/><w:bidi w:val="0"/><w:adjustRightInd/><w:snapToGrid/>'
            '<w:spacing w:line="360" w:lineRule="auto"/>')

def text_runs(text, rpr):
    """把 ⟦n⟧ 转为纯文本引用标记 [n]（与正文同格式，无域机制）"""
    out = []
    pos = 0
    for m in re.finditer(r'⟦(\d+)⟧', text):
        seg = text[pos:m.start()]
        if seg:
            out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(seg)}</w:t></w:r>')
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">[{m.group(1)}]</w:t></w:r>')
        pos = m.end()
    seg = text[pos:]
    if seg:
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(seg)}</w:t></w:r>')
    return ''.join(out)

SONG = '<w:rFonts w:hint="eastAsia" w:ascii="宋体" w:hAnsi="宋体" w:eastAsia="宋体" w:cs="宋体"/>'
FANGSONG = '<w:rFonts w:hint="eastAsia" w:ascii="仿宋" w:hAnsi="仿宋" w:eastAsia="仿宋" w:cs="仿宋"/>'

def add_par(ppr_inner, runs_xml):
    p = parse_xml(f'<w:p {nsdecls("w")}><w:pPr>{ppr_inner}</w:pPr>{runs_xml}</w:p>')
    body.append(p)
    return p

for kind, text in BLOCKS:
    if kind == 'title':
        m = re.match(r'(第.+?章)(\s+)(.*)', text)
        head, rest = m.group(1), m.group(3)
        rpr50 = '<w:rFonts w:hint="eastAsia" w:eastAsia="方正书宋_GBK"/><w:sz w:val="50"/>'
        rpr32 = '<w:rFonts w:hint="eastAsia" w:eastAsia="方正小标宋_GBK"/><w:sz w:val="32"/>'
        runs = (f'<w:r><w:rPr>{rpr50}</w:rPr><w:t xml:space="preserve">{esc(head)}</w:t></w:r>'
                f'<w:r><w:rPr>{rpr50}</w:rPr><w:t xml:space="preserve"> </w:t></w:r>'
                f'<w:r><w:rPr>{rpr32}</w:rPr><w:t xml:space="preserve"> </w:t></w:r>'
                f'<w:r><w:rPr>{rpr50}</w:rPr><w:t xml:space="preserve">{esc(rest)}</w:t></w:r>')
        add_par(PPR_BASE + '<w:jc w:val="center"/>', runs)
    elif kind == 'case_title':
        add_par(PPR_BASE, '')
        body[-1].append(copy.deepcopy(icon_run))
        rpr = '<w:rFonts w:hint="eastAsia" w:eastAsia="方正黑体_GBK"/><w:sz w:val="24"/>'
        run = parse_xml(f'<w:r {nsdecls("w")}><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(text)}</w:t></w:r>')
        body[-1].append(run)
    elif kind in ('case_body', 'case_q'):
        add_par(PPR_BASE + '<w:ind w:firstLineChars="200"/>',
                text_runs(text, FANGSONG + '<w:sz w:val="24"/><w:szCs w:val="24"/>'))
    elif kind == 'h2':
        add_par('<w:pStyle w:val="8"/>' + PPR_BASE + '<w:ind w:firstLineChars="200"/>'
                '<w:jc w:val="center"/><w:outlineLvl w:val="2"/>',
                text_runs(text, SONG + '<w:b/><w:bCs/><w:sz w:val="32"/>'))
    elif kind == 'h3':
        add_par('<w:pStyle w:val="9"/>' + PPR_BASE + '<w:ind w:firstLineChars="200"/>'
                '<w:jc w:val="left"/><w:outlineLvl w:val="3"/>',
                text_runs(text, SONG + '<w:b/><w:bCs/><w:sz w:val="30"/><w:szCs w:val="30"/>'))
    elif kind == 'h4':
        add_par('<w:pStyle w:val="7"/>' + PPR_BASE + '<w:ind w:firstLineChars="200"/>'
                '<w:jc w:val="left"/><w:outlineLvl w:val="4"/>',
                text_runs(text, SONG + '<w:b/><w:bCs/><w:sz w:val="28"/><w:szCs w:val="28"/>'))
    else:
        add_par(PPR_BASE + '<w:ind w:firstLineChars="200"/>',
                text_runs(text, SONG + '<w:sz w:val="24"/><w:szCs w:val="24"/>'))

# —— 文尾"参考文章"节 ——
REF_RPR = SONG + '<w:sz w:val="21"/><w:szCs w:val="21"/>'
add_par(PPR_BASE, '')
add_par(PPR_BASE + '<w:ind w:firstLineChars="200"/>',
        f'<w:r><w:rPr>{SONG}<w:b/><w:bCs/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>'
        f'<w:t xml:space="preserve">参考文章</w:t></w:r>')
used = []
for kind, text in BLOCKS:
    for m in re.finditer(r'⟦(\d+)⟧', text):
        n = int(m.group(1))
        if n not in used:
            used.append(n)
for n in sorted(used):
    assert n in ENDNOTES, f'⟦{n}⟧ 在 ENDNOTES 中无对应引文'
    add_par(PPR_BASE,
            f'<w:r><w:rPr>{REF_RPR}</w:rPr><w:t xml:space="preserve">[{n}] {esc(ENDNOTES[n])}</w:t></w:r>')

if sectPr is not None:
    body.append(sectPr)

doc.save(OUT)
print('saved:', OUT)
print(f'参考文章 {len(used)} 条。下一步必做:')
print(f'  python renumber_refs.py "{OUT}"            # 重排+双向核验')
print(f'  python renumber_refs.py "{OUT}" --strip 无引用提交版.docx')
