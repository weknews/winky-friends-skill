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
import html, json, re, sys, time, os, urllib.parse
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
        imgs = re.findall(r"!\[([^\]]*)\]\((kit/[^)\s]+)\)", s)
        if imgs and re.fullmatch(r"(\s*!\[[^\]]*\]\(kit/[^)\s]+\))+\s*", s):  # 그림 줄 → 그림판(kit 안만)
            out.append('<div class="shots">' + "".join(f'<figure class="shot"><img loading="lazy" src="/{E(f)}" alt="{E(a)}"><figcaption>{E(a)}</figcaption></figure>' for a, f in imgs) + "</div>"); i += 1; continue
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

assert "<h2>가</h2>" in md("# 가") and 'class="strip"' in md("> **윙키** 넵!") and "<td>2</td>" in md("|a|b|\n|-|-|\n|1|2|") and 'class="shot"' in md("![a](kit/x.jpg)") and "<img" not in md("![a](../x.jpg)")

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

NAME2KEY = {"윙키": "winky", "곰 아빠": "bear", "판다": "panda", "펭귄 선생님": "penguin"}
CAST = ["윙키", "곰 아빠", "판다", "펭귄 선생님", "거북 여사", "너구리 대리", "고양이 사장", "다람쥐 코치", "도치 실장"]
COLOR = {"윙키": "#e2a54b", "곰 아빠": "#8a5a3c", "판다": "#555", "펭귄 선생님": "#3b6e9c", "거북 여사": "#6f8f4e",
         "너구리 대리": "#8c7a63", "고양이 사장": "#d0773f", "다람쥐 코치": "#b5622f", "도치 실장": "#7a6f8f"}

def registry():
    return json.loads((ROOT / "kit/registry.json").read_text(encoding="utf-8"))

def face(name, reg=None):
    """인물 대표 그림(있으면) 또는 색 동그라미."""
    reg = reg or registry(); key = NAME2KEY.get(name)
    if key:
        files = [it["file"] for it in reg.get("items", {}).values() if it.get("actor") == key and it.get("file", "").endswith(".webp")]
        pick = next((f for f in files if "calm" in f and "bust" in f), None) or next((f for f in files if "calm" in f), files[0] if files else None)
        if pick: return f'<span class="face"><img src="/{E(pick)}" alt=""></span>'
    return f'<span class="face none" style="--c:{COLOR.get(name, "#999")}">{E(name[0])}</span>'

def req_html(r):
    a, rid = r["answer"], E(r["id"])
    cards = []
    for o in r.get("options", []):
        oid = E(o["id"]); chosen = a and a.get("choice") == o["id"]
        if "chain" in o:
            steps = "".join("<li>" + re.sub(r"^(그래서|그런데)", r'<b class="link">\1</b>', E(x)) + "</li>" for x in o["chain"])
            notes = "".join(f"<li>{inline(n)}</li>" for n in o.get("notes", []))
            body = f"""<p class="hook">{E(o["hook"])}</p>
            <dl class="facts"><dt>정보 한 줄</dt><dd class="info">{E(o["info"])}<small>{E(o["basis"])}</small></dd>
            <dt>결말</dt><dd>{E(o["end"])}</dd><dt>장소</dt><dd>{E(o["where"])}</dd><dt>새로 그릴 것</dt><dd>{E(o["art"])}</dd></dl>
            <details><summary>이야기 따라가기 · {len(o["chain"])}단계</summary><ol class="chain">{steps}</ol><ul class="notes">{notes}</ul></details>"""
            who = f'<p class="who">{face(o["who"])}<span>중심 <b>{E(o["who"])}</b></span><span class="chip">{E(o["tag"])}</span></p>'
        else:
            body, who = md(o.get("body", "")), ""
        btn = "" if a else f'<button class="pick" data-r="{rid}" data-o="{oid}">이 안으로</button>'
        cards.append(f'<article class="choice{" chosen" if chosen else ""}" id="o-{rid}-{oid}"><p class="num">안 {oid}</p><h3>「{E(o["title"])}」</h3>{who}{body}{btn}</article>')
    src = f'<p class="meta">원문 <code>{E(r["source"])}</code></p>' if r.get("source") else ""
    if a:
        foot = f'<p class="done">{E(a.get("at",""))}에 답함 · 고른 안 <b>{E(str(a.get("choice") or "없음"))}</b>{(" · " + E(a["reason"])) if a.get("reason") else ""}</p>'
    else:
        foot = f"""<div class="send" id="s-{rid}"><p class="picked" id="p-{rid}">안을 고르거나, 의견만 적어도 됩니다.</p>
        <label for="r-{rid}">고른 이유 (대본 맨 위에 적힙니다)</label><textarea id="r-{rid}" placeholder="예: 윙키가 뛰어다니는 그림이 제일 잘 떠오른다"></textarea><button class="go" onclick="send('{rid}')">보내기</button></div>"""
    return f"""<section class="req {'answered' if a else 'open'}" id="q-{rid}"><p class="eyebrow">{'답한 요청' if a else '결정해 주세요'}</p>
      <h2>{E(r["title"])}</h2><p class="lead">{inline(r.get("question",""))}</p>{src}<div class="choices">{"".join(cards)}</div>{foot}</section>"""

