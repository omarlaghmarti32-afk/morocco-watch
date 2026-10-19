#!/usr/bin/env python3
"""Generate the Arabic static dashboard from data/indicators.json."""
from __future__ import annotations

import html
import json
import math
import subprocess
from datetime import datetime, timezone
from email.utils import format_datetime
from hashlib import sha256
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape, quoteattr

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "indicators.json"
OUTPUT_FILE = ROOT / "output" / "index.html"
SITE_URL = "https://omarlaghmarti32-afk.github.io/morocco-watch/"
REPOSITORY_URL = "https://github.com/omarlaghmarti32-afk/morocco-watch"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def normalized_history(item: dict) -> list[dict]:
    """Return valid period/value points, preserving source order."""
    points: list[dict] = []
    for point in item.get("history", []):
        if not isinstance(point, dict):
            continue
        period = str(point.get("period", "")).strip()
        try:
            value = float(point.get("value"))
        except (TypeError, ValueError):
            continue
        if period and math.isfinite(value):
            points.append({"period": period, "value": value})
    return points


def render_card(item: dict) -> str:
    value = item.get("value")
    available = value is not None and str(value).strip() != ""
    formatted = esc(value) if available else "—"
    unit = esc(item.get("unit", ""))
    period = esc(item.get("period") or "الفترة غير محددة")
    source = item.get("source_url", "")
    source_html = (
        f'<a class="source-link" href="{esc(source)}" target="_blank" '
        'rel="noopener noreferrer">فتح المصدر ↗</a>'
        if source.startswith("https://")
        else '<span class="source-link muted">بانتظار توثيق المصدر</span>'
    )
    label = "بيانات موثقة" if available and item.get("reference") else "بانتظار بيانات موثقة"
    return f'''<article class="card" data-search="{esc(item.get('title', ''))} {esc(item.get('description', ''))}">
      <div class="card-top"><span class="icon">{esc(item.get('icon', '◈'))}</span><span class="status"><i></i>{esc(label)}</span></div>
      <h3>{esc(item.get('title', 'مؤشر'))}</h3><p class="description">{esc(item.get('description', ''))}</p>
      <div class="metric"><strong>{formatted}</strong><span>{unit}</span></div>
      <div class="meta"><span>الفترة: {period}</span><span>{esc(item.get('reference') or 'لا توجد قيمة منشورة بعد')}</span></div>
      {source_html}
    </article>'''


def render_chart_card(item: dict, canvas_id: str, title: str, unit: str) -> tuple[str, dict]:
    points = normalized_history(item)
    safe_title = esc(title)
    source_url = item.get("source_url", "")
    reference = esc(item.get("reference") or "المصدر الرسمي")
    source_html = (
        f'<a class="source-link chart-source" href="{esc(source_url)}" target="_blank" '
        f'rel="noopener noreferrer">المصدر: {reference} ↗</a>'
        if source_url.startswith("https://")
        else '<span class="source-link muted chart-source">بانتظار توثيق المصدر</span>'
    )
    empty_message = (
        "لا توجد نقاط زمنية موثقة بعد. أضف الفترة والقيمة والمصدر في ملف البيانات."
        if not points
        else ""
    )
    card = f'''<article class="chart-card">
      <div class="chart-heading"><div><h3>{safe_title}</h3><p>سلسلة زمنية من البيانات الموثقة</p></div><span class="chart-unit">{esc(unit)}</span></div>
      <div class="chart-stage">
        <p class="chart-empty" id="{canvas_id}-empty">{empty_message}</p>
        <canvas id="{canvas_id}" role="img" aria-label="{safe_title}" hidden></canvas>
      </div>
      {source_html}
    </article>'''
    payload = {"title": title, "unit": unit, "points": points}
    return card, payload


