"""ep01 「주스 세 잔」 9e판 회차 값. engine/build.py가 자기 이름공간에서 exec 한다(엔진 함수·표를 그대로 쓰고, 여기 값이 엔진 기본값을 덮는다).
원본: 1화 9e판 제작 폴더(ep01-v9)의 build.py. 코드는 그대로 옮기고 자리만 나눴다."""

# 판 배율(엔진 board_layers가 쓴다)
# 판 배율: 기록장만 나오는 컷은 펼침 300mm가 화면 폭의 3분의 2쯤(대본 2.4 안팎). 곰 손 조각 확대 1.3배 한도 안의 2.3.
#          잔 셋·통·기록장이 같이 나오는 7·9·21번은 1.75(주스 통 조각 확대가 1.3배를 넘지 않는 값, 대본 「배율을 낮춰도 된다」).
TPPM = {"note": 2.3, "cups": 1.75, "write": 4.0}   # write: 15·17번 글자 컷(README 「기획과 다르게 한 것」)

# 이름표(작은 카드, 멈추지 않는다). 화면 문구 점검: 「당뇨 2형 4년 차」 → 「2형 당뇨 4년 차」(README 점검표)
TAGS = {"winky": ("윙키", "상담소 알바"), "bear": ("곰 아빠", "딸바보 · 2형 당뇨 4년 차"), "penguin": ("펭귄 선생님", "위뉴 건강상담소")}
# 근거 자막. 화면 문구 점검: 「과일주스의 당도 유리당」 → 「과일주스의 당은 유리당」(「당도」가 糖度로 읽힌다)
# 9c: 18번 근거 자막을 「넣은 설탕과 같다」는 뜻이 먼저 읽히게(출처는 뒤로). 한 줄로는 화면 폭을 넘어 /에서 두 줄(둘째 줄은 아래 80px)
SOURCE_WHO, SOURCE_KDA = "과일주스의 당도/넣은 설탕과 같이 셉니다 · WHO 2015", "2025 당뇨병 진료지침 5-3"
# 9c 끝 화면: 가장 큰 줄 = 행동 메시지, 둘째 = 담당 선생님, 나머지(검수·근거·AI 표시)는 작게
END = [("과일은 갈지 말고", 96), ("씹어서, 적당히", 96), None,
       ("얼마나 드실지는", 64), ("담당 선생님과 정하세요", 64), None,
       ("의학 검수: 위뉴 의료진 ○○○ · 2026.11", 44), None,
       ("근거: 대한당뇨병학회", 44), ("2025 당뇨병 진료지침 · WHO 2015", 44), None,
       ("AI로 만든 그림입니다", 44)]
# 9c 시계: 2·19번 대사가 길어져 자막(초당 5음절)에 맞게 2번 +0.7, 19번 +0.4초. 대사 뒤 무음·정적에서 같은 1.1초를 거뒀다
#    (3·6·13·18번 대사 뒤 −0.1씩, 4번 덮은 기록장 멈춤 −0.1, 16번 반응 컷 −0.1, 끝 화면 음악 뒤 무음 −0.5). 전체 50.0초 그대로.
#    아래 시각은 모두 9b 시각으로 적고 W()가 9c 시각으로 옮긴다(판 컷 움직임은 대부분 밀기만, 4번만 0.9→0.8초로 살짝 빠르게)
_WK = [(0.0, 0.0), (1.2, 1.2), (4.1, 4.8), (7.4, 8.0), (8.3, 8.8), (10.2, 10.7), (11.9, 12.3), (25.6, 26.0), (27.7, 28.0), (30.1, 30.4),
       (30.6, 30.8), (31.8, 32.0), (34.7, 34.8), (38.5, 39.0), (49.5, 50.0), (50.0, 50.0)]
def W(t):
    if t is None: return None
    for (a, A), (b, B_) in zip(_WK, _WK[1:]):
        if t <= b + 1e-9: return round(A + (t - a) * (B_ - A) / (b - a), 4)
    return round(t + _WK[-1][1] - _WK[-1][0], 4)