# ---------- 화면 ----------
DOCS = [  # (탭 id, 이름, 파일 목록)
    ("world", "세계관", ["rules/world.md"]),
    ("lexicon", "사전", ["kit/lexicon/ajae.md", "kit/lexicon/memes.md"]),
    ("ledger", "장부", ["episodes/LEDGER.md"]),
    ("milestone", "마일스톤", ["MILESTONE.md"]),
    ("rules", "규칙", ["rules/wording.md", "rules/directing.md", "rules/stigma.md", "rules/non-medical-device.md"]),
]

def doc(f):
    return f'<article class="doc"><p class="path"><code>{E(f)}</code></p>{md((ROOT/f).read_text(encoding="utf-8"))}</article>'

def scripts_tab():
    files = sorted((ROOT / "episodes").glob("drafts/*.md"), reverse=True) + sorted((ROOT / "episodes").glob("ep*/*.md"))
    return "".join(doc(str(f.relative_to(ROOT))) for f in files) or "<p>아직 대본이 없습니다.</p>"

def assets_tab():
    reg = registry(); items = reg.get("items", {}); actors = reg.get("actors", {})
    out = ['<h2>인물</h2><div class="cast">']
    for n in CAST:
        key = NAME2KEY.get(n)
        poses = [(k, it["file"]) for k, it in items.items() if key and it.get("actor") == key and it.get("file", "").endswith((".webp", ".png"))]
        st = "그림 " + str(len(poses)) + "장" if poses else "그림 없음"
        grid = "".join(f'<figure><img loading="lazy" src="/{E(f)}" alt=""><figcaption>{E(k.split("-",1)[-1])}</figcaption></figure>' for k, f in poses)
        more = f'<details><summary>자세·표정 {len(poses)}개 보기</summary><div class="grid">{grid}</div></details>' if poses else '<p class="meta">대본이 정해지면 winky-assets로 만든다</p>'
        out.append(f'<article class="person{"" if poses else " empty"}">{face(n, reg)}<div><h3>{E(n)}</h3><p class="meta">{st}</p>{more}</div></article>')
    out.append("</div>")
    rest = {}
    for k, it in items.items():
        if it.get("kind") != "actor" and it.get("file", "").endswith((".webp", ".png", ".jpg")):
            rest.setdefault(it.get("kind", "기타"), []).append((k, it["file"]))
    for kind, lst in sorted(rest.items()):
        grid = "".join(f'<figure><img loading="lazy" src="/{E(f)}" alt=""><figcaption>{E(k)}</figcaption></figure>' for k, f in lst)
        out.append(f'<h2>{E(kind)} <span class="meta">{len(lst)}</span></h2><div class="grid">{grid}</div>')
    return "".join(out)

