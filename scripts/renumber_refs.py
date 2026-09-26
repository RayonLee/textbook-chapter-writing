# -*- coding: utf-8 -*-
"""
renumber_refs.py — 文内[N]+文尾"参考文章"式引用的重排与双向核验

适用形态: 正文 [1][2] 标注 + 文末"参考文章"节, 条目格式 "[N] 单位：链接"(纯文本, 无 Word 域)。

两种模式:
  1) 重排模式(默认): 以正文首次出现顺序为基准重编全部引用, 删除正文未出现的孤儿条目,
     双向核验(文中->文尾 / 文尾->文中)后写回。
       python renumber_refs.py 章节.docx [-o 输出.docx] [--ref-heading 参考文章]
  2) 无引用版(--strip): 另存副本, 正文 [N] 标记全部删除, "参考文章"整节删除, 原文件不动。
       python renumber_refs.py 章节.docx --strip 无引用版.docx
  3) 遗漏扫描(--check-missing, 只读): 列出正文不含[N]的段落并按信号词排可疑度,
     供人工判断哪些段落该有引用而没有(双向核验管不了这一维)。
       python renumber_refs.py 章节.docx --check-missing

实现要点(踩坑记录):
  * 引用标记可能跨 run 分裂(<w:t>[1</w:t><w:t>]</w:t>), 逐 run 正则替换必漏——
    按段落拼接全文, 用"字符-owner"映射做替换后按原 run 重建文本, 保留 run 格式。
  * 文尾重排不物理移动 XML 元素: 删孤儿段落, 幸存段落按文档顺序就地重写为新序号内容。
  * 核验"删除是否干净"要按条目内容/URL 查, 不能按编号查——新号会占用被删旧号。
  * 条目内容("单位：链接")一字不改, 只改编号。
"""
import re, sys, zipfile, shutil
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return f'{{{W}}}{t}'

CITE = re.compile(r'\[(\d{1,3})\]')   # 限1-3位数字, 排除[2024]等年份

def load(path):
    z = zipfile.ZipFile(path)
    tree = etree.fromstring(z.read('word/document.xml'))
    return z, tree

def ptext(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def edit_paragraph_runs(p, edits):
    """对段落做 span 替换并保留 run 格式。
    edits: [(start, end, replacement)] 基于段落拼接全文的坐标。
    原理: 每个保留字符留在原 run; 替换产生的新字符归属 span 起点所在 run。"""
    ts = list(p.iter(q('t')))
    if not ts: return
    owner, parts = [], []
    for idx, t in enumerate(ts):
        s = t.text or ''
        parts.append(s)
        owner.extend([idx] * len(s))
    full = ''.join(parts)
    # 生成新字符序列及其 owner
    new_chars, new_owner, cur = [], [], 0
    for start, end, rep in sorted(edits):
        for j in range(cur, start):
            new_chars.append(full[j]); new_owner.append(owner[j])
        o = owner[start] if start < len(owner) else (owner[-1] if owner else 0)
        for ch in rep:
            new_chars.append(ch); new_owner.append(o)
        cur = end
    for j in range(cur, len(full)):
        new_chars.append(full[j]); new_owner.append(owner[j])
    # 按 owner 归组(保持原相对顺序)写回各 run
    buckets = {i: [] for i in range(len(ts))}
    for ch, o in zip(new_chars, new_owner):
        buckets[o].append(ch)
    for i, t in enumerate(ts):
        t.text = ''.join(buckets[i])

def collect(tree, ref_heading):
    paras = tree.findall('.//' + q('p'))
    texts = [ptext(p) for p in paras]
    ref_start = next((i for i, t in enumerate(texts) if t.strip() == ref_heading), None)
    if ref_start is None:
        sys.exit(f'找不到"{ref_heading}"节标题段')
    firsts, seen = [], set()
    for t in texts[:ref_start]:
        for m in CITE.finditer(t):
            n = int(m.group(1))
            if n not in seen:
                seen.add(n); firsts.append(n)
    entries = []  # (old_num, content, p_element)
    for p in paras[ref_start + 1:]:
        m = re.match(r'\s*\[(\d{1,3})\]\s*(.*)', ptext(p), re.S)
        if m: entries.append((int(m.group(1)), m.group(2).strip(), p))
    return paras, texts, ref_start, firsts, entries

def report(firsts, entries, label):
    used, have = set(firsts), {n for n, _, _ in entries}
    print(f'[{label}] 正文不同编号 {len(used)} | 文尾条目 {len(have)}')
    print('  正文有而文尾缺失:', sorted(used - have) or '无')
    print('  文尾有而正文未用(孤儿):', sorted(have - used) or '无')
    print('  首次出现序列严格递增:', firsts == sorted(firsts))

def renumber(src, dst, ref_heading):
    z, tree = load(src)
    paras, texts, ref_start, firsts, entries = collect(tree, ref_heading)
    report(firsts, entries, '重排前')
    old2new = {old: i + 1 for i, old in enumerate(firsts)}
    # 正文重编号(等长或不等长均可, 字符归属重建)
    for p in paras[:ref_start]:
        full = ptext(p)
        edits = [(m.start(), m.end(), f'[{old2new[int(m.group(1))]}]')
                 for m in CITE.finditer(full)]
        if edits: edit_paragraph_runs(p, edits)
    # 文尾: 删孤儿 + 幸存段落就地重写为新序号
    orphans = {n for n, _, _ in entries} - set(firsts)
    for n, c, p in entries:
        if n in orphans:
            if p.find('.//' + q('sectPr')) is None:
                p.getparent().remove(p)
    surviving = [p for n, c, p in entries if n not in orphans]
    content_of = {n: c for n, c, _ in entries}
    assert len(surviving) == len(firsts), '正文与文尾不一一对应, 先人工处理缺失项'
    for new_num, p in zip(range(1, len(firsts) + 1), surviving):
        ts = list(p.iter(q('t')))
        if not ts: continue
        ts[0].text = f'[{new_num}] {content_of[firsts[new_num - 1]]}'
        for t in ts[1:]: t.text = ''
    write_back(z, tree, dst)
    # 复核
    z2, tree2 = load(dst)
    _, _, _, firsts2, entries2 = collect(tree2, ref_heading)
    report(firsts2, entries2, '重排后')
    assert firsts2 == list(range(1, len(firsts2) + 1)), '首次出现序列未严格递增!'
    assert {n for n, _, _ in entries2} == set(firsts2), '双向对应失败!'
    old_contents = {c for n, c, _ in entries} - {c for n, c, _ in entries if n in orphans}
    assert {c for _, c, _ in entries2} == old_contents, '条目内容被改动!'
    print('双向核验通过: 文中<->文尾一一对应, 条目内容零改动, 孤儿已删除')

def strip_citations(src, dst, ref_heading):
    z, tree = load(src)
    paras, texts, ref_start, firsts, entries = collect(tree, ref_heading)
    n_marks = 0
    for p in paras[:ref_start]:
        full = ptext(p)
        edits = [(m.start(), m.end(), '') for m in CITE.finditer(full)]
        n_marks += len(edits)
        if edits: edit_paragraph_runs(p, edits)
    n_paras = 0
    for p in paras[ref_start:]:
        if p.find('.//' + q('sectPr')) is None:
            p.getparent().remove(p); n_paras += 1
    write_back(z, tree, dst)
    z2, tree2 = load(dst)
    left = [ptext(p) for p in tree2.findall('.//' + q('p')) if CITE.search(ptext(p))]
    assert not left, f'仍有残留[N]: {left[:3]}'
    assert not any(ref_heading in ptext(p) for p in tree2.findall('.//' + q('p')))
    print(f'已生成无引用版: 删除正文标记 {n_marks} 处, 参考文章节 {n_paras} 段, 无残留')

def write_back(z, tree, dst):
    new_xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)
    items = [(item, z.read(item.filename)) for item in z.infolist()]  # 先全量读入内存, 再写(原地覆写时源即目标)
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item, data in items:
            if item.filename == 'word/document.xml':
                data = new_xml
            zout.writestr(item, data)
    z.close()

