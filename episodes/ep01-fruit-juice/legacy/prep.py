"""키트 만들기: series-kit/gen 원본 → 키 제거 → 잘라 kit/*.webp, 그리고 kit/kit.json(크기·앵커).
- 키 함수 key()는 ep01/prep.py 그대로(마젠타 min(r,b)-g, 파랑 b-max(r,g)).
- 한 장에 한 인물이라 덩어리를 나누지 않고 알파 둘레로 자른다.
- 같은 자세의 표정·동작 프레임(가족)은 기준 그림과 같은 자리로 자른다. 말하기·눈감음은 기준 그림 위에
  얼굴 칸(타원, 가장자리 흐림)만 그 프레임에서 옮겨 붙인다. 12fps로 번갈아도 몸이 떨리지 않는다.
- 7b: 손에 소품을 든 자세는 hold.py로 「실제로 쥔」 그림을 새로 만들었다(곰 손 조각 `bear-손`은 없앴다). 같은 몸의
  프레임은 정렬(align, 가로세로 같은 배율 + 이동)해 같은 자리로 자르고, 앵커는 옛 자세 앵커를 정렬로 옮긴다(derive).
- 파일 이름 한글은 NFC로 다루고, 저장 이름은 ASCII. kit.json 열쇠는 대본 이름 그대로.
- 앵커 좌표는 키잉·자른 뒤 조각(px)에서 눈금판을 보고 쟀다(아래 A). 사용: python3 prep.py"""
import json, os, shutil, unicodedata, glob
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "../series-kit/gen")
OLD = os.path.join(HERE, "../ep01/kit")
KIT = os.path.join(HERE, "kit")
SLUG = {"서기": "stand", "들기": "lift", "상반신": "bust", "내밀기": "reach", "뒤돌기": "back", "양손들기": "hold2",
        "숙이기": "bow", "평온": "calm", "웃음": "smile", "웃음2": "smile2", "말하기": "talk", "당황": "fluster",
        "놀람": "surprise", "시무룩": "sulk", "눈감음": "blink", "부채2": "fan2", "손": "paw",
        "들기컵": "liftcup", "들기측정기": "liftmeter", "상반신컵": "bustcup", "상반신컵가득": "bustcupfull", "내밀기컵": "reachcup",
        "내밀기컵가득": "reachcupfull", "따르기": "pour", "따르기기울임": "pourtilt", "양손컵": "hold2cup", "숙이기컵": "bowcup",
        "내밀기통": "reachjug", "양손사과": "hold2apple"}
OLD_POSE = {"bear-서기-웃음": "bear-stand", "bear-내밀기-웃음": "bear-handoff", "panda-양손들기-놀람": "panda-recv", "penguin-서기-평온": "penguin-stand"}
OLD_PROP = ["cup-empty", "cup-third", "cup-twothird", "cup-full", "apple-whole", "jug", "card", "card-s", "tape", "sweat",
            "strip-w-short", "strip-w-mid", "strip-w-long"]
