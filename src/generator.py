#!/usr/bin/env python3
"""Generate the static Arabic dashboard from data/indicators.json."""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "indicators.json"
OUTPUT_FILE = ROOT / "output" / "index.html"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_card(item: dict) -> str:
    value = item.get("value")
    available = value is not None and str(value).strip() != ""
    formatted = esc(value) if available else "—"
    unit = esc(item.get("unit", ""))
    period = esc(item.get("period") or "الفترة غير محددة")
    source = item.get("source_url", "")
    source_html = (f'<a class="source-link" href="{esc(source)}" target="_blank" rel="noopener noreferrer">فتح المصدر ↗</a>'
                   if source.startswith("https://") else '<span class="source-link muted">بانتظار توثيق المصدر</span>')
    label = "بيانات موثقة" if available and item.get("reference") else "بانتظار بيانات موثقة"
    return f'''<article class="card" data-search="{esc(item.get('title',''))} {esc(item.get('description',''))}">
      <div class="card-top"><span class="icon">{esc(item.get('icon','◈'))}</span><span class="status"><i></i>{esc(label)}</span></div>
      <h3>{esc(item.get('title','مؤشر'))}</h3><p class="description">{esc(item.get('description',''))}</p>
      <div class="metric"><strong>{formatted}</strong><span>{unit}</span></div>
      <div class="meta"><span>الفترة: {period}</span><span>{esc(item.get('reference') or 'لا توجد قيمة منشورة بعد')}</span></div>
      {source_html}
    </article>'''


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    cards = "\n".join(render_card(item) for item in data.get("indicators", []))
    updated = esc(data.get("updated_at", "لم تُحدّث البيانات بعد"))
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    page = f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0c1714">
<meta name="description" content="لوحة مستقلة لمتابعة مؤشرات المعيشة والعمل والسكن في المغرب مع توثيق المصادر والمنهجية.">
<title>مؤشر المواطن المغربي</title>
<style>
:root{{--bg:#0c1714;--panel:#13221d;--panel2:#182b24;--text:#f3f5ed;--muted:#a8b7ac;--line:#294137;--mint:#a6e3bd;--sand:#e8c98e;--red:#ec7e74}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 85% -10%,#204335 0,transparent 38%),var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.7}}
.wrap{{width:min(1120px,calc(100% - 36px));margin:auto}}header{{padding:30px 0;border-bottom:1px solid var(--line)}}.brand{{display:flex;align-items:center;gap:12px;font-weight:800;letter-spacing:.01em}}.flag{{width:30px;height:20px;background:#c83e49;border-radius:4px;display:grid;place-items:center;color:#fff;font-size:13px}}.brand small{{display:block;color:var(--muted);font-weight:500;font-size:12px}}.hero{{padding:70px 0 45px;max-width:800px}}.eyebrow{{color:var(--mint);font-size:13px;font-weight:700;letter-spacing:.08em}}h1{{font-size:clamp(34px,6vw,62px);line-height:1.15;margin:12px 0 18px;letter-spacing:-.04em}}.lead{{color:#c4d0c6;font-size:18px;max-width:680px;margin:0}}.notice{{display:flex;gap:12px;align-items:flex-start;background:#30291c;border:1px solid #615337;border-radius:14px;padding:15px 18px;color:#f0dfb8;margin:20px 0 28px;font-size:14px}}.notice b{{color:var(--sand)}}.toolbar{{display:flex;justify-content:space-between;gap:14px;align-items:center;margin:30px 0 18px}}.toolbar h2{{font-size:22px;margin:0}}.search{{background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:11px 14px;width:min(310px,100%);font:inherit;outline:none}}.search:focus{{border-color:var(--mint)}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}}.card{{padding:20px;background:linear-gradient(145deg,#182b24,#12201b);border:1px solid var(--line);border-radius:16px;min-height:260px;display:flex;flex-direction:column}}.card-top{{display:flex;justify-content:space-between;align-items:center}}.icon{{width:38px;height:38px;border-radius:11px;background:#244136;color:var(--mint);display:grid;place-items:center;font-size:18px}}.status{{font-size:11px;color:var(--sand);display:flex;align-items:center;gap:6px}}.status i{{width:7px;height:7px;border-radius:99px;background:var(--sand)}}.card h3{{margin:17px 0 4px;font-size:17px}}.description{{color:var(--muted);font-size:13px;margin:0;min-height:44px}}.metric{{display:flex;align-items:baseline;gap:8px;margin:13px 0 8px}}.metric strong{{font-size:34px;line-height:1;color:#e9eee8}}.metric span{{color:var(--muted);font-size:12px}}.meta{{border-top:1px solid var(--line);padding-top:10px;margin-top:auto;color:#8fa196;font-size:11px;display:flex;justify-content:space-between;gap:8px}}.source-link{{color:var(--mint);font-size:12px;text-decoration:none;margin-top:9px;width:max-content}}.source-link:hover{{text-decoration:underline}}.muted{{color:#89988e}}.empty{{display:none;color:var(--muted);padding:20px}}.method{{margin:58px 0 36px;display:grid;grid-template-columns:1fr 1fr;gap:18px}}.method article{{background:#111f1a;border:1px solid var(--line);border-radius:14px;padding:20px}}.method h2{{font-size:18px;margin:0 0 8px}}.method p,.method li{{font-size:13px;color:var(--muted)}}.method ul{{padding-right:20px;margin-bottom:0}}.sources{{display:flex;flex-wrap:wrap;gap:9px;margin-top:12px}}.sources a{{border:1px solid var(--line);color:#cbd8ce;padding:6px 10px;border-radius:99px;text-decoration:none;font-size:12px}}footer{{border-top:1px solid var(--line);padding:18px 0 28px;color:#84958a;font-size:12px;display:flex;justify-content:space-between;gap:12px}}@media(max-width:850px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}@media(max-width:580px){{.hero{{padding-top:48px}}.grid,.method{{grid-template-columns:1fr}}.toolbar{{align-items:stretch;flex-direction:column}}.search{{width:100%}}footer{{flex-direction:column}}}}
</style>
</head><body>
<header><div class="wrap brand"><span class="flag">✦</span><div>مؤشر المواطن المغربي<small>قراءة مستقلة للواقع بالأرقام والمصادر</small></div></div></header>
<main class="wrap"><section class="hero"><div class="eyebrow">المغرب · مؤشرات قابلة للتحقق</div><h1>كيف تتغير<br>معيشة المواطن؟</h1><p class="lead">لوحة أولية لمتابعة القدرة الشرائية والعمل والسكن والتنافسية، مع إظهار مصدر كل رقم وفترته بدل الاكتفاء بالعناوين.</p></section>
<div class="notice"><span>ⓘ</span><div><b>نسخة أولية — لا تعرض بيانات رسمية بعد.</b> لم تُملأ القيم حتى الآن لتجنب نشر أرقام غير متحققة. ستظهر المؤشرات بعد إدخال سلسلة موثقة ومراجعة تعريفها وفترتها.</div></div>
<section><div class="toolbar"><h2>المؤشرات الرئيسية</h2><input id="search" class="search" type="search" placeholder="ابحث عن مؤشر…" aria-label="ابحث عن مؤشر"></div><div class="grid">{cards}</div><p id="empty" class="empty">لا توجد مؤشرات مطابقة لبحثك.</p></section>
<section class="method"><article><h2>منهجية العرض</h2><p>لكل مؤشر قيمة وفترة مرجعية ووحدة قياس ورابط مصدر مباشر. لا تُعرض القيمة بوصفها موثقة ما لم يتوفر مرجع يمكن للقارئ فتحه. المقارنات الدولية تحتاج إلى توحيد التعريفات والفترات قبل نشرها.</p><ul><li>القيمة الفارغة تعني أن البيانات لم تُراجع وتُعتمد بعد.</li><li>تاريخ التحديث الحالي للبيانات: {updated}.</li><li>المشروع مستقل ولا يمثل الجهات المذكورة.</li></ul></article>
<article><h2>مصادر للرجوع والتحقق</h2><p>تُستخدم هذه البوابات للبحث عن السلاسل الأصلية، ولا يعني إدراجها أن الأرقام قد جُمعت أو تحققت بعد.</p><div class="sources"><a href="https://www.hcp.ma/" target="_blank" rel="noopener">المندوبية السامية للتخطيط</a><a href="https://www.bkam.ma/" target="_blank" rel="noopener">بنك المغرب</a><a href="https://data.worldbank.org/country/morocco" target="_blank" rel="noopener">البنك الدولي</a><a href="https://www.imf.org/en/Countries/MAR" target="_blank" rel="noopener">صندوق النقد الدولي</a></div></article></section></main>
<footer class="wrap"><span>مؤشر المواطن المغربي · مشروع مفتوح المصدر</span><span>بُنيت الصفحة من بيانات المشروع المحلية · لا تتبع المستخدم</span></footer>
<script>const q=document.getElementById('search');q.addEventListener('input',()=>{{const s=q.value.trim().toLocaleLowerCase('ar');let n=0;document.querySelectorAll('.card').forEach(c=>{{const ok=c.dataset.search.toLocaleLowerCase('ar').includes(s);c.style.display=ok?'flex':'none';if(ok)n++}});document.getElementById('empty').style.display=n?'none':'block'}});</script>
</body></html>'''
    OUTPUT_FILE.write_text(page, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE.relative_to(ROOT)} ({OUTPUT_FILE.stat().st_size} bytes)")

if __name__ == "__main__":
    main()