CUES = [(n, W(a), W(b)) for n, a, b in [("Q-TIME", 18.1, 19.3), ("Q-DOWN", 38.5, 39.3), ("Q-END", 47.0, 49.5)]]
D = W(50.0)
# 아이리스(7b 코드 그대로): 윙키 얼굴 쪽으로 줄어 → 얼굴 둘레에서 멈칫 → 닫힘 → 검정 0.4초(대본 23번)
IRIS = {k: (W(v) if k != "r_hold" else v) for k, v in dict(t0=45.8, small=46.2, hold=46.45, shut=46.6, end=47.0, r_hold=300).items()}

# ── 5. 판 도면(mm). 원점 = 화면 가운데(540, 960), 아래로 +. 잔·사과는 밑변 가운데, 기록장은 가운데, 손은 손바닥(연필 끝) 자리.
#    7·9·21번이 같은 줄 좌표를 쓴다(대본 「빈 잔 셋 나란히」).
ROW = 5                                      # 잔이 서는 줄(밑변). 곰 팔(아래)과 윙키 팔(위)이 둘 다 닿는 높이
SLOT = [-215, -95, 25]                       # 줄 자리 세 칸(왼쪽)
POUR = 150                                   # 따르는 자리(오른쪽, 통 아래)
JUG = (POUR + 110, ROW - 213, -30)          # 따를 때 통 가운데·기울기: 주둥이(조각 (10,70))가 잔 뚜껑 바로 위에 오는 자리(README)
NB_C = (-150, 170)                           # 덮인 기록장(줄 자리 바로 옆)
NB_O21 = (-60, 180)                          # 21번 펼친 기록장
NB_O = (0, 0)                                # 4번 펼친 기록장(화면 가운데)
NB_W = (-72, -30)                            # 15·17번: 오른쪽 면(표)을 화면 가운데로
CROOK = [(-8, 10, -5), (9, -12, 6), (-6, 16, -4)]   # 9번 삐뚤게 놓인 잔: (dX, dY, 기울기°)
OFF_B, OFF_T = 760, -760                     # 손이 화면 밖으로 나간 자리(아래·위, mm 기준 넉넉히)

KM = [("bear", "좌"), ("winky", "중"), ("panda", "우")]
OM = [("bear", "좌"), ("winky", "중"), ("penguin", "우")]     # 펭귄·곰 자리 바꿈(ep01-v7 README 2)
TOP_NB = lambda n: (n, "top", ("table", 600))                 # 식탁 윗면(곰 아빠 뒤라 M 컷에서는 가려진다)

# ── 6. 판 컷 움직임. 열쇠 [(시각, X, Y[, 기울기])], 프레임 바꾸기 [(시각, 조각)], 보이기 (나타남, 사라짐)
def cup_keys(slot_i, t_place, crooked):
    dx, dy, r = CROOK[slot_i] if crooked else (0, 0, 0)
    return dx, dy, r
def board_cut(n):
    """9c: 9b 시각으로 적은 조각 움직임을 W()로 옮긴다."""
    P = _board_cut(n)
    for p in P:
        p["keys"] = [(W(k[0]),) + tuple(k[1:]) for k in p["keys"]]; p["seq"] = [(W(t), f) for t, f in p["seq"]]
        if p["vis"]: p["vis"] = tuple(W(t) for t in p["vis"])
    return P
