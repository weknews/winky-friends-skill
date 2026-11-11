"""윙키와 친구들 장면 계산(엔진): 크기 레지스트리(mm) × 프리셋 px/mm, 놓이는 곳 넷, 컷 표 → EP/scene.json · EP/scene.js
컷마다 손으로 좌표를 적지 않는다. 좌표는 kit/registry.json(승인된 프리미티브의 mm 크기·앵커)과 회차 표(EP/episode.py의 CUTS, 판 도면)에서 나온다.
원본: ep01-v9/build.py(9e판). 회차 값은 episode.py로 뺐고, 그림 목록은 kit.json 대신 registry.json의 approved 항목만 쓴다.
사용: cd episodes/<회차> && python3 ../../engine/build.py  (또는 EP=episodes/<회차> python3 engine/build.py). Windows는 python3 대신 py"""
import json, os, random, re, sys
import numpy as np
from PIL import Image
from PIL import ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # 레포 뿌리. 그림 경로(kit/...)는 여기 기준
EP = os.path.abspath(os.environ.get("EP", os.getcwd()))                  # 회차 폴더(episode.py, thumb.html, 결과 scene.*·out/)
HERE = EP
sys.stdout.reconfigure(encoding="utf-8")                                 # Windows 콘솔·파이프에서도 한글 출력이 멈추지 않게
import setup_episode; setup_episode.link(EP)                             # 회차 폴더의 kit·fonts·lib·index.html(git에 없다)
REGISTRY = json.load(open(os.path.join(ROOT, "kit/registry.json"), encoding="utf-8"))
# 승인된 그림만 쓴다(draft는 엔진에 보이지 않는다 → check 1번 「이름」에서 걸린다)
K = {n: {k: v for k, v in e.items() if k not in ("kind", "status", "approved", "source", "prompt", "ref", "actor")}
     for n, e in REGISTRY["items"].items() if e.get("status") == "approved"}
FPS, TICK = 30, 1 / 12
q = lambda t: round(round(t * 12) / 12, 4)
# 9b 글꼴(그림체에 맞춤, 모두 OFL): jua = 대사 자막·이름표·근거·표지·끝 화면 큰 줄, dohyeon = 제목·「다음 날」·「그날 저녁」,
#    gaegu = 기록장·상자 손글씨, pre = 끝 화면 작은 줄(읽기 쉬운 Pretendard). index.html @font-face와 같은 이름
FONTS = {"jua": "Jua-Regular.ttf", "dohyeon": "DoHyeon-Regular.ttf", "gaegu": "Gaegu-Bold.ttf", "pre": "Pretendard-ExtraBold.woff2"}
_F = {}
def tw(s, px, font="pre"):                          # 글자 폭(px). CSS letter-spacing -0.02em 반영
    if (font, px) not in _F: _F[font, px] = ImageFont.truetype(os.path.join(ROOT, "kit/fonts", FONTS[font or "pre"]), px)
    return _F[font, px].getlength(s) - 0.02 * px * len(s)
G = lambda s, px: tw(s, px, "gaegu")

# ── 1. 크기 레지스트리 (KIT-SPEC 1절, mm). 머리 폭은 차렷 그림에서 잰 값
#    9판: 기록장(대본 「새로 만들 것」), 손 폭은 인물 원본 그림에서 잰 값(곰 들기 손 140px ÷ 0.847 px/mm, 윙키 양손들기 한 손 190px ÷ 2.0 px/mm),
#    연필은 보통 연필 길이. 손은 손바닥 폭(손가락 마디 가로)으로 배율을 맞춘다.
REG = {"char": {w: a["mm"] for w, a in REGISTRY["actors"].items() if a.get("status") == "approved"}, "prop": REGISTRY["sizes"]}   # kit/registry.json
def PROP_OF(n):
    if n.startswith("cup-"): return "cup"
    if n.startswith("apple"): return "apple"
    if n.startswith("jug"): return "jug"
    if n.startswith("bear-hand"): return "bear-paw"
    if n == "winky-hand": return "winky-paw"
    return n
# ── 2. 세트(배경 실측). base = 화면 폭 1080에 맞춘 배율(0.9375)에서 잰 기준 사물(px)과 px/mm
SETS = {
 "door":    {"CU": dict(bg="set-door-cu", z=1.0, floor=1210)},           # 사양: 바닥선 63% = 1210
 "kitchen": {"M": dict(bg="set-kitchen-w", ref="조리대 윗면 905·밑선 1310 (850mm)", ppm0=405 / 850, base=1310),
             "CU": dict(bg="set-kitchen-cu", z=1.0)},
 "office":  {"M": dict(bg="set-office-m", ref="책상 윗면 930·다리 끝 1318 (750mm)", ppm0=388 / 750, base=1318),
             "CU": dict(bg="set-office-cu", z=1.0)},
 "table":   {"판": dict(bg="set-table", z=1.0)},                          # 9판: 식탁·책상 윗면 근접 판(놓이는 곳 4 「판」)
 "end":     {"board": dict(bg="bg-end", z=1.0)},
}
# ── 3. 프리셋 (KIT-SPEC 2절). M은 7판에서 바꿨다(ep01-v7 README 「기획과 다르게 한 것」 1)
PRESET = {
 "M":  dict(ppm=0.54, pos={"좌": 200, "중": 540, "우": 880}),
 "CU": dict(ppm={"winky": 1.40}, head_top=300, bust_head_px=770),
}
SAFE = dict(l=60, r=1020, t=200, b=1700)
SUB = dict(y0=1500, y1=1700, px=68, lineh=100)
TAG_AT = {"좌하": (350, 1340), "우하": (730, 1340)}      # 9판: 자막 띠 바로 위(사양 1250에서 시작하면 3인 컷 가운데 윙키를 가린다)
CAPTION = dict(y0=220, y1=290, px=56)
FURN = {"table": 750, "counter": 850}           # 세트 고정물 높이(mm). 윗면 = 바닥선 − 80mm − 높이

