"""KIT-SPEC 7절 자동 검사 12개 + 7b 13번(손에 그린 소품) + 9판 14번(새 소품·판 크기)·15번(금지 표현). 렌더 전에 돈다. 하나라도 걸리면 종료 코드 1, 결과는 out/check.txt.
scene.json(build.py 결과)을 kit/registry.json 앵커·mm 크기로 다시 계산해 맞춰 본다. 사용: cd episodes/<회차> && python3 ../../engine/check.py"""
import json, os, re, sys
import numpy as np
import build as B
B.build()                                   # 판 도면(기록장 칸 글자 배치)을 채운다

HERE = B.EP
S = json.load(open(os.path.join(HERE, "scene.json"), encoding="utf-8")); K = B.K
FAIL, LOG = [], []
def ok(cond, no, msg):
    (LOG if cond else FAIL).append(f"[{no}] {'통과' if cond else '실패'} {msg}")
def ov(a, b): return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
def hit(a, b): return ov(a, b) > 0
SFX_NAMES = {n for n, e in B.REGISTRY["sfx"].items() if e.get("status") == "approved"}   # kit/registry.json sfx(승인된 효과음만)
CUE_SHEET = B.CUE_SHEET                      # 회차 대본 큐 시트(episode.py)
TOL = 0.05

# 1 이름
for c in B.CUTS:
    n = c["n"]
    ok(c["set"] in B.SETS and c["cam"] in B.SETS[c["set"]], 1, f"컷{n} 세트·프리셋 {c['set']}/{c['cam']}")
    for ch in c.get("chars", []):
        for _, p in ch[2]:
            f = B.fam_frame(ch[0], p); ok(f in K, 1, f"컷{n} 자세 {f}")
            if p.endswith("-말"): ok(f.replace("-평온", "-말하기") in K, 1, f"컷{n} 말하기 프레임 {f}")
    for pr in c.get("props", []):
        names = [x for _, x in pr[0]] if isinstance(pr[0], list) else [pr[0]]
        for x in names: ok(x in K, 1, f"컷{n} 소품 {x}")
    for s, _ in c.get("sfx", []): ok(s in SFX_NAMES, 1, f"컷{n} 효과음 {s}")
    if c["cam"] == "판":
        for P_ in B.board_cut(n):
            for x in [P_["f"]] + [f for _, f in P_["seq"]]: ok(x in K, 1, f"컷{n} 판 조각 {x}")
for cue in S["cues"]: ok(cue[0] in ("Q-OPEN", "Q-UP", "Q-DOWN", "Q-TIME", "Q-END"), 1, f"큐 이름 {cue[0]}")

