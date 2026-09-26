# -*- coding: utf-8 -*-
"""以样章为模板生成第十一章 docx —— 引用以文内括号注形式给出（不使用 Word 尾注）"""
import copy, re, shutil, sys
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import qn, nsdecls

sys.path.insert(0, '.')
from content import BLOCKS, ENDNOTES

SRC = '../第一章  数字经济概述.docx'
OUT = '../第十一章 数字经济新兴业态与数字治理.docx'

shutil.copy(SRC, OUT)
doc = Document(OUT)
body = doc.element.body

icon_run = None
for p in doc.paragraphs:
    if p.text.strip().startswith('小米智能家居'):
        for r in p._element.findall(qn('w:r')):
            if r.find(qn('w:drawing')) is not None:
                icon_run = copy.deepcopy(r)
                break
    if icon_run is not None:
        break
assert icon_run is not None

sectPr = body.find(qn('w:sectPr'))
for child in list(body):
    body.remove(child)

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

PPR_BASE = ('<w:keepNext w:val="0"/><w:keepLines w:val="0"/><w:pageBreakBefore w:val="0"/>'
            '<w:widowControl/><w:kinsoku/><w:wordWrap/><w:overflowPunct/><w:topLinePunct w:val="0"/>'
            '<w:autoSpaceDE/><w:autoSpaceDN/><w:bidi w:val="0"/><w:adjustRightInd/><w:snapToGrid/>'
            '<w:spacing w:line="360" w:lineRule="auto"/>')

CITE_RPR = '<w:rFonts w:hint="eastAsia"/><w:color w:val="808080"/><w:sz w:val="18"/><w:szCs w:val="18"/>'

def text_runs(text, rpr):
    """把 ⟦n⟧ 转为文内括号注（单位：链接，小字灰色）"""
    out = []
    pos = 0
    for m in re.finditer(r'⟦(\d+)⟧', text):
        seg = text[pos:m.start()]
        if seg:
            out.append(f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{esc(seg)}</w:t></w:r>')
        n = int(m.group(1))
        cite = f'（{ENDNOTES[n]}）'
        out.append(f'<w:r><w:rPr>{CITE_RPR}</w:rPr><w:t xml:space="preserve">{esc(cite)}</w:t></w:r>')
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
        m = re.match(r'(第十一章)(\s+)(.*)', text)
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

if sectPr is not None:
    body.append(sectPr)

doc.save(OUT)
print('saved:', OUT)