def _board_cut(n):
    """판 컷 n의 조각 목록: dict(id, f(첫 조각), seq=[(t, 조각)], keys=[(t, X, Y, rot)], vis=(t_on, t_off), z)"""
    P = []
    def piece(id_, f, keys, seq=None, vis=None, z=40): P.append(dict(id=id_, f=f, keys=keys, seq=seq or [], vis=vis, z=z))
    if n == 4:                                                     # 7.4~8.3 펼친 기록장 → 곰 손이 덮는다(7.7 탁)
        piece("nb", "notebook-open", [(7.4, *NB_O, 0)], vis=(7.4, 7.7), z=20)
        piece("nbc", "notebook-closed", [(7.4, NB_O[0] + 75, NB_O[1], 0)], vis=(7.7, None), z=20)       # 왼쪽 면을 넘겨 덮으면 오른쪽 반쪽 자리에 표지
        # 펼친 왼쪽 면에 손을 얹었다가(7.6) 오른쪽으로 넘겨 덮는다(7.7). 닫힌 기록장은 오른쪽 반쪽 자리
        piece("hand", "bear-hand-flat", [(7.4, -80, OFF_B), (7.55, -75, 40), (7.62, -70, 10), (7.7, 75, 15), (7.85, 75, 175), (8.3, 75, 175)], z=60)
    if n == 7:                                                     # 11.9~13.2 첫 잔을 줄에 놓고(12.0 톡), 새 잔에 따르고, 가져간다
        piece("nb", "notebook-closed", [(11.9, *NB_C, 0)], z=20)
        piece("c1", "cup-empty", [(11.9, SLOT[0] + 40, OFF_B - 100), (12.0, SLOT[0] + CROOK[0][0], ROW + CROOK[0][1], CROOK[0][2])], z=30)
        piece("hand", "bear-hand-flat", [(11.9, SLOT[0] + 40, OFF_B), (12.0, SLOT[0] + CROOK[0][0], ROW - 120), (12.08, SLOT[0], ROW - 120),
                                          (12.25, SLOT[0] + 60, OFF_B), (12.8, POUR, OFF_B), (12.9, POUR, ROW - 120), (13.2, POUR + 20, OFF_B - 60)], z=60)
        piece("c2", "cup-empty", [(11.9, POUR, ROW), (12.9, POUR, ROW), (13.2, POUR + 20, OFF_B - 60 + 150)],
              seq=[(12.2, "cup-third"), (12.4, "cup-twothird"), (12.6, "cup-full")], z=30)
        piece("jug", "jug", [(11.9, POUR + 150, OFF_T), (12.1, *JUG), (12.8, *JUG), (12.88, POUR + 160, OFF_T)], z=50)
    if n == 9:                                                     # 15.6~18.1 둘째 빈 잔(15.7 톡) → 따름 → 가져감 → 빈 채 돌아옴(17.1 톡) → 윙키 손이 가지런히(17.3 스윽)
        piece("nb", "notebook-closed", [(15.6, *NB_C, 0)], z=20)
        a = CROOK
        piece("c1", "cup-empty", [(15.6, SLOT[0] + a[0][0], ROW + a[0][1], a[0][2]), (17.33, SLOT[0] + a[0][0], ROW + a[0][1], a[0][2]), (17.42, SLOT[0], ROW, 0)], z=30)
        piece("c2", "cup-empty", [(15.6, SLOT[1] + 40, OFF_B - 100), (15.7, SLOT[1] + a[1][0], ROW + a[1][1], a[1][2]), (17.5, SLOT[1] + a[1][0], ROW + a[1][1], a[1][2]), (17.58, SLOT[1], ROW, 0)], z=30)
        piece("c3", "cup-empty", [(15.6, POUR, ROW), (16.5, POUR, ROW), (16.75, POUR + 20, OFF_B - 60 + 150), (16.95, SLOT[2] + 40, OFF_B - 100),
                                  (17.1, SLOT[2] + a[2][0], ROW + a[2][1], a[2][2]), (17.58, SLOT[2] + a[2][0], ROW + a[2][1], a[2][2]), (17.67, SLOT[2], ROW, 0)],
              seq=[(15.9, "cup-third"), (16.1, "cup-twothird"), (16.3, "cup-full"), (16.95, "cup-empty")], z=30)
        piece("jug", "jug", [(15.6, POUR + 150, OFF_T), (15.8, *JUG), (16.4, *JUG), (16.48, POUR + 160, OFF_T)], z=50)
        piece("hand", "bear-hand-flat", [(15.6, SLOT[1] + 40, OFF_B), (15.7, SLOT[1] + a[1][0], ROW - 120), (15.78, SLOT[1], ROW - 120), (15.95, SLOT[1] + 60, OFF_B),
                                         (16.4, POUR, OFF_B), (16.5, POUR, ROW - 120), (16.75, POUR + 20, OFF_B - 60), (16.95, SLOT[2] + 40, OFF_B),
                                         (17.1, SLOT[2] + a[2][0], ROW - 120), (17.18, SLOT[2], ROW - 120), (17.3, SLOT[2] + 60, OFF_B)], z=60)
        # 윙키 손(위에서): 잔 셋 뚜껑을 차례로 눌러 맞춘다
        piece("wh", "winky-hand", [(15.6, SLOT[0], OFF_T), (17.25, SLOT[0], OFF_T), (17.33, SLOT[0] + a[0][0], ROW - 200), (17.42, SLOT[0], ROW - 200),
                                   (17.5, SLOT[1] + a[1][0], ROW - 200 + a[1][1]), (17.58, SLOT[1], ROW - 200), (17.67, SLOT[2], ROW - 200), (17.75, SLOT[2], ROW - 200),
                                   (17.85, SLOT[2], OFF_T)], z=60)
    if n in (15, 17, 21):
        nb = NB_W if n != 21 else NB_O21
        piece("nb", "notebook-open", [(0, *nb, 0)], z=20)
    if n == 15:                                                    # 28.9~30.1 「사과주스 한 잔」을 한 자씩(29.0~29.9). 연필 끝이 다음 글자 자리
        piece("hand", "bear-hand-pencil", [(28.9, 60, OFF_B)] + WRITE_KEYS(15), z=60)
    if n == 17:                                                    # 30.6~31.8 「한」에 줄(30.7~31.0) → 위에 「세」(31.1~31.5)
        piece("hand", "bear-hand-pencil", WRITE_KEYS(17), z=60)
        piece("strike", "strike-1", [(30.6, *STRIKE_AT(), 0)], seq=[(30.7, "strike-1"), (30.8, "strike-2"), (30.92, "strike-3")], vis=(30.7, None), z=25)
    if n == 21:                                                    # 41.5~45.0 윙키 손이 잔 셋(41.6·41.85·42.1 톡) → 곰 손이 위로 밀어 줌(42.5~43.1 스윽) → 사과(43.3 톡)
        piece("ap1", "apple-whole", [(41.5, 215, 120)], z=30)
        piece("ap2", "apple-whole", [(41.5, 215, 260), (43.15, 215, 260), (43.3, SLOT[1], ROW)], z=30)
        PUSH = -150
        for i, tp in enumerate((41.6, 41.85, 42.1)):
            piece(f"c{i + 1}", "cup-empty", [(41.5, SLOT[i], ROW - 600), (tp - 0.09, SLOT[i], ROW - 330), (tp, SLOT[i], ROW), (42.5, SLOT[i], ROW), (43.1, SLOT[i], ROW + PUSH)],
                  vis=(tp - 0.09, None), z=30)
        wk = [(41.5, SLOT[0], OFF_T)]
        for i, tp in enumerate((41.6, 41.85, 42.1)):
            wk += [(tp - 0.09, SLOT[i], ROW - 330 - 200), (tp, SLOT[i], ROW - 200), (tp + 0.09, SLOT[i] + 20, ROW - 520)]
        wk += [(42.3, SLOT[2], OFF_T)]
        piece("wh", "winky-hand", wk, z=60)
        piece("hand", "bear-hand-flat", [(41.5, SLOT[1], OFF_B), (42.35, SLOT[1], OFF_B), (42.5, SLOT[1], ROW + 60), (43.1, SLOT[1], ROW + 60 + PUSH),
                                         (43.2, 215, 260 + 45), (43.3, SLOT[1], ROW + 45), (43.4, SLOT[1] + 30, ROW + 120), (45.0, SLOT[1] + 30, ROW + 120)], z=60)
    return P

