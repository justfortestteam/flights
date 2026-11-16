"""Builds index.html from data.json. Run: python3 build_page.py
data.json shape:
{"checked_at": "2026-11-16 15:00",
 "japan": [{"city": "沖繩 Okinawa",
            "bag":   {"price": 2168, "depart": "2027-04-16", "return": "2027-04-20", "airline": "香港航空", "note": "", "link": "https://..."} or null,
            "nobag": {same fields} or null}],
 "asia":  [{"city": "上海 Shanghai", "price": 1375, "depart": "...", "return": "...", "airline": "...", "note": "", "link": "..."}]}
"""
import datetime as dt, html, json

HOL = {'2026-12-25','2027-01-01','2027-02-08','2027-02-09','2027-03-26','2027-03-29','2027-04-05','2027-05-13',
       '2027-06-09','2027-07-01','2027-09-16','2027-10-01','2027-10-08','2027-12-27'}
WK = '一二三四五六日'
e = lambda s: html.escape(str(s or ''))

def day(s):
    x = dt.date.fromisoformat(s[:10]); return f"{x.day}/{x.month}（{WK[x.weekday()]}）"

def al(a, b):
    a, b, n = dt.date.fromisoformat(a[:10]), dt.date.fromisoformat(b[:10]), 0
    while a <= b:
        if a.weekday() < 5 and a.isoformat() not in HOL: n += 1
        a += dt.timedelta(1)
    return n

def link(u, text):
    return f'<a href="{e(u)}" target="_blank" rel="noopener">{text}</a>' if str(u or '').startswith('https://') else ''

def jp_card(r):
    b, n = r.get('bag'), r.get('nobag')
    m = b or n
    tag = '<span class="tag">連寄艙行李</span>' if b else '<span class="tag no">冇寄艙行李</span>'
    warn = f' <span class="warn">⚠ {e(m.get("note"))}</span>' if m.get('note') else ''
    out = [f'<div class="card"><div class="city">{e(r["city"])}</div>',
           f'<div class="pr"><span class="big">HK${m["price"]:,}</span>{tag}{warn}</div>',
           f'<div class="meta">{day(m["depart"])} → {day(m["return"])} · {al(m["depart"], m["return"])} 日 AL · {e(m["airline"])}</div>']
    if b and n:
        note = f'，{e(n["note"])}' if n.get('note') else ''
        out.append(f'<div class="alt">唔連寄艙行李：<b>HK${n["price"]:,}</b>（{day(n["depart"])} → {day(n["return"])}，{e(n["airline"])}{note}）</div>')
    elif not b:
        out.append('<div class="alt">要寄行李就喺航空公司官網加購。</div>')
    links = ' · '.join(x for x in [link(b and b.get('link'), '訂（連行李）' if n else '去 Kiwi.com 睇'), link(n and n.get('link'), '訂（唔連行李）' if b else '去 Kiwi.com 睇')] if x)
    out.append(f'<div class="lk">{links}</div></div>')
    return ''.join(out)

def one_card(r, k):
    m = r[k]
    tag = '<span class="tag">連寄艙行李</span>' if k == 'bag' else '<span class="tag no">冇寄艙行李</span>'
    warn = f' <span class="warn">⚠ {e(m.get("note"))}</span>' if m.get('note') else ''
    return (f'<div class="card"><div class="city">{e(r["city"])}</div>'
            f'<div class="pr"><span class="big">HK${m["price"]:,}</span>{tag}{warn}</div>'
            f'<div class="meta">{day(m["depart"])} → {day(m["return"])} · {al(m["depart"], m["return"])} 日 AL · {e(m["airline"])}</div>'
            f'<div class="lk">{link(m.get("link"), "去 Kiwi.com 睇")}</div></div>')

def asia_card(i, r):
    warn = f' <span class="warn">⚠ {e(r["note"])}</span>' if r.get('note') else ''
    return (f'<div class="card"><div class="city">{e(r["city"])}<span class="rk">#{i}</span></div>'
            f'<div class="pr"><span class="big">HK${r["price"]:,}</span><span class="tag">連寄艙行李</span>{warn}</div>'
            f'<div class="meta">{day(r["depart"])} → {day(r["return"])} · {al(r["depart"], r["return"])} 日 AL · {e(r["airline"])}</div>'
            f'<div class="lk">{link(r.get("link"), "去 Kiwi.com 睇")}</div></div>')