for C in S["cuts"]:
    n, cam = C["n"], C["cam"]; chars = [l for l in C["layers"] if l["kind"] == "char"]; props = [l for l in C["layers"] if l["kind"] == "prop"]
    # 2 크기
    for l in props:
        f = l["frames"][0]
        if f.startswith("strike"): continue                          # 연필 줄: 칸 글자 「한」 폭에 맞춘 획(소품 아님)
        reg = B.REG["prop"][B.PROP_OF(f) if f != "box-closed" else "box"]
        ppm = l.get("ppm") or (B.PRESET["CU"]["ppm"]["winky"] if cam == "CU" else B.PRESET[cam]["ppm"])
        an = K[f].get("anchor", {})
        if "paw" in an: mm = (an["paw"][2] - an["paw"][0]) * l["k"] / ppm; ok(abs(mm / reg["w"] - 1) < TOL, 2, f"컷{n} {f} 손바닥 폭 {mm:.0f}mm / {reg['w']}")
        elif f.startswith(("box", "notebook")): mm = l["w"] / ppm; ok(abs(mm / reg["w"] - 1) < TOL, 2, f"컷{n} {f} 폭 {mm:.0f}mm / {reg['w']}")
        else: mm = l["h"] / ppm; ok(abs(mm / reg["h"] - 1) < TOL, 2, f"컷{n} {f} 높이 {mm:.0f}mm / {reg['h']}")
    for l in chars:
        for f, p in l["pl"].items():
            an = K[f]["anchor"]; who = l["who"]; ppm = l["ppm"]
            hw = (an["head"][2] - an["head"][0]) * p["k"] / ppm
            if an.get("scale") == "head": ok(abs(hw / B.REG["char"][who]["headW"] - 1) < TOL, 2, f"컷{n} {f} 머리 폭 {hw:.0f}mm / {B.REG['char'][who]['headW']}")
            else: ok(abs((p["h"] - an.get("top", 0) * p["k"]) / ppm / B.REG["char"][who]["h"] - 1) < TOL, 2, f"컷{n} {f} 키 {(p['h'] - an.get('top', 0) * p['k']) / ppm:.0f}mm / {B.REG['char'][who]['h']} (머리 폭 {hw:.0f}mm, 참고)")
    # 3 놓이는 곳
    for l in props:
        if l["place"] in ("floor", "top"): ok(abs(l["y"] + l["h"] - l["foot"]) <= 4, 3, f"컷{n} {l['frames'][0]} {'바닥선' if l['place'] == 'floor' else '가구 윗면'}")
        elif l["place"] == "board": ok(cam == "판", 3, f"컷{n} {l['frames'][0]} 판 위")
        elif l["place"] in ("hand", "sweat"):
            holder = next(x for x in chars if x["who"] == l["holder"]); f0 = holder["frames"][0]; an = K[f0]["anchor"]; p = holder["pl"][f0]
            if True:
                ax, ay = an["hand"] if l["place"] == "hand" else an["sweat"]; X, Y = p["x"] + ax * p["k"], p["y"] + ay * p["k"]
            gx, gy = l["grip"]; ok(abs(l["x"] + gx * l["k"] - X) <= 4 and abs(l["y"] + gy * l["k"] - Y) <= 4, 3, f"컷{n} {l['frames'][0]} {'손' if l['place'] == 'hand' else '땀'} 앵커({l['holder']})")
        elif l["place"] == "seat":
            w = next(x for x in chars if x["who"] == "winky"); ok(abs(l["y"] + l["h"] - w["foot"]) <= 4, 3, f"컷{n} {l['frames'][0]} 의자 좌판 윗면")
    for l in chars:
        f0 = l["frames"][0]; p = l["pl"][f0]
        if cam == "CU" and "상반신" in f0: ok(abs(p["y"] - B.PRESET["CU"]["head_top"]) <= 4, 3, f"컷{n} {f0} 머리끝 y 300")
        else: ok(abs(p["y"] + p["h"] - l["foot"]) <= 4, 3, f"컷{n} {f0} 발끝 y {l['foot']:.0f}")
    # 4 자리
    for l in chars:
        f0 = l["frames"][0]; p = l["pl"][f0]; x = p["x"] + K[f0]["anchor"]["cx"] * p["k"]
        want = 540 if cam in ("CU", "board") else B.PRESET[cam]["pos"][l["at"]]
        ok(abs(x - want) <= 1, 4, f"컷{n} {l['who']} x {x:.0f} = {want}")
        if l["who"] == "winky" and cam in ("W", "M"):
            chair = next((x for x in props if x["frames"][0] == "chair"), None)
            ok(chair is not None and abs(p["y"] + p["h"] - (chair["y"] + K["chair"]["anchor"]["seat"] * chair["k"])) <= 4, 4, f"컷{n} 윙키는 의자 위")
    # 5 겹침: 몸통 x 범위 겹침 ≤ 좁은 쪽의 15%, 얼굴 상자 0, 소품이 남의 얼굴에 닿지 않음
    def boxes(l):
        out = []
        for f, p in l["pl"].items():
            an = K[f]["anchor"]; fa = an.get("face", an["head"]); t = an["torso"]
            out.append(dict(f=f, face=(p["x"] + fa[0] * p["k"], p["y"] + fa[1] * p["k"], p["x"] + fa[2] * p["k"], p["y"] + fa[3] * p["k"]),
                            torso=(p["x"] + t[0] * p["k"], p["x"] + t[1] * p["k"])))
        return out
    for i in range(len(chars)):
        for j in range(i + 1, len(chars)):
            for a in boxes(chars[i]):
                for b in boxes(chars[j]):
                    o = max(0, min(a["torso"][1], b["torso"][1]) - max(a["torso"][0], b["torso"][0]))
                    nar = min(a["torso"][1] - a["torso"][0], b["torso"][1] - b["torso"][0])
                    ok(o <= 0.15 * nar, 5, f"컷{n} 몸통 겹침 {a['f']}/{b['f']} {o / nar * 100:.0f}%")
                    ok(not hit(a["face"], b["face"]), 5, f"컷{n} 얼굴 상자 {a['f']}/{b['f']}")
    for l in props:
        if l["frames"][0] == "chair": continue
        r = (l["x"], l["y"], l["x"] + l["w"], l["y"] + l["h"])
        for ch in chars:
            if ch["who"] == l.get("holder") or l["place"] == "floor" and l["o"].get("front") == ch["who"] and False: continue
            for b in boxes(ch):
                if l["place"] == "floor" and l["o"].get("front") == ch["who"]: continue      # 1번: 상자 뒤 윙키는 대본 연출
                if l["frames"][0] == "sweat": continue
                ok(not hit(r, b["face"]), 5, f"컷{n} 소품 {l['frames'][0]} ↔ {b['f']} 얼굴")
    # 6 확대
    for l in chars:
        for f, p in l["pl"].items(): ok(p["k"] <= 1.3, 6, f"컷{n} {f} 조각 배율 {p['k']:.3f}")
    for l in props: ok(l["k"] <= 1.3, 6, f"컷{n} {l['frames'][0]} 조각 배율 {l['k']:.3f}")
    ok(1.0 - 1e-6 <= C["bg"]["zoom"] <= 1.15, 6, f"컷{n} 배경 확대 {C['bg']['zoom']:.3f}")
    ok(C["bg"]["x"] <= 0.5 and C["bg"]["y"] <= 0.5 and C["bg"]["x"] + C["bg"]["w"] >= 1079.5 and C["bg"]["y"] + C["bg"]["h"] >= 1919.5, 6, f"컷{n} 배경이 화면을 덮는다")
    # 7 글자 구역
    prot = [p["box"] for p in C["prot"]]
    for x in C["texts"]:
        if x["kind"] in ("label", "end"): continue
        rects = []
        for r in x["rows"]:
            if r.get("strips"): rects.append((r["sx"], r["sy"], r["sx"] + r["sw"], r["sy"] + r["sh"]))
            else: rects.append((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["px"]))
        if x["kind"] in ("card", "logo"): rects = [x["box"]]
        for R in rects:
            ok(R[0] >= B.SAFE["l"] - 0.5 and R[2] <= B.SAFE["r"] + 0.5 and R[1] >= B.SAFE["t"] - 0.5 and R[3] <= B.SAFE["b"] + 0.5, 7, f"컷{n} {x['kind']} 안전 여백 {tuple(round(v) for v in R)}")
            if x["kind"] == "sub": ok(R[1] >= B.SUB["y0"] - 0.5 and R[3] <= B.SUB["y1"] + 0.5, 7, f"컷{n} 자막 띠 y 1500~1700")
            if x["kind"] in ("title", "source"):                      # 9c: 두 줄 근거 자막은 줄마다 80px 아래
                i_ = rects.index(R); y0_, y1_ = B.CAPTION["y0"] + i_ * B.CAP_STEP, B.CAPTION["y1"] + i_ * B.CAP_STEP
                ok(R[1] >= y0_ - 0.5 and R[3] <= y1_ + 0.5, 7, f"컷{n} {x['kind']} {i_ + 1}줄 y {y0_}~{y1_}")
            bad = [p for p in prot if hit(R, p)]
            ok(not bad, 7, f"컷{n} {x['kind']} ↔ 보호 상자 {len(bad)}")
        for r in x["rows"]:
            if x["kind"] == "sub": ok(r["px"] >= 56, 7, f"컷{n} 자막 글자 {r['px']}px ≥ 56")      # 9b: 크기 하한
            if r.get("strips"): ok(r["w"] + 40 <= r["sw"], 7, f"컷{n} {x['kind']} 글자가 종이 띠 안 「{r['s']}」")
    # 8 칸 글자
    for x in C["texts"]:
        if x["kind"] not in ("label", "card"): continue
        tb = x["textBox"]
        for r in x["rows"]:
            w = B.tw(r["s"], r["px"], r.get("font")); tb = r.get("box") or x["textBox"]
            ok(r["x"] >= tb[0] - 0.5 and r["x"] + w <= tb[2] + 0.5 and r["y"] >= tb[1] - 0.5 and r["y"] + r["px"] <= tb[3] + 0.5, 8, f"컷{n} 칸 글자 「{r['s']}」 {r['px']}px")
    # 9 호흡
    subs = [x for x in C["texts"] if x["kind"] == "sub"]
    ok(len(subs) <= 1, 9, f"컷{n} 대사 {len(subs)}줄")
    for x in subs:
        dur = x["t1"] - x["t0"]; nsy = len(C["line"]["syl"])
        ok(dur >= 1.2 - 1e-6, 9, f"컷{n} 자막 {dur:.2f}초")
        ok(nsy / dur <= 5.0 + 1e-6, 9, f"컷{n} {nsy}음절 / {dur:.2f}초 = {nsy / dur:.2f}")
        ok(C["line"]["end"] <= C["t1"] + 1e-6, 9, f"컷{n} 목소리가 컷 안에서 끝남 {C['line']['end']}")
        for r in x["rows"]: ok(len(r["s"].replace(" ", "")) <= 14, 9, f"컷{n} 한 줄 14자 「{r['s']}」")