# 칸 글자(기록장). 「간식」 칸 글자 자리: 아래 줄 「사과주스 한 잔」, 위 줄은 「한」 위의 「세」
ENTRY = "사과주스 한 잔"
NB_LABELS = ["아침", "점심", "저녁", "간식"]
WRITE_T = (29.0, 29.9)
_NB = {}
def nb_text(nb, ppm):
    """펼친 기록장 조각(층 nb)의 칸 글자 배치: 칸 이름 넷 + 간식 칸 글자. 크기는 6절 공식(칸 높이 × 0.7 ÷ 줄 수, 칸 폭 × 0.9 ÷ 글자 폭)."""
    an = K["notebook-open"]["anchor"]; box = lambda r: (nb["x"] + r[0] * nb["w"], nb["y"] + r[1] * nb["h"], nb["x"] + r[2] * nb["w"], nb["y"] + r[3] * nb["h"])
    rows = []
    lab = [box(r) for r in an["labels"]]
    lpx = int(min(min((b[3] - b[1]) * 0.7, (b[2] - b[0]) * 0.9 / (G(s, 100) / 100)) for b, s in zip(lab, NB_LABELS)))
    for b, s in zip(lab, NB_LABELS):
        w = G(s, lpx); rows.append(dict(s=s, px=lpx, x=(b[0] + b[2]) / 2 - w / 2, y=(b[1] + b[3]) / 2 - lpx * 0.55, w=w, weight=700, font="gaegu", box=b))
    e = box(an["entry"]); epx = int(min((e[3] - e[1]) * 0.7 / 2, (e[2] - e[0]) * 0.9 / (G(ENTRY, 100) / 100)))
    base = nb["y"] + an["base"] * nb["h"]                                              # 남긴 아래 줄에 글자 밑을 맞춘다
    x0 = e[0] + (e[2] - e[0]) * 0.05; y1 = base - epx * 0.98; y0 = y1 - epx * 1.12
    chars = []
    for i, c in enumerate(ENTRY):
        xx = x0 + G(ENTRY[:i], epx) if i else x0
        if c != " ": chars.append(dict(s=c, px=epx, x=xx, y=y1, w=G(c, epx), weight=700, font="gaegu", box=e, pen=True, i=i))
    han = next(c for c in chars if c["s"] == "한")
    se = dict(s="세", px=epx, x=han["x"] + han["w"] / 2 - G("세", epx) / 2, y=y0, w=G("세", epx), weight=700, font="gaegu", box=e, pen=True, i=99)
    return rows, chars, han, se, e
