"""r05 「하나만요」 회차 값(대본 2판, episodes/drafts/2026-11-13-r05-hanaman-script.md). engine/build.py가 자기 이름공간에서 exec 한다.
대본 시각 그대로 쓴다(시계 W() 없음). 대본과 다르게 한 것은 README.md 「기획과 다르게 한 것」."""

# 판 배율: 쪽지 컷 6.0(1·8번, 쪽지 750px), 5.0(22번), 7.0(35번, 아빠 글씨가 읽히게). 손은 조각 확대 1.3 한도 안에서 따로(판다 손 2.3, 곰 연필 손 4.0 = ep01 글자 컷)
TPPM = {"big": 6.0, "note": 5.0, "end": 7.0, "panda": 2.3, "bear": 4.0}
REG["prop"].setdefault("panda-paw", {"w": 200})   # ponytail: 판다 손바닥 폭(손가락 마디 가로) = panda-내밀기-웃음에서 잰 190px ÷ 0.936px/mm. 레지스트리 sizes에 올리면 지운다
TEAL = "set-table-teal"                           # 판 컷·끝 화면 깔판(2차, 흰 판 대신)
END_COLOR = ("#FFD45A", "#FFF3D6")                # 짙은 청록 끝 화면: 큰 줄 노랑, 작은 줄 따뜻한 흰색

TAGS = {"bear": ("곰 아빠", "마을버스 기사 · 2형 당뇨"), "hedgehog": ("도치 실장", "판다네 실장님 · 302호"), "penguin": ("펭귄 선생님", "위뉴 건강상담소 · 퇴근함")}
END = [("부모님이 당뇨면", 96), ("나도 검사 대상이에요", 96), None,
       ("검사는 담당 선생님과", 64), ("상의하세요", 64), None,
       ("의학 검수: 위뉴 의료진 ○○○ · 날짜", 44), None,
       ("근거: 대한당뇨병학회", 44), ("2025 당뇨병 진료지침 1-2", 44), None,
       ("AI로 만든 그림입니다", 44)]
# 큐 시트(대본). 2차: 전환 스팅 0.6초를 앞 컷 끝 0.3초부터 깔아 새 장면 첫 대사와 0.2초만 겹친다(덕킹). 30번은 첫 대사를 0.2초 늦췄다(초당 5음절 한도)
CUES = [("Q-TIME", 6.2, 6.8), ("Q-TIME", 18.0, 18.6), ("Q-TIME", 26.1, 26.7), ("Q-TIME", 55.4, 56.0), ("Q-DOWN", 63.5, 64.1), ("Q-END", 70.7, 73.7)]
CUE_SHEET = set(CUES)
CUE_OVERLAP = 0.3                                 # check 10 허용: 스팅이 앞 컷 자막 꼬리·새 대사 머리와 겹치는 최대 초(덕킹 −8dB)
D = 73.7

# ── 쪽지(note-list) 칸: 조각 상자 안 비율. 위 판 = 제목, 아래 판 = 비어 있는 띠(마지막 컷 아빠 글씨), 줄 = 판다 글씨 열두 줄(그림)
NOTE_TITLE, NOTE_BAND = (0.08, 0.025, 0.92, 0.105), (0.04, 0.89, 0.96, 0.99)   # 아빠 글씨 띠는 판보다 조금 넓게(손글씨가 넘친다)
NOTE_LINE_Y = [0.155 + 0.0645 * i for i in range(12)]       # 줄 가운데(그림에서 잰 값)
NOTE_LINE_X = (0.19, 0.91)                                  # 줄(그은 지그재그 포함) 가로 범위
TITLE_S, DAD_S = "의사 선생님께 물어볼 것", "우리 딸도 검사 받아야 돼요?"
PEN = "#4A4E58"