def git_stdout(*args: str) -> str:
    """Run a read-only Git command and return stdout, or an empty string."""
    try:
        result = subprocess.run(
            ["git", *args], cwd=ROOT, text=True, capture_output=True, check=False
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def parse_datetime(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        parsed = datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def data_at_ref(ref: str) -> dict | None:
    raw = git_stdout("show", f"{ref}:data/indicators.json")
    if not raw:
        return None
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def has_observations(item: dict | None) -> bool:
    if not item:
        return False
    if item.get("value") is not None:
        return True
    return any(
        isinstance(point, dict) and point.get("value") is not None
        for point in item.get("history", [])
    )


def latest_metric(item: dict | None) -> dict | None:
    if not item:
        return None
    value = item.get("value")
    period = item.get("period")
    if value is None and item.get("history"):
        point = item["history"][-1]
        if isinstance(point, dict):
            value = point.get("value")
            period = point.get("period")
    if value is None:
        return None
    return {"value": value, "unit": item.get("unit", ""), "period": period}


def metric_text(metric: dict | None) -> str:
    if not metric:
        return "لا توجد قيمة حالية موثقة"
    period = f" ({metric['period']})" if metric.get("period") else ""
    unit = f" {metric['unit']}" if metric.get("unit") else ""
    return f"{metric['value']}{unit}{period}"


def changed_indicators(previous: dict, current: dict) -> list[dict]:
    old_rows = {
        str(item.get("id")): item
        for item in previous.get("indicators", [])
        if isinstance(item, dict) and item.get("id")
    }
    new_rows = {
        str(item.get("id")): item
        for item in current.get("indicators", [])
        if isinstance(item, dict) and item.get("id")
    }
    changes: list[dict] = []
    for indicator_id in sorted(set(old_rows) | set(new_rows)):
        old = old_rows.get(indicator_id)
        new = new_rows.get(indicator_id)
        if old == new or not (has_observations(old) or has_observations(new)):
            continue
        display = new or old or {}
        before = latest_metric(old)
        after = latest_metric(new)
        title = str(display.get("title", indicator_id))
        if before and after and before.get("value") != after.get("value"):
            summary = f"{title}: من {metric_text(before)} إلى {metric_text(after)}"
        else:
            summary = f"{title}: {metric_text(after or before)}"
        changes.append({
            "id": indicator_id,
            "title": title,
            "summary": summary,
            "previous": before,
            "current": after,
            "source_url": display.get("source_url"),
            "reference": display.get("reference"),
        })
    return changes


def change_entries(data: dict, limit: int = 25) -> list[dict]:
    """Build a stable, newest-first changelog from commits touching the data file."""
    log = git_stdout(
        "log", "-n", "200", "--format=%H%x1f%cI%x1f%s", "--",
        str(DATA_FILE.relative_to(ROOT)),
    )
    entries: list[dict] = []
    for line in log.splitlines():
        parts = line.split("\x1f", 2)
        if len(parts) != 3:
            continue
        commit, committed_at, subject = parts
        current = data_at_ref(commit)
        previous = data_at_ref(f"{commit}^")
        if current is None:
            continue
        changes = changed_indicators(previous or {}, current)
        if not changes:
            continue
        names = [change["title"] for change in changes]
        title = "تحديث بيانات المؤشرات: " + "، ".join(names[:4])
        if len(names) > 4:
            title += f"، ومؤشرات أخرى ({len(names) - 4})"
        entries.append({
            "id": commit,
            "published_at": parse_datetime(committed_at).isoformat(),
            "title": title,
            "summary": "؛ ".join(change["summary"] for change in changes),
            "commit_message": subject,
            "url": f"{REPOSITORY_URL}/commit/{commit}",
            "changes": changes,
        })
        if len(entries) >= limit:
            break

    if entries:
        return entries

    # Fallback for source archives or shallow clones without usable Git history.
    changes = []
    for item in data.get("indicators", []):
        if not isinstance(item, dict) or not has_observations(item):
            continue
        changes.append({
            "id": item.get("id"),
            "title": item.get("title", item.get("id", "مؤشر")),
            "summary": f"{item.get('title', 'مؤشر')}: {metric_text(latest_metric(item))}",
            "previous": None,
            "current": latest_metric(item),
            "source_url": item.get("source_url"),
            "reference": item.get("reference"),
        })
    snapshot = json.dumps(data, ensure_ascii=False, sort_keys=True, allow_nan=False)
    snapshot_id = sha256(snapshot.encode("utf-8")).hexdigest()[:16]
    updated_at = str(data.get("updated_at", ""))
    published_at = parse_datetime(updated_at or datetime.now(timezone.utc).isoformat())
    return [{
        "id": f"snapshot-{snapshot_id}",
        "published_at": published_at.isoformat(),
        "title": "لقطة البيانات الحالية",
        "summary": "؛ ".join(change["summary"] for change in changes)
        or "لا توجد قيم مؤشرات موثقة حالياً.",
        "commit_message": "",
        "url": f"{SITE_URL}api/v1/indicators.json",
        "changes": changes,
    }]


def render_rss(entries: list[dict]) -> str:
    items = []
    for entry in entries:
        pub_date = format_datetime(parse_datetime(entry["published_at"]))
        items.append(
            "<item>"
            f"<title>{xml_escape(entry['title'])}</title>"
            f"<link>{xml_escape(entry['url'])}</link>"
            f"<guid isPermaLink=\"false\">morocco-watch:{xml_escape(entry['id'])}</guid>"
            f"<pubDate>{xml_escape(pub_date)}</pubDate>"
            f"<description>{xml_escape(entry['summary'])}</description>"
            "</item>"
        )
    last_build = format_datetime(parse_datetime(entries[0]["published_at"]))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">'
        "<channel>"
        "<title>تحديثات مؤشرات المواطن المغربي</title>"
        f"<link>{xml_escape(SITE_URL)}</link>"
        "<description>سجل تحديثات البيانات الرسمية لمؤشرات المغرب.</description>"
        "<language>ar</language>"
        f"<atom:link href={quoteattr(SITE_URL + 'feed.xml')} rel=\"self\" type=\"application/rss+xml\"/>"
        f"<lastBuildDate>{xml_escape(last_build)}</lastBuildDate>"
        + "".join(items)
        + "</channel></rss>\n"
    )


def render_atom(entries: list[dict]) -> str:
    feed_id = SITE_URL + "atom.xml"
    items = []
    for entry in entries:
        published = parse_datetime(entry["published_at"]).isoformat().replace("+00:00", "Z")
        entry_id = f"urn:morocco-watch:update:{entry['id']}"
        items.append(
            "<entry>"
            f"<id>{xml_escape(entry_id)}</id>"
            f"<title>{xml_escape(entry['title'])}</title>"
            f"<updated>{xml_escape(published)}</updated>"
            f"<link href={quoteattr(entry['url'])} rel=\"alternate\"/>"
            f"<summary>{xml_escape(entry['summary'])}</summary>"
            "</entry>"
        )
    latest = parse_datetime(entries[0]["published_at"]).isoformat().replace("+00:00", "Z")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="ar">'
        f"<id>{xml_escape(feed_id)}</id>"
        "<title>تحديثات مؤشرات المواطن المغربي</title>"
        f"<updated>{xml_escape(latest)}</updated>"
        f"<link href={quoteattr(feed_id)} rel=\"self\" type=\"application/atom+xml\"/>"
        f"<link href={quoteattr(SITE_URL)} rel=\"alternate\" type=\"text/html\"/>"
        "<subtitle>سجل تحديثات البيانات الرسمية لمؤشرات المغرب.</subtitle>"
        + "".join(items)
        + "</feed>\n"
    )