def WRITE_KEYS(n):
    """연필 끝 열쇠(mm): 15번은 글자마다 그 글자 오른쪽 아래, 17번은 「한」을 가로질러 긋고 위로 올라 「세」."""
    rows, chars, han, se, e = _NB["layout"]; p = TPPM["write"]
    mm = lambda x, y: ((x - 540) / p, (y - 960) / p)
    if n == 15:
        t0, t1 = WRITE_T; ks = []; dt = (t1 - t0) / len(chars)
        for j, c in enumerate(chars):
            ks.append((t0 + j * dt, *mm(c["x"] + c["w"] * 0.2, c["y"] + c["px"] * 0.85)))
            ks.append((t0 + (j + 0.75) * dt, *mm(c["x"] + c["w"] * 0.95, c["y"] + c["px"] * 0.6)))
        last = ks[-1]; return ks + [(30.1, last[1], last[2])]
    yc = han["y"] + han["px"] * 0.55
    return [(30.6, *mm(chars[-1]["x"] + chars[-1]["w"], chars[-1]["y"] + chars[-1]["px"] * 0.6)), (30.7, *mm(han["x"] - 4, yc)), (31.0, *mm(han["x"] + han["w"] + 4, yc)),
            (31.1, *mm(se["x"], se["y"] + se["px"] * 0.8)), (31.5, *mm(se["x"] + se["w"], se["y"] + se["px"] * 0.5)), (31.8, *mm(se["x"] + se["w"], se["y"] + se["px"] * 0.5))]
def STRIKE_AT():
    rows, chars, han, se, e = _NB["layout"]; p = TPPM["write"]
    return ((han["x"] + han["w"] / 2 - 540) / p, (han["y"] + han["px"] * 0.55 - 960) / p)

