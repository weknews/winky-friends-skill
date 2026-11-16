"""윙키 스튜디오: 설정·인물·대본·에셋을 한 화면에서 보고, 에이전트가 올린 결정 요청에 답하는 로컬 화면.
impeccable live처럼 돌아간다: 에이전트가 요청을 올리고(studio/requests/<id>.json), 사람이 화면에서 고르면
studio/answers/<id>.json 이 생기고, 백그라운드로 돌던 `wait` 가 그 답을 출력하고 끝난다.

  python3 engine/studio.py serve [--port 8765]   # 화면 띄우기 (http://localhost:8765)
  python3 engine/studio.py wait <id> [--timeout 초] # 답이 올 때까지 기다림 (Claude Code: 백그라운드로 돌린다)
  python3 engine/studio.py list                   # 대기 중인 요청

요청 파일 모양:
  {"id": "...", "title": "...", "question": "...", "source": "episodes/drafts/....md",
   "body": "마크다운(보기 자료, 안 위에)", "after": "마크다운(긴 자료, 보내기 아래)", "options": [{"id": "1", "title": "...", "body": "마크다운"}], "reason": true}
요청 쓰는 규칙(화면이 이것에 기대어 있다. 전체 절차는 rules/studio.md):
  - question 첫 문장 = 봐 달라는 것 하나. 길면 화면에서 두 줄로 접힌다
  - body 의 첫 mp4 는 왼쪽에 고정된다. 영상 시각은 목록 맨 앞에 **N초** 로 쓰면 누르는 단추가 된다
  - 그림 캡션에 그림 이름(에셋 이름)을 넣는다 — [고칠 것]을 누르면 캡션이 메모에 들어간다
  - 안 id "fix" 는 메모가 있어야 보내진다. 안이 3개 이하면 맨 아래 바의 단추로, 4개 이상이면 카드에서 고른다
표준 라이브러리만 쓴다. localhost 에만 붙는다.
"""
import subprocess, html, json, re, sys, threading, time, os, urllib.parse
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
        IMG = r"!\[([^\]]*)\]\((kit/[^)\s]+)\)"
        if re.fullmatch(r"(\s*" + IMG + r")+\s*", s):  # 그림 줄 → 그림판(kit 안만). 빈 줄로 떨어진 그림 줄도 한 판으로 모은다
            imgs = []
            while i < len(lines):
                t = lines[i].strip()
                if not t: i += 1; continue
                if not re.fullmatch(r"(\s*" + IMG + r")+\s*", t): break
                imgs += re.findall(IMG, t); i += 1
            fig = lambda a, f: (f'<figure class="shot"><video controls preload="metadata" playsinline src="/{E(f)}"></video><figcaption>{E(a)}</figcaption></figure>' if f.endswith(".mp4")
                               else f'<figure class="shot"><img loading="lazy" src="/{E(f)}" alt="{E(a)}"><figcaption>{E(a)}</figcaption></figure>')
            out.append('<div class="shots">' + "".join(fig(a, f) for a, f in imgs) + "</div>"); continue
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

assert md("![a](kit/a.jpg)\n\n![b](kit/b.jpg)").count('class="shots"') == 1
assert "<h2>가</h2>" in md("# 가") and 'class="strip"' in md("> **윙키** 넵!") and "<td>2</td>" in md("|a|b|\n|-|-|\n|1|2|") and 'class="shot"' in md("![a](kit/x.jpg)") and "<video" in md("![v](kit/x.mp4)") and "<img" not in md("![a](../x.jpg)")