# 가족: 기준 그림, [(프레임, 옮겨 붙일 칸(원본 좌표 x0,y0,x1,y1) 또는 None=통째)]
FAMILY = {
 "winky-서기-평온": [("winky-서기-말하기", (300, 600, 700, 830)), ("winky-서기-눈감음", (300, 600, 700, 830)),
                   ("winky-서기-놀람", None), ("winky-서기-당황", None), ("winky-서기-웃음", None)],
 "bear-상반신-평온": [("bear-상반신-말하기", (330, 470, 680, 920)), ("bear-상반신-눈감음", (300, 430, 720, 660)),
                    ("bear-상반신-웃음", None), ("bear-상반신-당황", None)],
 "penguin-상반신-평온": [("penguin-상반신-말하기", (260, 545, 720, 745)), ("penguin-상반신-눈감음", (260, 545, 720, 745)),
                       ("penguin-상반신-부채2", None)],
 "bear-들기-웃음": [("bear-들기-웃음2", None)],
 "winky-숙이기-웃음": [("winky-숙이기-당황", None)],
}
PAWP, PAWPC, TIPP, PENP = (0, 0, 581, 620), (290, 330), (6, 50), (6, 50, 440, 470)   # 연필 손(큰 판, 15·17번 4.0 px/mm용)
NBC_TEXT = (0.16, 0.195, 0.85, 0.37)                                                   # 닫힌 기록장 표지의 흰 칸
# ── 앵커(조각 px). cx=몸 중심(발 사이), head=머리 상자(귀 빼고, 얼굴 보호 상자), torso=몸통 x 범위(팔·귀·꼬리 빼고),
#    face=이목구비 상자(눈~입, 보호 상자·겹침 검사), hand=손바닥 중심(소품이 얹히는 곳), sweat=땀 붙는 곳, scale=배율 기준('h' 키 / 'head' 머리 폭)
A = {
 "winky-서기-평온": dict(face=(200, 340, 580, 530), cx=380, head=(130, 200, 630, 520), torso=(200, 560), sweat=(600, 260), scale="h"),
 "winky-서기-시무룩": dict(face=(230, 250, 560, 400), cx=394, head=(134, 50, 654, 410), torso=(230, 560), scale="head"),
 "winky-내밀기-웃음": dict(face=(280, 450, 700, 700), cx=450, head=(130, 230, 800, 720), torso=(250, 650), hand=(150, 760), scale="h"),
 "winky-양손들기-웃음": dict(face=(270, 430, 670, 660), cx=452, head=(152, 240, 782, 680), torso=(270, 640), hand=(452, 720), scale="h"),
 "winky-숙이기-웃음": dict(face=(230, 360, 560, 520), cx=460, head=(190, 230, 650, 540), torso=(330, 600), hand=(450, 610), sweat=(640, 250), scale="head"),
 "bear-서기-웃음": dict(face=(320, 290, 680, 560), cx=500, head=(140, 10, 850, 600), torso=(130, 870), scale="h"),
 "bear-서기-당황": dict(face=(330, 280, 700, 560), cx=486, head=(130, 10, 820, 600), torso=(120, 850), sweat=(230, 310), scale="h"),
 "bear-들기-웃음": dict(face=(310, 280, 670, 560), cx=490, head=(136, 10, 826, 600), torso=(100, 820), hand=(866, 650), scale="h"),
 "bear-들기-당황": dict(face=(280, 270, 640, 560), cx=456, head=(100, 10, 800, 600), torso=(70, 800), hand=(765, 700), scale="h"),
 "bear-내밀기-웃음": dict(face=(340, 260, 640, 540), cx=404, head=(84, 10, 654, 600), torso=(40, 680), hand=(930, 660), scale="h"),
 "bear-상반신-평온": dict(face=(320, 460, 690, 905), cx=483, head=(110, 120, 820, 940), torso=(0, 967), hand=(790, 1000), sweat=(745, 470), scale="head"),   # 9판 13번: 관자놀이 땀
 "panda-양손들기-놀람": dict(face=(220, 220, 700, 480), cx=460, head=(10, 60, 710, 600), torso=(130, 600), hand=(630, 690), scale="h"),
 "panda-내밀기-웃음": dict(face=(230, 220, 680, 470), cx=480, head=(56, 60, 706, 580), torso=(180, 700), hand=(60, 680), scale="h"),
 "panda-뒤돌기": dict(face=(0, 60, 610, 550), cx=300, head=(0, 60, 610, 550), torso=(80, 540), hand=(740, 690), scale="h"),
 "penguin-서기-평온": dict(face=(220, 150, 600, 320), cx=428, head=(98, 0, 678, 370), torso=(60, 820), scale="h"),
 "penguin-상반신-평온": dict(face=(180, 200, 620, 380), cx=406, head=(56, 0, 706, 440), torso=(0, 859), fan=(560, 340, 800, 720), scale="head"),
 # 소품: grip=손에 쥐는 점(없으면 아래 가운데). seat=의자 좌판 윗면 y. text=칸 글자 상자(비율)
 "jug": dict(grip=(255, 150)),
 "chair": dict(seat=640),
 "box-closed": dict(text=(0.19, 0.43, 0.80, 0.85)),
 "meter": dict(),
 # 9판 새 조각(눈금판에서 잼, 조각 px). paw = 손바닥 상자(폭이 레지스트리 손 폭), pawc = 손바닥 가운데(움직임 기준점), tip = 연필 끝, pencil = 연필 끝~지우개 끝
 "bear-hand-flat": dict(paw=(0, 20, 308, 330), pawc=(154, 190)),
 "bear-hand-pencil": dict(paw=PAWP, pawc=PAWPC, tip=TIPP, pencil=PENP),
 "winky-hand": dict(paw=(0, 1180, 332, 1471), pawc=(166, 1340)),
 # 펼친 기록장: 칸 이름 네 칸(아침·점심·저녁·간식)과 간식 칸 글자 자리(비율). 4번 칸은 아래 두 줄 위에 「세」가 들어갈 빈 줄이 있다
 "notebook-open": dict(labels=[(0.5305, 0.1377, 0.6395, 0.2808), (0.5305, 0.3359, 0.6395, 0.4758), (0.5305, 0.5341, 0.6395, 0.6773), (0.5305, 0.7357, 0.6395, 0.8811)],
                       entry=(0.6577, 0.7159, 0.9448, 0.8943), base=785 / 908),        # base = 글자 밑줄(남긴 아래 줄)
 "notebook-closed": dict(text=NBC_TEXT),
}

