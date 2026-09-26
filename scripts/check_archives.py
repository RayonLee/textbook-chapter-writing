# -*- coding: utf-8 -*-
"""
check_archives.py — 存档质量核验：逐文件检查"首行URL与正文关键事实词"是否命中
用法: python check_archives.py 存档目录 urls.tsv
  urls.tsv 每行: 编号<TAB>URL<TAB>关键事实词（可多个，用|分隔）
  例: 1\thttp://paper.people.com.cn/...\t70%|大疆
另做两件必查:
  1) 首行 URL 与正文是否同一来源（防止复用旧文件头文错配）
  2) 人工打开最薄的文件（<300字符）确认不是 JS 空壳
"""
import os, re, sys

def main():
    outdir, tsv = sys.argv[1], sys.argv[2]
    bad = []
    for line in open(tsv, encoding='utf-8'):
        line = line.rstrip('\n').rstrip('\r')
        if not line.strip(): continue
        parts = line.split('\t')
        n, url = parts[0], parts[1]
        kws = parts[2].split('|') if len(parts) > 2 else []
        path = os.path.join(outdir, f'{n}.txt')
        if not os.path.exists(path):
            bad.append((n, '文件缺失', url)); continue
        s = open(path, encoding='utf-8').read()
        head = s.splitlines()[0]
        if url.rstrip('.') not in head:
            bad.append((n, '首行URL与清单不一致（疑似头文错配）', url)); continue
        miss = [k for k in kws if k not in s]
        if miss:
            bad.append((n, f'关键事实词未命中: {miss}', url))
        if len(s) < 300:
            bad.append((n, f'内容过薄({len(s)}字符)，需人工确认', url))
    print(f'核验完成；异常 {len(bad)}:')
    for x in bad: print(' ', x)

if __name__ == '__main__':
    main()