# ── 7. 컷 표 (대본 9판, 제작 시각은 README 「기획과 다르게 한 것」 1: 자막 1.2초·초당 5음절 규칙 때문에 여섯 곳을 늘려 50.0초)
#    who: 인물, at: 자리, seq: (시각, 자세-표정). '말' = 대사 중 평온↔말하기 교대
#    line: (인물, 시작, 대사(자막 줄은 /로), 목소리 표시). props: (조각, 놓이는 곳, 대상[, 옵션]). tag: 이름표(인물, 자리)
CUTS = [
 dict(n=1, t=(0.0, 1.2), set="door", cam="CU", chars=[("winky", "중", [(0, "서기-말")])],
      props=[("box-closed", "floor", 1080, dict(label="사과/엄마가", front="winky"))],
      line=("winky", 0.0, "택배요!"), tag=("winky", "우하"), sfx=[("띵동", 0.0)]),   # 9e: 첫 컷 로고 뺌(로고는 썸네일에만), 제목 글자도 넣지 않음
 dict(n=2, t=(1.2, 4.1), set="kitchen", cam="M", chars=[("bear", "좌", [(0, "서기-웃음")]), ("winky", "중", [(0, "서기-웃음")]), ("panda", "우", [(0, "내밀기-웃음")])],
      props=[("cup-full", "hand", "panda", dict(grip="bottom")), TOP_NB("notebook-open"), ("box-open", "floor", 1380), ("jug", "top", ("counter", 1310))],
      line=("panda", 1.2, "아빠, 엄마가 사과 보냈어./설탕 안 넣고 갈았어~")),
 dict(n=3, t=(4.1, 7.4), set="kitchen", cam="CU", chars=[("bear", "중", [(0, "상반신컵가득-말"), ("끝", "상반신컵가득-평온")])],
      line=("bear", 4.1, "과일인데 뭐~/몸에 좋은 건 안 적어도 되지."), tag=("bear", "좌하")),
 dict(n=4, t=(7.4, 8.3), set="table", cam="판", ppm="note", sfx=[("탁", 7.7)]),
 dict(n=5, t=(8.3, 10.2), set="kitchen", cam="CU", chars=[("bear", "중", [(0, "상반신컵가득-웃음"), (8.5, "상반신컵-웃음"), (8.6, "상반신컵-말"), ("끝", "상반신컵-웃음")])],
      line=("bear", 8.6, "캬~ 맛있다. 한 잔만 더!"), sfx=[("꿀꺽", 8.4)]),
 dict(n=6, t=(10.2, 11.9), set="kitchen", cam="M", chars=[("bear", "좌", [(0, "내밀기컵-웃음")]), ("winky", "중", [(0, "따르기-웃음")]), ("panda", "우", [(0, "뒤돌기")])],
      props=[TOP_NB("notebook-closed")], line=("winky", 10.2, "제가 따라 드릴게요!")),
 dict(n=7, t=(11.9, 13.2), set="table", cam="판", ppm="cups", sfx=[("톡", 12.0), ("쪼르륵", 12.2)]),
 dict(n=8, t=(13.2, 15.6), set="kitchen", cam="CU", chars=[("bear", "중", [(0, "상반신컵가득-말"), ("끝", "상반신컵가득-웃음")])],
      line=("bear", 13.2, "잔이 작잖아~/두 잔이 한 잔이지.")),
 dict(n=9, t=(15.6, 18.1), set="table", cam="판", ppm="cups", sfx=[("톡", 15.7), ("쪼르륵", 15.9), ("톡", 17.1), ("스윽", 17.3)]),
 dict(n=10, t=(18.1, 21.3), set="office", cam="M", chars=[("bear", "좌", [(0, "들기-웃음")]), ("winky", "중", [(0, "서기-평온")]), ("penguin", "우", [(0, "서기-평온")])],
      props=[("notebook-closed", "hand", "bear", dict(grip="center"))], title=(18.1, 19.3, "다음 날"), tag=("penguin", "우하"),
      line=("penguin", 19.3, "어제 간식은 뭐 드셨어요?")),
 dict(n=11, t=(21.3, 23.6), set="office", cam="CU", chars=[("bear", "중", [(0, "상반신-웃음"), (21.4, "상반신-말"), ("끝", "상반신-웃음")])],
      line=("bear", 21.4, "아뇨, 먹은 건 하나도 없어요.")),
 dict(n=12, t=(23.6, 25.6), set="office", cam="CU", chars=[("winky", "중", [(0, "서기-웃음"), (23.6, "서기-말"), ("끝", "서기-웃음")])],
      line=("winky", 23.6, "맞아요!/주스만 세 잔이요.")),
 dict(n=13, t=(25.6, 27.7), set="office", cam="CU", chars=[("bear", "중", [(0, "상반신-당황"), (26.4, "상반신-말"), ("끝", "상반신-당황")])],
      props=[("sweat", "sweat", "bear", dict(show=25.7))], sfx=[("삐질", 25.7)],
      line=("bear", 26.4, "…마신 것도 쳐요?", {0: "당황"})),
 dict(n=14, t=(27.7, 28.9), set="office", cam="CU", chars=[("penguin", "중", [(0, "상반신-말"), ("끝", "상반신-평온")])],
      line=("penguin", 27.7, "치죠.")),
 dict(n=15, t=(28.9, 30.1), set="table", cam="판", ppm="write", sfx=[("사각", 29.0)], write=True),
 dict(n=16, t=(30.1, 30.6), set="office", cam="M", chars=[("bear", "좌", [(0, "들기-당황")]), ("winky", "중", [(0, "서기-웃음")]), ("penguin", "우", [(0, "서기-평온")])],
      props=[("notebook-open", "hand", "bear", dict(grip="center"))]),
 dict(n=17, t=(30.6, 31.8), set="table", cam="판", ppm="write", sfx=[("사각", 30.7), ("사각", 31.1)], write=True),
 dict(n=18, t=(31.8, 34.7), set="office", cam="M", chars=[("bear", "좌", [(0, "들기-웃음")]), ("winky", "중", [(0, "서기-평온")]), ("penguin", "우", [(0, "서기-평온")])],
      props=[("notebook-open", "hand", "bear", dict(grip="center"))], source=SOURCE_WHO,
      line=("penguin", 31.8, "설탕 안 넣어도/주스엔 당이 있어요.")),
 dict(n=19, t=(34.7, 38.5), set="office", cam="CU", chars=[("penguin", "중", [(0, "상반신-말"), ("끝", "상반신-평온")])], source=SOURCE_KDA,
      line=("penguin", 34.7, "과일도 갈면 달라요./배가 안 불러서 자꾸 마시게 돼요.")),
 dict(n=20, t=(38.5, 41.5), set="kitchen", cam="M", chars=[("bear", "좌", [(0, "서기-웃음")]), ("winky", "중", [(0, "서기-웃음")]), ("panda", "우", [(0, "내밀기-웃음")])],
      props=[("jug-empty", "hand", "panda", dict(grip="bottom")), ("apple-whole", "top", ("table", 520)), ("apple-whole", "top", ("table", 680)), TOP_NB("notebook-open")],
      title=(38.5, 39.3, "그날 저녁"), line=("bear", 39.3, "오늘은 그냥 사과로 먹을게.")),
 dict(n=21, t=(41.5, 45.0), set="table", cam="판", ppm="cups", write=True, sfx=[("톡", 41.6), ("톡", 41.85), ("톡", 42.1), ("스윽", 42.5), ("톡", 43.3)],
      line=("bear", 43.4, "윙키도 하나 먹어라."), title=(43.3, 44.8, "갈지 않고, 씹어서")),   # 9c: 사과를 놓는 순간 1.5초
 dict(n=22, t=(45.0, 47.0), set="kitchen", cam="CU", chars=[("winky", "중", [(0, "양손들기-웃음")])], iris=True,
      props=[("apple-whole", "hand", "winky", dict(grip="low"))], sfx=[("아삭", 45.3), ("띠로리", 45.8), ("뿅", 46.45)]),
 dict(n=23, t=(47.0, 50.0), set="end", cam="board", chars=[], end=True),
]

