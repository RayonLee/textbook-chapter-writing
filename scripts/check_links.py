# -*- coding: utf-8 -*-
"""
check_links.py — 交付前终检: 批量测试文档"参考文章"全部URL能否打开到正确网页
用法: python check_links.py 章节.docx [--ref-heading 参考文章]

判定规则(踩坑记录):
  * 软404: HTTP 200 但标题含"404/不存在/出错"——真死链(本项目: 搜狐转载页当天被删)。
  * JS空壳: 正文可见文本过薄(<500字符)——读者浏览器虽能渲染, 但存档与抽检困难, 建议换源。
  * 假阴性: urllib 被 CDN/WAF 拒(DJI 假404)或 TLS 握手失败(gov.cn/cac.gov.cn 系
    UNEXPECTED_EOF)——异常项必须用 curl + 完整浏览器头复核后再下结论:
      curl -sL --compressed -A "Mozilla/5.0 ... Chrome/126.0 Safari/537.36" URL
  * 假阳性: 原始HTML含关键词≠页面可见内容(可能在 script/JSON blob 里)——
    "网页覆盖引用事实"的判断要基于去脚本后的可见文本。
  * 确认死链后的换源顺序: 官方原始页 > 官方镜像 > 权威媒体服务端渲染转载页;
    文档条目、存档txt首行URL、引用清单三处必须同步更新。
"""
import re, sys, json, ssl, gzip, io
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from lxml import etree

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/126.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/pdf,*/*',
      'Accept-Language': 'zh-CN,zh;q=0.9'}
CTX = ssl.create_default_context(); CTX.check_hostname = False; CTX.verify_mode = ssl.CERT_NONE
BAD_TITLE = ('404', '不存在', '出错', '错误', 'Not Found', 'denied')

def extract_urls(docx, ref_heading):
    z = zipfile.ZipFile(docx) if False else None
    import zipfile as zf
    with zf.ZipFile(docx) as z:
        tree = etree.fromstring(z.read('word/document.xml'))
    texts = [''.join(t.text or '' for t in p.iter(W + 't')) for p in tree.iter(W + 'p')]
    start = next((i for i, t in enumerate(texts) if t.strip() == ref_heading), None)
    if start is None:
        sys.exit(f'找不到"{ref_heading}"节')
    urls = {}
    for t in texts[start + 1:]:
        m = re.match(r'\s*\[(\d{1,3})\]\s*(.*)', t, re.S)
        if m and '：' in m.group(2):
            urls[int(m.group(1))] = m.group(2).strip().split('：', 1)[1].strip()
    return urls

def decode_html(raw):
    enc = 'utf-8'
    m = re.search(br'charset=["\']?([\w-]+)', raw[:3000], re.I)
    if m: enc = m.group(1).decode('ascii', 'ignore')
    try: s = raw.decode(enc, 'ignore')
    except LookupError: s = raw.decode('utf-8', 'ignore')
    if '\ufffd' in s[:2000]:
        s = raw.decode('gb18030', 'ignore')
    return s

def visible_text(html):
    s = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>|<!--[\s\S]*?-->', '', html)
    s = re.sub(r'<[^>]+>', ' ', s)
    import html as H
    return re.sub(r'\s+', ' ', H.unescape(s))

def test(item):
    n, u = item
    try:
        r = urlopen(Request(u, headers=UA), timeout=20, context=CTX)
        raw = r.read(300000)
        if r.headers.get('Content-Encoding') == 'gzip':
            raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
        html = decode_html(raw)
        tm = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
        title = re.sub(r'\s+', ' ', tm.group(1)).strip()[:50] if tm else ''
        vis = visible_text(html)
        if any(k in title for k in BAD_TITLE):
            return (n, '软404', u, title)
        if len(vis) < 500:
            return (n, 'JS空壳?', u, title)
        return (n, 'OK', u, title)
    except HTTPError as e:
        return (n, f'HTTP {e.code}', u, '')
    except Exception as e:
        return (n, f'需curl复核: {type(e).__name__}', u, str(e)[:50])

def main():
    docx = sys.argv[1]
    ref_heading = '参考文章'
    if '--ref-heading' in sys.argv:
        ref_heading = sys.argv[sys.argv.index('--ref-heading') + 1]
    urls = extract_urls(docx, ref_heading)
    print(f'共 {len(urls)} 条URL, 并发测试…')
    with ThreadPoolExecutor(max_workers=10) as ex:
        results = sorted(ex.map(test, urls.items()))
    bad = [r for r in results if r[1] != 'OK']
    print(f'正常 {len(results) - len(bad)}/{len(results)}; 待复核 {len(bad)}:')
    for n, st, u, t in bad:
        print(f'  [{n}] {st} {u[:80]} {t}')
    if bad:
        print('处理: 先用 curl+完整浏览器头复核误报; 确认死链后按 官方>镜像>权威转载 换源,')
        print('并同步更新 文档条目 / 存档txt首行URL / 引用清单 三处。')

if __name__ == '__main__':
    main()