# ── 7b: 소품을 실제로 쥔 자세(hold.py로 생성, 전부 마젠타 키). 같은 몸의 프레임은 정렬(가로세로 같은 배율 + 이동) 뒤 바꿔 끼운다.
REFS = os.path.join(GEN, "ref-hold")
HOLD_BASE = {"bear-handoff.webp": "bear-내밀기-웃음", "panda-recv.webp": "panda-양손들기-놀람"}   # 기준 그림의 조각 이름
# 가족(정렬): 기준 → [(새 이름, 원본 이름, 옮겨 붙일 칸(원본 좌표) 또는 None=통째, 칸의 원본 좌표계 기준(정렬 대상), 컵 채우기)]
# 컵 채우기: 편집으로 컵을 채우게 하면 컵이 매번 다시 커졌다(1.3~1.5배). 그래서 가득 찬 프레임은 빈 컵 그림의 창(크림색)만
# 주스색(ep01 cup-full 창 색)으로 바꿔 만든다. 컵 모양·크기·손이 빈 컵 프레임과 같아 12fps로 바꿔 끼워도 안 튄다.
FAMILY2 = {
 "bear-상반신컵-평온": [("bear-상반신컵가득-웃음", "bear-상반신-웃음", (300, 430, 720, 920), "bear-상반신-평온", True),
                     ("bear-상반신컵가득-평온", None, None, None, True),                                                  # 9판 3·8번: 찬 잔을 든 채 말한다
                     ("bear-상반신컵가득-말하기", "bear-상반신-말하기", (330, 470, 680, 920), "bear-상반신-평온", True),
                     ("bear-상반신컵가득-눈감음", "bear-상반신-눈감음", (300, 430, 720, 660), "bear-상반신-평온", True),
                     ("bear-상반신컵-말하기", "bear-상반신-말하기", (330, 470, 680, 920), "bear-상반신-평온", False),
                     ("bear-상반신컵-눈감음", "bear-상반신-눈감음", (300, 430, 720, 660), "bear-상반신-평온", False),
                     ("bear-상반신컵-웃음", "bear-상반신-웃음", (300, 430, 720, 920), "bear-상반신-평온", False),
                     ("bear-상반신컵가득-당황", "bear-상반신-당황", (300, 430, 720, 920), "bear-상반신-평온", True)],   # 9b 썸네일: 찬 잔 들고 당황
 "bear-내밀기컵-웃음": [("bear-내밀기컵가득-웃음", None, None, None, True)],
 "bear-들기측정기-웃음": [("bear-들기측정기-당황", "bear-들기측정기-당황", None, None, False)],
 "winky-따르기-웃음": [("winky-따르기기울임-웃음", "winky-따르기기울임-웃음", None, None, False)],
 "winky-숙이기컵-웃음": [("winky-숙이기컵-당황", "winky-숙이기컵-당황", None, None, False)],
}
# 9c: 사과주스 색(연노랑·연두). 9b까지는 ep01 cup-full 창 색(183, 209, 89)이었고, 쥔 그림 컵 창의 크림색이 다 안 바뀌어 우유·라테처럼 보였다.
#     fill_cup과 아래 juice_recolor(키트 잔·통·쥔 그림의 주스 창)가 같은 값을 쓴다.
JUICE = np.array([214, 222, 112], float)
GLASS = np.array([226, 236, 240], float)             # 9c: 빈 잔 창(주스 없는 윗부분 포함). 크림색이면 우유가 든 것처럼 보여서 맑은 유리 쪽으로
def fill_cup(img, box, col=JUICE):
    """box(원본 좌표) 안의 크림색 컵 창만 주스색으로. 명암은 채널별 배율로 유지, 경계는 색 거리로 부드럽게.
    9c: 창 가장자리의 그늘진 크림색까지 바뀌게 색 거리 45 → 90, 대신 하늘색 컵 몸통(파랑 > 빨강)은 뺀다."""
    out = img.astype(float).copy(); x0, y0, x1, y1 = [int(v) for v in box]; r = out[y0:y1, x0:x1, :3]
    cand = (r[..., 0] > 215) & (r[..., 1] > 200) & (r[..., 2] > 165) & (r[..., 0] > r[..., 2] + 20)
    if cand.sum() < 20: return img                    # 크림색 창이 없는 그림(주스가 든 컵)
    cream = np.median(r[cand], 0); d = np.sqrt(((r - cream) ** 2).sum(-1)); w = (np.clip(1 - d / 90, 0, 1) * (r[..., 2] < r[..., 0]))[..., None]
    r[:] = r * (1 - w) + r * (col / cream) * w
    return out.clip(0, 255).astype(np.uint8)