def overview(reqs):
    reg = registry()
    open_r = [r for r in reqs if not r["answer"]]
    todo = "".join(f'<a class="todo" href="#decide"><b>{E(r["title"])}</b><span>{len(r.get("options",[]))}안 중 하나 고르기 →</span></a>' for r in open_r) \
        or '<p class="meta">지금 기다리는 결정이 없습니다.</p>'
    drawn = sum(1 for n in CAST if NAME2KEY.get(n))
    cast = "".join(f'<a class="mini" href="#people">{face(n, reg)}<span>{E(n)}</span></a>' for n in CAST)
    ms = (ROOT / "MILESTONE.md").read_text(encoding="utf-8")
    done, left = len(re.findall(r"^- \[x\]", ms, re.M)), re.findall(r"^- \[ \] (.+)$", ms, re.M)
    pct = round(100 * done / max(1, done + len(left)))
    short = lambda x: re.sub(r"`[^`]*`|\(.*?\)|\*\*", "", x).split("→")[0].split(":")[0].strip()[:34]
    nxt = "".join(f"<li>{E(short(x))}</li>" for x in left[:3])
    eps = sorted(p.name for p in (ROOT / "episodes").glob("ep*") if p.is_dir())
    drafts = sorted(p.name for p in (ROOT / "episodes/drafts").glob("*.md")) if (ROOT / "episodes/drafts").exists() else []
    return f"""<div class="home">
      <section class="panel wide"><p class="eyebrow">지금 할 일</p>{todo}</section>
      <section class="panel"><p class="eyebrow">인물 9명</p><div class="minis">{cast}</div><p class="meta">그림 있는 인물 {drawn}명 · 없는 인물 {9-drawn}명</p><a class="more-link" href="#people">인물 바이블</a></section>
      <section class="panel"><p class="eyebrow">진행</p><div class="bar"><i style="width:{pct}%"></i></div><p class="big">{pct}%</p><p class="meta">끝낸 일 {done} · 남은 일 {len(left)}</p><p class="sub">다음 할 일</p><ul class="next">{nxt}</ul><a class="more-link" href="#milestone">마일스톤 전체</a></section>
      <section class="panel"><p class="eyebrow">회차</p><p class="big">{len(eps)}<small>편 완성</small></p><p class="meta">초안 {len(drafts)}개</p><a class="more-link" href="#scripts">대본 보기</a></section>
    </div>"""

def page():
    reqs = requests(); n_open = sum(1 for r in reqs if not r["answer"])
    tabs = [("home", "한눈에", overview(reqs)),
            ("decide", "결정" + (f' <em>{n_open}</em>' if n_open else ""), "".join(req_html(r) for r in reqs) or "<p>올라온 결정 요청이 없습니다.</p>"),
            ("people", "인물", '<iframe src="/characters" title="인물 바이블"></iframe>'),
            ("scripts", "대본", scripts_tab()),
            ("assets", "그림", assets_tab())]
    for tid, name, files in DOCS:
        tabs.append((tid, name, "".join(doc(f) for f in files if (ROOT / f).exists())))
    prim = [t for t in tabs if t[0] in ("home", "decide", "people", "scripts", "assets")]
    more = [t for t in tabs if t not in prim]
    nav = "".join(f'<a href="#{t}" data-t="{t}">{n}</a>' for t, n, _ in prim)
    nav += '<details class="more"><summary data-t="more">자료</summary><div>' + "".join(f'<a href="#{t}" data-t="{t}">{n}</a>' for t, n, _ in more) + "</div></details>"
    secs = "".join(f'<section class="tab" id="{t}" hidden>{b}</section>' for t, _, b in tabs)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>윙키 스튜디오</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jua&family=IBM+Plex+Sans+KR:wght@400;500;600&display=swap"><style>{CSS}</style></head><body>