# ── 4. 목소리 (KIT-SPEC 5절)
VOICE = {w: a["voice"] for w, a in REGISTRY["actors"].items()}   # kit/registry.json actors.*.voice

# ── 음절 박자 (KIT-SPEC 5절 문장 부호·감정). 9판: 「~」 앞 음절은 늘여 읽는다(대본 구어체 규칙) = 0.18초 더
NUM = {"2": "이"}
LONG = 0.18
def syllables(who, t0, text, opt):
    """자막 글자 → [(시각, 글자, 반음, 음량dB, 줄번호, 길게)] 와 끝 시각. 받침·뜻은 상관없다(소리는 sound.py)."""
    v = VOICE[who]; out = []; t = t0; lines = text.split("/")
    for li, s in enumerate(lines):
        emo = opt.get(li, "")
        rate = v["rate"] * (1.2 if emo == "놀람" else 0.8 if emo == "시무룩" else 1)
        s2 = "".join(NUM.get(c, c) for c in s)
        hs = [i for i, c in enumerate(s2) if "가" <= c <= "힣"]
        for i, c in enumerate(s2):
            if c == "…": t += 0.3; continue
            if c == "," and not opt.get("nocomma"): t += 0.15; continue
            if not ("가" <= c <= "힣"): continue
            k = hs.index(i); n = len(hs); semi, db = 0.0, 0.0
            tail = s2[hs[-1] + 1:] if hs else ""
            if "?" in tail and k >= n - 2: semi += 3 if k == n - 2 else 5
            if "!" in tail and k == n - 1: semi += 2; db += 3
            lng = s2[i + 1:i + 2] == "~"
            out.append(dict(t=round(t, 3), ch=c, semi=semi, db=db, line=li, emo=emo, long=lng)); t += 1 / rate + (LONG if lng else 0)
            if s2[i + 1:i + 2] in (".", "?", "!") and k < n - 1: t += 0.12       # 줄 안 문장 끝(「캬~ 맛있다. 한 잔만 더!」)
        if li < len(lines) - 1 and s.rstrip()[-1:] in "!.?~": t += 0.1
    return out, round(t, 3)

def split_lines(text): return [s.strip() for s in text.split("/")]

# ── 배치 계산
def bg_layer(c):
    S = SETS[c["set"]][c["cam"]]; a = K[S["bg"]]
    base = 1080 / a["w"]
    if c["cam"] == "M":
        ppm = PRESET["M"]["ppm"]; z = ppm / S["ppm0"]                     # 배경을 프리셋 px/mm에 맞춰 한 값으로 키운다
        floor = S["base"] * z + 80 * ppm                                   # 뒷벽 가구 밑선 = 바닥선 − 80mm
    else:
        z = S.get("z", 1.0); floor = S.get("floor"); ppm = None
    w, h = a["w"] * base * z, a["h"] * base * z
    return dict(name=S["bg"], file=a["file"], x=(1080 - w) / 2, y=(1920 - h) / 2 if c["set"] == "table" else 0, w=w, h=h, zoom=z, scale=base * z, floor=floor, ppm=ppm)

def piece_scale(name, who, ppm):
    a = K[name]; an = a["anchor"]
    if an.get("scale") == "head": return REG["char"][who]["headW"] * ppm / (an["head"][2] - an["head"][0])
    return REG["char"][who]["h"] * ppm / (a["h"] - an.get("top", 0))      # top: 머리 위로 든 소품을 뺀 귀 끝(7b 윙키 따르기)

def fam_frame(who, pose):          # '서기-말' 같은 상태 → 실제 그림 이름
    p = pose[:-2] + "-평온" if pose.endswith("-말") else pose
    return f"{who}-{p}"

def prop_k(f, ppm):
    """판·바닥·윗면 소품의 배율: 레지스트리 mm × px/mm ÷ 조각 px. 손은 손바닥 폭, 기록장은 폭, 나머지는 높이."""
    a = K[f]; r = REG["prop"][PROP_OF(f) if f != "box-closed" else "box"]; an = a.get("anchor", {})
    if "paw" in an: return r["w"] * ppm / (an["paw"][2] - an["paw"][0])
    if f.startswith(("notebook", "box")): return r["w"] * ppm / a["w"]
    if f.startswith("strike"): return 1.0
    return r["h"] * ppm / a["h"]