def _mm(fx, fy): return ((fx - 0.5) * 125, (fy - 0.5) * 210)     # 쪽지 안 비율 → 판 mm(쪽지 가운데 = 원점)
_x0, _x1 = _mm(NOTE_LINE_X[0], 0)[0], _mm(NOTE_LINE_X[1], 0)[0]
OFF_B = 400                                                 # 손이 화면 아래 밖(mm)

def board_cut(n):
    P = []
    def piece(id_, f, keys, seq=None, vis=None, z=40, ppm=None, crop=None): P.append(dict(id=id_, f=f, keys=keys, seq=seq or [], vis=vis, z=z, ppm=ppm, crop=crop))
    if n == 1:      # 0.0~2.0 펼친 쪽지 1.45초 → 판다 손이 아래 반을 올려 접는다(1.4 스윽)
        piece("nb", "note-list", [(0, 0, 0)], vis=(0, 1.45), z=20)
        piece("nbf", "note-list-folded", [(0, 0, -52.5)], vis=(1.45, None), z=20)
        piece("hand", "panda-hand", [(0, 20, OFF_B), (0.9, 20, OFF_B), (1.15, 20, 98), (1.25, 20, 98), (1.45, 20, -15), (1.55, 20, -15), (1.8, 20, OFF_B), (2.0, 20, OFF_B)], z=60, ppm="panda")
    if n == 8:      # 13.3~14.9 판다 손이 펼쳐 든 쪽지: 열두 줄에 표시 하나 없다
        piece("nb", "note-list", [(0, 0, 0)], z=20)
        piece("hand", "panda-hand", [(13.3, 40, OFF_B), (13.5, 40, 100), (14.9, 40, 100)], z=60, ppm="panda")
    if n == 22:     # 41.8~43.6 곰 연필 손이 첫 세 줄을 긋는다(사각 ×3). 그은 줄 = note-list-crossed의 그 줄을 왼쪽부터 세 번에 걸쳐 드러낸다
        piece("nb", "note-list", [(0, 0, 0)], z=20)
        ks = [(41.8, _x0, OFF_B)]
        for i in range(3):
            fy = NOTE_LINE_Y[i]; y = _mm(0, fy)[1]; ts = 41.95 + 0.5 * i
            ks += [(ts, _x0, y), (ts + 0.3, _x1, y)]
            for j in (1, 2, 3):
                piece(f"x{i}{j}", "note-list-crossed", [(0, 0, 0)], vis=(ts + 0.1 * (j - 1), None), z=25,
                      crop=(NOTE_LINE_X[0], fy - 0.031, NOTE_LINE_X[0] + (NOTE_LINE_X[1] - NOTE_LINE_X[0]) * j / 3, fy + 0.031))
        ks += [(43.15, _x1, _mm(0, NOTE_LINE_Y[2])[1]), (43.45, _x1 + 20, OFF_B), (43.6, _x1 + 20, OFF_B)]
        piece("hand", "bear-hand-pencil", ks, z=60, ppm="bear")
    if n == 35:     # 67.7~70.7 판다 손이 접힌 쪽지를 펴면(68.3) 열두 줄이 다 그어져 있고 맨 아래에 아빠 글씨
        piece("nbf", "note-list-folded", [(0, 0, 0)], vis=(67.7, 68.3), z=20)
        piece("nbx", "note-list-crossed", [(0, 0, 0)], vis=(68.3, None), z=20)
        piece("hand", "panda-hand", [(67.7, 15, 300), (67.95, 15, 48), (68.3, 15, 95), (68.55, 15, 300), (70.7, 15, 300)], z=60, ppm="panda")
    return P

