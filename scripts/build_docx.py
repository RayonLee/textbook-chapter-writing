# -*- coding: utf-8 -*-
"""
build_docx.py — 以样章 docx 为模板生成教材章节 docx，注入真实 Word 尾注（十进制编号）
用法: 把 content.py（含 BLOCKS、ENDNOTES）与本脚本放同一目录，
      修改下方 TEMPLATE/OUTPUT 常量后运行: python build_docx.py
content.py 格式:
  BLOCKS = [("title"|"case_title"|"case_body"|"case_q"|"h2"|"h3"|"h4"|"body"|"endq", "文本"), ...]
  ENDNOTES = {1: "单位：链接", ...}   # 正文中用 ⟦n⟧ 标记引用位置
要点: 尾注分隔符规范为 Word 标准 id=-1/0；settings 与 sectPr 双处写 numFmt=decimal，
      且 numFmt 必须放在 endnote 分隔符引用之后，否则 Word 忽略设置退回罗马数字。
"""
import copy, re, shutil, sys
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import qn, nsdecls

sys.path.insert(0, '.')
from content import BLOCKS, ENDNOTES

TEMPLATE = '../第一章  数字经济概述.docx'   # 样章路径（提供样式与案例图标）
OUTPUT = '../新章节.docx'
CASE_ICON_ANCHOR = '小米智能家居'           # 样章中案例标题段的起始文字（用于提取图标）
TITLE_PREFIX = '第十一章'                   # 章标题前缀（用于拆分大号字排版）

shutil.copy(TEMPLATE, OUTPUT)
doc = Document(OUTPUT)
body = doc.element.body

# 提取案例标题图标（含 drawing 的 run），新章节案例标题复用
icon_run = None
for p in doc.paragraphs:
    if p.text.strip().startswith(CASE_ICON_ANCHOR):
        for r in p._element.findall(qn('w:r')):
            if r.find(qn('w:drawing')) is not None:
                icon_run = copy.deepcopy(r)
                break
    if icon_run is not None:
        break

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
    out = []
    pos = 0
    for m in re.finditer(r'⟦(\d+)⟧', text):
        seg = text[pos:m.start()]
        if seg:
            out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(seg)}</w:t></w:r>')
        eid = int(m.group(1)) + 1  # 真实尾注从 id=2 起（-1/0 留给分隔符）
        out.append(f'<w:r><w:rPr><w:rStyle w:val="EndnoteReference"/></w:rPr>'
                   f'<w:endnoteReference w:id="{eid}"/></w:r>')
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
        m = re.match(r'(第[一二三四五六七八九十]+章)(\s+)(.*)', text)
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
        if icon_run is not None:
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

# sectPr：节级尾注编号设为十进制（Word 中尾注编号格式本是节级属性）
if sectPr is not None:
    sectPr.insert(0, parse_xml(f'<w:endnotePr {nsdecls("w")}><w:numFmt w:val="decimal"/></w:endnotePr>'))
    body.append(sectPr)

# EndnoteReference / EndnoteText 样式
styles_el = doc.styles.element
if not styles_el.findall(qn('w:style') + "[@" + qn('w:styleId') + "='EndnoteReference']"):
    st = ('<w:style w:type="character" w:styleId="EndnoteReference">'
          '<w:name w:val="endnote reference"/><w:basedOn w:val="1"/><w:uiPriority w:val="99"/>'
          '<w:semiHidden/><w:unhideWhenUsed/>'
          '<w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>'
          '<w:style w:type="paragraph" w:styleId="EndnoteText">'
          '<w:name w:val="endnote text"/><w:basedOn w:val="1"/><w:uiPriority w:val="99"/>'
          '<w:semiHidden/><w:unhideWhenUsed/>'
          '<w:pPr><w:spacing w:line="240" w:lineRule="auto"/></w:pPr>'
          '<w:rPr><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr></w:style>')
    for frag in parse_xml('<w:dummy %s>%s</w:dummy>' % (nsdecls('w'), st)):
        styles_el.append(frag)

# endnotes.xml：分隔符规范为 Word 标准 id=-1/0，再追加真实尾注
en_part = None
for rel in doc.part.rels.values():
    if 'endnotes' in rel.reltype:
        en_part = rel.target_part
        break
assert en_part is not None
en_xml = en_part.blob.decode('utf-8')
en_xml = re.sub(r'(<w:endnote w:type="separator" w:id=")0(">)', r'\g<1>-1\g<2>', en_xml, count=1)
en_xml = re.sub(r'(<w:endnote w:type="continuationSeparator" w:id=")1(">)', r'\g<1>0\g<2>', en_xml, count=1)
frags = []
for n in sorted(ENDNOTES):
    eid = n + 1
    frags.append(
        f'<w:endnote w:id="{eid}"><w:p><w:pPr><w:pStyle w:val="EndnoteText"/></w:pPr>'
        f'<w:r><w:rPr><w:rStyle w:val="EndnoteReference"/></w:rPr><w:endnoteRef/></w:r>'
        f'<w:r><w:rPr><w:rFonts w:hint="eastAsia"/><w:sz w:val="18"/><w:szCs w:val="18"/></w:rPr>'
        f'<w:t xml:space="preserve"> {esc(ENDNOTES[n])}</w:t></w:r></w:p></w:endnote>')
en_xml = en_xml.replace('</w:endnotes>', ''.join(frags) + '</w:endnotes>')
en_part._blob = en_xml.encode('utf-8')

# settings.xml：整体替换 endnotePr（先分隔符引用、后 numFmt——顺序不能反）
settings_el = doc.settings.element
old_enpr = settings_el.find(qn('w:endnotePr'))
if old_enpr is not None:
    settings_el.remove(old_enpr)
new_enpr = parse_xml(f'<w:endnotePr {nsdecls("w")}><w:endnote w:id="-1"/><w:endnote w:id="0"/><w:numFmt w:val="decimal"/></w:endnotePr>')
fpr = settings_el.find(qn('w:footnotePr'))
if fpr is not None:
    fpr.addnext(new_enpr)
else:
    settings_el.append(new_enpr)

doc.save(OUTPUT)
print('saved:', OUTPUT)
