"""윙키 스튜디오: 설정·인물·대본·에셋을 한 화면에서 보고, 에이전트가 올린 결정 요청에 답하는 로컬 화면.
impeccable live처럼 돌아간다: 에이전트가 요청을 올리고(studio/requests/<id>.json), 사람이 화면에서 고르면
studio/answers/<id>.json 이 생기고, 백그라운드로 돌던 `wait` 가 그 답을 출력하고 끝난다.

  python3 engine/studio.py serve [--port 8765]   # 화면 띄우기 (http://localhost:8765)
  python3 engine/studio.py wait <id> [--timeout 초] # 답이 올 때까지 기다림 (Claude Code: 백그라운드로 돌린다)
  python3 engine/studio.py list                   # 대기 중인 요청

요청 파일 모양:
  {"id": "...", "title": "...", "question": "...", "source": "episodes/drafts/....md",
   "options": [{"id": "1", "title": "...", "body": "마크다운"}], "reason": true}
표준 라이브러리만 쓴다. localhost 에만 붙는다.
"""
import html, json, re, sys, time, os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQ, ANS = ROOT / "studio/requests", ROOT / "studio/answers"
E = html.escape

# ---------- 마크다운 (이 레포 문서에 쓰는 만큼만) ----------
def inline(t):
    t = E(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t

def md(text):
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        s = lines[i].strip()
        if not s: i += 1; continue
        m = re.match(r"(#{1,4}) (.*)", s)
        if m:
            n = len(m.group(1)) + 1; out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); i += 1; continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                r = lines[i].strip()
                if not re.match(r"^\|[-:\s|]+\|$", r): rows.append([c.strip() for c in r.strip("|").split("|")])
                i += 1
            h = "".join(f"<th>{inline(c)}</th>" for c in rows[0])
            b = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="tbl"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'); continue
        if s.startswith(">"):
            blk = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                blk.append(lines[i].strip()[1:].strip()); i += 1
            dl = [re.match(r"\*\*(.+?)\*\*\s*(.*)", x) for x in blk]
            if all(dl):  # 대사 블록 → 자막 띠
                out.append('<div class="dlg">' + "".join(
                    f'<div class="ln"><span class="who">{E(m.group(1))}</span><span class="strip">{inline(m.group(2))}</span></div>' for m in dl) + "</div>")
            else:
                out.append(f"<blockquote>{'<br>'.join(inline(x) for x in blk)}</blockquote>")
            continue
        if re.match(r"(- |\d+\. )", s):
            tag = "ol" if s[0].isdigit() else "ul"; items = []
            while i < len(lines) and re.match(r"\s*(- |\d+\. )", lines[i]):
                items.append(re.sub(r"^\s*(- |\d+\. )", "", lines[i])); i += 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>"); continue
        para = []
        while i < len(lines) and lines[i].strip() and not re.match(r"(#|\||>|- |\d+\. )", lines[i].strip()):
            para.append(lines[i].strip()); i += 1
        out.append(f"<p>{inline(' '.join(para))}</p>")
    return "\n".join(out)

assert "<h2>가</h2>" in md("# 가") and 'class="strip"' in md("> **윙키** 넵!") and "<td>2</td>" in md("|a|b|\n|-|-|\n|1|2|")