# 13 (7b) 손에 그린 소품 크기 ±10%, 의자 위 컵, 따르기 높이
PROP_MM = {"cup": 190, "jug": 200, "meter": 100, "apple": 90}
for C in S["cuts"]:
    n = C["n"]; chars = [l for l in C["layers"] if l["kind"] == "char"]; props = [l for l in C["layers"] if l["kind"] == "prop"]
    for l in chars:
        for f, p in l["pl"].items():
            h = K[f]["anchor"].get("held")
            if h: mm = (h[4] - h[2]) * p["k"] / l["ppm"]; ok(abs(mm / PROP_MM[h[0]] - 1) <= 0.10, 13, f"컷{n} {f} 손에 그린 {h[0]} {mm:.0f}mm / {PROP_MM[h[0]]}")
    chair = next((x for x in props if x["frames"][0] == "chair"), None)
    for l in props:
        if l["place"] != "seat": continue
        ck = chair["k"]; cup = (l["x"], l["y"], l["x"] + l["w"], l["y"] + l["h"])
        ok(chair["y"] + 578 * ck <= cup[3] <= chair["y"] + 698 * ck and chair["x"] + B.SEAT_X[0] * ck <= cup[0] and cup[2] <= chair["x"] + B.SEAT_X[1] * ck, 13, f"컷{n} 윙키 컵이 좌판 윗면 안 {tuple(round(v) for v in cup)}")
        w = next(x for x in chars if x["who"] == "winky"); hit_px = 0
        for f, p in w["pl"].items():
            A = B.alpha(f); X0, X1 = int((cup[0] - p["x"]) / p["k"]), int((cup[2] - p["x"]) / p["k"]) + 1; Y0, Y1 = int((cup[1] - p["y"]) / p["k"]), int((cup[3] - p["y"]) / p["k"]) + 1
            hit_px += int(A[max(0, Y0):max(0, Y1), max(0, X0):max(0, X1)].sum())
        ok(hit_px == 0, 13, f"컷{n} 윙키 컵이 윙키 몸과 겹치지 않음({hit_px}px)")
    for l in chars:                                 # 의자 위 윙키 발이 좌판 안
        if l["who"] != "winky" or not chair: continue
        for f, p in l["pl"].items():
            A = B.alpha(f); cols = np.where(A[-max(3, int(A.shape[0] * 0.03)):].any(0))[0]
            x0, x1 = p["x"] + cols[0] * p["k"], p["x"] + cols[-1] * p["k"]
            ok(chair["x"] + B.SEAT_X[0] * chair["k"] <= x0 and x1 <= chair["x"] + B.SEAT_X[1] * chair["k"], 13, f"컷{n} {f} 발이 좌판 안 {x0:.0f}~{x1:.0f}")
    pour = [(f, p, l) for l in chars for f, p in l["pl"].items() if "spout" in K[f]["anchor"]]
    cups = [(f, p, l) for l in chars for f, p in l["pl"].items() if "mouth" in K[f]["anchor"]]
    for f, p, l in pour:
        sx, sy = p["x"] + K[f]["anchor"]["spout"][0] * p["k"], p["y"] + K[f]["anchor"]["spout"][1] * p["k"]
        for g, q, m in cups:
            hb = K[g]["anchor"]["held"]; cx0, cx1 = q["x"] + hb[1] * q["k"], q["x"] + hb[3] * q["k"]; my = q["y"] + K[g]["anchor"]["mouth"][1] * q["k"]
            ok(cx0 - 10 <= sx <= cx1 + 10 and sy <= my, 13, f"컷{n} {f} 주둥이 ({sx:.0f},{sy:.0f}) 이 {g} 컵 위(x {cx0:.0f}~{cx1:.0f}, 뚜껑 y {my:.0f})")