def board_layers(c):
    """판 컷: 조각마다 첫 열쇠 자리에 놓고, 움직임은 12fps 사건(dx, dy, 기울기)으로."""
    ppm = TPPM[c["ppm"]]; L = []; E = []; t0, t1 = c["t"]
    scr = lambda X, Y: (540 + X * ppm, 960 + Y * ppm)
    for P in board_cut(c["n"]):
        f = P["f"]; frames = list(dict.fromkeys([f] + [n for _, n in P["seq"]]))
        a = K[f]; an = a.get("anchor", {})
        k = prop_k(f, ppm) if not f.startswith("strike") else _NB["strike_k"]
        if "paw" in an: ax, ay = an.get("tip", an["pawc"])                          # 손: 손바닥 가운데(연필 손은 연필 끝)
        elif f.startswith(("notebook", "strike")): ax, ay = a["w"] / 2, a["h"] / 2
        else: ax, ay = a["w"] / 2, a["h"]                                          # 잔·사과·통: 밑변 가운데
        if f == "jug": ax, ay = a["w"] / 2, a["h"] / 2
        X0, Y0 = P["keys"][0][1], P["keys"][0][2]; sx, sy = scr(X0, Y0)
        l = dict(id=f"c{c['n']}-{P['id']}", kind="prop", place="board", frames=frames, k=k, x=sx - ax * k, y=sy - ay * k, w=a["w"] * k, h=a["h"] * k,
                 z=P["z"], prop=PROP_OF(f), ppm=ppm, origin=(sx, sy), o={})
        L.append(l)
        # 움직임: 열쇠 사이를 12fps 계단으로 선형 보간
        ks = P["keys"]; ticks = [q(t0 + i * TICK) for i in range(int(round((t1 - t0) * 12)) + 1)]; prev = None
        for t in ticks:
            if t >= t1: break
            if t <= ks[0][0]: kk = ks[0]
            elif t >= ks[-1][0]: kk = ks[-1]
            else:
                j = max(i for i in range(len(ks)) if ks[i][0] <= t + 1e-6); A, B = ks[j], ks[min(j + 1, len(ks) - 1)]
                u = 0 if B[0] == A[0] else (t - A[0]) / (B[0] - A[0]); kk = tuple(A[m] + (B[m] - A[m]) * u if m < len(A) and m < len(B) else (A[m] if m < len(A) else 0) for m in range(4))
            X, Y = kk[1], kk[2]; rot = kk[3] if len(kk) > 3 else 0
            x, y = scr(X, Y); cur = (round(x - sx, 1), round(y - sy, 1), round(rot, 1))
            if cur != prev:
                E.append((t, l["id"], None, cur[0], cur[1]))
                if prev is None or cur[2] != prev[2]: E.append((t, l["id"], "rot", cur[2], None))
            prev = cur
        for tt, n in P["seq"]: E.append((q(tt), l["id"], n, None, None))
        if P["vis"]:
            on, off = P["vis"]; E.append((q(t0), l["id"], "hide", None, None)); E.append((q(on), l["id"], frames[0] if not P["seq"] else P["seq"][0][1], None, None))
            if off: E.append((q(off), l["id"], "hide", None, None))
    return L, E