# ---------- 결정 요청 ----------
def requests():
    REQ.mkdir(parents=True, exist_ok=True)
    out = []
    for p in sorted(REQ.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        r = json.loads(p.read_text(encoding="utf-8"))
        a = ANS / f"{r['id']}.json"
        r["answer"] = json.loads(a.read_text(encoding="utf-8")) if a.exists() else None
        out.append(r)
    return out

def answer(data):
    rid = re.sub(r"[^\w.-]", "", data.get("id", ""))
    if not (REQ / f"{rid}.json").exists(): return False
    ANS.mkdir(parents=True, exist_ok=True)
    data["at"] = time.strftime("%Y-%m-%d %H:%M")
    (ANS / f"{rid}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return True

def req_html(r):
    a = r["answer"]
    opts = "".join(f'''<label class="opt"><input type="radio" name="c-{E(r["id"])}" value="{E(o["id"])}" {"checked" if a and a.get("choice")==o["id"] else ""} {"disabled" if a else ""}>
      <div><h4>{E(o["id"])}. {E(o["title"])}</h4>{md(o.get("body",""))}</div></label>''' for o in r.get("options", []))
    src = f'<p class="meta">원문: <code>{E(r["source"])}</code></p>' if r.get("source") else ""
    if a:
        foot = f'<p class="done">✓ {E(a.get("at",""))} 고름: <b>{E(str(a.get("choice")))}</b> · {E(a.get("reason",""))}</p>'
    else:
        foot = f'''<textarea id="r-{E(r["id"])}" placeholder="고른 이유, 또는 다른 의견 (선택 없이 의견만 보내도 됩니다)"></textarea>
      <button onclick="send('{E(r["id"])}')">보내기</button>'''
    return f'''<section class="req {'answered' if a else 'open'}" id="q-{E(r["id"])}"><h3>{E(r["title"])}</h3>
      <p>{inline(r.get("question",""))}</p>{src}<div class="opts">{opts}</div>{foot}</section>'''

# ---------- 화면 ----------
DOCS = [  # (탭 id, 이름, 파일 목록)
    ("world", "세계관", ["rules/world.md"]),
    ("lexicon", "사전", ["kit/lexicon/ajae.md", "kit/lexicon/memes.md"]),
    ("ledger", "장부", ["episodes/LEDGER.md"]),
    ("milestone", "마일스톤", ["MILESTONE.md"]),
    ("rules", "규칙", ["rules/wording.md", "rules/directing.md", "rules/stigma.md", "rules/non-medical-device.md"]),
]

def scripts_tab():
    files = sorted((ROOT / "episodes").glob("drafts/*.md"), reverse=True) + sorted((ROOT / "episodes").glob("ep*/*.md"))
    if not files: return "<p>아직 대본이 없습니다.</p>"
    toc = "".join(f'<li><a href="#doc-{i}">{E(str(f.relative_to(ROOT)))}</a></li>' for i, f in enumerate(files))
    body = "".join(f'<article class="doc" id="doc-{i}"><p class="meta"><code>{E(str(f.relative_to(ROOT)))}</code></p>{md(f.read_text(encoding="utf-8"))}</article>' for i, f in enumerate(files))
    return f"<ul class='toc'>{toc}</ul>{body}"

def assets_tab():
    reg = json.loads((ROOT / "kit/registry.json").read_text(encoding="utf-8"))
    groups = {}
    for name, it in reg.get("items", {}).items():
        f = it.get("file", "")
        if f.endswith((".png", ".webp", ".jpg")):
            groups.setdefault(it.get("actor") or it.get("kind", "기타"), []).append((name, f))
    actors = reg.get("actors", {})
    out = []
    for g, items in sorted(groups.items()):
        st = actors.get(g, {}).get("status", "")
        cards = "".join(f'<figure><img loading="lazy" src="/{E(f)}" alt="{E(n)}"><figcaption>{E(n)}</figcaption></figure>' for n, f in items)
        out.append(f'<h3>{E(g)} <span class="meta">{len(items)}장 {E(st)}</span></h3><div class="grid">{cards}</div>')
    missing = ["거북 여사", "너구리 대리", "고양이 사장", "다람쥐 코치", "도치 실장"]  # ponytail: 손으로 적음. 인물 그림이 생기면 registry actors 로 계산
    out.insert(0, f'<p class="meta">그림이 아직 없는 인물: {E(", ".join(missing))}</p>')
    return "".join(out)

def page():
    reqs = requests(); n_open = sum(1 for r in reqs if not r["answer"])
    tabs = [("decide", f"결정 대기 {n_open}" if n_open else "결정 대기", "".join(req_html(r) for r in reqs) or "<p>올라온 결정 요청이 없습니다.</p>"),
            ("people", "인물", '<iframe src="/characters" title="인물 바이블"></iframe>'),
            ("scripts", "대본·초안", scripts_tab()),
            ("assets", "에셋", assets_tab())]
    for tid, name, files in DOCS:
        tabs.append((tid, name, "".join(f'<article class="doc"><p class="meta"><code>{E(f)}</code></p>{md((ROOT/f).read_text(encoding="utf-8"))}</article>' for f in files if (ROOT/f).exists())))
    nav = "".join(f'<a href="#{t}" data-t="{t}">{E(n)}</a>' for t, n, _ in tabs)
    secs = "".join(f'<section class="tab" id="{t}" hidden>{b}</section>' for t, _, b in tabs)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>윙키 스튜디오</title><style>{CSS}</style></head><body>
<header><b>윙키 스튜디오</b><span class="meta">모래언덕 빌라</span><nav>{nav}</nav></header><main>{secs}</main>
<script>{JS}</script></body></html>"""

CSS = """
:root{--bg:#f4efe4;--paper:#fffdf8;--ink:#2a2823;--mute:#6e685c;--line:#ddd4c2;--acc:#2f7d6d;--acc2:#e6f1ec;--strip:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#1c1b18;--paper:#25241f;--ink:#ece6d8;--mute:#a59e8f;--line:#3a3832;--acc:#6cc3ad;--acc2:#21332e;--strip:#f3efe6}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.7 "Apple SD Gothic Neo","Pretendard",system-ui,sans-serif}
header{position:sticky;top:0;z-index:2;background:var(--paper);border-bottom:1px solid var(--line);padding:10px 20px;display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center}
header b{font-size:17px}nav{display:flex;flex-wrap:wrap;gap:4px;margin-left:auto}
nav a{color:var(--ink);text-decoration:none;padding:3px 10px;border-radius:14px;border:1px solid transparent}
nav a.on{background:var(--acc2);border-color:var(--acc);color:var(--acc)}nav a:focus-visible{outline:2px solid var(--acc)}
main{max-width:1100px;margin:0 auto;padding:20px}.meta{color:var(--mute);font-size:13px}
h2,h3,h4,h5{line-height:1.3;margin:1.2em 0 .4em}code{background:var(--acc2);padding:0 .3em;border-radius:3px;font-size:.88em}
.doc{background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:4px 24px 18px;margin-bottom:18px;min-width:0}
.tbl{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{color:var(--mute);font-weight:600}
blockquote{border-left:3px solid var(--line);margin:8px 0;padding:2px 12px;color:var(--mute)}
.dlg{background:#8d9a8a22;border-radius:6px;padding:10px;display:flex;flex-direction:column;gap:5px;margin:8px 0}
.ln{display:flex;flex-direction:column}.who{font-size:11px;color:var(--mute)}.strip{align-self:flex-start;background:var(--strip);color:#24231f;padding:2px 10px;border-radius:2px;font-size:16px}
iframe{width:100%;height:calc(100vh - 110px);border:0;border-radius:6px;background:var(--paper)}
.req{background:var(--paper);border:1px solid var(--line);border-left:5px solid var(--acc);border-radius:6px;padding:6px 20px 16px;margin-bottom:20px}
.req.answered{border-left-color:var(--line);opacity:.85}
.opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.opt{display:flex;gap:8px;border:1px solid var(--line);border-radius:6px;padding:8px 12px;cursor:pointer;min-width:0}.opt:has(input:checked){border-color:var(--acc);background:var(--acc2)}
.opt>div{min-width:0}.opt h4{margin:.2em 0}textarea{width:100%;min-height:70px;margin-top:12px;font:inherit;padding:8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--ink)}
button{margin-top:8px;padding:7px 18px;border:0;border-radius:6px;background:var(--acc);color:#fff;font:inherit;cursor:pointer}.done{color:var(--acc);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px}figure{margin:0;background:var(--paper);border:1px solid var(--line);border-radius:6px;padding:6px}
figure img{width:100%;height:120px;object-fit:contain}figcaption{font-size:11px;color:var(--mute);word-break:break-all}.toc{columns:2}
"""

JS = """
function show(){const t=(location.hash||'#decide').slice(1);let hit=false;
document.querySelectorAll('.tab').forEach(s=>{const on=s.id===t||!!s.querySelector('#'+CSS.escape(t));s.hidden=!on;hit=hit||on});
if(!hit)document.getElementById('decide').hidden=false;
document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('on',a.dataset.t===t||(!hit&&a.dataset.t==='decide')))}
addEventListener('hashchange',show);show();
async function send(id){const c=document.querySelector('input[name="c-'+id+'"]:checked');const reason=document.getElementById('r-'+id).value.trim();
if(!c&&!reason){alert('하나를 고르거나 의견을 적어 주세요.');return}
const r=await fetch('/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,choice:c?c.value:null,reason})});
if(r.ok)location.reload();else alert('저장하지 못했습니다.')}
let ver=null;setInterval(async()=>{try{const v=await (await fetch('/version')).text();if(ver&&v!==ver&&!document.activeElement.matches('textarea'))location.reload();ver=v}catch(e){}},2000);
"""

def version():  # 화면에 보이는 파일이 바뀌면 값이 바뀐다
    pats = ["rules/*.md", "kit/lexicon/*.md", "episodes/**/*.md", "MILESTONE.md", "studio/**/*.json", "kit/registry.json"]
    return str(max((p.stat().st_mtime for pat in pats for p in ROOT.glob(pat)), default=0))

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/": return self.send(200, page())
        if p == "/version": return self.send(200, version(), "text/plain")
        if p == "/characters":
            import studio_characters
            return self.send(200, "<!doctype html><meta charset='utf-8'>" + studio_characters.render((ROOT / "rules/characters.md").read_text(encoding="utf-8")))
        if p.startswith("/kit/"):
            f = (ROOT / p.lstrip("/")).resolve()
            if f.is_file() and (ROOT / "kit") in f.parents:  # kit 밖은 안 내준다
                ct = {".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg"}.get(f.suffix, "application/octet-stream")
                return self.send(200, f.read_bytes(), ct)
        self.send(404, "없음", "text/plain; charset=utf-8")
    def do_POST(self):
        if self.path != "/answer": return self.send(404, "없음", "text/plain; charset=utf-8")
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        ok = answer(data)
        self.send(200 if ok else 400, "ok" if ok else "요청 없음", "text/plain; charset=utf-8")

def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "serve"
    if cmd == "serve":
        port = int(args[args.index("--port") + 1]) if "--port" in args else 8765
        sys.path.insert(0, str(ROOT / "engine"))
        print(f"윙키 스튜디오: http://localhost:{port}", flush=True)
        ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
    elif cmd == "wait":
        rid = args[1]; limit = float(args[args.index("--timeout") + 1]) if "--timeout" in args else 3600
        end = time.time() + limit; f = ANS / f"{rid}.json"
        while time.time() < end:
            if f.exists(): print(f.read_text(encoding="utf-8")); return
            time.sleep(1)
        print(json.dumps({"id": rid, "timeout": True})); sys.exit(2)
    elif cmd == "list":
        for r in requests(): print(("대기 " if not r["answer"] else "끝   ") + r["id"], "-", r["title"])

if __name__ == "__main__":
    main()