# 10 음악
mus = [(a, b) for _, a, b in S["cues"]]
speech = []
for C in S["cuts"]:
    for x in C["texts"]:
        if x["kind"] == "sub": speech.append((x["t0"], x["t1"]))
    if C["line"]: speech.append((C["line"]["syl"][0]["t"], C["line"]["end"]))
for a, b in mus:
    for s0, s1 in speech: ok(min(b, s1) - max(a, s0) <= 1e-6, 10, f"음악 {a}~{b} ↔ 대사 {s0}~{s1:.2f}")
tot = sum(b - a for a, b in mus); ok(tot <= 0.2 * S["D"], 10, f"음악 합 {tot:.1f}초 = {tot / S['D'] * 100:.0f}%")
ok({tuple(c) for c in S["cues"]} <= CUE_SHEET, 10, "큐 시트 밖 음악 없음")
# 11 표기
end = " ".join(r["s"] for C in S["cuts"] for x in C["texts"] if x["kind"] == "end" for r in x["rows"])
for w in ("의학 검수", "근거", "AI로 만든 그림입니다", "담당 선생님"): ok(w in end, 11, f"끝 화면 「{w}」")
# 9e 로고는 썸네일(thumb.html)에만. 본편 장면에는 로고 상자가 없다. 화면 어디에도 「1화」 없음
ok(not [x for C in S["cuts"] for x in C["texts"] if x["kind"] == "logo"], 11, "본편에 로고 없음(썸네일에만)")
ok("logo-main" in open(os.path.join(HERE, "thumb.html"), encoding="utf-8").read(), 11, "썸네일 로고 있음")
allt = json.dumps(S, ensure_ascii=False) + open(os.path.join(HERE, "thumb.html"), encoding="utf-8").read() + open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
ok("1화" not in allt, 11, "화면 어디에도 「1화」 없음")
# 14 (9판) 새 소품: 기록장 폭·높이 둘 다 ±10%(가로세로 같은 배율이라 비율이 틀리면 한쪽이 벗어난다), 연필 길이(손바닥 폭 대비) ±10%,
#    판 컷 잔은 모두 같은 배율, 손은 화면 끝에서 들어온다(팔이 화면 가장자리까지 닿음, 떠 있는 팔 없음)
for C in S["cuts"]:
    n = C["n"]
    for l in C["layers"]:
        f = l["frames"][0]; ppm = l.get("ppm")
        if l["kind"] != "prop" or not ppm: continue
        for g in l["frames"]:
            if g.startswith("notebook"):
                r = B.REG["prop"][g]; a = K[g]; kk = B.prop_k(g, ppm)
                for dim, px_ in (("w", a["w"]), ("h", a["h"])): mm = px_ * kk / ppm; ok(abs(mm / r[dim] - 1) <= 0.10, 14, f"컷{n} {g} {dim} {mm:.0f}mm / {r[dim]}")
        an = K[f].get("anchor", {})
        if "pencil" in an:
            pl = an["pencil"]; mm = ((pl[2] - pl[0]) ** 2 + (pl[3] - pl[1]) ** 2) ** 0.5 * l["k"] / ppm
            ok(abs(mm / B.REG["prop"]["pencil"]["l"] - 1) <= 0.10, 14, f"컷{n} {f} 연필 {mm:.0f}mm / {B.REG['prop']['pencil']['l']}")
    cups = [l for l in C["layers"] if l.get("place") == "board" and l["frames"][0].startswith("cup")]
    if cups: ok(max(l["k"] for l in cups) - min(l["k"] for l in cups) < 1e-9, 14, f"컷{n} 판 잔 {len(cups)}개 같은 배율 {cups[0]['k']:.3f}")
    for l in C["layers"]:
        if l.get("place") != "board" or "paw" not in K[l["frames"][0]].get("anchor", {}): continue
        f = l["frames"][0]; up = f == "winky-hand"                 # 윙키 손은 위에서, 곰 손은 아래에서
        evs = [e for e in C["events"] if e[1] == l["id"] and e[2] is None]
        bad = [e for e in evs if (l["y"] + e[4] > 0.5 if up else l["y"] + l["h"] + e[4] < 1919.5)]
        ok(not bad, 14, f"컷{n} {f} 팔이 화면 {'위' if up else '아래'} 끝까지 닿음(벗어난 순간 {len(bad)})")