def build():
    scene = dict(D=D, fps=FPS, cuts=[], cues=CUES, freeze=[])
    if "prebuild" in globals(): prebuild()        # 회차 준비(episode.py)
    for c in CUTS:
        t0, t1 = c["t"]; bg = bg_layer(c); L = []; texts = []; ev = []
        cam = c["cam"]
        line = c.get("line"); syl, vend = ([], None)
        if line:
            opt = line[3] if len(line) > 3 else {}
            syl, vend = syllables(line[0], line[1], line[2], opt)
        chars = {}
        for ci, ch in enumerate(c.get("chars", [])):
            who, at, seq = ch[0], ch[1], ch[2]; ex = ch[3] if len(ch) > 3 else {}
            first = fam_frame(who, seq[0][1])
            if cam == "CU":
                if K[first]["anchor"].get("scale") == "head" and "상반신" in first:   # 상반신: 머리 폭 770px, 머리끝 y 300
                    a = K[first]["anchor"]; k = PRESET["CU"]["bust_head_px"] / (a["head"][2] - a["head"][0])
                    ppm = k * (a["head"][2] - a["head"][0]) / REG["char"][who]["headW"]; foot = None
                else:
                    ppm = PRESET["CU"]["ppm"][who]; foot = PRESET["CU"]["head_top"] + REG["char"][who]["h"] * ppm
                x = 540
            else:
                ppm = PRESET[cam]["ppm"]; x = PRESET[cam]["pos"][at]; foot = bg["floor"]
            chair = who == "winky" and (cam == "M" or (cam == "CU" and c["set"] != "door"))
            holds = any("held" in K[fam_frame(who, p)]["anchor"] for _, p in seq) or any(pr[1] == "hand" and pr[2] == who for pr in c.get("props", []))
            chars[who] = dict(who=who, at=at, x=x, ppm=ppm, foot=foot, chair=chair, seq=seq, ex=ex, z=20 if at == "중" else 22 if holds else 10)
        # 의자(윙키 발판): 바닥선에 놓고 좌판 윗면이 윙키 발끝
        for who, C in chars.items():
            if not C["chair"]: continue
            a = K["chair"]; ppm = C["ppm"]; k = REG["prop"]["chair"]["h"] * ppm / a["h"]
            if cam == "CU": seat = C["foot"]; floor = seat + (a["h"] - a["anchor"]["seat"]) * k
            else: floor = bg["floor"]; seat = floor - (a["h"] - a["anchor"]["seat"]) * k
            L.append(dict(id=f"c{c['n']}-chair", kind="prop", place="floor", frames=["chair"], k=k, x=C["x"] - a["w"] * k / 2, y=floor - a["h"] * k,
                          w=a["w"] * k, h=a["h"] * k, z=15, foot=floor, prop="chair"))
            C["foot"] = seat; C["seat"] = seat; C["seatk"] = k
        # 인물 조각: 자세마다 한 층(img 여러 장)
        for who, C in chars.items():
            names = []
            for _, p in C["seq"]:
                n = fam_frame(who, p)
                if n not in names: names.append(n)
                if p.endswith("-말"):
                    talk = n.replace("-평온", "-말하기")
                    if talk in K and talk not in names: names.append(talk)
            for n in list(names):
                b = n.rsplit("-", 1)[0]
                for extra in (b + "-눈감음", b + "-부채2"):
                    if extra in K and extra not in names and K[extra].get("family") == K[n].get("family"): names.append(extra)
            pl = {}
            for n in names:
                a = K[n]; an = a["anchor"]; k = piece_scale(n, who, C["ppm"]) if not (cam == "CU" and "상반신" in n) else PRESET["CU"]["bust_head_px"] / (an["head"][2] - an["head"][0])
                w, h = a["w"] * k, a["h"] * k
                if cam == "CU" and "상반신" in n: top = PRESET["CU"]["head_top"]
                else: top = C["foot"] - h
                left = C["x"] - an["cx"] * k
                pl[n] = dict(k=k, x=left, y=top, w=w, h=h)
            C["pl"] = pl; C["names"] = names
            L.append(dict(id=f"c{c['n']}-{who}", kind="char", who=who, at=C["at"], frames=names, pl=pl, z=C["z"], chair=C["chair"],
                          foot=C["foot"], ppm=C["ppm"], cam=cam))
        # 소품
        for pi, pr in enumerate(c.get("props", [])):
            spec, place, tgt = pr[0], pr[1], pr[2]; o = pr[3] if len(pr) > 3 else {}
            seq = spec if isinstance(spec, list) else [(t0, spec)]
            frames = [n for _, n in seq]; fr0 = frames[0]
            P = dict(id=f"c{c['n']}-p{pi}", kind="prop", place=place, frames=list(dict.fromkeys(frames)), seq=seq, z=40, o=o, prop=PROP_OF(fr0))
            if place in ("floor", "top"):
                ppm = PRESET["CU"]["ppm"]["winky"] if cam == "CU" else PRESET[cam]["ppm"]
                X = tgt if place == "floor" else tgt[1]; x = 540 + (X - 1080) * ppm
                a = K[fr0]; k = prop_k(fr0, ppm)
                base = bg["floor"] if place == "floor" else bg["floor"] - (80 + FURN[tgt[0]]) * ppm      # 윗면 = 가구 밑선(바닥선 − 80mm) − 높이
                y = base - a["h"] * k
                P.update(k=k, x=x - a["w"] * k / 2, y=y, w=a["w"] * k, h=a["h"] * k, foot=base, z=30 if place == "floor" else 5, ppm=ppm)
            else:
                C = chars[tgt]; ppm = C["ppm"]
                pose = fam_frame(tgt, C["seq"][0][1]); pp = C["pl"][pose]; an = K[pose]["anchor"]
                ax, ay = an["hand"] if place == "hand" else an["sweat"]
                X = pp["x"] + ax * pp["k"]; Y = pp["y"] + ay * pp["k"]
                a = K[fr0]; k = prop_k(fr0, ppm)
                g = K[fr0].get("anchor", {}).get("grip", (a["w"] / 2, a["h"]))
                if o.get("grip") == "bottom": g = (a["w"] / 2, a["h"])          # 받쳐 들기
                if o.get("grip") == "center": g = (a["w"] / 2, a["h"] * 0.62)   # 기록장·사과: 손바닥이 아래쪽 3분의 1 뒤에 가린다(종이 인형 방식)
                if o.get("grip") == "low": g = (a["w"] / 2, a["h"] * 0.3)       # 22번 사과: 두 손이 사과 윗부분을 감싼다(입을 가리지 않게)
                if place == "sweat": g = (a["w"] / 2, a["h"] / 2); P["z"] = 45
                P.update(k=k, x=X - g[0] * k, y=Y - g[1] * k, w=a["w"] * k, h=a["h"] * k, anchor=(X, Y), ppm=ppm, holder=tgt, grip=g)
            L.append(P)
        bev = []
        if cam == "판":
            BL, bev = board_layers(c); L += BL
        # 이름표·자막·제목·근거·끝 화면·칸 글자
        prot = protect_boxes(L, c)
        if line:
            lines = split_lines(line[2]); s0 = line[1]; s1 = t1
            if c.get("iris"): s1 = IRIS["t0"]
            PROT[:] = prot; texts.append(sub_layout(c, lines, s0, s1))
        if c.get("title"): texts.append(caption(c["title"][2], c["title"][0], c["title"][1], "title"))
        if c.get("source"): texts.append(caption(c["source"], t0, t1, "source"))
        if c.get("tag"): texts.append(tag_layout(c["tag"], t0, t1, prot, [(r["sx"], r["sy"], r["sx"] + r["sw"], r["sy"] + r["sh"]) for x in texts if x["kind"] == "sub" for r in x["rows"]]))
        if c.get("end"): texts.append(end_layout(t0, t1))   # 9e: 끝 화면 로고 뺌
        if c.get("logo"): texts.append(logo_layout("inline", *c["logo"], top=CAPTION["y0"] - 15, w=LOGO_OPEN_W))
        for P in L:
            if P.get("o", {}).get("label"): texts.append(label_layout(P, P["o"]["label"]))
            if P.get("place") == "board" and P["frames"][0] == "notebook-open": texts.append(notebook_texts(c, P))
            if P.get("place") == "board" and "notebook-closed" in P["frames"]: texts.append(cover_text(c, P))
        C2 = dict(n=c["n"], t0=t0, t1=t1, set=c["set"], cam=cam, bg=bg, layers=sorted(L, key=lambda l: l["z"]), texts=texts,
                  line=dict(who=line[0], t0=line[1], text=line[2], syl=syl, end=vend) if line else None,
                  sfx=c.get("sfx", []), freeze=None, prot=prot, still=c.get("still", False))
        if c.get("iris"): C2["iris"] = iris(L)
        C2["events"] = sorted(events(C2, chars, c) + bev, key=lambda e: e[0])
        scene["cuts"].append(C2)
    return scene