def render_changelog_page(entries: list[dict]) -> str:
    cards = []
    for entry in entries:
        changed_rows = []
        for change in entry.get("changes", []):
            current_text = metric_text(change.get("current"))
            previous = change.get("previous")
            detail = (
                f"من {metric_text(previous)} إلى {current_text}"
                if previous and previous.get("value") != (change.get("current") or {}).get("value")
                else current_text
            )
            source = change.get("source_url") or ""
            source_html = (
                f'<a href="{esc(source)}" rel="noopener noreferrer">المصدر</a>'
                if source.startswith("https://") else ""
            )
            changed_rows.append(
                f"<li><strong>{esc(change.get('title', 'مؤشر'))}</strong>: "
                f"{esc(detail)} {source_html}</li>"
            )
        commit = entry.get("url", "")
        commit_html = (
            f'<a href="{esc(commit)}" rel="noopener noreferrer">تفاصيل الالتزام</a>'
            if commit.startswith("https://github.com/") else ""
        )
        cards.append(
            '<article class="entry">'
            f"<time datetime=\"{esc(entry['published_at'])}\">{esc(entry['published_at'][:10])}</time>"
            f"<h2>{esc(entry['title'])}</h2><p>{esc(entry['summary'])}</p>"
            f"<ul>{''.join(changed_rows)}</ul>"
            f"<small>{esc(entry.get('commit_message', ''))} {commit_html}</small>"
            "</article>"
        )
    return f'''<!doctype html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>سجل تغييرات المؤشرات | مؤشر المواطن المغربي</title>
<link rel="alternate" type="application/rss+xml" title="RSS" href="../feed.xml">
<link rel="alternate" type="application/atom+xml" title="Atom" href="../atom.xml">
<style>body{{margin:0;background:#0c1714;color:#f3f5ed;font:16px/1.8 system-ui,sans-serif}}main{{width:min(900px,calc(100% - 32px));margin:40px auto}}a{{color:#a6e3bd}}.top{{display:flex;gap:16px;flex-wrap:wrap}}.entry{{border:1px solid #294137;background:#13221d;border-radius:14px;padding:20px;margin:16px 0}}time,small{{color:#a8b7ac}}h1{{margin-bottom:4px}}h2{{margin:6px 0}}ul{{padding-right:22px}}</style></head>
<body><main><p><a href="../">العودة إلى المؤشرات</a></p><h1>سجل تغييرات المؤشرات</h1>
<p>يُنشأ السجل من التزامات Git التي غيّرت بيانات المؤشرات. اشترك عبر <span class="top"><a href="../feed.xml">RSS</a><a href="../atom.xml">Atom</a><a href="../api/v1/changelog.json">JSON</a></span>.</p>
{''.join(cards) if cards else '<p>لا توجد تغييرات موثقة بعد.</p>'}</main></body></html>'''


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    indicators = data.get("indicators", [])
    by_id = {item.get("id"): item for item in indicators}
    cards = "\n".join(render_card(item) for item in indicators)

    chart_specs = [
        ("purchasing-power", "power-chart", "تطور القدرة الشرائية للأسر", "نقطة تحسّن"),
        ("unemployment-national", "unemployment-chart", "تطور معدل البطالة الوطني", "%"),
        ("youth-unemployment", "youth-chart", "تطور بطالة الشباب (15–24 سنة)", "%"),
    ]
    chart_cards: list[str] = []
    chart_payload: dict[str, dict] = {}
    for indicator_id, canvas_id, title, unit in chart_specs:
        item = by_id.get(indicator_id, {})
        card, payload = render_chart_card(item, canvas_id, title, unit)
        chart_cards.append(card)
        chart_payload[canvas_id] = payload

    chart_json = json.dumps(chart_payload, ensure_ascii=False, allow_nan=False).replace("</", "<\\/")
    updated = esc(data.get("updated_at", "لم تُحدّث البيانات بعد"))

    css = r'''
:root{--bg:#0c1714;--panel:#13221d;--text:#f3f5ed;--muted:#a8b7ac;--line:#294137;--mint:#a6e3bd;--sand:#e8c98e}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 85% -10%,#204335 0,transparent 38%),var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",sans-serif;line-height:1.7}
.wrap{width:min(1120px,calc(100% - 36px));margin:auto}header{padding:30px 0;border-bottom:1px solid var(--line)}.brand{display:flex;align-items:center;gap:12px;font-weight:800}.flag{width:30px;height:20px;background:#c83e49;border-radius:4px;display:grid;place-items:center;color:#fff;font-size:13px}.brand small{display:block;color:var(--muted);font-weight:500;font-size:12px}
.hero{padding:70px 0 45px;max-width:800px}.eyebrow{color:var(--mint);font-size:13px;font-weight:700;letter-spacing:.08em}h1{font-size:clamp(34px,6vw,62px);line-height:1.15;margin:12px 0 18px;letter-spacing:-.04em}.lead{color:#c4d0c6;font-size:18px;max-width:680px;margin:0}
.notice{display:flex;gap:12px;align-items:flex-start;background:#30291c;border:1px solid #615337;border-radius:14px;padding:15px 18px;color:#f0dfb8;margin:20px 0 28px;font-size:14px}.notice b{color:var(--sand)}
.toolbar{display:flex;justify-content:space-between;gap:14px;align-items:center;margin:30px 0 18px}.toolbar h2{font-size:22px;margin:0}.search{background:var(--panel);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:11px 14px;width:min(310px,100%);font:inherit;outline:none}.search:focus{border-color:var(--mint)}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.card{padding:20px;background:linear-gradient(145deg,#182b24,#12201b);border:1px solid var(--line);border-radius:16px;min-height:260px;display:flex;flex-direction:column}.card-top{display:flex;justify-content:space-between;align-items:center}.icon{width:38px;height:38px;border-radius:11px;background:#244136;color:var(--mint);display:grid;place-items:center;font-size:18px}.status{font-size:11px;color:var(--sand);display:flex;align-items:center;gap:6px}.status i{width:7px;height:7px;border-radius:99px;background:var(--sand)}.card h3{margin:17px 0 4px;font-size:17px}.description{color:var(--muted);font-size:13px;margin:0;min-height:44px}.metric{display:flex;align-items:baseline;gap:8px;margin:13px 0 8px}.metric strong{font-size:34px;line-height:1;color:#e9eee8}.metric span{color:var(--muted);font-size:12px}.meta{border-top:1px solid var(--line);padding-top:10px;margin-top:auto;color:#8fa196;font-size:11px;display:flex;justify-content:space-between;gap:8px}.source-link{color:var(--mint);font-size:12px;text-decoration:none;margin-top:9px;width:max-content}.source-link:hover{text-decoration:underline}.muted{color:#89988e}.empty{display:none;color:var(--muted);padding:20px}
.trends{margin:56px 0 30px}.section-intro{margin-bottom:18px}.section-intro h2{font-size:22px;margin:0}.section-intro p{color:var(--muted);font-size:13px;margin:4px 0}.chart-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.chart-card{background:linear-gradient(145deg,#182b24,#12201b);border:1px solid var(--line);border-radius:16px;padding:20px;min-width:0}.chart-heading{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:10px}.chart-heading h3{font-size:17px;margin:0}.chart-heading p{color:var(--muted);font-size:12px;margin:3px 0 0}.chart-unit{font-size:11px;color:var(--mint);border:1px solid var(--line);padding:2px 9px;border-radius:20px;white-space:nowrap}.chart-stage{height:260px;position:relative;display:grid;place-items:center}.chart-stage canvas{width:100%!important;height:100%!important}.chart-empty{color:var(--muted);font-size:13px;text-align:center;max-width:330px;margin:0}.chart-empty[hidden],canvas[hidden]{display:none!important}
.method{margin:58px 0 36px;display:grid;grid-template-columns:1fr 1fr;gap:18px}.method article{background:#111f1a;border:1px solid var(--line);border-radius:14px;padding:20px}.method h2{font-size:18px;margin:0 0 8px}.method p,.method li{font-size:13px;color:var(--muted)}.method ul{padding-right:20px;margin-bottom:0}.sources{display:flex;flex-wrap:wrap;gap:9px;margin-top:12px}.sources a{border:1px solid var(--line);color:#cbd8ce;padding:6px 10px;border-radius:99px;text-decoration:none;font-size:12px}footer{border-top:1px solid var(--line);padding:18px 0 28px;color:#84958a;font-size:12px;display:flex;justify-content:space-between;gap:12px}
@media(max-width:850px){.grid{grid-template-columns:repeat(2,1fr)}.chart-grid{grid-template-columns:1fr}}@media(max-width:580px){.hero{padding-top:48px}.grid,.method{grid-template-columns:1fr}.toolbar{align-items:stretch;flex-direction:column}.search{width:100%}footer{flex-direction:column}.chart-card{padding:16px}.chart-stage{height:230px}}
'''

    script = r'''
const q=document.getElementById('search');
q.addEventListener('input',()=>{const s=q.value.trim().toLocaleLowerCase('ar');let n=0;document.querySelectorAll('.card').forEach(c=>{const ok=c.dataset.search.toLocaleLowerCase('ar').includes(s);c.style.display=ok?'flex':'none';if(ok)n++});document.getElementById('empty').style.display=n?'none':'block'});
const trendData=__TREND_DATA__;
const palette={"power-chart":{"line":"#a6e3bd","fill":"rgba(166,227,189,.12)"},"unemployment-chart":{"line":"#e8c98e","fill":"rgba(232,201,142,.12)"},"youth-chart":{"line":"#df9c91","fill":"rgba(223,156,145,.12)"}};
for(const [id,series] of Object.entries(trendData)){
  const canvas=document.getElementById(id),empty=document.getElementById(`${id}-empty`);
  if(!series.points.length)continue;
  if(typeof Chart==='undefined'){empty.textContent='تعذر تحميل مكتبة الرسم البياني. تحقق من الاتصال بالإنترنت.';continue;}
  empty.hidden=true;canvas.hidden=false;
  const colors=palette[id];
  new Chart(canvas,{type:'line',data:{labels:series.points.map(p=>p.period),datasets:[{label:series.title,data:series.points.map(p=>p.value),borderColor:colors.line,backgroundColor:colors.fill,fill:true,tension:.28,pointRadius:4,pointHoverRadius:6,borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{legend:{display:false},tooltip:{rtl:true,textDirection:'rtl',callbacks:{label:(ctx)=>`${ctx.parsed.y} ${series.unit}`}}},scales:{x:{ticks:{color:'#a8b7ac',maxRotation:0},grid:{color:'rgba(168,183,172,.08)'}},y:{beginAtZero:false,title:{display:true,text:series.unit,color:'#a8b7ac'},ticks:{color:'#a8b7ac'},grid:{color:'rgba(168,183,172,.12)'}}}}});
}
'''.replace("__TREND_DATA__", chart_json)

    template = '''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0c1714">
<meta name="description" content="لوحة مستقلة لمتابعة مؤشرات المعيشة والعمل والسكن في المغرب مع توثيق المصادر والمنهجية.">
<link rel="alternate" type="application/rss+xml" title="RSS — تحديثات المؤشرات" href="feed.xml">
<link rel="alternate" type="application/atom+xml" title="Atom — تحديثات المؤشرات" href="atom.xml">
<title>مؤشر المواطن المغربي</title>
<style>__CSS__</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
</head><body>
<header><div class="wrap brand"><span class="flag">✦</span><div>مؤشر المواطن المغربي<small>قراءة مستقلة للواقع بالأرقام والمصادر</small></div></div></header>
<main class="wrap"><section class="hero"><div class="eyebrow">المغرب · مؤشرات قابلة للتحقق</div><h1>كيف تتغير<br>معيشة المواطن؟</h1><p class="lead">لوحة أولية لمتابعة القدرة الشرائية والعمل والسكن والتنافسية، مع إظهار مصدر كل رقم وفترته بدل الاكتفاء بالعناوين.</p></section>
<div class="notice"><span>ⓘ</span><div><b>أُضيفت قيم موثقة للبطالة والقدرة الشرائية من HCP.</b> تعرض كل قيمة الفترة والمصدر. تبقى المؤشرات التي لا تتوفر لها بيانات موثقة فارغة.</div></div>
<section><div class="toolbar"><h2>المؤشرات الرئيسية</h2><input id="search" class="search" type="search" placeholder="ابحث عن مؤشر…" aria-label="ابحث عن مؤشر"></div><div class="grid">__CARDS__</div><p id="empty" class="empty">لا توجد مؤشرات مطابقة لبحثك.</p></section>
<section class="trends"><div class="section-intro"><h2>تطور المؤشرات</h2><p>رسوم تفاعلية؛ حرّك المؤشر فوق النقاط لعرض القيمة والفترة. لا تظهر خطوط قبل إدخال بيانات موثقة.</p></div><div class="chart-grid">__CHART_CARDS__</div></section>
<section class="method"><article><h2>منهجية العرض</h2><p>لكل مؤشر قيمة وفترة مرجعية ووحدة قياس ورابط مصدر مباشر. لا تُعرض القيمة بوصفها موثقة ما لم يتوفر مرجع يمكن للقارئ فتحه. المقارنات الدولية تحتاج إلى توحيد التعريفات والفترات قبل نشرها.</p><ul><li>القيمة الفارغة تعني أن البيانات لم تُراجع وتُعتمد بعد.</li><li>تاريخ التحديث الحالي للبيانات: __UPDATED__.</li><li>المشروع مستقل ولا يمثل الجهات المذكورة.</li></ul></article>
<article><h2>مصادر للرجوع والتحقق</h2><p>تُستخدم هذه البوابات للبحث عن السلاسل الأصلية، ولا يعني إدراجها أن الأرقام قد جُمعت أو تحققت بعد.</p><div class="sources"><a href="https://www.hcp.ma/" target="_blank" rel="noopener">المندوبية السامية للتخطيط</a><a href="https://www.bkam.ma/" target="_blank" rel="noopener">بنك المغرب</a><a href="https://data.worldbank.org/country/morocco" target="_blank" rel="noopener">البنك الدولي</a><a href="https://www.imf.org/en/Countries/MAR" target="_blank" rel="noopener">صندوق النقد الدولي</a></div></article></section></main>
<footer class="wrap"><span>مؤشر المواطن المغربي · مشروع مفتوح المصدر</span><span class="sources"><a href="changelog/">سجل التغييرات</a><a href="feed.xml">RSS</a><a href="atom.xml">Atom</a></span></footer>
<script>__SCRIPT__</script>
</body></html>'''

    page = (template.replace("__CSS__", css)
            .replace("__CARDS__", cards)
            .replace("__CHART_CARDS__", "\n".join(chart_cards))
            .replace("__UPDATED__", updated)
            .replace("__SCRIPT__", script))
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(page, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE.relative_to(ROOT)} ({OUTPUT_FILE.stat().st_size} bytes)")

    api_file = OUTPUT_FILE.parent / "api" / "v1" / "indicators.json"
    api_file.parent.mkdir(parents=True, exist_ok=True)
    api_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Generated {api_file.relative_to(ROOT)} ({api_file.stat().st_size} bytes)")

    entries = change_entries(data)
    rss_file = OUTPUT_FILE.parent / "feed.xml"
    atom_file = OUTPUT_FILE.parent / "atom.xml"
    changelog_file = OUTPUT_FILE.parent / "changelog" / "index.html"
    changelog_json = OUTPUT_FILE.parent / "api" / "v1" / "changelog.json"
    changelog_file.parent.mkdir(parents=True, exist_ok=True)
    rss_file.write_text(render_rss(entries), encoding="utf-8")
    atom_file.write_text(render_atom(entries), encoding="utf-8")
    changelog_file.write_text(render_changelog_page(entries), encoding="utf-8")
    changelog_json.write_text(
        json.dumps({"entries": entries}, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    for generated in (rss_file, atom_file, changelog_file, changelog_json):
        print(f"Generated {generated.relative_to(ROOT)} ({generated.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