# 15 (9판) 화면 글자에 혈당 숫자·판정 표현이 없다
# M1(11-12): 낱말 통째 금지(「이상하네」「좋아요!」「안 돼~」까지 막았다) → rules/non-medical-device.md가 막는 것만 패턴으로.
# ponytail: 한 줄 안만 본다. 두 줄에 걸친 판정은 지침 대조표·사람 검토가 잡는다
FORBID = [
    r"\d[\d,.]*\s*(mg|㎎|mmol|kcal|g\b|그램|ml|mL|㎖|밀리)",                     # 수치 + 단위(혈당·당 그램·용량)
    r"(혈당|당화|HbA1c|수치).{0,6}\d",                                           # 혈당·수치 + 숫자
    r"(혈당|당화|HbA1c|수치).{0,8}(정상|이상|위험|높|낮|올랐|올라|떨어|내려)",     # 판정
    r"(정상|위험|높은|낮은)\s*(혈당|수치)",
    r"때문에.{0,6}(올랐|올라갔|높아졌|생겼)",                                     # 원인 단정
    r"(먹|마시|드시)(으)?면\s*안\s*(돼요|된다|됩니다|돼\.)",                       # 금지
    r"(줄여야|끊어야|드셔야|먹어야|마셔야)\s*(해|합|한다|돼)",                     # 지시
]
def forbidden(s): return [p for p in FORBID if re.search(p, s)]
for s in ("혈당 130", "공복 혈당이 높아요", "주스 때문에 올랐다", "이건 먹으면 안 돼요", "당을 줄여야 해요", "200mL"): assert forbidden(s), s
for s in ("이상하네~", "좋아요!", "안 돼~", "혈당에 좋대~", "계단이 위험해!", "당 0%", "주스 세 잔"): assert not forbidden(s), s
for C in S["cuts"]:
    for x in C["texts"]:
        for r in x["rows"]:
            ok(not forbidden(r["s"]), 15, f"컷{C['n']} 수치·판정·금지·지시 표현 없음 「{r['s']}」")