# 손에 그린 소품 상자(키트 조각 좌표, prep 뒤 눈금판에서 잼): held=(소품, x0, y0, x1, y1). 컵은 빨대 끝~밑바닥(레지스트리 190mm = cup-full.webp 전체 높이, 빨대 포함).
# 크기 검사(레지스트리 ±10%)·보호 상자에 쓴다. 통은 주둥이 끝(spout), 컵은 뚜껑 윗면 가운데(mouth)도 적는다(6·7번 따르기 검사).
HELD = {
 "winky-따르기-웃음": dict(held=("jug", 0, 3, 362, 338), top=165),        # 7회차: 통을 머리 위로. top = 귀 끝(키는 귀 끝~발)
 "winky-따르기기울임-웃음": dict(spout=(2, 228), top=165),             # 기울인 통은 크기 검사에서 뺀다(높이가 기울기로 바뀜)
 "winky-양손컵-웃음": dict(held=("cup", 345, 548, 550, 935)),
 "winky-숙이기컵-웃음": dict(held=("cup", 355, 500, 508, 778)),
 "bear-내밀기컵-웃음": dict(held=("cup", 697, 677, 778, 838), mouth=(737, 725)),     # 허리 높이(5회차 무릎 그림은 ref-hold/v7/…-무릎.png, 안 씀)
 "panda-양손사과-놀람": dict(held=("apple", 645, 610, 702, 690)),
 "bear-상반신컵-평온": dict(held=("cup", 667, 986, 755, 1145)),
 "bear-들기컵-웃음": dict(held=("cup", 791, 585, 870, 739)),
 "bear-들기측정기-웃음": dict(held=("meter", 810, 632, 842, 719)),
 "panda-내밀기통-웃음": dict(held=("jug", 15, 461, 250, 703)),        # 258mm: 크기 못 맞춰 장면에서 안 씀(README)
}