def extra_texts(c, L):
    """판 위 쪽지 칸 글자: 제목(판다 글씨), 줄 그은 쪽지 아래 띠에 아빠 글씨. 조각 층에 붙어 같이 숨고 움직인다."""
    out = []
    for l in L:
        if l.get("place") != "board" or l["frames"][0] not in ("note-list", "note-list-crossed") or l.get("crop"): continue
        # 제목 = 인쇄한 듯 주아 굵게(남색), 아빠 한 줄 = 개구 굵은 연필 손글씨(짙은 회색). 둘이 다르게 보이게
        items = [(NOTE_TITLE, TITLE_S, "jua", "#10233F")] + ([(NOTE_BAND, DAD_S, "gaegu", "#24262C")] if l["frames"][0] == "note-list-crossed" else [])
        rows = []
        for fb, s, f, col in items:
            b = (l["x"] + fb[0] * l["w"], l["y"] + fb[1] * l["h"], l["x"] + fb[2] * l["w"], l["y"] + fb[3] * l["h"])
            px = int(min((b[3] - b[1]) * 0.8, (b[2] - b[0]) * 0.95 / (tw(s, 100, f) / 100))); w = tw(s, px, f)
            rows.append(dict(s=s, px=px, x=(b[0] + b[2]) / 2 - w / 2, y=(b[1] + b[3]) / 2 - px * 0.55, w=w, weight=800, font=f, box=list(b), color=col))
        out.append(dict(kind="label", t0=None, t1=None, layer=l["id"], textBox=rows[0]["box"], rows=rows))
    return out