def _warp_cut(c):
    c["t"] = tuple(W(t) for t in c["t"])
    if c.get("line"): c["line"] = (c["line"][0], W(c["line"][1])) + tuple(c["line"][2:])
    if c.get("title"): c["title"] = (W(c["title"][0]), W(c["title"][1]), c["title"][2])
    c["sfx"] = [(n, W(t)) for n, t in c.get("sfx", [])]
    c["chars"] = [(ch[0], ch[1], [(W(t) if isinstance(t, float) else t, p) for t, p in ch[2]]) + tuple(ch[3:]) for ch in c.get("chars", [])]
    for pr in c.get("props", []):
        if len(pr) > 3 and "show" in pr[3]: pr[3]["show"] = W(pr[3]["show"])
for _c in CUTS: _warp_cut(_c)

def cover_text(c, P):
    """덮인 기록장 표지 칸 「식사 기록장」. 펼친 프레임(4번 7.7 전)에서는 숨는다."""
    a = K["notebook-closed"]; tb = a["anchor"]["text"]; k = prop_k("notebook-closed", P["ppm"])
    w, h = a["w"] * k, a["h"] * k; cx, cy = P["origin"]; x0, y0 = cx - w / 2, cy - h / 2
    box = (x0 + tb[0] * w, y0 + tb[1] * h, x0 + tb[2] * w, y0 + tb[3] * h)
    s = "식사 기록장"; px = int(min((box[3] - box[1]) * 0.7, (box[2] - box[0]) * 0.9 / (tw(s, 100, "jua") / 100))); ww = tw(s, px, "jua")
    on = next((tt for tt, n in board_cut(c["n"])[0]["seq"] if n == "notebook-closed"), None) if P["frames"][0] != "notebook-closed" else None
    return dict(kind="label", t0=on, t1=None, layer=P["id"], textBox=box,
                rows=[dict(s=s, px=px, x=(box[0] + box[2]) / 2 - ww / 2, y=(box[1] + box[3]) / 2 - px * 0.55, w=ww, weight=800, t0=on, font="jua")])