def protect_boxes(L, c):
    """보호 상자: 얼굴(이목구비 상자), 손에 그린 소품, 손에 든 소품, 핵심 소품(소품 칸 첫째), 부채. 판 컷은 기록장·잔·손."""
    B = []
    for l in L:
        if l["kind"] == "char":
            for n in l["frames"]:
                an = K[n]["anchor"]; p = l["pl"][n]; h = an.get("face", an["head"])
                B.append(dict(kind="face", who=l["who"], frame=n, box=(p["x"] + h[0] * p["k"], p["y"] + h[1] * p["k"], p["x"] + h[2] * p["k"], p["y"] + h[3] * p["k"])))
                if "held" in an:
                    hb = an["held"][1:]; B.append(dict(kind="prop", who=l["who"], frame=n, box=(p["x"] + hb[0] * p["k"], p["y"] + hb[1] * p["k"], p["x"] + hb[2] * p["k"], p["y"] + hb[3] * p["k"])))
                if "fan" in an:
                    f = an["fan"]; B.append(dict(kind="hand", who=l["who"], frame=n, box=(p["x"] + f[0] * p["k"], p["y"] + f[1] * p["k"], p["x"] + f[2] * p["k"], p["y"] + f[3] * p["k"])))
        elif l["place"] == "top": continue                          # 가구 윗면(인물 뒤) 소품은 가려져 있어 보호하지 않는다
        elif l["place"] == "board":
            if l["frames"][0].startswith(("notebook", "cup")):
                B.append(dict(kind="prop", who=None, frame=l["frames"][0], box=(l["x"], l["y"], l["x"] + l["w"], l["y"] + l["h"])))
        elif l["place"] in ("hand", "sweat") or l is next((x for x in L if x["kind"] == "prop" and x["prop"] != "chair" and x["place"] != "top"), None):
            B.append(dict(kind="prop", who=l.get("holder"), frame=l["frames"][0], box=(l["x"], l["y"], l["x"] + l["w"], l["y"] + l["h"])))
    return B

def strip_for(w, h):
    for n in ("strip-w-short", "strip-w-mid", "strip-w-long"):
        a = K[n]; sw = a["w"] / a["h"] * h
        if sw >= w: return n, sw
    a = K["strip-w-long"]; return "strip-w-long", a["w"] / a["h"] * h