# ── 컷 표(대본 2판). 자리: 두 사람 컷은 좌2·우2. 판다 「내밀기」는 그림이 왼쪽으로만 내밀어서, 판다가 건네는 컷은 받는 사람이 판다 왼쪽(README)
DOOR_E = "set-door-m-evening"
CU_G, CU_A, CU_B = "set-door-cu-g", "set-recycle-cu-a", "set-recycle-cu-b"
TALK = lambda pose, t, emo_end=None: [(0, pose + "-웃음" if emo_end == "웃음" else pose + "-평온"), (t, pose + "-말"), ("끝", pose + ("-웃음" if emo_end == "웃음" else "-평온"))]
CUTS = [
 # S1 아침
 dict(n=1, t=(0.0, 2.0), set="table", cam="판", ppm="big", bg=TEAL, title=(0.0, 2.0, "아빠 진료 날 아침"), sfx=[("스윽", 1.4)]),
 dict(n=2, t=(2.0, 4.4), set="door", cam="M", chars=[("bear", "좌2", [(0, "신발신기-웃음"), (3.3, "신발신기쪽지-웃음")]), ("panda", "우2", [(0, "내밀기쪽지-웃음"), (3.3, "내밀기-웃음")])],
      line=("panda", 2.1, "아빠, 오늘 이거 꼭 물어봐."), sfx=[("스윽", 3.2)]),
 dict(n=3, t=(4.4, 6.5), set="door", cam="CU", bg=CU_G, chars=[("bear", "중", TALK("상반신쪽지", 4.5, "웃음"))],
      line=("bear", 4.5, "허허허! 시험 보러 가냐?"), tag=("bear", "좌하")),
 # S2 저녁
 dict(n=4, t=(6.5, 7.9), set="door", cam="M", bg=DOOR_E, chars=[("bear", "좌2", [(0, "서기쪽지-웃음")], dict(move=[(6.5, -160), (6.9, 0)])), ("panda", "우2", [(0, "서기-말")])],
      title=(6.5, 7.7, "그날 저녁"), line=("panda", 6.6, "아빠, 뭐래?"), sfx=[("탁", 6.5)]),
 dict(n=5, t=(7.9, 9.9), set="door", cam="CU", bg=CU_G, chars=[("bear", "중", TALK("상반신쪽지", 8.0, "웃음"))], line=("bear", 8.0, "허허허! 젊어 보인대.")),
 dict(n=6, t=(9.9, 11.3), set="door", cam="M", bg=DOOR_E, chars=[("bear", "좌2", [(0, "서기쪽지-웃음")]), ("panda", "우2", [(0, "서기-말")])], line=("panda", 10.0, "그거 말고.")),
 dict(n=7, t=(11.3, 13.3), set="door", cam="CU", bg=CU_G, chars=[("bear", "중", [(0, "상반신쪽지-말"), ("끝", "상반신쪽지-당황")])], line=("bear", 11.4, "그 말밖에 안 하던데.")),
 dict(n=8, t=(13.3, 14.9), set="table", cam="판", ppm="big", bg=TEAL, sfx=[("스윽", 13.4)]),   # 2차: 펼친 쪽지를 크게(표시 하나 없다)
 dict(n=9, t=(14.9, 16.3), set="door", cam="CU", bg=CU_G, chars=[("panda", "중", [(0, "상반신-시무룩")])],
      line=("panda", 15.0, "아 진짜…", {0: "시무룩"})),
 dict(n=10, t=(16.3, 18.3), set="door", cam="M", bg=DOOR_E, chars=[("bear", "좌2", [(0, "서기쪽지-당황")]), ("panda", "우2", [(0, "서기-말")])],
      line=("panda", 16.4, "다음엔 나도 같이 가.")),
 # S3 회사
 dict(n=11, t=(18.3, 22.4), set="company", cam="M", chars=[("panda", "좌2", [(0, "서기-말")]), ("hedgehog", "우2", [(0, "앉기-평온")], dict(mag=1.35))],
      title=(18.3, 19.5, "다음 날"), tag=("hedgehog", "우하"), line=("panda", 18.4, "실장님, 반차 좀 쓸게요./아빠 병원 따라가려고요.")),
 dict(n=12, t=(22.4, 25.0), set="company", cam="CU", chars=[("hedgehog", "중", [(0, "상반신-당황")])],
      line=("hedgehog", 22.5, "(많이 편찮으신가… 묻지 말자)", {0: "속마음"})),
 dict(n=13, t=(25.0, 26.4), set="company", cam="M", chars=[("panda", "좌2", [(0, "서기-평온")]), ("hedgehog", "우2", [(0, "앉기-말")], dict(mag=1.35))],
      line=("hedgehog", 25.1, "네. 다녀와요."), sfx=[("톡", 26.0)]),
 # S4 분리수거장(밤)
 dict(n=14, t=(26.4, 28.0), set="recycle", cam="M", chars=[("penguin", "좌2", [(0, "퇴근-서기-평온")]), ("panda", "우2", [(0, "양손들기-놀람")])],
      title=(26.4, 27.6, "진료 이틀 전 밤"), tag=("penguin", "좌상"), line=("panda", 26.5, "선생님!"), sfx=[("탁", 26.4)]),
 dict(n=15, t=(28.0, 29.5), set="recycle", cam="CU", bg=CU_A, chars=[("penguin", "중", [(0, "퇴근-상반신-눈감음")])],
      tag=("penguin", "좌상", True), line=("penguin", 28.1, "…퇴근했는데요.")),
 dict(n=16, t=(29.5, 31.5), set="recycle", cam="M", chars=[("penguin", "좌2", [(0, "퇴근-서기-평온")]), ("panda", "우2", [(0, "내밀기쪽지-웃음")])], line=("panda", 29.6, "모레 아빠 병원 가요.")),
 dict(n=17, t=(31.5, 33.6), set="recycle", cam="M", chars=[("penguin", "좌2", [(0, "퇴근-서기-평온")]), ("panda", "우2", [(0, "내밀기쪽지펼침-웃음")])],
      line=("panda", 31.6, "이거 다 물어봐도 돼요?"), sfx=[("스윽", 31.7)]),
 dict(n=18, t=(33.6, 35.4), set="recycle", cam="CU", bg=CU_A, chars=[("penguin", "중", TALK("퇴근-상반신", 33.7))], line=("penguin", 33.7, "진료 3분이에요.")),
 dict(n=19, t=(35.4, 37.2), set="recycle", cam="CU", bg=CU_A, chars=[("penguin", "중", TALK("퇴근-상반신", 35.5))], line=("penguin", 35.5, "…하나만 고르세요.")),
 dict(n=20, t=(37.2, 39.0), set="recycle", cam="M", chars=[("bear", "좌2", [(0, "들기-웃음"), (38.6, "들기쪽지-웃음")], dict(move=[(37.2, -620), (37.75, 0)])), ("panda", "우2", [(0, "내밀기쪽지-웃음"), (38.6, "내밀기-웃음")])],   # 3차: 쪽지를 쥔 손을 그림에 구웠다(떠 있는 스티커 대신)
      line=("panda", 37.3, "아빠, 하나만 골라.")),
 dict(n=21, t=(39.0, 41.8), set="recycle", cam="CU", bg=CU_B, chars=[("bear", "중", TALK("상반신", 39.1, "웃음"))], line=("bear", 39.1, "허허허! 원 플러스 원은 안 되냐?")),
 dict(n=22, t=(41.8, 43.6), set="table", cam="판", ppm="note", bg=TEAL, line=("bear", 41.9, "이건 아빠도 알아."), sfx=[("사각", 41.95), ("사각", 42.45), ("사각", 42.95)]),
 dict(n=23, t=(43.6, 45.0), set="recycle", cam="CU", bg=CU_B, chars=[("panda", "중", [(0, "상반신-놀람")])], line=("panda", 43.7, "그걸 왜 지워!", {0: "놀람"})),
 dict(n=24, t=(45.0, 47.8), set="recycle", cam="M", chars=[("penguin", "좌2", [(0, "퇴근-서기-평온")]), ("panda", "우2", [(0, "서기-평온")])], line=("penguin", 45.1, "근데 따님은 검사 받아 봤어요?"), sfx=[("탁", 45.0)]),
 dict(n=25, t=(47.8, 49.2), set="recycle", cam="CU", bg=CU_B, chars=[("panda", "중", TALK("상반신", 47.9))], line=("panda", 47.9, "네?")),
 dict(n=26, t=(49.2, 51.6), set="recycle", cam="CU", bg=CU_A, chars=[("penguin", "중", TALK("퇴근-상반신", 49.3))], line=("penguin", 49.3, "아버님이 당뇨시잖아요.")),
 dict(n=27, t=(51.6, 52.9), set="recycle", cam="CU", bg=CU_B, chars=[("panda", "중", [(0, "상반신-놀람")])], still=True),
 dict(n=28, t=(52.9, 54.3), set="recycle", cam="CU", bg=CU_B, chars=[("bear", "중", [(0, "상반신쪽지-걱정")])],   # 3차: 걱정 얼굴판(웃음기 없음)
      line=("bear", 53.0, "…너 안 받았어?", {0: "시무룩"})),
 dict(n=29, t=(54.3, 55.7), set="recycle", cam="CU", bg=CU_B, chars=[("panda", "중", [(0, "상반신-시무룩")])], line=("panda", 54.4, "아직.", {0: "속삭임"})),
 # S5 회사
 dict(n=30, t=(55.7, 60.2), set="company", cam="M", chars=[("panda", "좌2", [(0, "서기-말")]), ("hedgehog", "우2", [(0, "앉기-평온")], dict(mag=1.35))],
      title=(55.7, 56.9, "다음 날"), line=("panda", 56.0, "실장님, 반차 하나만 더요./이번엔 제 검사 받으려고요.")),
 dict(n=31, t=(60.2, 62.3), set="company", cam="CU", chars=[("hedgehog", "중", [(0, "상반신-당황"), (60.8, "상반신-가시")])],
      line=("hedgehog", 60.3, "(…무슨 검사지? 묻지 말자)", {0: "속마음"})),
 dict(n=32, t=(62.3, 63.8), set="company", cam="M", chars=[("panda", "좌2", [(0, "서기-평온")]), ("hedgehog", "우2", [(0, "앉기-말")], dict(mag=1.35))],
      line=("hedgehog", 62.4, "네. 잘 받고 와요."), sfx=[("톡", 63.4)]),
 # S6 대기실
 dict(n=33, t=(63.8, 65.9), set="clinic", cam="M", chars=[("bear", "좌2", [(0, "앉기쪽지-평온")]), ("panda", "우2", [(0, "앉기-평온")])],   # 3차: 판다 쪽으로 쪽지를 내민 그림을 구웠다
      title=(63.8, 65.0, "아빠 진료 날"), line=("panda", 63.9, "그거 아직 갖고 있었어?")),
 dict(n=34, t=(65.9, 67.7), set="clinic", cam="CU", chars=[("bear", "중", TALK("상반신", 66.0))], line=("bear", 66.0, "하나만 물으라며.")),
 dict(n=35, t=(67.7, 70.7), set="table", cam="판", ppm="end", bg=TEAL, sfx=[("스윽", 68.2)]),
 dict(n=36, t=(70.7, 73.7), set="end", cam="board", bg=TEAL, chars=[], end=True),
]