<header><div class="bar-in"><a class="brand" href="#home">윙키 스튜디오<small>모래언덕 빌라</small></a><nav>{nav}</nav></div></header><main>{secs}</main>
<dialog id="lb"><img alt=""><p></p></dialog><script>{JS}</script></body></html>"""

CSS = """
/* 토큰: 색 5개, 글자 14/16/18/22/30, 간격 4·8·12·16·24·32·48 */
:root{--bg:#f2ede2;--surface:#fffdf8;--ink:#26241e;--mute:#635d50;--accent:#22705f;
--line:color-mix(in srgb,var(--mute) 22%,transparent);--tint:color-mix(in srgb,var(--accent) 11%,var(--surface));
--f-d:"Jua","IBM Plex Sans KR",system-ui,sans-serif;--f-b:"IBM Plex Sans KR","Apple SD Gothic Neo",system-ui,sans-serif}
@media (prefers-color-scheme:dark){:root{--bg:#1a1916;--surface:#24231f;--ink:#efe9dc;--mute:#b3ac9c;--accent:#74c9b3;color-scheme:dark}}
*{box-sizing:border-box}html{scroll-padding-top:120px}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.7 var(--f-b);word-break:keep-all}
a{color:var(--accent)}h1,h2,h3{font-family:var(--f-d);font-weight:400;line-height:1.3;text-wrap:balance;margin:0}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px;border-radius:6px}
.meta{color:var(--mute);font-size:14px;margin:0}.eyebrow{font-size:14px;font-weight:600;color:var(--accent);margin:0 0 8px}
code{background:var(--tint);padding:0 4px;border-radius:4px;font-size:14px}
/* 머리 */
header{position:sticky;top:0;z-index:5;background:var(--surface);border-bottom:1px solid var(--line)}
.bar-in{max-width:1180px;margin:0 auto;padding:8px max(16px,env(safe-area-inset-left,0px));display:flex;flex-wrap:wrap;align-items:center;gap:8px 24px}
.brand{font-family:var(--f-d);font-size:22px;color:var(--ink);text-decoration:none;min-height:44px;display:flex;align-items:center;gap:8px}
.brand small{font-family:var(--f-b);font-size:14px;color:var(--mute)}
nav{display:flex;flex-wrap:wrap;gap:4px;align-items:center}
nav a,nav summary{display:flex;align-items:center;gap:6px;min-height:44px;padding:0 14px;border-radius:8px;color:var(--mute);text-decoration:none;font-size:16px;cursor:pointer;list-style:none}
nav summary::-webkit-details-marker{display:none}nav summary::after{content:"▾";font-size:12px}
nav a:hover,nav summary:hover{color:var(--ink);background:var(--bg)}nav a.on,nav summary.on{color:var(--ink);background:var(--tint);font-weight:600}
nav em{font-style:normal;background:var(--accent);color:var(--surface);border-radius:10px;padding:0 8px;font-size:14px;line-height:1.5}
.more{position:relative}.more>div{position:absolute;right:0;top:48px;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:8px;display:grid;min-width:160px;box-shadow:0 8px 24px #0000001f}
main{max-width:1180px;margin:0 auto;padding:32px max(16px,env(safe-area-inset-left,0px)) 48px}
/* 한눈에 */
.home{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:8px;min-width:0}
.panel.wide{grid-column:1/-1;background:var(--tint);border-color:transparent}
.todo{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px 16px;align-items:center;min-height:56px;text-decoration:none;color:var(--ink);background:var(--surface);border-radius:12px;padding:12px 24px;font-size:18px}
.todo span{color:var(--accent);font-size:16px;font-weight:600}
.minis{display:grid;grid-template-columns:repeat(3,1fr);gap:12px 8px;margin:8px 0}.mini{display:flex;flex-direction:column;align-items:center;gap:4px;text-decoration:none;color:var(--ink);font-size:14px;text-align:center}
.big{font-family:var(--f-d);font-size:30px;margin:0;line-height:1.2}.big small{font-family:var(--f-b);font-size:16px;color:var(--mute);margin-left:4px}
.sub{font-size:14px;font-weight:600;margin:8px 0 0}.bar{height:8px;background:var(--line);border-radius:4px;overflow:hidden}.bar i{display:block;height:100%;background:var(--accent)}
.next{margin:0;padding-left:20px;font-size:16px}.more-link{margin-top:auto;min-height:44px;display:flex;align-items:center;font-weight:600}.more-link::after{content:" →";white-space:pre}
.face{display:inline-grid;place-items:center;width:52px;height:52px;border-radius:50%;overflow:hidden;background:var(--bg);flex:none}
.face img{width:100%;height:100%;object-fit:cover;object-position:50% 12%}.face.none{background:var(--c);color:#fff;font-family:var(--f-d);font-size:22px}
/* 결정 */
.req{margin-bottom:48px}.req h2{font-size:30px;margin-bottom:8px}.lead{font-size:18px;max-width:60ch;margin:0 0 8px}
.choices{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:24px;margin-top:24px;align-items:stretch}
.choice{background:var(--surface);border:2px solid var(--line);border-radius:16px;padding:24px;display:flex;flex-direction:column;gap:12px;min-width:0}
.choice.sel{border-color:var(--accent);box-shadow:0 0 0 4px var(--tint)}.choice.chosen{border-color:var(--accent)}
.choice .num{margin:0;font-size:14px;font-weight:600;color:var(--mute)}.choice h3{font-size:22px}
.who{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:0;font-size:16px}.who .face{width:44px;height:44px}
.chip{font-size:14px;border:1px solid var(--line);border-radius:12px;padding:0 8px;color:var(--mute)}
.hook{font-size:18px;margin:0}
.facts{display:grid;grid-template-columns:1fr;gap:4px;margin:0;font-size:16px}.facts dt{font-size:14px;font-weight:600;color:var(--mute);margin-top:8px}.facts dd{margin:0}
.facts .info{background:var(--tint);border-radius:8px;padding:8px 12px;font-weight:600}.facts small{display:block;color:var(--mute);font-weight:400;font-size:14px}
details>summary{cursor:pointer}.choice details summary{min-height:44px;display:flex;align-items:center;color:var(--accent);font-weight:600}
.chain{padding-left:24px;margin:8px 0}.chain li{margin:8px 0}.link{color:var(--accent);font-weight:600}.notes{font-size:14px;color:var(--mute);padding-left:20px}
.pick{margin-top:auto;min-height:48px;border:2px solid var(--accent);border-radius:12px;background:transparent;color:var(--accent);font:600 16px var(--f-b);cursor:pointer}
.pick:hover,.choice.sel .pick{background:var(--accent);color:var(--surface)}
.send{margin-top:24px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:24px;display:grid;grid-template-columns:1fr auto;gap:12px 16px;align-items:end}
.picked{grid-column:1/-1;margin:0;font-size:16px}.send label{grid-column:1/-1;font-size:14px;font-weight:600}
.send textarea{min-height:56px;font:inherit;padding:12px;border:1px solid var(--mute);border-radius:12px;background:var(--bg);color:var(--ink);resize:vertical}
.go{min-height:48px;padding:0 32px;border:0;border-radius:12px;background:var(--accent);color:var(--surface);font:600 16px var(--f-b);cursor:pointer}
.done{color:var(--accent);font-weight:600;margin-top:16px}.req.answered .choice:not(.chosen){opacity:.6}
@media (max-width:600px){.send{grid-template-columns:1fr}.go{width:100%}}
/* 문서 */
.doc{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:16px clamp(16px,4vw,48px) 32px;margin:0 auto 24px;max-width:860px;min-width:0}
.doc h2{font-size:30px;margin:16px 0 8px}.doc h3{font-size:22px;margin:32px 0 8px;padding-top:16px;border-top:1px solid var(--line)}.doc h4{font-size:18px;margin:24px 0 8px}
.doc p,.doc li{max-width:68ch}.path{margin:8px 0 0;font-size:14px;color:var(--mute)}
.toc{background:var(--bg);border-radius:12px;padding:12px 16px 12px 40px;margin:8px 0 16px}.toc a{display:inline-block;padding:6px 0}
.tbl{overflow-x:auto;margin:12px 0}table{border-collapse:collapse;width:100%;font-size:15px}th,td{border-bottom:1px solid var(--line);padding:8px 12px;text-align:left;vertical-align:top}th{color:var(--mute);font-weight:600;font-size:14px}
blockquote{border-left:4px solid var(--accent);margin:12px 0;padding:8px 16px;background:var(--tint);border-radius:0 8px 8px 0}
.dlg{background:var(--bg);border-radius:12px;padding:12px;display:flex;flex-direction:column;gap:8px;margin:12px 0;max-width:520px}
.ln{display:flex;flex-direction:column}.ln .who{font-size:14px;color:var(--mute)}.strip{align-self:flex-start;background:#fff;color:#24231f;padding:4px 12px;border-radius:4px;font-family:var(--f-d);font-size:18px;box-shadow:0 1px 0 #0000001a}
iframe{width:100%;height:calc(100vh - 140px);border:1px solid var(--line);border-radius:16px;background:var(--surface)}
/* 그림 */
.tab>h2{font-size:22px;margin:32px 0 12px}.cast{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr));gap:16px}
.person{display:flex;gap:16px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:16px;min-width:0}
.person>div{min-width:0;flex:1}.person h3{font-size:22px}.person .face{width:72px;height:72px}.person.empty{border-style:dashed}
.person details summary{min-height:44px;display:flex;align-items:center;color:var(--accent);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:8px;margin-top:8px}figure{margin:0;background:var(--bg);border-radius:8px;padding:8px}
figure img{width:100%;height:112px;object-fit:contain;cursor:zoom-in}
.shots{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:16px;margin:12px 0}.shot img{height:auto;max-height:78vh}.choices:has(.shots){grid-template-columns:1fr}
#lb{border:0;padding:0;background:transparent;max-width:96vw;max-height:96vh}#lb::backdrop{background:rgba(0,0,0,.85)}#lb img{display:block;max-width:96vw;max-height:92vh;object-fit:contain;cursor:zoom-out}#lb p{color:#fff;text-align:center;margin:6px 0 0;font-size:15px}figcaption{font-size:14px;color:var(--mute);text-align:center;word-break:break-all}
@media (max-width:860px){.home{grid-template-columns:1fr}.more>div{right:auto;left:0}}
@media (max-width:600px){main{padding-top:24px}.req h2,.doc h2{font-size:22px}.lead{font-size:16px}nav a,nav summary{padding:0 10px}.brand small{display:none}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
"""

JS = """
const lb=document.getElementById('lb');document.addEventListener('click',e=>{const i=e.target.closest('figure img');if(i){lb.querySelector('img').src=i.src;lb.querySelector('p').textContent=i.alt||i.closest('figure').querySelector('figcaption')?.textContent||'';lb.showModal();return}if(e.target.closest('#lb'))lb.close()});
function show(){const t=(location.hash||'#home').slice(1);const tab=document.getElementById(t)?.closest('.tab')||document.getElementById('home');
document.querySelectorAll('.tab').forEach(s=>s.hidden=s!==tab);
document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('on',a.dataset.t===tab.id));const m=document.querySelector('.more');m.removeAttribute('open');m.querySelector('summary').classList.toggle('on',!!m.querySelector('a.on'));
if(document.getElementById(t)&&t!==tab.id)document.getElementById(t).scrollIntoView();else setTimeout(()=>scrollTo(0,0),0)}
addEventListener('hashchange',show);show();
document.querySelectorAll('.doc').forEach(d=>{const hs=[...d.querySelectorAll('h3')];if(hs.length<4)return;
const ol=document.createElement('ol');ol.className='toc';hs.forEach((h,i)=>{h.id=h.id||('t'+Math.random().toString(36).slice(2,8));
const li=document.createElement('li');const a=document.createElement('a');a.href='#';a.textContent=h.textContent;a.onclick=e=>{e.preventDefault();h.scrollIntoView({behavior:'smooth'})};li.append(a);ol.append(li)});
(d.querySelector('h2')||d.firstChild).after(ol)});
const picked={};
document.querySelectorAll('.pick').forEach(b=>b.onclick=()=>{const r=b.dataset.r,o=b.dataset.o;picked[r]=o;
document.querySelectorAll('#q-'+CSS.escape(r)+' .choice').forEach(c=>c.classList.toggle('sel',c.id==='o-'+r+'-'+o));
const t=document.querySelector('#o-'+CSS.escape(r)+'-'+CSS.escape(o)+' h3').textContent;
document.getElementById('p-'+r).innerHTML='고른 안: <b>안 '+o+' '+t+'</b> · 이유를 한 줄 적고 보내 주세요';const ta=document.getElementById('r-'+r);ta.scrollIntoView({behavior:'smooth',block:'center'});ta.focus({preventScroll:true})});
async function send(id){const reason=document.getElementById('r-'+id).value.trim();const choice=picked[id]||null;
if(!choice&&!reason){document.getElementById('p-'+id).textContent='안을 고르거나 의견을 적어 주세요.';return}
const r=await fetch('/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,choice,reason})});
document.getElementById('p-'+id).textContent=r.ok?'보냈습니다. 다음 단계로 넘어갑니다.':'저장하지 못했습니다. 서버가 켜져 있는지 봐 주세요.';if(r.ok)setTimeout(()=>location.reload(),900)}
let ver=null;setInterval(async()=>{try{const v=await (await fetch('/version')).text();
if(ver&&v!==ver&&!document.activeElement.matches('textarea')&&!Object.keys(picked).length)location.reload();ver=v}catch(e){}},2000);
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
        p = urllib.parse.unquote(self.path.split("?")[0])  # 한글 파일 이름
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