def align(base, var):
    """var 를 base 에 맞추는 (배율 s, 이동 tx, ty): base 좌표 = s × var 좌표 + t. 알파 실루엣 상관(FFT), 반 해상도."""
    A = (base[..., 3] > 128).astype(np.float32); B = (var[..., 3] > 128).astype(np.float32)
    h, w = A.shape; f = 0.5; a = np.asarray(Image.fromarray(A * 255).resize((int(w * f), int(h * f)))) / 255
    Fa = np.fft.rfft2(a); best = None
    for sc in np.arange(0.92, 1.0801, 0.005):
        bw, bh = int(w * f * sc), int(h * f * sc)
        b = np.zeros_like(a); bi = np.asarray(Image.fromarray(B * 255).resize((bw, bh))) / 255
        b[: min(bh, a.shape[0]), : min(bw, a.shape[1])] = bi[: a.shape[0], : a.shape[1]]
        cc = np.fft.irfft2(Fa * np.conj(np.fft.rfft2(b)), a.shape)
        i = np.unravel_index(np.argmax(cc), cc.shape); v = cc[i] / np.sqrt(a.sum() * b.sum())
        dy, dx = [(i[k] if i[k] <= a.shape[k] // 2 else i[k] - a.shape[k]) for k in (0, 1)]
        if best is None or v > best[0]: best = (v, sc, dx / f, dy / f)
    return best[1], best[2], best[3], best[0]

def warp(var, s, tx, ty, size):
    im = Image.fromarray(var, "RGBA"); im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    C = Image.new("RGBA", size, (0, 0, 0, 0)); C.paste(im, (round(tx), round(ty))); return np.asarray(C)

def key(a, k):                                   # ep01/prep.py 와 같다
    r, g, b = [a[..., i].astype(np.float32) for i in range(3)]
    spill = (np.minimum(r, b) - g) if k == "m" else (b - np.maximum(r, g))
    alpha = 1 - np.clip((spill - 30) / 60, 0, 1)
    ex = np.clip(spill, 0, None) * 0.85
    if k == "m": r, b = r - ex, b - ex
    else: b = b - ex
    return np.dstack([r, g, b, alpha * 255]).clip(0, 255).astype(np.uint8)

def slug(n): return "-".join(SLUG.get(p, p) for p in n.split("-"))
def bbox(rgba): return Image.fromarray(rgba[..., 3]).point(lambda v: 255 if v > 40 else 0).getbbox()

def patch(base, var, box):                        # 기준 그림 위에 타원 칸만 옮겨 붙인다(가장자리 12px 흐림)
    h, w = base.shape[:2]; x0, y0, x1, y1 = box
    yy, xx = np.mgrid[0:h, 0:w]
    m = (((xx - (x0 + x1) / 2) / ((x1 - x0) / 2)) ** 2 + ((yy - (y0 + y1) / 2) / ((y1 - y0) / 2)) ** 2) <= 1
    # 그림마다 털색이 조금 달라 테두리가 보인다: 타원 둘레 띠에서 두 그림의 평균 색을 맞춘다(채널별 배율)
    big = (((xx - (x0 + x1) / 2) / ((x1 - x0) / 2 + 30)) ** 2 + ((yy - (y0 + y1) / 2) / ((y1 - y0) / 2 + 30)) ** 2) <= 1
    ring = big & ~m & (base[..., 3] > 200) & (var[..., 3] > 200)
    gain = np.ones(4); gain[:3] = base[ring][:, :3].mean(0) / np.maximum(var[ring][:, :3].mean(0), 1)
    var = (var * gain).clip(0, 255)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10))) / 255.0
    return (base * (1 - m[..., None]) + var * m[..., None]).round().astype(np.uint8)

def derive(raw, K):
    """7b 새 그림의 앵커: 기준 그림(옛 자세 + 붙인 소품)에 정렬해 옛 조각 앵커를 옮긴다. 소품 상자(HELD)는 눈금판에서 잰 값."""
    R = json.load(open(os.path.join(REFS, "refs.json"))); out = {}
    for n, m in R.items():
        if n not in raw: continue
        ref = key(np.asarray(Image.open(os.path.join(REFS, m["ref"])).convert("RGB")), "m"); ref[..., 3][ref[..., 3] < 24] = 0
        s_, tx, ty, v = align(ref, raw[n][1]); cx0, cy0 = bbox(raw[n][1])[:2]
        old = HOLD_BASE.get(m["base"], m["base"]); ao = A[old]
        X = lambda x: (m["ox"] + m["fit"] * x - tx) / s_ - cx0
        Y = lambda y: (m["oy"] + m["fit"] * y - ty) / s_ - cy0
        a = dict(scale=ao["scale"], cx=round(X(ao["cx"])), derived=dict(old=old, align=[round(s_, 4), round(tx, 1), round(ty, 1), round(float(v), 3)]))
        for k in ("face", "head", "fan"):
            if k in ao: b = ao[k]; a[k] = (round(X(b[0])), round(Y(b[1])), round(X(b[2])), round(Y(b[3])))
        a["torso"] = (round(X(ao["torso"][0])), round(X(ao["torso"][1])))
        if "sweat" in ao: a["sweat"] = (round(X(ao["sweat"][0])), round(Y(ao["sweat"][1])))
        for fam_n in [n] + [f[0] for f in FAMILY2.get(n, [])]:
            if fam_n in HELD: a2 = dict(a); a2.update(HELD[fam_n]); out[fam_n] = a2
        out.setdefault(n, a)
    return out