# ── 3차 연출(Fable 디렉터 연출 패스 2026-11-13, 미르님 「48·52초 밋밋, 29초 펭귄이 멈춰 있다」)
# 1) 시간 늘리기: 15번 +0.3(빤히 보는 한 박), 27번 +0.5(늦게 깨닫는 정지), 29번 +0.2(「아직.」 뒤 정적). 아래 값은 옛 시각, SH가 새 시각으로 옮긴다
RETIME = [(29.5, 0.3), (52.9, 0.5), (55.7, 0.2)]
def SH(t): return round(t + sum(d for b, d in RETIME if t >= b - 1e-6), 3) if isinstance(t, (int, float)) else t
for _c in CUTS:
    _c["t"] = tuple(SH(v) for v in _c["t"])
    if _c.get("line"): _c["line"] = (_c["line"][0], SH(_c["line"][1]), *_c["line"][2:])
    if _c.get("title"): _c["title"] = (SH(_c["title"][0]), SH(_c["title"][1]), _c["title"][2])
    _c["sfx"] = [(n, SH(t)) for n, t in _c.get("sfx", [])]
    _c["chars"] = [(ch[0], ch[1], [(SH(t), p) for t, p in ch[2]], *([dict(ch[3], **({"move": [(SH(a), b) for a, b in ch[3]["move"]]} if "move" in ch[3] else {}))] if len(ch) > 3 else [])) for ch in _c.get("chars", [])]
    _c["props"] = [(*pr[:3], dict(pr[3], vis=tuple(SH(v) if v is not None else None for v in pr[3]["vis"])) if len(pr) > 3 and "vis" in pr[3] else (pr[3] if len(pr) > 3 else {})) for pr in _c.get("props", [])]
