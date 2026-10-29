import html
import json
from datetime import datetime
from pathlib import Path

CSS = """
:root{--pass:#16a34a;--fail:#dc2626;--skip:#9ca3af;--bg:#f3f4f6;--ink:#111827}
*{box-sizing:border-box}
body{margin:0;font-family:Segoe UI,system-ui,sans-serif;background:var(--bg);color:var(--ink)}
header{background:linear-gradient(135deg,#0f172a,#1e40af);color:#fff;padding:28px 40px}
header h1{margin:0 0 4px;font-size:26px}header p{margin:0;opacity:.8}
main{max-width:1200px;margin:0 auto;padding:24px}
.cards{display:flex;gap:16px;flex-wrap:wrap;margin:-48px 0 24px}
.card{flex:1;min-width:150px;background:#fff;border-radius:12px;padding:16px 20px;box-shadow:0 2px 8px #0002}
.card b{display:block;font-size:30px}.card span{color:#6b7280;font-size:13px;text-transform:uppercase}
.card.pass b{color:var(--pass)}.card.fail b{color:var(--fail)}
.bar{height:10px;border-radius:5px;background:var(--fail);overflow:hidden;margin:8px 0 20px}
.bar div{height:100%;background:var(--pass)}
.filters{margin-bottom:16px}.filters button{border:0;background:#fff;padding:8px 16px;border-radius:20px;margin-right:8px;cursor:pointer;box-shadow:0 1px 3px #0002}
.filters button.on{background:#1e40af;color:#fff}
details.sc{background:#fff;border-radius:12px;margin-bottom:12px;box-shadow:0 1px 4px #0002;border-left:6px solid var(--skip)}
details.sc.passed{border-color:var(--pass)}details.sc.failed,details.sc.error{border-color:var(--fail)}
summary{padding:14px 18px;cursor:pointer;display:flex;align-items:center;gap:12px;font-weight:600}
.badge{font-size:12px;padding:3px 10px;border-radius:12px;color:#fff;background:var(--skip);text-transform:uppercase}
.badge.passed{background:var(--pass)}.badge.failed,.badge.error{background:var(--fail)}
.tag{font-size:12px;color:#1e40af;background:#dbeafe;padding:2px 8px;border-radius:10px;font-weight:400}
.time{margin-left:auto;color:#6b7280;font-weight:400;font-size:13px}
.steps{padding:4px 18px 18px}
.step{display:flex;gap:16px;padding:12px 0;border-top:1px solid #e5e7eb;align-items:flex-start}
.step .txt{flex:1}.step .kw{font-weight:700;color:#1e40af}
.step .dot{display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--skip);margin-right:8px}
.step .dot.passed{background:var(--pass)}.step .dot.failed,.step .dot.error{background:var(--fail)}
.step small{color:#6b7280;margin-left:8px}
pre{background:#fef2f2;color:#991b1b;padding:10px;border-radius:8px;white-space:pre-wrap;font-size:12px}
.shot{width:220px;border-radius:8px;border:1px solid #d1d5db;cursor:zoom-in;transition:.15s}
.shot:hover{box-shadow:0 4px 12px #0004}
#lb{display:none;position:fixed;inset:0;background:#000d;align-items:center;justify-content:center;z-index:9;cursor:zoom-out}
#lb img{max-width:94vw;max-height:94vh;border-radius:8px}
"""

JS = """
function filt(s,b){document.querySelectorAll('.filters button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
document.querySelectorAll('details.sc').forEach(d=>{d.style.display=(s==='all'||d.classList.contains(s))?'':'none'})}
function zoom(i){var l=document.getElementById('lb');l.firstChild.src=i.src;l.style.display='flex'}
document.getElementById('lb').onclick=function(){this.style.display='none'}
"""


class Report:
    def __init__(self, base_url: str):
        self.started = datetime.now()
        self.base_url = base_url.rstrip("/")
        self.scenarios = []
        self.current = None

    def start_scenario(self, scenario):
        self.current = {
            "name": scenario.name,
            "feature": scenario.feature.name,
            "tags": [str(t) for t in scenario.effective_tags],
            "steps": [],
        }
        self.scenarios.append(self.current)

    def add_step(self, step, screenshot_b64):
        self.current["steps"].append(
            {
                "keyword": step.keyword,
                "name": step.name,
                "status": step.status.name,
                "duration": step.duration,
                "error": step.error_message or "",
                "shot": screenshot_b64,
            }
        )

    def end_scenario(self, scenario):
        self.current["status"] = scenario.status.name
        self.current["duration"] = sum(s["duration"] for s in self.current["steps"])

    def write(self, path: Path) -> None:
        total = len(self.scenarios)
        passed = sum(s["status"] == "passed" for s in self.scenarios)
        failed = total - passed
        duration = sum(s["duration"] for s in self.scenarios)
        pct = round(100 * passed / total) if total else 0

        parts = [
            f"<!doctype html><meta charset='utf-8'><title>ICS Cards test report</title><style>{CSS}</style>",
            "<header><h1>ICS Cards - Selenium + behave report</h1>",
            f"<p>{self.started:%d %b %Y %H:%M} &middot; {html.escape(self.base_url)}</p></header><main>",
            "<div class='cards'>",
            f"<div class='card'><span>Scenarios</span><b>{total}</b></div>",
            f"<div class='card pass'><span>Passed</span><b>{passed}</b></div>",
            f"<div class='card fail'><span>Failed</span><b>{failed}</b></div>",
            f"<div class='card'><span>Duration</span><b>{duration:.0f}s</b></div></div>",
            f"<div class='bar'><div style='width:{pct}%'></div></div>",
            "<div class='filters'><button class='on' onclick=\"filt('all',this)\">All</button>"
            "<button onclick=\"filt('passed',this)\">Passed</button>"
            "<button onclick=\"filt('failed',this)\">Failed</button></div>",
        ]
        for sc in self.scenarios:
            status = sc["status"]
            css = "failed" if status in ("failed", "error") else status
            tags = "".join(f"<span class='tag'>@{html.escape(t)}</span>" for t in sc["tags"])
            parts.append(
                f"<details class='sc {css}'><summary><span class='badge {css}'>{status}</span>"
                f"{html.escape(sc['name'])} {tags}<span class='time'>{sc['duration']:.1f}s</span></summary>"
                "<div class='steps'>"
            )
            for st in sc["steps"]:
                img = (
                    f"<img class='shot' onclick='zoom(this)' src='data:image/png;base64,{st['shot']}'>"
                    if st["shot"]
                    else ""
                )
                err = f"<pre>{html.escape(st['error'])}</pre>" if st["error"] else ""
                parts.append(
                    f"<div class='step'><div class='txt'><span class='dot {st['status']}'></span>"
                    f"<span class='kw'>{html.escape(st['keyword'])}</span> {html.escape(st['name'])}"
                    f"<small>{st['duration']:.2f}s</small>{err}</div>{img}</div>"
                )
            parts.append("</div></details>")
        parts.append(f"</main><div id='lb'><img></div><script>{JS}</script>")
        path.write_text("".join(parts), encoding="utf-8")