# 12 컵
for C in S["cuts"]:
    for l in C["layers"]:
        for f in l["frames"]:
            if "cup" in f or "glass" in f or "mug" in f: ok(f in ("cup-empty", "cup-third", "cup-twothird", "cup-full"), 12, f"컷{C['n']} 컵 조각 {f}")
# 6(덧) 금지 표현: 한 축 배율·기울임·3D 회전·CSS 도형·그림자·그라데이션·필터
html = open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
css = "\n".join(re.findall(r"<style>(.*?)</style>", html, re.S)) + "\n".join(re.findall(r"cssText\s*[+]?=\s*`([^`]*)`", html))
for pat in (r"scaleX", r"scaleY", r"skew", r"rotateX", r"rotateY", r"rotate3d", r"perspective", r"box-shadow", r"text-shadow", r"gradient", r"filter\s*:", r"border-radius", r"border\s*:", r"clip-path", r"outline\s*:"):
    n_ = len(re.findall(pat, html if pat.startswith(("scale", "skew", "rotate", "persp")) else css))
    ok(n_ == 0, 6, f"index.html 금지 표현 「{pat}」 {n_}")
# 7b 아이리스: 원형 마스크(clipPath)는 전환 효과로만 허용(제작자). iris 표시가 붙은 줄 밖에서는 0이어야 한다
bad = [l for l in html.splitlines() if re.search(r"clip-?[pP]ath", l) and "// iris" not in l]
ok(not bad, 6, f"index.html 마스크는 아이리스 줄에만 {len(bad)}")
ir = [C for C in S["cuts"] if C.get("iris")]
for C in ir:
    st = C["iris"]["steps"]; ok(st[-1][1] == 0 and all(a[1] >= b[1] for a, b in zip(st, st[1:])), 6, f"컷{C['n']} 아이리스 반지름이 줄기만 하고 0에서 닫힘")
    ok(abs(C["iris"]["end"] - C["t1"]) < 1e-6 and C["iris"]["end"] - st[-1][0] >= 0.1, 6, f"컷{C['n']} 닫힌 뒤 검정 {C['iris']['end'] - st[-1][0]:.2f}초, 끝 화면으로")