_board_cut0 = board_cut
def board_cut(n):
    P = _board_cut0(n)
    for p in P:
        p["keys"] = [(SH(k[0]), *k[1:]) for k in p["keys"]]
        if p["vis"]: p["vis"] = tuple(SH(v) if v is not None else None for v in p["vis"])
    return P
CUES = [(n, SH(a), SH(b)) for n, a, b in CUES if n != "Q-TIME" or a < 55]
CUES.insert(3, ("Q-TIME", 56.6, 57.2))           # 29번 「아직.」 꼬리를 덮지 않게 30번 경계 0.1초 앞에서
CUE_SHEET = set(CUES); D = SH(D)

# 2) 컷마다 카메라·연기·효과·자막 연기(새 시각). 자세 바꾸기는 레지스트리에 있는 그림만
C_ = {c["n"]: c for c in CUTS}
def SEQ(n, who, seq):
    c = C_[n]; c["chars"] = [(ch[0], ch[1], seq if ch[0] == who else ch[2], *ch[3:]) for ch in c["chars"]]
def LINE(n, text=None, t=None):
    l = C_[n]["line"]; C_[n]["line"] = (l[0], t if t is not None else l[1], text or l[2], *l[3:])
DIRECT = {
 1:  dict(fx=[("push", 1.0, 1.04, 0.0, 1.4)], sfx_add=[("톡", 1.5)]),
 2:  dict(fx=[("act", "panda", "lean", 2.1), ("act", "bear", "pop", 3.3)], text="아빠, 오늘 이거 *꼭* 물어봐."),
 3:  dict(fx=[("act", "bear", "hop", 4.5)]),
 4:  dict(fx=[("push", 1.0, 1.05, 6.9, 7.9), ("act", "bear", "pop", 6.9), ("act", "panda", "lean", 6.6)]),
 5:  dict(fx=[("act", "bear", "hop", 8.0)], text="허허허! *젊어* 보인대."),
 6:  dict(fx=[("act", "bear", "pop", 10.4)], seq=("bear", [(0, "서기쪽지-웃음"), (10.4, "서기쪽지-당황")])),
 7:  dict(fx=[("push", 1.0, 1.05, 11.4, 13.3), ("act", "bear", "slump", 12.7)], seq=("bear", [(0, "상반신쪽지-말"), (12.6, "상반신쪽지-당황")]), sfx_add=[("삐질", 12.8)]),
 8:  dict(fx=[("push", 1.0, 1.06, 13.6, 14.9)]),
 9:  dict(fx=[("act", "panda", "slump", 15.0)], seq=("panda", [(0, "상반신-눈감음"), (15.0, "상반신-시무룩")])),
 10: dict(fx=[("act", "panda", "hop", 16.4), ("act", "bear", "recoil", 16.9, 0.5)], text="다음엔 나도 *같이* 가."),
 11: dict(fx=[("act", "panda", "pop", 18.4), ("act", "panda", "lean", 20.4), ("act", "hedgehog", "pop", 20.6)], seq=("hedgehog", [(0, "앉기-평온"), (20.6, "앉기-당황")])),
 12: dict(fx=[("push", 1.0, 1.08, 22.5, 25.0), ("act", "hedgehog", "shiver", 23.9)], seq=("hedgehog", [(0, "상반신-당황"), (24.0, "상반신-눈감음")]), sfx_add=[("꿀꺽", 24.0)]),
 13: dict(fx=[("act", "hedgehog", "pop", 26.0), ("act", "panda", "hop", 26.1)], ono=("톡", 26.0)),
 14: dict(fx=[("act", "panda", "hop", 26.5), ("act", "penguin", "recoil", 26.7), ("mark", "!", "penguin", 26.7, 28.0)], text="!!선생님!"),
 15: dict(fx=[("push", 1.0, 1.07, 28.0, 28.4), ("act", "penguin", "slump", 28.4), ("mark", "…", "penguin", 28.1, 28.8)],   # 목소리가 컷 안에서 끝나게 대사를 28.45로(디렉터 28.55)
          seq=("penguin", [(0, "퇴근-상반신-평온"), (28.4, "퇴근-상반신-눈감음"), (28.45, "퇴근-상반신-말"), (29.6, "퇴근-상반신-눈감음")]), t=28.45),
 16: dict(fx=[("act", "panda", "lean", 29.9), ("act", "penguin", "slump", 30.2)]),
 17: dict(fx=[("pull", 1.06, 1.0, 32.0, 32.6), ("act", "penguin", "recoil", 32.1)], seq=("panda", [(0, "내밀기쪽지-웃음"), (32.0, "내밀기쪽지펼침-웃음")]), ono=("스윽", 32.0)),
 18: dict(fx=[("act", "penguin", "pop", 34.6)], text="진료 *3분*이에요."),
 19: dict(fx=[("push", 1.0, 1.06, 35.8, 37.5)], seq=("penguin", [(0, "퇴근-상반신-눈감음"), (36.0, "퇴근-상반신-말"), ("끝", "퇴근-상반신-평온")]), text="…*하나만* 고르세요."),
 20: dict(fx=[("act", "bear", "pop", 38.05), ("act", "bear", "pop", 38.9), ("act", "panda", "lean", 37.6)], sfx_add=[("스윽", 38.9)]),
 21: dict(fx=[("act", "bear", "hop", 39.4)]),   # 강조하면 줄이 안전 여백을 넘는다(check 7)
 22: dict(fx=[("push", 1.0, 1.05, 42.2, 43.9)], ono=("사각", 42.25)),
 23: dict(fx=[("shake", 44.0, 0.25, 6), ("act", "panda", "recoil", 44.0), ("lines", 44.0, 45.3)], text="!!그걸 왜 지워!"),
 24: dict(fx=[("push", 1.0, 1.06, 46.6, 48.1), ("act", "penguin", "lean", 45.5, 0.5)], cam_on="panda", text="^근데 *따님*은 검사 받아 봤어요?"),
 25: dict(fx=[("act", "panda", "recoil", 48.3, 0.5), ("mark", "?", "panda", 48.3, 49.5)], seq=("panda", [(0, "상반신-평온"), (48.3, "상반신-말"), (48.6, "상반신-당황")]), t=48.3),
 26: dict(text="*아버님*이 당뇨시잖아요."),
 27: dict(fx=[("snap", 1.22, 52.3), ("dim", 52.3, 53.7), ("act", "panda", "shiver", 53.1)], seq=("panda", [(0, "상반신-당황"), (52.3, "상반신-놀람")]), ono=("쿵", 52.3, 1.0), sfx_add=[("쿵", 52.3)]),
 28: dict(fx=[("push", 1.0, 1.05, 53.7, 55.1), ("act", "bear", "lean", 53.8, 0.5)]),
 29: dict(fx=[("pull", 1.05, 1.0, 55.2, 56.7), ("act", "panda", "slump", 55.2)], seq=("panda", [(0, "상반신-눈감음"), (55.2, "상반신-시무룩")]), text="..아직."),
 30: dict(fx=[("act", "panda", "pop", 57.0), ("act", "hedgehog", "pop", 59.3)], seq=("hedgehog", [(0, "앉기-평온"), (59.3, "앉기-당황")]), text="실장님, 반차 하나만 더요./이번엔 *제* 검사 받으려고요."),
 31: dict(fx=[("push", 1.0, 1.08, 61.3, 63.3), ("act", "hedgehog", "pop", 61.8), ("act", "hedgehog", "shiver", 62.0), ("lines", 61.8, 63.3)],
          seq=("hedgehog", [(0, "상반신-당황"), (61.8, "상반신-가시"), (62.6, "상반신-눈감음")]), ono=("뿅", 61.8), sfx_add=[("뿅", 61.8), ("꿀꺽", 62.6)]),
 32: dict(fx=[("act", "hedgehog", "pop", 64.4)], ono=("톡", 64.4)),
 33: dict(fx=[("act", "bear", "lean", 64.9), ("act", "panda", "recoil", 65.0, 0.5)]),
 34: dict(fx=[("push", 1.0, 1.05, 67.0, 68.7)], seq=("bear", [(0, "상반신-평온"), (67.0, "상반신-말"), (68.3, "상반신-웃음")]), text="*하나만* 물으라며."),
 35: dict(fx=[("push", 1.0, 1.10, 69.9, 71.2)]),
}
if "penguin-퇴근-서기-말하기" in K:                # 24번 반전 대사: 펭귄 입이 움직여야 누가 묻는지 보인다(디렉터 새 그림 요청)
    DIRECT[24]["seq"] = ("penguin", [(0, "퇴근-서기-평온"), (C_[24]["line"][1], "퇴근-서기-말"), ("끝", "퇴근-서기-평온")])
for n, d in DIRECT.items():
    c = C_[n]
    if "fx" in d: c["fx"] = d["fx"]
    if "seq" in d: SEQ(n, *d["seq"])
    if "text" in d or "t" in d: LINE(n, d.get("text"), d.get("t"))
    if "ono" in d: c["ono"] = d["ono"]
    if "cam_on" in d: c["cam_on"] = d["cam_on"]
    c["sfx"] = sorted(c.get("sfx", []) + d.get("sfx_add", []), key=lambda x: x[1])