d = json.load(open('data.json', encoding='utf-8'))
page = f'''<!DOCTYPE html><html lang="zh-HK"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>香港出發平機票</title><style>
body{{font-family:"Noto Sans HK","PingFang HK","Microsoft JhengHei",sans-serif;margin:0;padding:20px;background:#f6f5f1;color:#1f1e1d}}
h1{{font-size:24px;margin:0 0 4px}} h2{{font-size:18px;margin:24px 0 4px}} .sub{{color:#6b6a66;font-size:13px;margin:0 0 12px;line-height:1.6}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:10px}}
.card{{background:#fff;border:1px solid #e3e1da;border-radius:10px;padding:12px 14px}}
.city{{font-weight:600;font-size:16px;display:flex;justify-content:space-between}} .rk{{color:#8a8984;font-weight:400;font-size:12px}}
.pr{{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap;margin:4px 0}} .big{{font-size:24px;font-weight:600}}
.tag{{font-size:11px;border:1px solid #3d8b4f;color:#2d6b3b;border-radius:99px;padding:1px 8px}} .tag.no{{border-color:#c47f17;color:#8a5a10}}
.warn{{font-size:11px;color:#b3392b}} .meta{{font-size:13px}} .alt{{font-size:12px;color:#6b6a66;border-top:1px solid #eee;margin-top:6px;padding-top:6px;line-height:1.6}} .alt b{{color:#1f1e1d}}
.lk{{font-size:12px;margin-top:6px}}
.seg{{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0 10px}} .seg button{{font:inherit;font-size:13px;padding:6px 14px;border-radius:99px;border:1px solid #cfccc3;background:#fff;color:#1f1e1d;cursor:pointer}}
.seg button[aria-pressed="true"]{{background:#1f1e1d;color:#fff;border-color:#1f1e1d}} a{{color:#1f1e1d}} .foot{{font-size:11px;color:#8a8984;margin-top:20px;line-height:1.6}}
</style></head><body>
<h1>香港出發平機票</h1>
<p class="sub">Kiwi.com 查價時間：{e(d["checked_at"])}（每個工作日早上更新）。來回、直航、玩 3 至 5 晚，價錢已包稅同附加費（港幣）。</p>
<h2>日本</h2>
<div class="seg" role="tablist">
<button data-v="all" aria-pressed="true">全部</button><button data-v="bag" aria-pressed="false">只睇連寄艙行李</button><button data-v="nobag" aria-pressed="false">只睇唔連寄艙行李</button>
</div>
<div id="v-all"><p class="sub">大字係連 1 件寄艙行李嘅價錢；細字係唔連寄艙行李（只有手提）嘅價錢。</p><div class="grid">{"".join(jp_card(r) for r in d["japan"])}</div></div>
<div id="v-bag" hidden><p class="sub">已連 1 件寄艙行李，由平至貴。冇出現嘅城市即係 Kiwi 冇連行李嘅票價。</p><div class="grid">{"".join(one_card(r, "bag") for r in sorted([x for x in d["japan"] if x.get("bag")], key=lambda x: x["bag"]["price"]))}</div></div>
<div id="v-nobag" hidden><p class="sub">唔連寄艙行李（只有手提），由平至貴。要寄行李就要另外加錢。</p><div class="grid">{"".join(one_card(r, "nobag") for r in sorted([x for x in d["japan"] if x.get("nobag")], key=lambda x: x["nobag"]["price"]))}</div></div>
<h2>亞洲最平 10 個城市（連寄艙行李）</h2>
<div class="grid">{"".join(asia_card(i + 1, r) for i, r in enumerate(d["asia"]))}</div>
<p class="foot">價錢以查價時為準，隨時會變，訂票前請喺航空公司官網再核實。「兩張單程票」即去程同回程分開出票，去程延誤唔保障回程。AL 按星期一至五上班計，已扣香港公眾假期，出發日同回程日都計一整日。</p>
<script>
document.querySelectorAll('.seg button').forEach(function(b){{b.addEventListener('click',function(){{
document.querySelectorAll('.seg button').forEach(function(x){{x.setAttribute('aria-pressed',x===b?'true':'false')}});
['all','bag','nobag'].forEach(function(v){{document.getElementById('v-'+v).hidden=(v!==b.dataset.v)}});}})}});
</script>
</body></html>'''
open('index.html', 'w', encoding='utf-8').write(page)
print('index.html written')
