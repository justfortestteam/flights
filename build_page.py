"""Builds index.html from data.json. Run: python3 build_page.py
data.json shape:
{"checked_at": "2026-11-16 15:00",
 "japan": [{"city": "沖繩 Okinawa",
            "bag":   {"price": 2168, "depart": "2027-04-16", "return": "2027-04-20", "airline": "香港航空", "note": "", "link": "https://..."} or null,
            "nobag": {same fields} or null}],
 "asia":  [{"city": "上海 Shanghai", "price": 1375, "depart": "...", "return": "...", "airline": "...", "note": "", "link": "..."}],
 "hk_airlines": [{"city": "台北 Taipei", "options": {"CX": {"price": 1900, "depart": "...", "return": "...", "out": "CX488 08:00", "in": "CX469 22:25", "note": "", "link": "..."} or null, "HX": ..., "HB": ...}}],
 "world": [{"city": "倫敦 London", "price": 5268, "depart": "...", "return": "...", "airline": "...", "stops": "直航 or 經北京轉機", "note": "", "link": "..."}]}
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

def world_card(i, r):
    warn = f' <span class="warn">⚠ {e(r["note"])}</span>' if r.get('note') else ''
    n = (dt.date.fromisoformat(r["return"][:10]) - dt.date.fromisoformat(r["depart"][:10])).days
    return (f'<div class="card"><div class="city">{e(r["city"])}<span class="rk">#{i}</span></div>'
            f'<div class="pr"><span class="big">HK${r["price"]:,}</span><span class="tag">連寄艙行李</span>{warn}</div>'
            f'<div class="meta">{day(r["depart"])} → {day(r["return"])} · {n} 晚 · {al(r["depart"], r["return"])} 日 AL</div>'
            f'<div class="meta">{e(r["airline"])} · {e(r.get("stops"))}</div>'
            f'<div class="lk">{link(r.get("link"), "去 Kiwi.com 睇")}</div></div>')

AIRS = [("CX", "國泰"), ("HX", "香港航空"), ("HB", "大灣區航空"), ("UO", "HK Express")]

def hk_card(r):
    opts = r["options"]
    prices = [opts[c]["price"] for c, _ in AIRS if opts.get(c) and c != "UO"]
    best = min(prices) if prices else None
    rows = []
    for code, name in AIRS:
        m = opts.get(code)
        if not m:
            rows.append(f'<div class="al-row none"><span class="al-n">{name}</span><span class="al-p">Kiwi 冇呢個價</span></div>')
            continue
        hi = ' best' if m["price"] == best else ''
        n = (dt.date.fromisoformat(m["return"][:10]) - dt.date.fromisoformat(m["depart"][:10])).days
        note = f' · <span class="warn">{e(m["note"])}</span>' if m.get("note") else ''
        if code == "UO":
            hi = ' lcc'
            note += ' · <span class="warn">冇寄艙行李，要另加</span>'
        rows.append(f'<a class="al-row{hi}" href="{e(m["link"])}" target="_blank" rel="noopener"><span class="al-n">{name}</span>'
                    f'<span class="al-p">HK${m["price"]:,}</span>'
                    f'<span class="al-d">{day(m["depart"])} → {day(m["return"])} · {n} 晚 · {al(m["depart"], m["return"])} 日 AL{note}<br>去 {e(m["out"])} · 回 {e(m["in"])}</span></a>')
    return f'<div class="card"><div class="city">{e(r["city"])}</div>{"".join(rows)}</div>'

def asia_card(i, r):
    warn = f' <span class="warn">⚠ {e(r["note"])}</span>' if r.get('note') else ''
    return (f'<div class="card"><div class="city">{e(r["city"])}<span class="rk">#{i}</span></div>'
            f'<div class="pr"><span class="big">HK${r["price"]:,}</span><span class="tag">連寄艙行李</span>{warn}</div>'
            f'<div class="meta">{day(r["depart"])} → {day(r["return"])} · {al(r["depart"], r["return"])} 日 AL · {e(r["airline"])}</div>'
            f'<div class="lk">{link(r.get("link"), "去 Kiwi.com 睇")}</div></div>')

def calendar(d):
    import calendar as C
    trips = []
    def add(dep, ret, city, price, kind, lk, grp):
        a, b = dt.date.fromisoformat(dep[:10]), dt.date.fromisoformat(ret[:10])
        trips.append((a, b, price, city, kind, lk, grp))
    for r in d["japan"]:
        for k in ("bag", "nobag"):
            m = r.get(k)
            if m: add(m["depart"], m["return"], r["city"], m["price"], k, m.get("link"), "jp")
    for r in d["asia"]:
        add(r["depart"], r["return"], r["city"], r["price"], "bag", r.get("link"), "as")
    for r in d.get("world", []):
        add(r["depart"], r["return"], r["city"], r["price"], "bag", r.get("link"), "ww")
    if not trips: return '<p class="sub">冇資料。</p>'
    trips.sort(key=lambda t: (t[0], t[2]))
    first = min(t[0] for t in trips); last = max(t[1] for t in trips)
    y, mth = first.year, first.month
    out = []
    while (y, mth) <= (last.year, last.month):
        weeks = []
        for week in C.Calendar(firstweekday=6).monthdatescalendar(y, mth):
            ws, we = week[0], week[-1]
            days = ''.join(
                f'<div class="dn{" out" if x.month != mth else ""}{" hol" if (x.isoformat() in HOL or x.weekday() == 6) else ""}">{x.day}</div>'
                for x in week)
            bars = []
            for a, b, price, city, kind, lk, grp in trips:
                if b < ws or a > we: continue
                s0, s1 = max(a, ws), min(b, we)
                c0, c1 = (s0 - ws).days + 1, (s1 - ws).days + 2
                n = (b - a).days
                name = city.split(" ")[0]
                tagk = "連行李" if kind == "bag" else "手提"
                cont_l = '◀ ' if a < ws else ''
                cont_r = ' ▶' if b > we else ''
                label = (f'<b>{e(name)}</b> ${price:,} <i>{tagk}·{n}晚</i>' if a >= ws else f'<b>{e(name)}</b> <i>續</i>')
                tip = f'{city} HK${price:,}，{day(a.isoformat())} → {day(b.isoformat())}，{n} 晚，{tagk}'
                href = e(lk) if str(lk or '').startswith('https://') else '#'
                bars.append(f'<a class="bar {grp}{" nb" if kind != "bag" else ""}" style="grid-column:{c0}/{c1}" href="{href}" target="_blank" rel="noopener" title="{e(tip)}">{cont_l}{label}{cont_r}</a>')
            weeks.append(f'<div class="wk"><div class="days">{days}</div><div class="bars">{"".join(bars)}</div></div>')
        out.append(f'<h3>{y} 年 {mth} 月</h3><div class="calwrap"><div class="cal"><div class="hd"><div>日</div><div>一</div><div>二</div><div>三</div><div>四</div><div>五</div><div>六</div></div>{"".join(weeks)}</div></div>')
        mth += 1
        if mth == 13: y, mth = y + 1, 1
    return ''.join(out)

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
h3{{font-size:15px;margin:18px 0 6px}}
.calwrap{{overflow-x:auto}} .cal{{min-width:640px;background:#fff;border:1px solid #e3e1da;border-radius:8px;overflow:hidden}}
.hd,.days,.bars{{display:grid;grid-template-columns:repeat(7,1fr)}}
.hd div{{font-size:12px;color:#6b6a66;padding:4px 6px;background:#faf9f6;border-bottom:1px solid #e3e1da}}
.wk{{border-bottom:1px solid #eeece6;min-height:56px;padding-bottom:4px}} .wk:last-child{{border-bottom:0}}
.dn{{font-size:11px;color:#6b6a66;padding:3px 6px}} .dn.out{{color:#c9c7c0}} .dn.hol{{color:#b3392b;font-weight:600}}
.bars{{grid-auto-flow:row dense;gap:2px 0;padding:0 2px}}
.bar{{display:block;margin:0 2px;padding:2px 6px;border-radius:5px;text-decoration:none;color:#1f1e1d;font-size:11px;line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.bar.jp{{background:#d9ecdf}} .bar.as{{background:#dde2f2}} .bar.ww{{background:#f3e3cf}} .bar.nb{{background-image:repeating-linear-gradient(135deg,transparent 0 6px,rgba(255,255,255,.55) 6px 9px)}}
.bar b{{font-weight:600}} .bar i{{font-style:normal;color:#55544f}}
.promo{{margin:10px 0 14px;padding:10px 12px;border-radius:10px;background:#fff4e5;border:1px solid #f0b46a;font-size:13px;line-height:1.6}}
.al-row{{display:grid;grid-template-columns:80px auto;column-gap:8px;padding:6px 8px;margin-top:6px;border:1px solid #eeece6;border-radius:8px;text-decoration:none;color:#1f1e1d}}
.al-row.best{{border-color:#3d8b4f;background:#eef6f0}} .al-row.none{{color:#9a988f}} .al-row.lcc{{border-style:dashed;background:#faf8f3}}
.al-n{{font-size:13px;font-weight:600}} .al-p{{font-size:16px;font-weight:600;text-align:right}} .al-row.none .al-p{{font-size:12px;font-weight:400}}
.al-d{{grid-column:1/3;font-size:12px;color:#6b6a66;line-height:1.5}}
.legend{{display:inline-block;padding:1px 8px;border-radius:5px;font-size:11px}}
@media (max-width:600px){{
body{{padding:12px}} h1{{font-size:20px}} h2{{font-size:16px;margin-top:18px}} h3{{font-size:14px;margin:14px 0 4px}}
.sub{{font-size:12px}} .big{{font-size:20px}} .meta{{font-size:12px}} .city{{font-size:15px}} .tag,.warn{{font-size:10px}}
.grid{{grid-template-columns:1fr;gap:8px}} .card{{padding:10px 12px}}
.seg button{{font-size:12px;padding:5px 10px}}
.calwrap{{overflow:visible}} .cal{{min-width:0}}
.hd div{{font-size:10px;padding:3px 2px;text-align:center}} .dn{{font-size:10px;padding:2px 3px}}
.wk{{min-height:40px;padding-bottom:3px}}
.bar{{font-size:9px;padding:1px 3px;margin:0 1px;border-radius:3px;line-height:1.35}} .bar i{{display:none}}
.legend{{font-size:10px}}
}}
.seg button[aria-pressed="true"]{{background:#1f1e1d;color:#fff;border-color:#1f1e1d}} a{{color:#1f1e1d}} .foot{{font-size:11px;color:#8a8984;margin-top:20px;line-height:1.6}}
</style></head><body>
<h1>香港出發平機票</h1>
<p class="sub">Kiwi.com 查價時間：{e(d["checked_at"])}（每個工作日早上更新）。來回、直航；星期四至六出發、星期日至二返，一定包一個週末，玩 2 至 4 晚（最多 3 日 AL）；價錢已包稅同附加費（港幣）。</p>
{'<div class="promo"><b>限時：HK Express 大專生優惠</b>（20/11 10:00 至 24/11 23:45 預訂）<br>出發 3/12/2026 至 30/6/2027。單程未連稅：$88 起；沖繩、濟州、曼谷、布吉 $118 起（連 20kg 行李 $268）；東京成田、名古屋、小松、高松、首爾、釜山 $198 起（連 20kg 行李 $348）。訂單入面只要有一位合資格大專生，同行朋友都用同一個價，但要一齊出發。只可以喺 HK Express 官網學生專頁訂，下面嘅價錢冇計呢個優惠。</div>' if d["checked_at"][:10] <= "2026-11-24" else ''}
<div class="seg view" role="tablist">
<button data-view="cards" aria-pressed="true">卡片</button><button data-view="cal" aria-pressed="false">月曆</button><button data-view="hk" aria-pressed="false">Local Airline</button>
</div>
<div id="view-cal" hidden>
<p class="sub">每條橫條由出發日拉到回程日。<span class="legend bar jp">日本</span> <span class="legend bar as">亞洲其他</span> <span class="legend bar ww">亞洲以外</span> <span class="legend bar jp nb">斜紋 = 唔連寄艙行李</span>；紅字日子係星期日或者香港公眾假期；撳橫條去 Kiwi.com 睇。</p>
{calendar(d)}
</div>
<div id="view-hk" hidden>
<h2>Local Airline：國泰、香港航空、大灣區航空、HK Express</h2>
<p class="sub">日本、台灣、曼谷、首爾；直航來回、包一個週末、玩 2 至 4 晚。國泰、香港航空、大灣區航空嘅價錢已連 1 件寄艙行李，綠色係三間之中最平。HK Express 嘅價錢冇寄艙行李（只有 1 件隨身物品），行李要另加，所以唔同其他三間直接比較。撳一行去 Kiwi.com 睇。</p>
<div class="grid">{"".join(hk_card(r) for r in sorted(d.get("hk_airlines", []), key=lambda r: (min([o["price"] for k, o in r["options"].items() if o and k != "UO"] or [99999]), min([o["price"] for o in r["options"].values() if o] or [99999]))))}</div>
</div>
<div id="view-cards">
<h2>日本</h2>
<div class="seg jpseg" role="tablist">
<button data-v="all" aria-pressed="true">全部</button><button data-v="bag" aria-pressed="false">只睇連寄艙行李</button><button data-v="nobag" aria-pressed="false">只睇唔連寄艙行李</button>
</div>
<div id="v-all"><p class="sub">大字係連 1 件寄艙行李嘅價錢；細字係唔連寄艙行李（只有手提）嘅價錢。</p><div class="grid">{"".join(jp_card(r) for r in d["japan"])}</div></div>
<div id="v-bag" hidden><p class="sub">已連 1 件寄艙行李，由平至貴。冇出現嘅城市即係 Kiwi 冇連行李嘅票價。</p><div class="grid">{"".join(one_card(r, "bag") for r in sorted([x for x in d["japan"] if x.get("bag")], key=lambda x: x["bag"]["price"]))}</div></div>
<div id="v-nobag" hidden><p class="sub">唔連寄艙行李（只有手提），由平至貴。要寄行李就要另外加錢。</p><div class="grid">{"".join(one_card(r, "nobag") for r in sorted([x for x in d["japan"] if x.get("nobag")], key=lambda x: x["nobag"]["price"]))}</div></div>
<h2>亞洲最平 10 個城市（連寄艙行李）</h2>
<div class="grid">{"".join(asia_card(i + 1, r) for i, r in enumerate(d["asia"]))}</div>
<h2>亞洲以外最平 10 個城市（連寄艙行李）</h2>
<p class="sub">歐洲、澳紐、美加等；星期五或六出發、下個星期日或一返，跨兩個週末，玩 8 至 10 晚；最多轉機一次，同一張票（除咗標明「兩張單程票」）。</p>
<div class="grid">{"".join(world_card(i + 1, r) for i, r in enumerate(d.get("world", [])))}</div>
</div>
<p class="foot">價錢以查價時為準，隨時會變，訂票前請喺航空公司官網再核實。「兩張單程票」即去程同回程分開出票，去程延誤唔保障回程。AL 按星期一至五上班計，已扣香港公眾假期，出發日同回程日都計一整日。</p>
<script>
document.querySelectorAll('.jpseg button').forEach(function(b){{b.addEventListener('click',function(){{
document.querySelectorAll('.jpseg button').forEach(function(x){{x.setAttribute('aria-pressed',x===b?'true':'false')}});
['all','bag','nobag'].forEach(function(v){{document.getElementById('v-'+v).hidden=(v!==b.dataset.v)}});}})}});
document.querySelectorAll('.view button').forEach(function(b){{b.addEventListener('click',function(){{
document.querySelectorAll('.view button').forEach(function(x){{x.setAttribute('aria-pressed',x===b?'true':'false')}});
['cards','cal','hk'].forEach(function(v){{document.getElementById('view-'+v).hidden=b.dataset.view!==v}});}})}});
</script>
</body></html>'''
open('index.html', 'w', encoding='utf-8').write(page)
print('index.html written')