def strips(cx, cy, need, h):
    """종이 띠 조각들: 한 장으로 모자라면 긴 띠를 40px 겹쳐 잇는다. [(이름, x, y, w, h)]"""
    n, sw = strip_for(need, h)
    if sw >= need: return [(n, cx - sw / 2, cy - h / 2, sw, h)]
    W = {k: K[k]["w"] / K[k]["h"] * h for k in ("strip-w-short", "strip-w-mid", "strip-w-long")}
    combos = sorted(((W[a] + W[b] - 40, a, b) for a in W for b in W), key=lambda c: c[0])
    tot, a, b = next(c for c in combos if c[0] >= need)
    ov = 40
    if tot > SAFE["r"] - SAFE["l"]: ov = W[a] + W[b] - need; tot = need     # 9c: 두 장이 화면 폭을 넘으면 더 겹쳐 붙인다(늘이지 않음)
    x0 = cx - tot / 2
    return [(a, x0, cy - h / 2, W[a], h), (b, x0 + W[a] - ov, cy - h / 2, W[b], h)]

PROT = []
def sub_layout(c, lines, s0, s1):
    px, lh = SUB["px"], SUB["lineh"]; n = len(lines)
    ys = [SUB["y0"] + (SUB["y1"] - SUB["y0"]) / 2 + (i - (n - 1) / 2) * lh for i in range(n)]
    rows = []
    for s, y in zip(lines, ys):
        w = tw(s, px, "jua")
        for dx in [0] + [d * sg for d in range(10, 310, 10) for sg in (-1, 1)]:     # 9판: 줄이 손에 든 소품(보호 상자)에 닿으면 그 줄만 옆으로 민다
            st = strips(540 + dx, y, w + 80, lh); R = (st[0][1], y - lh / 2, st[-1][1] + st[-1][3], y + lh / 2)
            if R[0] >= SAFE["l"] and R[2] <= SAFE["r"] and not any(hit(R, p["box"]) for p in PROT): break
        rows.append(dict(s=s, px=px, x=540 + dx - w / 2, y=y - px * 0.5, w=w, font="jua", strips=st, sx=st[0][1], sy=y - lh / 2, sw=st[-1][1] + st[-1][3] - st[0][1], sh=lh, dx=dx))
    return dict(kind="sub", t0=s0, t1=s1, rows=rows)

CAP_STEP = 80                                   # 9c: 두 줄 근거 자막의 둘째 줄 간격
def caption(s, t0, t1, kind):
    f = "dohyeon" if kind == "title" else "jua"
    px = CAPTION["px"]; h = CAPTION["y1"] - CAPTION["y0"]; rows = []
    for i, s1 in enumerate(s.split("/")):
        y = (CAPTION["y0"] + CAPTION["y1"]) / 2 + i * CAP_STEP; w = tw(s1, px, f); st = strips(540, y, w + 70, h)
        rows.append(dict(s=s1, px=px, x=540 - w / 2, y=y - px * 0.5, w=w, font=f, strips=st, sx=st[0][1], sy=y - h / 2, sw=st[-1][1] + st[-1][3] - st[0][1], sh=h))
    return dict(kind=kind, t0=t0, t1=t1, rows=rows)

def hit(a, b): return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

TAG_SC = 0.67
def TAG_PX(bw, bh):
    fs, ns = [], []
    for name, feat in TAGS.values():
        feats = feat.split(" · "); nl = 1 + len(feats)
        fs.append(min(bh * 0.7 / nl, min(bw * 0.9 / (tw(f, 100, "jua") / 100) for f in feats))); ns.append(min(bh * 0.7 / nl * 1.35, bw * 0.9 / (tw(name, 100, "jua") / 100)))
    return int(min(fs)), int(min(ns))