# ---------- 결정 요청 ----------
def requests():
    REQ.mkdir(parents=True, exist_ok=True)
    out = []
    for p in sorted(REQ.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        r = json.loads(p.read_text(encoding="utf-8"))
        a = ANS / f"{r['id']}.json"
        r["answer"] = json.loads(a.read_text(encoding="utf-8")) if a.exists() else None
        r["_t"] = p.stat().st_mtime
        out.append(r)
    return out

def refuse(req, data, answered):
    """요청 상태: 열림 → 답함(한 번만). 받을 수 없는 답이면 (코드, 까닭), 받을 수 있으면 None."""
    if req is None: return 400, "요청 없음"
    if answered: return 409, "이미 답한 요청"     # 에이전트가 첫 답으로 이미 움직였다. 덮어쓰면 아무도 모른다
    ids = [o["id"] for o in req.get("options", [])]
    if ids and data.get("choice") not in ids: return 400, "없는 안"
    if data.get("choice") == "fix" and not (data.get("reason") or "").strip(): return 400, "고칠 것을 적어 주세요"

_R = {"options": [{"id": "go"}, {"id": "fix"}]}
assert refuse(_R, {"choice": "go"}, False) is None and refuse(_R, {"choice": "go"}, True)[0] == 409 and refuse(None, {}, False)[0] == 400
assert refuse(_R, {"choice": "x"}, False)[0] == 400 and refuse(_R, {"choice": "fix", "reason": " "}, False)[0] == 400 and refuse(_R, {"choice": "fix", "reason": "0:48 입"}, False) is None

ANSWERING = threading.Lock()
def answer(data):
    rid = re.sub(r"[^\w.-]", "", data.get("id", "")); rf, af = REQ / f"{rid}.json", ANS / f"{rid}.json"
    with ANSWERING:
        no = refuse(json.loads(rf.read_text(encoding="utf-8")) if rid and rf.exists() else None, data, af.exists())
        if no: return no
        ANS.mkdir(parents=True, exist_ok=True)
        data["at"] = time.strftime("%Y-%m-%d %H:%M")
        tmp = af.with_suffix(".tmp"); tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"); os.replace(tmp, af)   # wait가 반쯤 쓴 답을 읽지 않게
    return 200, "ok"

NAME2KEY = {"윙키": "winky", "곰 아빠": "bear", "판다": "panda", "펭귄 선생님": "penguin", "거북 여사": "turtle", "너구리 대리": "raccoon", "고양이 사장": "cat", "다람쥐 코치": "squirrel", "도치 실장": "hedgehog"}
CAST = ["윙키", "곰 아빠", "판다", "펭귄 선생님", "거북 여사", "너구리 대리", "고양이 사장", "다람쥐 코치", "도치 실장"]
COLOR = {"윙키": "#e2a54b", "곰 아빠": "#8a5a3c", "판다": "#555", "펭귄 선생님": "#3b6e9c", "거북 여사": "#6f8f4e",
         "너구리 대리": "#8c7a63", "고양이 사장": "#d0773f", "다람쥐 코치": "#b5622f", "도치 실장": "#7a6f8f"}

def registry():
    return json.loads((ROOT / "kit/registry.json").read_text(encoding="utf-8"))

def face(name, reg=None):
    """인물 대표 그림(있으면) 또는 색 동그라미."""
    reg = reg or registry(); key = NAME2KEY.get(name)
    if key:
        its = [(k, it["file"]) for k, it in reg.get("items", {}).items() if it.get("actor") == key and it.get("kind") == "actor" and it.get("file", "").endswith(".webp")]
        rank = lambda kf: next((i for i, t in enumerate(["상반신-평온", "bust-calm", "서기-평온", "stand-calm", "calm", "평온"]) if t in kf[0] + kf[1] and "퇴근" not in kf[0]), 9)
        pick = min(its, key=rank)[1] if its else None  # 정면 상반신 평온 먼저, 뒤돌기·손은 대표로 안 씀
        if pick: return f'<span class="face"><img src="/{E(pick)}" alt=""></span>'
    return f'<span class="face none" style="--c:{COLOR.get(name, "#999")}">{E(name[0])}</span>'

def chips(h):
    """목록·굵은 글씨 맨 앞의 「N초」를 영상 넘기기 단추로(본문 다른 초는 길이라서 안 건드림)."""
    f = lambda m: f'{m.group(1)}<button type="button" class="t" data-s="{m.group(2)}">▶ {int(m.group(2)) // 60}:{int(m.group(2)) % 60:02d}</button>'
    return re.sub(r"(<li><strong>|<li>|<strong>)(\d{1,3})초", f, h)

assert 'data-s="48"' in chips("<li><strong>48초 「네?」</strong></li>") and "data-s" not in chips("<p>0.3초 늘렸습니다</p>")

VID = re.compile(r'<div class="shots"><figure class="shot"><video[^>]*src="([^"]+)"></video><figcaption>(.*?)</figcaption></figure></div>')

def req_html(r):
    """영상이 있으면 2단(왼쪽 영상 고정 | 오른쪽 근거), 맨 아래 행동 바 고정 — 2026-11-16 Fable UX 검토."""
    a, rid, opts = r["answer"], E(r["id"]), r.get("options", [])
    many = len(opts) > 3   # 이야기 고르기처럼 안이 많으면 카드에서 고르고 바에서 보낸다
    cards = []
    for o in opts:
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
        if not body.strip() and not who and not many: continue   # 설명 없는 안은 바의 단추로 충분
        btn = f'<button class="pick" data-r="{rid}" data-o="{oid}">이 안으로</button>' if many and not a else ""
        cards.append(f'<article class="choice{" chosen" if chosen else ""}" id="o-{rid}-{oid}"><p class="num">「{E(o["title"])}」을 고르면</p>{who}{body}{btn}</article>')
    bh = md(r.get("body", "")); m = VID.search(bh); stage = ""
    if m:
        bh = re.sub(r"<h5>[^<]*</h5>\s*$", "", bh[:m.start()]) + bh[m.end():]   # 영상 바로 위 제목은 영상과 함께 왼쪽으로
        bh = re.sub(r"<h5>[^<]*</h5>\s*(?=<h5>|$)", "", bh)   # 내용 없이 남은 제목
        stage = (f'<aside class="stage"><video controls playsinline preload="metadata" src="{m.group(1)}"></video><p class="meta">{m.group(2)}</p>'
                 + ("" if a else '<button type="button" class="now">지금 초를 메모에 넣기</button>') + "</aside>")
    ev = chips(bh + (f'<h5>안마다 하는 일</h5><div class="choices">{"".join(cards)}</div>' if cards and not many else f'<div class="choices">{"".join(cards)}</div>' if cards else "") + md(r.get("after", "")))
    src = f'<p class="meta src">원문 <code>{E(r["source"])}</code></p>' if r.get("source") else ""
    if a:
        pick = next((o["title"] for o in opts if o["id"] == a.get("choice")), None)
        foot = f'<p class="done">{E(a.get("at",""))}에 답함{(" · 「" + E(pick) + "」") if pick else " · 의견만"}{(" · " + E(a["reason"])) if a.get("reason") else ""}</p>'
    else:
        btns = (f'<button class="opt pri" data-r="{rid}" data-o="">고른 안으로 보내기</button>' if many else
                "".join(f'<button class="opt{" pri" if k == 0 else ""}" data-r="{rid}" data-o="{E(o["id"])}" data-need="{int(o["id"] == "fix")}">{E(o["title"])}</button>' for k, o in enumerate(opts)))
        foot = (f'<div class="act" id="s-{rid}"><div class="memo"><textarea id="r-{rid}" rows="1" aria-label="메모" placeholder="고칠 것·의견 — 그림의 [고칠 것]이나 영상 초 단추를 누르면 여기 들어갑니다"></textarea>'
                f'<p class="picked" id="p-{rid}"></p></div><div class="btns">{btns}</div></div>')
    return f"""<section class="req {'answered' if a else 'open'}{' media' if stage else ''}" id="q-{rid}"><div class="hd"><p class="eyebrow">{'답한 요청' if a else '결정해 주세요'}</p>
      <h2>{E(r["title"])}</h2><p class="lead">{inline(r.get("question",""))}</p></div>{stage}<div class="ev">{ev}{src}</div>{foot}</section>"""

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
    """문서마다 접고 최신 것만 펼친다(통째로 이으면 6만 px)."""
    files = sorted((ROOT / "episodes").glob("drafts/*.md"), reverse=True) + sorted((ROOT / "episodes").glob("ep*/*.md"))
    def one(i, f):
        rel = str(f.relative_to(ROOT)); t = next((l[2:] for l in f.read_text(encoding="utf-8").splitlines() if l.startswith("# ")), f.stem)
        return f'<details class="docx"{" open" if i == 0 else ""}><summary><b>{E(t)}</b><span class="meta">{E(rel)}</span></summary>{doc(rel)}</details>'
    return "".join(one(i, f) for i, f in enumerate(files)) or "<p>아직 대본이 없습니다.</p>"

IMG_EXT = (".webp", ".png", ".jpg")
def fig(k, f, cap=None, draft=False):
    return f'<figure class="{"draft" if draft else ""}"><img loading="lazy" src="/{E(f)}" alt="{E(k)}"><figcaption>{E(cap or k)}{"<small>승인 기다림</small>" if draft else ""}</figcaption></figure>'

def waiting(reg):
    return [(k, it) for k, it in reg.get("items", {}).items() if it.get("status") != "approved" and it.get("file", "").endswith(IMG_EXT)]

def assets_tab():
    reg = registry(); items = reg.get("items", {})
    w = waiting(reg)
    out = [f'<h2>승인 기다림 <span class="meta">{len(w)}장</span></h2><div class="grid big">{"".join(fig(k, it["file"], draft=True) for k, it in w)}</div>' if w else ""]
    out.append('<h2>인물</h2><div class="cast">')
    for n in CAST:
        key = NAME2KEY.get(n)
        poses = [(k, it["file"]) for k, it in items.items() if key and it.get("actor") == key and it.get("file", "").endswith((".webp", ".png"))]
        poses.sort(key=lambda kf: items[kf[0]].get("status") == "approved")
        nd = sum(1 for k, _ in poses if items[k].get("status") != "approved")
        st = ("그림 " + str(len(poses)) + "장" + (f' · <b class="wait">승인 기다림 {nd}</b>' if nd else "")) if poses else "그림 없음"
        grid = "".join(fig(k, f, k.split("-", 1)[-1], items[k].get("status") != "approved") for k, f in poses)
        more = f'<details><summary>자세·표정 {len(poses)}개 보기</summary><div class="grid">{grid}</div></details>' if poses else '<p class="meta">대본이 정해지면 winky-assets로 만든다</p>'
        out.append(f'<article class="person{"" if poses else " empty"}">{face(n, reg)}<div><h3>{E(n)}</h3><p class="meta">{st}</p>{more}</div></article>')
    out.append("</div>")
    rest = {}
    for k, it in items.items():
        if it.get("kind") != "actor" and it.get("file", "").endswith(IMG_EXT):
            rest.setdefault(it.get("kind", "기타"), []).append((k, it["file"]))
    KIND = {"set": "세트", "prop": "소품", "hand": "손", "fx": "효과", "logo": "로고", "ui": "화면 요소"}
    for kind, lst in sorted(rest.items(), key=lambda kv: list(KIND).index(kv[0]) if kv[0] in KIND else 99):
        out.append(f'<h2>{E(KIND.get(kind, kind))} <span class="meta">{len(lst)}</span></h2><div class="grid">{"".join(fig(k, f) for k, f in lst)}</div>')
    return "".join(out)

def decide_tab(reqs):
    """열린 요청만 크게. 답한 요청은 날짜별 한 줄 기록(누르면 원래 화면) — 2026-11-13 미르님 「결정에 쌓인다」."""
    opn = "".join(req_html(r) for r in reqs if not r["answer"]) or '<p class="meta">지금 기다리는 결정이 없습니다.</p>'
    done = sorted((r for r in reqs if r["answer"]), key=lambda r: r["answer"].get("at", ""), reverse=True)
    rows, day = [], None
    for r in done:
        a = r["answer"]; d = a.get("at", "")[:10]
        if d != day: rows.append(f'<h3 class="day">{E(d)}</h3>'); day = d
        pick = next((o["title"] for o in r.get("options", []) if o["id"] == a.get("choice")), "의견만")
        rows.append(f'<details class="log"><summary><span class="t">{E(a.get("at", "")[11:])}</span><b>{E(r["title"])}</b><span class="chose">→ {E(pick)}</span>'
                    f'{("<q>" + E(a["reason"]) + "</q>") if a.get("reason") else ""}</summary>{req_html(r)}</details>')
    return f'<h2>기다리는 결정</h2>{opn}<h2>지난 결정 <span class="meta">{len(done)}</span></h2><div class="logs">{"".join(rows)}</div>'

def changes_tab():
    """최근 고친 것(커밋) — 개발 기록이라 한눈에서 자료로 내렸다."""
    try: log = subprocess.run(["git", "log", "-30", "--format=%ad\t%s", "--date=format:%m-%d %H:%M"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    except OSError: log = []
    tidy = lambda m: re.sub(r"^\w+\([^)]*\):\s*", "", m)
    return '<article class="doc"><h2>최근 고친 것</h2><ul class="changes">' + "".join(
        f'<li><span class="t">{E(l.split(chr(9))[0])}</span><span>{E(tidy(l.split(chr(9), 1)[-1]))}</span></li>' for l in log) + "</ul></article>"

def first_mp4(r):
    m = re.search(r"\]\((kit/[^)\s]+\.mp4)\)", r.get("body", "") + r.get("after", "")); return m and m.group(1)

def films():
    """완성 영상: episodes/<회차>/out/<회차>.mp4, 새것 먼저."""
    fs = [p for p in (ROOT / "episodes").glob("*/out/*.mp4") if p.stem == p.parent.parent.name]
    return sorted(fs, key=lambda p: p.stat().st_mtime, reverse=True)

def overview(reqs):
    reg = registry()
    open_r = [r for r in reqs if not r["answer"]]
    def turn(r):
        v = first_mp4(r); n = len(re.findall(r"!\[[^\]]*\]\(kit/[^)]+\.(?:jpg|png|webp)\)", r.get("body", "") + r.get("after", "")))
        what = " · ".join(x for x in ["영상" if v else "", f"그림 {n}장" if n else "", f"{len(r.get('options', []))}안"] if x)
        poster = f'<video muted playsinline preload="metadata" src="/{E(v)}#t=1"></video>' if v else ""
        return (f'<a class="turn" href="#q-{E(r["id"])}">{poster}<div><b>{E(r["title"])}</b><span class="meta">{what} · {time.strftime("%m-%d %H:%M", time.localtime(r["_t"]))} 올라옴</span>'
                f'<span class="cta">보고 결정하기 →</span></div></a>')
    if open_r:
        first = f'<section class="panel wide mine"><p class="eyebrow">지금 내 차례 {len(open_r)}건</p>{"".join(turn(r) for r in open_r)}</section>'
    else:
        last = max((r for r in reqs if r["answer"]), key=lambda r: r["answer"].get("at", ""), default=None)
        lp = last and next((o["title"] for o in last.get("options", []) if o["id"] == last["answer"].get("choice")), "의견만")
        first = (f'<section class="panel wide"><p class="eyebrow">지금 내 차례</p><p class="big">기다리는 결정 없음</p>'
                 + (f'<p class="meta">마지막 답 {E(last["answer"].get("at", ""))} · {E(last["title"])} → 「{E(lp)}」</p>' if last else "") + "</section>")
    w = waiting(reg)
    wait = (f'<section class="panel wide"><p class="eyebrow">승인 기다리는 그림 {len(w)}장</p><div class="grid big">{"".join(fig(k, it["file"], draft=True) for k, it in w)}</div></section>') if w else ""
    fl = films()
    film = (f'<section class="panel film"><p class="eyebrow">가장 최근 완성 영상</p><video controls playsinline preload="metadata" src="/{E(str(fl[0].relative_to(ROOT)))}"></video>'
            f'<p class="meta">{E(fl[0].stem)} · {time.strftime("%m-%d %H:%M", time.localtime(fl[0].stat().st_mtime))}</p></section>') if fl else ""
    ms = (ROOT / "MILESTONE.md").read_text(encoding="utf-8")
    done, left = len(re.findall(r"^- \[x\]", ms, re.M)), re.findall(r"^- \[ \] (.+)$", ms, re.M)
    pct = round(100 * done / max(1, done + len(left)))
    short = lambda x: re.sub(r"`[^`]*`|\(.*?\)|\*\*", "", x).split("→")[0].split(":")[0].strip()[:40]
    nxt = "".join(f"<li>{E(short(x))}</li>" for x in left[:3])
    drafts = sorted((ROOT / "episodes/drafts").glob("*.md")) if (ROOT / "episodes/drafts").exists() else []
    cast = "".join(f'<a class="mini" href="#people">{face(n, reg)}<span>{E(n)}</span></a>' for n in CAST)
    return f"""<div class="home">{first}{wait}{film}
      <section class="panel"><p class="eyebrow">진행</p><div class="bar"><i style="width:{pct}%"></i></div><p class="big">{pct}%</p><p class="meta">끝낸 일 {done} · 남은 일 {len(left)} · 완성 영상 {len(fl)}편 · 대본 초안 {len(drafts)}개</p>
      <p class="sub">다음 할 일</p><ul class="next">{nxt}</ul><a class="more-link" href="#milestone">마일스톤 전체</a></section>
      <section class="panel wide"><p class="eyebrow">인물 9명</p><div class="minis">{cast}</div></section>
    </div>"""

def page():
    reqs = requests(); n_open = sum(1 for r in reqs if not r["answer"])
    tabs = [("home", "한눈에", overview(reqs)),
            ("decide", "결정" + (f' <em>{n_open}</em>' if n_open else ""), decide_tab(reqs)),
            ("people", "인물", '<iframe src="/characters" title="인물 바이블"></iframe>'),
            ("scripts", "대본", scripts_tab()),
            ("assets", "그림", assets_tab())]
    for tid, name, files in DOCS:
        tabs.append((tid, name, "".join(doc(f) for f in files if (ROOT / f).exists())))
    tabs.append(("changes", "최근 고친 것", changes_tab()))
    prim = [t for t in tabs if t[0] in ("home", "decide", "people", "scripts", "assets")]
    more = [t for t in tabs if t not in prim]
    nav = "".join(f'<a href="#{t}" data-t="{t}">{n}</a>' for t, n, _ in prim)
    nav += '<details class="more"><summary data-t="more">자료</summary><div>' + "".join(f'<a href="#{t}" data-t="{t}">{n}</a>' for t, n, _ in more) + "</div></details>"
    secs = "".join(f'<section class="tab" id="{t}" hidden>{b}</section>' for t, _, b in tabs)
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>윙키 스튜디오</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jua&family=IBM+Plex+Sans+KR:wght@400;500;600&display=swap"><style>{CSS}</style></head><body>
<header><div class="bar-in"><a class="brand" href="#home">윙키 스튜디오<small>모래언덕 빌라</small></a><nav>{nav}</nav></div></header>
<div id="fresh" hidden><span>새 내용이 올라왔습니다</span><button type="button" onclick="location.reload()">새로 보기</button></div><main>{secs}</main>
<dialog id="lb"><img alt=""><div class="lbbar"><button type="button" class="prev" aria-label="이전">←</button><p></p><button type="button" class="lbflag">고칠 것</button><button type="button" class="next" aria-label="다음">→</button></div></dialog><script>{JS}</script></body></html>"""

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
.home{grid-template-columns:minmax(0,320px) minmax(0,1fr)}
.turn{display:flex;gap:24px;align-items:center;text-decoration:none;color:var(--ink);background:var(--surface);border-radius:12px;padding:16px;min-height:72px}
.turn video{width:160px;aspect-ratio:9/16;object-fit:cover;background:#000;border-radius:8px;flex:none;pointer-events:none}
.turn div{display:flex;flex-direction:column;gap:8px}.turn b{font:400 26px/1.3 var(--f-d)}
.cta{align-self:flex-start;min-height:56px;display:inline-flex;align-items:center;padding:0 28px;border-radius:12px;background:var(--accent);color:var(--surface);font-weight:600;font-size:17px}
.film video{width:100%;max-width:280px;aspect-ratio:9/16;background:#000;border-radius:12px}
.minis{grid-template-columns:repeat(auto-fill,minmax(88px,1fr))!important}
.minis{display:grid;grid-template-columns:repeat(3,1fr);gap:12px 8px;margin:8px 0}.mini{display:flex;flex-direction:column;align-items:center;gap:4px;text-decoration:none;color:var(--ink);font-size:14px;text-align:center}
.big{font-family:var(--f-d);font-size:30px;margin:0;line-height:1.2}.big small{font-family:var(--f-b);font-size:16px;color:var(--mute);margin-left:4px}
.sub{font-size:14px;font-weight:600;margin:8px 0 0}.bar{height:8px;background:var(--line);border-radius:4px;overflow:hidden}.bar i{display:block;height:100%;background:var(--accent)}
.next{margin:0;padding-left:20px;font-size:16px}.more-link{margin-top:auto;min-height:44px;display:flex;align-items:center;font-weight:600}.more-link::after{content:" →";white-space:pre}
.face{display:inline-grid;place-items:center;width:52px;height:52px;border-radius:50%;overflow:hidden;background:var(--bg);flex:none}
.face img{width:100%;height:100%;object-fit:cover;object-position:50% 12%}.face.none{background:var(--c);color:#fff;font-family:var(--f-d);font-size:22px}
/* 결정 */
.req{margin-bottom:48px}.req h2{font-size:30px;margin-bottom:8px}.lead{font-size:18px;max-width:60ch;margin:0 0 8px}
.lead.clamp{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.more-lead{border:0;background:none;color:var(--accent);font:600 15px var(--f-b);padding:0;min-height:32px;cursor:pointer}
.req h4,.req h5{font:400 22px/1.3 var(--f-d);margin:32px 0 12px;padding-top:16px;border-top:1px solid var(--line)}.ev>h5:first-child{border-top:0;padding-top:0;margin-top:0}
.req.media{display:grid;grid-template-columns:380px minmax(0,1fr);gap:0 32px}.req.media>.hd,.req.media>.act,.req.media>.done{grid-column:1/-1}.hd{margin-bottom:24px}
.stage{position:sticky;top:76px;align-self:start;display:flex;flex-direction:column;gap:8px}
.stage video{width:100%;height:min(676px,calc(100vh - 230px));background:#000;border-radius:12px;display:block}
.now,.lbflag,.flag{min-height:44px;border:1px solid var(--accent);border-radius:10px;background:var(--surface);color:var(--accent);font:600 15px var(--f-b);cursor:pointer;padding:0 14px}
.t{display:inline-flex;align-items:center;min-height:36px;padding:0 12px;margin:0 6px 0 0;border-radius:999px;border:1px solid var(--accent);background:var(--tint);color:var(--accent);font:600 15px var(--f-b);font-variant-numeric:tabular-nums;cursor:pointer;vertical-align:middle}
.shot{position:relative}.shot .flag{position:absolute;right:12px;top:12px;background:color-mix(in srgb,var(--surface) 92%,transparent)}
figure.flagged{outline:3px solid #d0773f;outline-offset:2px}figure.flagged .flag,.lbflag.on{background:#d0773f;border-color:#d0773f;color:#fff}
.act{position:sticky;bottom:0;z-index:4;display:flex;gap:12px;align-items:flex-start;padding:12px 16px;margin-top:24px;background:var(--surface);border:1px solid var(--line);border-radius:16px 16px 0 0;box-shadow:0 -8px 24px #0000001a}
.memo{flex:1;min-width:0}.memo textarea{width:100%;min-height:48px;max-height:160px;font:inherit;padding:10px 12px;border:1px solid var(--mute);border-radius:12px;background:var(--bg);color:var(--ink);resize:none;display:block}
.picked{margin:4px 0 0;font-size:14px;color:var(--mute);min-height:1em}.picked:empty{display:none}
.btns{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}
.opt{min-height:48px;padding:0 20px;border:2px solid var(--accent);border-radius:12px;background:var(--surface);color:var(--accent);font:600 16px var(--f-b);cursor:pointer}.opt.pri{background:var(--accent);color:var(--surface)}
.opt:disabled{opacity:.5;cursor:default}.sent{margin:0;font-weight:600;color:var(--accent);font-size:17px}
.src{margin-top:32px}
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
.day{font-size:14px;margin:20px 0 6px;color:var(--mute)}.log{border-top:1px solid var(--line)}.log>summary{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;padding:12px 4px;cursor:pointer;list-style:none}
.log>summary .t,.changes .t{font-variant-numeric:tabular-nums;color:var(--mute);font-size:14px;min-width:48px;flex:none}.log>summary .chose{color:var(--accent);font-weight:600}.log>summary q{flex-basis:100%;color:var(--mute);font-size:14px;margin-left:60px}
.log[open]>summary{background:var(--tint)}.changes{list-style:none;padding:0;margin:0}.changes li{display:flex;gap:12px;padding:6px 0;border-top:1px solid var(--line);font-size:15px}
.wait{color:var(--accent)}.person figure.draft{outline:3px solid var(--accent);border-radius:8px}.person figcaption small{display:block;color:var(--accent);font-size:12px}
figure.draft{outline:3px solid var(--accent)}figcaption small{display:block;color:var(--accent);font-size:13px}
.done{color:var(--accent);font-weight:600;margin-top:16px}.req.answered .choice:not(.chosen){opacity:.6}
.docx{max-width:860px;margin:0 auto 12px}.docx>summary{display:flex;flex-direction:column;gap:2px;min-height:56px;justify-content:center;padding:8px 16px;background:var(--surface);border:1px solid var(--line);border-radius:12px;list-style:none}.docx>summary b{font:400 20px var(--f-d)}.docx[open]>summary{margin-bottom:12px}
#fresh{position:fixed;top:72px;left:50%;transform:translateX(-50%);z-index:6;display:flex;gap:12px;align-items:center;background:var(--ink);color:var(--surface);padding:8px 8px 8px 20px;border-radius:999px;box-shadow:0 8px 24px #0003}#fresh[hidden]{display:none}#fresh button{min-height:40px;border:0;border-radius:999px;padding:0 16px;background:var(--accent);color:var(--surface);font:600 15px var(--f-b);cursor:pointer}
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
.tab>h2{font-size:22px;margin:32px 0 12px}.cast{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr));gap:16px;align-items:start}
.person{display:flex;gap:16px;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:16px;min-width:0}
.person>div{min-width:0;flex:1}.person h3{font-size:22px}.person .face{width:72px;height:72px}.person.empty{border-style:dashed}
.person details summary{min-height:44px;display:flex;align-items:center;color:var(--accent);font-weight:600}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:8px;margin-top:8px}.grid.big{grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}.grid.big img{height:240px}figure{margin:0;background:var(--bg);border-radius:8px;padding:8px}
figure img{width:100%;height:160px;object-fit:contain;cursor:zoom-in}
.shots{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr));gap:16px;margin:12px 0}.shots:has(>figure:only-child){grid-template-columns:1fr}.shot img{height:auto;max-height:78vh}.shot video{width:100%;max-height:82vh;background:#000;border-radius:8px}.choices:has(.shots){grid-template-columns:1fr}
#lb{border:0;padding:0;background:transparent;max-width:96vw;max-height:96vh}#lb::backdrop{background:rgba(0,0,0,.85)}#lb img{display:block;max-width:96vw;max-height:calc(96vh - 64px);object-fit:contain;cursor:zoom-out;margin:0 auto}
.lbbar{display:flex;gap:12px;align-items:center;justify-content:center;margin-top:8px}.lbbar p{color:#fff;margin:0;font-size:15px;min-width:12ch;text-align:center}
.lbbar .prev,.lbbar .next{min-width:56px;min-height:44px;border:1px solid #fff6;border-radius:10px;background:#0006;color:#fff;font-size:20px;cursor:pointer}figcaption{font-size:14px;color:var(--mute);text-align:center;word-break:break-all}
@media (max-width:860px){.home{grid-template-columns:1fr}.brand{display:none}.bar-in{flex-wrap:nowrap;padding-top:2px;padding-bottom:2px}
nav{flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}nav a,nav summary{white-space:nowrap}.more{position:static}.more>div{position:fixed;right:8px;top:52px;z-index:7}
.req.media{display:block}.stage{position:static}.stage video{height:min(70vh,calc((100vw - 32px)*16/9))}
.shots{display:flex;overflow-x:auto;scroll-snap-type:x mandatory;gap:12px}.shots>figure{flex:0 0 85%;scroll-snap-align:start}
.act{flex-direction:column;align-items:stretch;padding-bottom:max(12px,env(safe-area-inset-bottom))}.btns>*{flex:1}
.turn{gap:16px;padding:12px}.turn video{width:96px}.turn b{font-size:20px}}
@media (max-width:600px){main{padding-top:24px}.req h2,.doc h2{font-size:22px}.lead{font-size:16px}nav a,nav summary{padding:0 10px}.brand small{display:none}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
"""

JS = """
const $$=(q,el=document)=>[...el.querySelectorAll(q)],fmt=s=>Math.floor(s/60)+':'+String(Math.floor(s%60)).padStart(2,'0');
const cap=im=>im.closest('figure')?.querySelector('figcaption')?.textContent||im.alt||'';
/* 고칠 것 표시: 그림을 찍으면 메모에 「캡션: 」 줄 */
function memo(req){return req&&req.querySelector('.act textarea')}
function grow(t){t.style.height='auto';t.style.height=Math.min(t.scrollHeight+2,160)+'px'}
function addLine(req,line){const t=memo(req);if(!t)return;t.value=(t.value.trim()?t.value.replace(/\\s*$/,'')+'\\n':'')+line;grow(t);t.focus();t.setSelectionRange(t.value.length,t.value.length);count(req)}
function count(req){const n=$$('figure.flagged',req).length,p=req.querySelector('.picked');if(p&&!p.dataset.lock)p.textContent=n?'고칠 것으로 표시한 그림 '+n+'장':''}
function flag(fig){const req=fig.closest('.req.open');if(!req)return;const c=cap(fig.querySelector('img')),t=memo(req);
if(fig.classList.toggle('flagged'))addLine(req,c+': ');else{t.value=t.value.split('\\n').filter(l=>!l.startsWith(c+':')).join('\\n');grow(t);count(req)}
lbSync()}
$$('.req.open figure.shot').forEach(f=>{if(!f.querySelector('img'))return;const b=document.createElement('button');b.type='button';b.className='flag';b.textContent='고칠 것';f.append(b)});
/* 라이트박스: 같은 요청·격자 안에서 ← → 넘기기 */
const lb=document.getElementById('lb'),lbImg=lb.querySelector('img'),lbP=lb.querySelector('p'),lbF=lb.querySelector('.lbflag');let lbL=[],lbI=0;
function lbShow(i){lbI=(i+lbL.length)%lbL.length;const im=lbL[lbI];lbImg.src=im.src;lbP.textContent=cap(im)+(lbL.length>1?'  ·  '+(lbI+1)+' / '+lbL.length:'');lbSync()}
function lbSync(){const im=lbL[lbI],f=im&&im.closest('figure'),on=!!f&&f.classList.contains('flagged');lbF.hidden=!(f&&f.closest('.req.open')&&f.classList.contains('shot'));lbF.classList.toggle('on',on);lbF.textContent=on?'고칠 것 ✓':'고칠 것'}
lb.querySelector('.prev').onclick=()=>lbShow(lbI-1);lb.querySelector('.next').onclick=()=>lbShow(lbI+1);lbF.onclick=()=>flag(lbL[lbI].closest('figure'));
lb.addEventListener('click',e=>{if(e.target===lb||e.target===lbImg)lb.close()});
addEventListener('keydown',e=>{if(!lb.open)return;if(e.key==='ArrowLeft')lbShow(lbI-1);if(e.key==='ArrowRight')lbShow(lbI+1)});
document.addEventListener('click',e=>{
 const fb=e.target.closest('.flag');if(fb){flag(fb.closest('figure'));return}
 const t=e.target.closest('.t');if(t){const v=t.closest('.req')?.querySelector('video');if(v){v.currentTime=+t.dataset.s;v.play();if(matchMedia('(max-width:860px)').matches)v.scrollIntoView({behavior:'smooth',block:'center'})}return}
 const nw=e.target.closest('.now');if(nw){const req=nw.closest('.req'),v=req.querySelector('.stage video');addLine(req,fmt(v.currentTime)+' ');return}
 const i=e.target.closest('figure img');if(i&&!lb.open){lbL=$$('figure img',i.closest('.req,.grid,.shots')||document);lbShow(lbL.indexOf(i));lb.showModal()}});
/* 탭 */
function show(){const t=(location.hash||'#home').slice(1);const tab=document.getElementById(t)?.closest('.tab')||document.getElementById('home');
$$('.tab').forEach(s=>s.hidden=s!==tab);
$$('nav a').forEach(a=>a.classList.toggle('on',a.dataset.t===tab.id));const m=document.querySelector('.more');m.removeAttribute('open');m.querySelector('summary').classList.toggle('on',!!m.querySelector('a.on'));
clampLeads();if(document.getElementById(t)&&t!==tab.id)document.getElementById(t).scrollIntoView();else setTimeout(()=>scrollTo(0,0),0)}
addEventListener('hashchange',show);
$$('.doc').forEach(d=>{const hs=$$('h3',d);if(hs.length<4)return;
const ol=document.createElement('ol');ol.className='toc';hs.forEach(h=>{h.id=h.id||('t'+Math.random().toString(36).slice(2,8));
const li=document.createElement('li');const a=document.createElement('a');a.href='#';a.textContent=h.textContent;a.onclick=e=>{e.preventDefault();h.scrollIntoView({behavior:'smooth'})};li.append(a);ol.append(li)});
(d.querySelector('h2')||d.firstChild).after(ol)});
/* 긴 설명은 두 줄로 접기 */
function clampLeads(){$$('.req .lead:not([data-c])').forEach(l=>{if(!l.offsetParent)return;l.dataset.c=1;l.classList.add('clamp');if(l.scrollHeight<=l.clientHeight+2){l.classList.remove('clamp');return}
const b=document.createElement('button');b.type='button';b.className='more-lead';b.textContent='더 보기';b.onclick=()=>{l.classList.toggle('clamp');b.textContent=l.classList.contains('clamp')?'더 보기':'접기'};l.after(b)})}
document.addEventListener('toggle',clampLeads,true);
show();
/* 보내기 */
const picked={};
$$('.pick').forEach(b=>b.onclick=()=>{const r=b.dataset.r,o=b.dataset.o;picked[r]=o;
$$('#q-'+CSS.escape(r)+' .choice').forEach(c=>c.classList.toggle('sel',c.id==='o-'+r+'-'+o));
const p=document.getElementById('p-'+r);p.dataset.lock=1;p.textContent='고른 안: '+document.querySelector('#o-'+CSS.escape(r)+'-'+CSS.escape(o)+' .num').textContent.replace('을 고르면','')});
$$('.act textarea').forEach(t=>t.addEventListener('input',()=>grow(t)));
$$('.opt').forEach(b=>b.onclick=()=>send(b));
async function send(b){const id=b.dataset.r,box=document.getElementById('s-'+id),p=document.getElementById('p-'+id),reason=document.getElementById('r-'+id).value.trim();
const choice=b.dataset.o||picked[id]||null;
if(!choice){p.dataset.lock=1;p.textContent='위 카드에서 안을 먼저 골라 주세요.';return}
if(b.dataset.need==='1'&&!reason){p.dataset.lock=1;p.textContent='무엇을 고칠지 적거나, 그림의 [고칠 것]·영상 초를 눌러 주세요.';memo(box.closest('.req')).focus();return}
$$('button',box).forEach(x=>x.disabled=true);
const r=await fetch('/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,choice,reason})}).catch(()=>({ok:false}));
if(r.status===409){box.innerHTML='<p class="sent">이미 답한 요청입니다. 「새로 보기」를 눌러 주세요.</p>';document.getElementById('fresh').hidden=false;return}
if(!r.ok){$$('button',box).forEach(x=>x.disabled=false);p.dataset.lock=1;p.textContent='저장하지 못했습니다. 서버가 켜져 있는지 봐 주세요.';return}
const title=b.dataset.o?b.textContent:(document.querySelector('#o-'+CSS.escape(id)+'-'+CSS.escape(choice)+' .num')?.textContent.replace('을 고르면','')||choice);
box.innerHTML='<p class="sent">✓ '+new Date().toTimeString().slice(0,5)+' 「'+title+'」 보냄 · 에이전트가 이어서 작업합니다</p>';ver=null}
/* 새 내용: 보는 중엔 새로고침하지 않고 띠만 띄운다(다른 탭에 있고 쓰던 메모가 없을 때만 바로 새로고침) */
let ver=null;setInterval(async()=>{try{const v=await (await fetch('/version')).text();
if(ver&&v!==ver){if(document.hidden&&!$$('.act textarea').some(t=>t.value.trim()))location.reload();else document.getElementById('fresh').hidden=false}ver=v}catch(e){}},2000);
"""

def version():  # 화면에 보이는 파일이 바뀌면 값이 바뀐다
    pats = ["rules/*.md", "kit/lexicon/*.md", "episodes/**/*.md", "MILESTONE.md", "studio/**/*.json", "kit/registry.json"]
    return str(max((p.stat().st_mtime for pat in pats for p in ROOT.glob(pat)), default=0))

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype="text/html; charset=utf-8"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-cache"); self.end_headers(); self.wfile.write(b)  # no-cache: 같은 이름으로 고친 그림이 옛것으로 안 보이게
    def do_GET(self):
        p = urllib.parse.unquote(self.path.split("?")[0])  # 한글 파일 이름
        if p == "/": return self.send(200, page())
        if p == "/version": return self.send(200, version(), "text/plain")
        if p == "/characters":
            import studio_characters
            return self.send(200, "<!doctype html><meta charset='utf-8'>" + studio_characters.render((ROOT / "rules/characters.md").read_text(encoding="utf-8")))
        if p.startswith(("/kit/", "/episodes/")):
            f = (ROOT / p.lstrip("/")).resolve()
            if f.is_file() and ((ROOT / "kit") in f.parents or f in films()):  # kit 밖은 완성 영상만
                ct = {".webp": "image/webp", ".png": "image/png", ".jpg": "image/jpeg", ".mp4": "video/mp4"}.get(f.suffix, "application/octet-stream")
                data = f.read_bytes(); rg = re.match(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
                if rg:  # 영상 넘기기(Range)
                    a0 = int(rg.group(1)); a1 = int(rg.group(2) or len(data) - 1); part = data[a0:a1 + 1]
                    self.send_response(206); self.send_header("Content-Type", ct); self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Content-Range", f"bytes {a0}-{a1}/{len(data)}"); self.send_header("Content-Length", str(len(part))); self.end_headers(); self.wfile.write(part); return
                return self.send(200, data, ct)
        self.send(404, "없음", "text/plain; charset=utf-8")
    def do_POST(self):
        if self.path != "/answer": return self.send(404, "없음", "text/plain; charset=utf-8")
        data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        self.send(*answer(data), "text/plain; charset=utf-8")

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
        if not f.exists() and not (REQ / f"{rid}.json").exists(): sys.exit(f"요청 {rid} 가 없다(studio/requests/{rid}.json). id를 확인한다")   # 틀린 id로 한 시간 기다리지 않게
        while time.time() < end:
            if f.exists(): print(f.read_text(encoding="utf-8")); return
            time.sleep(1)
        print(json.dumps({"id": rid, "timeout": True})); sys.exit(2)
    elif cmd == "list":
        for r in requests(): print(("대기 " if not r["answer"] else "끝   ") + r["id"], "-", r["title"])

if __name__ == "__main__":
    main()