# 引用遗漏信号: 含数字/英文缩写/书名号/引语/年份/据·按照·标准·报告等词的无引用段落是重点嫌疑
SIGNAL = re.compile(
    r'\d|[A-Za-z]{2,}|《[^》]+》|“[^”]+”|据|按照|依据|标准|报告|白皮书|发布|研究|显示')

def check_missing(src, ref_heading):
    """只读扫描: 列出正文中不含[N]引用标记的段落, 供人工判断是否存在引用遗漏。
    标题/思考题/短段自动略过; 命中信号词越多的越可疑。
    双向核验(文中<->文尾)不能保证"该有引用的都有引用"——本模式补这一维。
    本项目教训: "数据加密与身份认证"整段零引用(AES/RSA/SM2/MFA/零信任均为事实断言),
    靠用户人工阅读才发现。"""
    z, tree = load(src)
    paras = tree.findall('.//' + q('p'))
    texts = [ptext(p) for p in paras]
    ref_start = next((i for i, t in enumerate(texts) if t.strip() == ref_heading), len(texts))
    print('正文无引用段落扫描(标题/短段已略过, 按可疑度排序):')
    rows = []
    for i, t in enumerate(texts[:ref_start]):
        t = t.strip()
        if len(t) < 40:            # 短段多为标题/过渡句
            continue
        if CITE.search(t):         # 已有引用
            continue
        if re.match(r'^[（(]?[一二三四五六七八九十\d]+[）).、]', t):  # 编号标题/思考题
            continue
        hits = len(SIGNAL.findall(t))
        rows.append((hits, i, t))
    if not rows:
        print('  无(所有长段落均含引用)')
        return
    for hits, i, t in sorted(rows, reverse=True):
        flag = '⚠高疑' if hits >= 8 else ('·待判' if hits >= 4 else '·可能可不引(概念/过渡句)')
        print(f'  {flag} 信号{hits:2d} 段{i}: {t[:60]}…')
    z.close()
    print('说明: 扫描只列嫌疑, 是否必须补引由人判断——凡含具体数据、专有名词、技术参数、')
    print('政策文件名、引语的段落必须有引用; 纯概念阐释/过渡句可不引。')


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    src = args[0]
    ref_heading = '参考文章'
    if '--ref-heading' in args:
        i = args.index('--ref-heading'); ref_heading = args[i + 1]
    if '--strip' in args:
        i = args.index('--strip'); strip_citations(src, args[i + 1], ref_heading)
    elif '--check-missing' in args:
        check_missing(src, ref_heading)
    else:
        dst = src
        if '-o' in args:
            i = args.index('-o'); dst = args[i + 1]
        if dst == src:
            shutil.copy(src, src + '.bak')
            print(f'原文件已备份为 {src}.bak')
        renumber(src, dst, ref_heading)