def main():
    os.makedirs(KIT, exist_ok=True)
    src = {unicodedata.normalize("NFC", os.path.basename(f)[:-4]): f for f in glob.glob(os.path.join(GEN, "*.png"))}
    raw = {}
    for n, f in src.items():
        im0 = Image.open(f); im = im0.convert("RGB")
        if n.startswith("set-"): raw[n] = ("bg", im); continue
        if im0.mode == "RGBA" and np.asarray(im0)[..., 3].min() < 10:                 # 9판: 투명 바탕으로 나온 그림은 알파 그대로
            a = np.asarray(im0).copy(); a[..., 3][(a[..., 3] < 230) & (a[..., :3].max(-1) < 40)] = 0   # 둘레의 검은 반투명 번짐(그림자 아님, 생성 찌꺼기)은 걷는다
            a[..., 3][a[..., 3] < 24] = 0; raw[n] = ("piece", a); continue
        px = np.asarray(im)[4, 4]; mag = px[0] > 200 and px[2] > 200 and px[1] < 90        # 7b 그림은 윙키도 마젠타 키(컵·통이 하늘색)
        a = key(np.asarray(im), "m" if mag else "b"); a[..., 3][a[..., 3] < 24] = 0
        raw[n] = ("piece", a)
    K = {}
    def save(n, rgba, crop, extra=None):
        im = Image.fromarray(rgba, "RGBA").crop(crop); out = slug(n) + ".webp"
        im.save(os.path.join(KIT, out), quality=92, method=6)
        K[n] = {"file": "kit/" + out, "w": im.width, "h": im.height, **(extra or {})}
    done = set()
    for b, frames in FAMILY.items():                 # 가족은 기준 그림 자리로 자른다
        base = raw[b][1]; crop = bbox(base)
        save(b, base, crop, {"family": b})
        for v, box in frames:
            var = raw[v][1]; img = patch(base, var, box) if box else var
            save(v, img, crop, {"family": b, "patched": bool(box)}); done.add(v)
        done.add(b)
    for b, frames in FAMILY2.items():                # 7b 가족: 정렬해서 같은 자리로
        base = raw[b][1]; crop = bbox(base); H, W = base.shape[:2]
        save(b, base, crop, {"family": b})
        for new, srcn, box, oldbase, fill in frames:
            img = base; info = {"family": b}
            if fill:
                if b not in HELD: continue                           # 상자를 재기 전(처음 한 번)
                hb = HELD[b]["held"]; img = fill_cup(base, (hb[1] + crop[0], hb[2] + crop[1], hb[3] + crop[0], hb[4] + crop[1])); info["filled"] = True
            if srcn:
                s_, tx, ty, v = align(base, raw[oldbase or srcn][1])
                var = warp(raw[srcn][1], s_, tx, ty, (W, H))
                img = patch(img, var, (box[0] * s_ + tx, box[1] * s_ + ty, box[2] * s_ + tx, box[3] * s_ + ty)) if box else var
                info.update(patched=bool(box), aligned=[round(s_, 4), round(tx, 1), round(ty, 1), round(float(v), 3)])
            save(new, img, crop, info); done.add(new)
        done.add(b)
    for n, (kind, a) in raw.items():
        if n in done: continue
        if kind == "bg":
            out = slug(n) + ".jpg"; a.save(os.path.join(KIT, out), quality=90); K[n] = {"file": "kit/" + out, "w": a.width, "h": a.height}
        else: save(n, a, bbox(a))
    for n, o in OLD_POSE.items():
        shutil.copy(os.path.join(OLD, o + ".webp"), os.path.join(KIT, slug(n) + ".webp"))
        im = Image.open(os.path.join(KIT, slug(n) + ".webp")); K[n] = {"file": "kit/" + slug(n) + ".webp", "w": im.width, "h": im.height, "from": "ep01/kit/" + o}
    for n in OLD_PROP:
        shutil.copy(os.path.join(OLD, n + ".webp"), os.path.join(KIT, n + ".webp"))
        im = Image.open(os.path.join(KIT, n + ".webp")); K[n] = {"file": "kit/" + n + ".webp", "w": im.width, "h": im.height, "from": "ep01/kit"}
    shutil.copy(os.path.join(OLD, "bg-end.jpg"), os.path.join(KIT, "bg-end.jpg"))
    im = Image.open(os.path.join(KIT, "bg-end.jpg")); K["bg-end"] = {"file": "kit/bg-end.jpg", "w": im.width, "h": im.height, "from": "ep01/kit"}
    # 아이리스 종이(7b): 검정 색지와 찢긴 단면의 크림색 섬유. 결은 시드 고정 잡음(그림 아님, 종이 질감)
    rng = np.random.default_rng(2401)
    for n, base, amp in (("iris-black", (24, 22, 26), 7), ("iris-rim", (246, 238, 220), 9)):
        fib = np.asarray(Image.fromarray((rng.standard_normal((480, 270)) * 40 + 128).clip(0, 255).astype(np.uint8)).resize((1080, 1920), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2)), float)
        grain = rng.standard_normal((1920, 1080)) * 0.5
        im = (np.array(base, float)[None, None, :] + ((fib - 128) / 40 + grain)[..., None] * amp).clip(0, 255).astype(np.uint8)
        Image.fromarray(im).save(os.path.join(KIT, n + ".jpg"), quality=88); K[n] = {"file": "kit/" + n + ".jpg", "w": 1080, "h": 1920}
    # 9판: 간식 칸의 위쪽 줄(조각 y 739~750)은 지운다. 그 줄이 「사과주스 한 잔」 글자 허리를 지나 전부 그은 것처럼 보였다.
    #      아래 줄(y 785)을 글자 밑줄로 쓰고, 지운 자리 위가 「세」가 들어갈 빈 줄이다. 줄 위아래 종이 색을 열마다 이어 칠한다.
    nb = np.asarray(Image.open(os.path.join(KIT, "notebook-open.webp")).convert("RGBA")).astype(float)
    line = (nb[744, :, 2] - nb[744, :, 0] > 20) & (np.arange(nb.shape[1]) > 880)
    up, dn = nb[728:734].mean(0), nb[756:762].mean(0)
    for i, y in enumerate(range(738, 752)):
        u = (i + 0.5) / 14; nb[y, line] = (up * (1 - u) + dn * u)[line]
    Image.fromarray(nb.clip(0, 255).astype(np.uint8), "RGBA").save(os.path.join(KIT, "notebook-open.webp"), quality=92, method=6)
    # 9판: 빈 주스 통(20번 판다 손). 통 그림의 연두 주스 칸만 통 안쪽 유리 색으로 바꾼다(7b fill_cup과 같은 색 바꾸기, 모양·크기 그대로)
    j = np.asarray(Image.open(os.path.join(KIT, "jug.webp")).convert("RGBA")).astype(float); r, g, b = j[..., 0], j[..., 1], j[..., 2]
    green = (g > r + 25) & (g > b + 40) & (j[..., 3] > 200)
    glass = np.median(j[(r > 225) & (g > 225) & (b > 215) & (j[..., 3] > 200)][:, :3], 0); juice = np.median(j[green][:, :3], 0)
    w = np.clip(1 - np.sqrt(((j[..., :3] - juice) ** 2).sum(-1)) / 70, 0, 1)[..., None]
    j[..., :3] = j[..., :3] * (1 - w) + j[..., :3] * (glass / juice) * w
    Image.fromarray(j.clip(0, 255).astype(np.uint8), "RGBA").save(os.path.join(KIT, "jug-empty.webp"), quality=92, method=6)
    K["jug-empty"] = {"file": "kit/jug-empty.webp", "w": int(j.shape[1]), "h": int(j.shape[0]), "from": "jug.webp 색 바꾸기", "anchor": {"grip": [255, 150]}}
    # 9판: 연필 줄(17번 「한」에 긋는 한 획). 흑연 회색 한 획을 시드 고정 흔들림으로 그린 그림 셋(1/3, 2/3, 끝까지). 같은 캔버스라 바꿔 끼워도 안 튄다
    rng2 = np.random.default_rng(1711); W_, H_ = 320, 44; xs = np.arange(W_)
    yc = H_ / 2 + 2.2 * np.sin(xs / 37 + 0.4) + np.cumsum(rng2.normal(0, 0.18, W_)); th = 5.5 + 1.2 * np.sin(xs / 23) + rng2.normal(0, 0.4, W_)
    yy = np.arange(H_)[:, None]; core = np.clip(1 - np.abs(yy - yc[None, :]) / th[None, :], 0, 1) ** 0.6
    grain = np.clip(0.75 + 0.35 * rng2.standard_normal((H_, W_)), 0, 1); al = (core * grain * 235).clip(0, 255)
    for i, frac in enumerate((0.34, 0.67, 1.0), 1):
        a_ = al.copy(); a_[:, int(W_ * frac):] = 0; a_[:, :int(W_ * frac)] *= np.clip((int(W_ * frac) - xs[:int(W_ * frac)]) / 6, 0.35, 1)[None, :] if frac < 1 else 1
        im = np.zeros((H_, W_, 4), np.uint8); im[..., 0], im[..., 1], im[..., 2] = 74, 78, 88; im[..., 3] = a_.astype(np.uint8)
        Image.fromarray(im, "RGBA").save(os.path.join(KIT, f"strike-{i}.png")); K[f"strike-{i}"] = {"file": f"kit/strike-{i}.png", "w": W_, "h": H_, "from": "prep.py 연필 줄"}
    # 9c: 주스 창 색을 JUICE 하나로(잔 셋·통·주스 쥔 그림). 사과(파랑 성분이 거의 없는 진한 연두)는 b > 50 조건으로 빠진다
    for n in [n for n in K if n in ("cup-full", "cup-third", "cup-twothird", "jug") or (n.split("-")[0] in ("bear", "winky", "panda") and any(w in n for w in ("컵", "따르기", "통")))]:
        f = os.path.join(KIT, os.path.basename(K[n]["file"])); a = np.asarray(Image.open(f).convert("RGBA")).astype(float); r, g, b = a[..., 0], a[..., 1], a[..., 2]
        m = (g > r + 10) & (g > b + 60) & (b > 50) & (r > 140) & (a[..., 3] > 200)
        if m.sum() < 50: continue
        jm = np.median(a[m][:, :3], 0); w = (np.clip(1 - np.sqrt(((a[..., :3] - jm) ** 2).sum(-1)) / 60, 0, 1) * (b > 40))[..., None]
        a[..., :3] = a[..., :3] * (1 - w) + a[..., :3] * (JUICE / jm) * w
        Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA").save(f, quality=92, method=6) if f.endswith(".webp") else Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA").save(f)
    # 9c: 빈 잔의 크림색 창 → GLASS(판 잔 셋 전체, 쥔 그림은 컵 상자 안만). 「가득」 프레임은 위에서 주스로 채웠다
    for n in [n for n in K if n in ("cup-empty", "cup-third", "cup-twothird") or ("컵" in n and "가득" not in n and n.split("-")[0] in ("bear", "winky"))]:
        f = os.path.join(KIT, os.path.basename(K[n]["file"])); a = np.asarray(Image.open(f).convert("RGBA"))
        hb = (HELD.get(K[n].get("family", n)) or HELD.get(n) or {}).get("held")
        box = (hb[1], hb[2], hb[3], hb[4]) if hb else (0, 0, a.shape[1], a.shape[0])
        Image.fromarray(fill_cup(a, box, GLASS), "RGBA").save(f, quality=92, method=6)
    # 9c: 판의 빈 잔(9·21번 「다 마신 잔」)은 바닥에 주스가 조금 남은 모습. 1/3 잔의 주스 층 아래 4분의 1만 옮겨 온다(두 그림은 같은 틀)
    e = np.asarray(Image.open(os.path.join(KIT, "cup-empty.webp")).convert("RGBA")).copy(); t = np.asarray(Image.open(os.path.join(KIT, "cup-third.webp")).convert("RGBA"))
    tf = t.astype(int); jm = (tf[..., 1] > tf[..., 0] + 5) & (tf[..., 1] > tf[..., 2] + 60) & (tf[..., 3] > 200); ys = np.where(jm.any(1))[0]
    jm[: ys.max() - (ys.max() - ys.min()) // 4] = False; w_ = min(e.shape[1], t.shape[1]); e[:, :w_][jm[:, :w_]] = t[:, :w_][jm[:, :w_]]
    Image.fromarray(e, "RGBA").save(os.path.join(KIT, "cup-empty.webp"), quality=92, method=6)
    AD = derive(raw, K)
    for n in K:                                       # 앵커: 가족 프레임은 기준 그림 값을 물려받는다
        fam = K[n].get("family")
        a = A.get(n) or AD.get(n) or ((A.get(fam) or AD.get(fam)) if fam else None)
        if a: K[n]["anchor"] = a
    json.dump(K, open(os.path.join(KIT, "kit.json"), "w"), ensure_ascii=False, indent=1)
    miss = [n for n in K if not n.startswith(("set-", "bg-", "cup", "strip", "card", "tape", "apple", "sweat", "box-open", "iris")) and "anchor" not in K[n]]
    print("조각", len(K), "앵커 없음", miss)

if __name__ == "__main__":
    main()
