# -*- coding: utf-8 -*-
"""
download_clean.py — 按清单下载引用来源并清洗为纯文本存档
用法: python download_clean.py urls.tsv 输出目录
  urls.tsv 每行: 编号<TAB>URL （如 1\thttps://www.gov.cn/...）
产出: 输出目录/编号.txt（首行为“尾注N存档 | 原始URL：…”+ 纯正文）
要点: GBK 老站自动转码；两级页脚规则（软标记只截行不中断、强标记才中断）；
      清洗后人工用关键事实词复核，JS 空壳页换权威镜像或手抄存档。
"""
import html as html_mod, os, re, subprocess, sys

CJK = re.compile(r'[一-鿿]')
def cjk_len(s):
    return len(CJK.findall(s))

SOFT_FOOT = re.compile(
    r'扫一扫|二维码|扫码|分享到|朋友圈|关注.{0,6}(公众号|微博|微信)|'
    r'下载.{0,8}(APP|App|客户端)|打开.{0,10}(APP|App|客户端)|微信扫一扫')
STRONG_FOOT = re.compile(
    r'ICP备|ICP证|备案号|许可证|版权所有|Copyright|©|举报电话|举报邮箱|违法和不良信息|'
    r'未经.{0,4}授权.{0,6}(转载|摘编|复制)|责任?编辑|责编|校对|值班编委|'
    r'相关(推荐|阅读|文章)|更多精彩内容|推荐阅读|热门(推荐|资讯|文章)|猜你喜欢|'
    r'阅读下一篇|查看余下全文|网站地图|联系我们|关于我们|免责声明|隐私(政策|保护)|用户协议|服务协议|'
    r'广告服务|诚聘英才|法律声明|友情链接|意见与建议|使用帮助')
NAV_SHORT = re.compile(
    r'^(ICP备|备案|许可证|版权所有|举报电话|联系我们|关于我们|网站地图|免责声明|隐私政策|用户协议|'
    r'服务协议|广告服务|诚聘英才|法律声明|友情链接|意见与建议|使用帮助|首页|登录|登陆|注册|搜索|下载|'
    r'客户端|视频|图片|直播|要闻|财经|股票|基金|科技|汽车|体育|娱乐|时尚|教育|房产|旅游|健康|游戏|'
    r'文化|军事|历史|专题|专栏|社区|论坛|博客|微博|微信|English|个人中心|退出|设置|消息|通知|关注|'
    r'精选|原创|综合|滚动|国内|国际|社会|观点|评论|深度|人物|产经|公司|市场|行情|数据|研报|新闻中心|'
    r'小字号|中字号|大字号|标准|护眼|夜间|日间|浅色|深色|听新闻|返回|上一篇|下一篇|打印|关闭|展开|'
    r'收起|更多|详情|广告|推广|商城|订阅|充值|会员|举报|回复|收藏|分享|顶|踩|确定|取消|提交|热搜|'
    r'热词|排行榜|最新|最热|焦点|头条|推荐|邮箱|热线|电话|传真|地址|邮编|官方|官网|官方微博|'
    r'官方微信|小程序|公众号|视频号|大字|小字|语音|朗读|无障碍|关怀版|长辈版|适老化|手机版|触屏版|'
    r'电脑版|加入收藏|设为首页|客户端下载|>>|>|<|正文|来源|作者|时间|字号)[:：]?$')
JS_WARN = re.compile(r'没有启用[jJ]ava|enable [jJ]ava|without [jJ]ava[Ss]cript|请开启以便继续访问')
PUNCT = re.compile(r'[，。：；！？、“”‘’《》（）0-9]')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

def fetch(url, dest):
    subprocess.run(['curl', '-L', '-sS', '--compressed', '-A', UA, '--connect-timeout', '15',
                    '--max-time', '90', '--retry', '2', '-o', dest, url], capture_output=True)
    return os.path.exists(dest) and os.path.getsize(dest) > 500

def html_to_text(raw):
    """老政府网站常为 GB2312/GBK：先 UTF-8，失败或乱码多则 GB18030"""
    for enc in ('utf-8', 'gb18030'):
        try:
            s = raw.decode(enc); break
        except UnicodeDecodeError:
            continue
    else:
        s = raw.decode('utf-8', errors='ignore')
    if s.count('\ufffd') > 20:
        s = raw.decode('gb18030', errors='ignore')
    s = re.sub(r'(?is)<script.*?</script>|<style.*?</style>|<!--.*?-->', ' ', s)
    s = re.sub(r'(?i)</(p|div|li|h[1-6]|tr|section|article|td)\s*>|<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html_mod.unescape(s)
    lines = [re.sub(r'[ \t\u3000]+', ' ', ln).strip() for ln in s.splitlines()]
    return '\n'.join(ln for ln in lines if ln)

def wrap(long_line, width=110):
    parts = re.split(r'(?<=[。！？；])', long_line)
    out, buf = [], ''
    for p in parts:
        if len(buf) + len(p) <= width:
            buf += p
        else:
            if buf: out.append(buf)
            buf = p
    if buf: out.append(buf)
    return out

def clean_lines(lines):
    body, pre, started, content_count = [], [], False, 0
    for ln in lines:
        ln = ln.strip().strip('﻿')
        if not ln: continue
        if JS_WARN.search(ln): continue
        if len(ln) <= 22 and (NAV_SHORT.match(ln) or (cjk_len(ln) == 0 and len(ln) < 12)): continue
        m = SOFT_FOOT.search(ln)
        if m:
            ln = ln[:m.start()].strip(' |，,。;；')
            if cjk_len(ln) < 25: continue
        m2 = STRONG_FOOT.search(ln)
        if m2:
            prefix = ln[:m2.start()].strip(' |，,。;；')
            if cjk_len(prefix) >= 25:
                body.extend(wrap(prefix)); content_count += 1
            elif re.match(r'^(责任编辑|责编|校对|值班编委)[:：\s]', ln):
                continue
            if started and content_count >= 3: break
            continue
        if '![' in ln or ln.startswith(']('): continue
        if len(ln) < 45 and not PUNCT.search(ln):
            if not started:
                pre.append(ln); pre = pre[-3:]
            continue
        if cjk_len(ln) < 12 and len(ln) < 40:
            if not started:
                pre.append(ln); pre = pre[-3:]
            continue
        if not started:
            started = True; pre = []
        body.extend(wrap(ln)); content_count += 1
    return [ln for ln in body
            if not (cjk_len(ln) < 12 and len(ln) < 40 and not re.search(r'[，。：；！？、0-9%§—…·]', ln))]

def main():
    tsv, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    os.makedirs('dl_raw', exist_ok=True)
    fails = []
    for line in open(tsv, encoding='utf-8'):
        line = line.rstrip('\n').rstrip('\r')
        if not line.strip(): continue
        n, url = line.split('\t', 1)
        raw = f'dl_raw/{n}.raw'
        ok = (os.path.exists(raw) and os.path.getsize(raw) > 500) or fetch(url, raw)
        if not ok:
            fails.append((n, 'DL-FAIL', url)); continue
        body = clean_lines(html_to_text(open(raw, 'rb').read()).splitlines())
        with open(os.path.join(outdir, f'{n}.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write(f'尾注{n}存档 | 原始URL：{url}\n\n' + '\n'.join(body) + '\n')
        if len(body) < 3:
            fails.append((n, f'THIN:{len(body)}行-疑似JS空壳，需换源或手抄', url))
    print(f'完成；异常 {len(fails)}:')
    for x in fails: print(' ', x)

if __name__ == '__main__':
    main()