def notebook_texts(c, P):
    """펼친 기록장 칸 글자: 칸 이름 넷(늘), 간식 칸 「사과주스 한 잔」(15번 한 자씩, 17·21번 처음부터), 「한」 줄(17번 긋기, 21번 처음부터), 「세」(17번 31.1~)."""
    a = K["notebook-open"]; k = prop_k("notebook-open", P["ppm"]); cx, cy = P["origin"]
    nb = dict(x=cx - a["w"] * k / 2, y=cy - a["h"] * k / 2, w=a["w"] * k, h=a["h"] * k)
    rows, chars, han, se, e = nb_text(nb, P["ppm"]); n = c["n"]; out = [dict(r) for r in rows]
    shut = next((tt for tt, f in board_cut(n)[0]["seq"] if f == "notebook-closed"), None)       # 4번: 덮이면 칸 이름도 사라진다
    for r in out: r["box"] = list(r["box"]); r["t1"] = shut
    if n in (15, 17, 21):
        dt = (WRITE_T[1] - WRITE_T[0]) / len(chars)
        for j, ch in enumerate(chars):
            r = dict(ch); r["box"] = list(e); r["t0"] = W(WRITE_T[0] + (j + 0.6) * dt) if n == 15 else None; out.append(r)
    if n in (17, 21):
        r = dict(se); r["box"] = list(e); r["t0"] = W(31.35) if n == 17 else None; out.append(r)
    res = dict(kind="label", t0=None, t1=None, layer=P["id"], textBox=e, rows=out, pen=True)
    if n == 21: res["strike"] = dict(x=han["x"] - 5, yc=han["y"] + han["px"] * 0.55, w=han["w"] + 10)
    return res

# 엔진 build() 첫머리에서 부른다: 펼친 기록장 칸 글자 배치(15·17번 판 배율 기준). 연필 열쇠·줄 긋기가 이 값을 쓴다
def prebuild():
    a = K["notebook-open"]; p = TPPM["write"]; k = prop_k("notebook-open", p)
    nb0 = dict(x=540 + NB_W[0] * p - a["w"] * k / 2, y=960 + NB_W[1] * p - a["h"] * k / 2, w=a["w"] * k, h=a["h"] * k)
    _NB["layout"] = nb_text(nb0, p); han = _NB["layout"][2]
    _NB["strike_k"] = (han["w"] + 10) / K["strike-3"]["w"]

# check.py 10번: 대본 9판 큐 시트(9b 제작 시각을 9c 시계 W()로). 이 밖의 음악 큐가 나오면 실패
CUE_SHEET = {(n, W(a), W(b)) for n, a, b in (("Q-TIME", 18.1, 19.3), ("Q-DOWN", 38.5, 39.3), ("Q-END", 47.0, 49.5))}