def tag_layout(tg, t0, t1, prot, avoid):
    """이름표: 작은 카드(card-s, 520×300 안에 그림 비율 그대로). 멈추지 않고 그 컷 동안만 붙어 있다.
    글자는 6절 칸 글자 공식. 한 줄이 「 · 」로 이어진 두 말이면 같은 크기로 위아래에 둔다(카드 폭에서 한 줄로 두면 26px라 안 읽힌다).
    자리: 사양 후보(좌하·우하)에서 시작해 안전 여백 안으로, 얼굴·소품·자막과 겹치면 위로 올린다."""
    who, at = tg; name, feat = TAGS[who]; feats = feat.split(" · ")
    a = K["card-s"]; found = None
    for sc in (TAG_SC,):                                               # 이름표 셋은 같은 크기(3번 곰 아빠 컷에서 얼굴과 자막 사이에 들어가는 0.67배)
        W = 520 * sc; H = a["h"] / a["w"] * W
        if H > 300 * sc: H = 300 * sc; W = a["w"] / a["h"] * H
        cx = SAFE["l"] + W / 2 if at.startswith("좌") else SAFE["r"] - W / 2   # 가장자리에 붙여 가운데 인물을 덜 가린다
        for cy in list(range(TAG_AT[at][1], 1701, 5)) + list(range(TAG_AT[at][1] - 5, 1150, -5)):   # 아래로 먼저, 위로는 1150까지(머리를 가리지 않게)
            box = (cx - W / 2, cy - H / 2 - 10, cx + W / 2, cy + H / 2)
            if box[3] <= SAFE["b"] and not any(hit(box, p["box"]) for p in prot) and not any(hit(box, r) for r in avoid): found = (W, H, cx, cy, box); break
        if found: break
    if not found: raise SystemExit(f"이름표({who})가 보호 상자를 피할 자리가 없다")
    W, H, cx, cy, box = found
    tb = (cx - W / 2 + W * 0.11, cy - H / 2 + H * 0.15, cx + W / 2 - W * 0.11, cy + H / 2 - H * 0.15)
    bw, bh = tb[2] - tb[0], tb[3] - tb[1]; nl = 1 + len(feats)
    fpx, npx = TAG_PX(bw, bh)                                         # 글자 크기도 셋이 같다: 6절 공식을 셋에 다 맞는 값(가장 작은 값)으로
    gap = (bh - npx - len(feats) * fpx * 1.15) / (nl + 1)
    rows = [dict(s=name, px=npx, x=tb[0], y=tb[1] + gap, w=tw(name, npx, "jua"), font="jua")]; y = tb[1] + gap * 2 + npx
    for f in feats: rows.append(dict(s=f, px=fpx, x=tb[0], y=y, w=tw(f, fpx, "jua"), weight=700, font="jua")); y += fpx * 1.15
    return dict(kind="card", img="card-s", who=who, t0=t0, t1=t1, card=dict(x=cx - W / 2, y=cy - H / 2, w=W, h=H), tape=dict(x=cx - 60, y=cy - H / 2 - 10, w=120, h=K["tape"]["h"] / K["tape"]["w"] * 120),
                textBox=tb, rows=rows, box=box)

def label_layout(P, label):
    tb = K[P["frames"][0]]["anchor"]["text"]
    box = (P["x"] + tb[0] * P["w"], P["y"] + tb[1] * P["h"], P["x"] + tb[2] * P["w"], P["y"] + tb[3] * P["h"])
    lines = label.split("/"); bw, bh = box[2] - box[0], box[3] - box[1]
    px = int(min(bh * 0.7 / len(lines), bw * 0.9 / max(G(s, 100) / 100 for s in lines)))
    rows = []; y0 = (box[1] + box[3]) / 2 - len(lines) * px * 1.15 / 2
    for i, s in enumerate(lines): w = G(s, px); rows.append(dict(s=s, px=px, x=(box[0] + box[2]) / 2 - w / 2, y=y0 + i * px * 1.15 + px * 0.075, w=w, weight=700, font="gaegu"))
    return dict(kind="label", t0=None, t1=None, layer=P["id"], textBox=box, rows=rows)


def end_layout(t0, t1):
    rows = []; y = 500
    for r in END:
        if r is None: y += 50; continue
        s, px = r; f = "jua" if px > 60 else "pre"; w = tw(s, px, f); rows.append(dict(s=s, px=px, x=540 - w / 2, y=y, w=w, weight=800 if px > 60 else 700, font=f)); y += px * 1.45
    return dict(kind="end", t0=t0, t1=t1, rows=rows)

# 9d 시리즈 로고(../logo/README.md): 그림이라 글자 줄이 아니라 상자 하나. 첫 컷 위쪽은 한 줄형, 끝 화면 아래는 큰 로고를 작게
LOGO = {"inline": "kit/logo/logo-inline.png", "main": "kit/logo/logo-main.png"}
LOGO_OPEN_W, LOGO_END_TOP = 900, 1450
def logo_layout(name, t0, t1, top, w=None, bottom=None):
    im = Image.open(os.path.join(ROOT, LOGO[name])); r = im.height / im.width
    if w is None: w = (bottom - top) / r
    h = w * r; box = (540 - w / 2, top, 540 + w / 2, top + h)
    return dict(kind="logo", t0=t0, t1=t1, file=LOGO[name], x=box[0], y=box[1], w=w, h=h, box=box, rows=[])

def iris(L):
    """아이리스 아웃(7b 그대로): 중심 = 인물의 이목구비 상자 가운데(조각 앵커에서 계산, 손으로 적지 않음)."""
    ch = next(l for l in L if l["kind"] == "char"); f = ch["frames"][0]; p = ch["pl"][f]; fa = K[f]["anchor"]["face"]
    cx = p["x"] + (fa[0] + fa[2]) / 2 * p["k"]; cy = p["y"] + (fa[1] + fa[3]) / 2 * p["k"]
    R0 = max(((cx - x) ** 2 + (cy - y) ** 2) ** 0.5 for x in (0, 1080) for y in (0, 1920)) + 40
    I = IRIS; steps = []
    n1 = round((I["small"] - I["t0"]) * 12)
    for j in range(n1 + 1):
        u = j / n1; steps.append((q(I["t0"] + j * TICK), R0 + (I["r_hold"] - R0) * (1 - (1 - u) ** 2)))
    n2 = round((I["shut"] - I["hold"]) * 12)
    for j in range(1, n2 + 1):
        u = j / n2; steps.append((q(I["hold"] + j * TICK), I["r_hold"] * (1 - u ** 2)))
    rnd = random.Random(2401)
    jag = [[round(rnd.uniform(-1, 1), 3) for _ in range(96)] for _ in range(2)]
    return dict(cx=round(cx, 1), cy=round(cy, 1), steps=[(t, round(r, 1)) for t, r in steps], rim=9, jag=jag, end=I["end"])