bgs = [m for m in re.findall(r"([^{}]*)\{[^}]*background\s*:", css)]
ok(all(sel.strip() in ("html, body",) for sel in bgs), 6, f"CSS 배경색은 html/body 바탕 하나만 {bgs}")

# 16 레지스트리: 승인된 프리미티브 파일이 모두 있고, 회차가 draft 그림을 쓰지 않는다(엔진 K에는 approved만 들어간다)
for n_, e_ in B.REGISTRY["items"].items():
    if e_.get("status") == "approved": ok(os.path.exists(os.path.join(B.ROOT, e_["file"])), 16, f"레지스트리 {n_} 파일 {e_['file']}")
used = {f for C in S["cuts"] for l in C["layers"] for f in l["frames"]} | {C["bg"]["name"] for C in S["cuts"]}
for f in sorted(used): ok(B.REGISTRY["items"].get(f, {}).get("status") == "approved", 16, f"장면이 쓰는 {f} 승인됨")
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
by = {}
for s in LOG + FAIL: by.setdefault(s.split("]")[0] + "]", []).append(s)
summary = [f"{k} 통과 {sum('통과' in s for s in v)} / 실패 {sum('실패' in s for s in v)}" for k, v in sorted(by.items(), key=lambda kv: int(kv[0][1:-1]))]
open(os.path.join(HERE, "out/check.txt"), "w", encoding="utf-8").write("\n".join(summary + ["", "── 실패"] + FAIL + ["", "── 전체"] + LOG))
print("\n".join(summary)); print("실패", len(FAIL)); [print(" ", f) for f in FAIL[:40]]
sys.exit(1 if FAIL else 0)