SEAT_X = (35, 626)            # chair 조각에서 좌판 앵커 높이(y 640)의 좌판 좌우 끝(7b, check.py 13번이 쓴다)
_ALPHA = {}
def alpha(n):
    if n not in _ALPHA: _ALPHA[n] = np.asarray(Image.open(os.path.join(ROOT, K[n]["file"])).getchannel("A")) > 40
    return _ALPHA[n]

# ── 12fps 사건: (시각, 층 id, 프레임 이름 또는 None, dx, dy)
def events(C, chars, c):
    t0, t1 = C["t0"], C["t1"]; E = []
    syl = C["line"]["syl"] if C["line"] else []; vend = C["line"]["end"] if C["line"] else None
    speaker = C["line"]["who"] if C["line"] else None
    rnd = random.Random(7000 + C["n"])
    for who, ch in chars.items():
        lid = f"c{C['n']}-{who}"
        st = []
        for t, p in ch["seq"]:
            if t == "끝": t = vend
            st.append((max(t, t0) if t else t0, p))
        def state(t):
            cur = st[0][1]
            for tt, p in st:
                if t >= tt - 1e-6: cur = p
            return cur
        ticks = [q(t0 + i * TICK) for i in range(int(round((t1 - t0) * 12)) + 1)]
        talking = {}
        if who == speaker:
            for i, s in enumerate(syl):
                nxt = syl[i + 1]["t"] if i + 1 < len(syl) else s["t"] + 0.2
                talking[q(s["t"])] = "open"
                if q(s["t"]) + TICK < q(nxt) - 1e-6: talking[q(s["t"] + TICK)] = "close"
        blinks = set(); tb = t0 + rnd.uniform(0.8, 1.6)
        while tb < t1: blinks.update({q(tb), q(tb + TICK)}); tb += rnd.uniform(3.0, 4.0)
        prev = None; mouth = "close"; fan = 0; held = [l for l in C["layers"] if l.get("holder") == who]
        for i, t in enumerate(ticks):
            if t >= t1: break
            p = state(t); base = fam_frame(who, p); fr = base; dy = 0; dx = 0
            if t in talking: mouth = talking[t]
            speaking = who == speaker and syl and syl[0]["t"] - 1e-6 <= t < (vend or 0) + 0.05
            if C["cam"] == "CU" and p.endswith("-말") and speaking:
                fr = base.replace("-평온", "-말하기") if mouth == "open" else base
            elif C["cam"] == "M" and speaking and mouth == "open":
                dy = -6                                       # 넓은 컷: 말하는 조각이 살짝 까딱
            bl = base.rsplit("-", 1)[0] + "-눈감음"
            if t in blinks and bl in ch["pl"] and fr == base and base.endswith("-평온"):
                fr = bl
            fn = base.rsplit("-", 1)[0] + "-부채2"
            if fn in ch["pl"] and fr == base and not speaking:
                if i % 3 == 0: fan ^= 1
                if fan: fr = fn
            cur = (fr, round(dx, 1), dy)
            if cur != prev:
                E.append((t, lid, fr, round(dx, 1), dy))
                for h in held:
                    if not h["o"].get("show"): E.append((t, h["id"], None, round(dx, 1), dy))
            prev = cur
    for l in C["layers"]:
        if l["kind"] != "prop" or l.get("place") == "board": continue
        o = l.get("o", {})
        for tt, n in l.get("seq", []):
            E.append((q(tt), l["id"], n, None, None))
        if o.get("show") is not None:
            s = o["show"]; E.append((q(t0), l["id"], "hide", None, None))
            for j in range(4): E.append((q(s + j * TICK), l["id"], l["frames"][0], 0, 8 * j))
    return E


# ── 회차 값: EP/episode.py (CUTS, D, CUES, IRIS, TAGS, END, 판 컷 움직임 등). 엔진 이름을 덮어쓸 수 있다
exec(compile(open(os.path.join(EP, "episode.py"), encoding="utf-8").read(), os.path.join(EP, "episode.py"), "exec"), globals())

if __name__ == "__main__":
    sc = build()
    json.dump(sc, open(os.path.join(HERE, "scene.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(HERE, "scene.js"), "w", encoding="utf-8").write("window.SCENE=" + json.dumps(sc, ensure_ascii=False) + ";window.KIT=" + json.dumps(K, ensure_ascii=False) + ";")
    for c in sc["cuts"]:
        print(c["n"], c["set"], c["cam"], "층", len(c["layers"]), "사건", len(c["events"]), "목소리", (c["line"]["syl"][0]["t"], c["line"]["end"]) if c["line"] else "-", "컷 끝", c["t1"])
