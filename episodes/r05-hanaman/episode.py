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
# 주머니 쪽지: 주머니 선에 밑을 대고 15° 기울여 꽂는다. 넓은 컷 배율에서 67px라 1.5배(mag)로 키웠다(README)
NOTE_POCKET = lambda vis=None, at=(0.66, 0.55): ("note-list-folded", "on", "bear", dict(at=at, grip="bottom", mag=1.5, rot=15, **({"vis": vis} if vis else {})))
DOOR_E = "set-door-m-evening"
CU_G, CU_A, CU_B = "set-door-cu-g", "set-recycle-cu-a", "set-recycle-cu-b"
TALK = lambda pose, t, emo_end=None: [(0, pose + "-웃음" if emo_end == "웃음" else pose + "-평온"), (t, pose + "-말"), ("끝", pose + ("-웃음" if emo_end == "웃음" else "-평온"))]
CUTS = [
 # S1 아침
 dict(n=1, t=(0.0, 2.0), set="table", cam="판", ppm="big", bg=TEAL, title=(0.0, 2.0, "아빠 진료 날 아침"), sfx=[("스윽", 1.4)]),
 dict(n=2, t=(2.0, 4.4), set="door", cam="M", chars=[("bear", "좌2", [(0, "신발신기-웃음")]), ("panda", "우2", [(0, "내밀기-웃음")])],
      props=[("note-list-folded", "hand", "panda", dict(vis=(2.0, 3.3))), NOTE_POCKET((3.3, None), (0.6, 0.48))],
      line=("panda", 2.1, "아빠, 오늘 이거 꼭 물어봐."), sfx=[("스윽", 3.2)]),
 dict(n=3, t=(4.4, 6.5), set="door", cam="CU", bg=CU_G, chars=[("bear", "중", TALK("상반신", 4.5, "웃음"))],
      line=("bear", 4.5, "허허허! 시험 보러 가냐?"), tag=("bear", "좌하")),
 # S2 저녁
 dict(n=4, t=(6.5, 7.9), set="door", cam="M", bg=DOOR_E, chars=[("bear", "좌2", [(0, "서기-웃음")], dict(move=[(6.5, -160), (6.9, 0)])), ("panda", "우2", [(0, "서기-말")])],
      props=[NOTE_POCKET()], title=(6.5, 7.7, "그날 저녁"), line=("panda", 6.6, "아빠, 뭐래?"), sfx=[("탁", 6.5)]),
 dict(n=5, t=(7.9, 9.9), set="door", cam="CU", bg=CU_G, chars=[("bear", "중", TALK("상반신", 8.0, "웃음"))],
      props=[NOTE_POCKET(at=(0.68, 0.74))], line=("bear", 8.0, "허허허! 젊어 보인대.")),
 dict(n=6, t=(9.9, 11.3), set="door", cam="M", bg=DOOR_E, chars=[("bear", "좌2", [(0, "서기-웃음")]), ("panda", "우2", [(0, "서기-말")])],
      props=[NOTE_POCKET()], line=("panda", 10.0, "그거 말고.")),
 dict(n=7, t=(11.3, 13.3), set="door", cam="CU", bg=CU_G, chars=[("bear", "중", [(0, "상반신-말"), ("끝", "상반신-당황")])],
      props=[NOTE_POCKET(at=(0.68, 0.74))], line=("bear", 11.4, "그 말밖에 안 하던데.")),
 dict(n=8, t=(13.3, 14.9), set="table", cam="판", ppm="big", bg=TEAL, sfx=[("스윽", 13.4)]),   # 2차: 펼친 쪽지를 크게(표시 하나 없다)
 dict(n=9, t=(14.9, 16.3), set="door", cam="CU", bg=CU_G, chars=[("panda", "중", [(0, "상반신-시무룩")])],
      line=("panda", 15.0, "아 진짜…", {0: "시무룩"})),
 dict(n=10, t=(16.3, 18.3), set="door", cam="M", bg=DOOR_E, chars=[("bear", "좌2", [(0, "서기-당황")]), ("panda", "우2", [(0, "서기-말")])],
      line=("panda", 16.4, "다음엔 나도 같이 가.")),
 # S3 회사
 dict(n=11, t=(18.3, 22.4), set="company", cam="M", chars=[("panda", "좌2", [(0, "서기-말")]), ("hedgehog", "우2", [(0, "앉기-평온")])],
      title=(18.3, 19.5, "다음 날"), tag=("hedgehog", "우하"), line=("panda", 18.4, "실장님, 반차 좀 쓸게요./아빠 병원 따라가려고요.")),
 dict(n=12, t=(22.4, 25.0), set="company", cam="CU", chars=[("hedgehog", "중", [(0, "상반신-당황")])],
      line=("hedgehog", 22.5, "(많이 편찮으신가… 묻지 말자)", {0: "속마음"})),
 dict(n=13, t=(25.0, 26.4), set="company", cam="M", chars=[("panda", "좌2", [(0, "서기-평온")]), ("hedgehog", "우2", [(0, "앉기-말")])],
      line=("hedgehog", 25.1, "네. 다녀와요."), sfx=[("톡", 26.0)]),
 # S4 분리수거장(밤)
 dict(n=14, t=(26.4, 28.0), set="recycle", cam="M", chars=[("penguin", "좌2", [(0, "퇴근-서기-평온")]), ("panda", "우2", [(0, "양손들기-놀람")])],
      title=(26.4, 27.6, "진료 이틀 전 밤"), tag=("penguin", "좌상"), line=("panda", 26.5, "선생님!"), sfx=[("탁", 26.4)]),
 dict(n=15, t=(28.0, 29.5), set="recycle", cam="CU", bg=CU_A, chars=[("penguin", "중", [(0, "퇴근-상반신-눈감음")])],
      tag=("penguin", "좌상", True), line=("penguin", 28.1, "…퇴근했는데요.")),
 dict(n=16, t=(29.5, 31.5), set="recycle", cam="M", chars=[("penguin", "좌2", [(0, "퇴근-서기-평온")]), ("panda", "우2", [(0, "내밀기-웃음")])],
      props=[("note-list-folded", "hand", "panda")], line=("panda", 29.6, "모레 아빠 병원 가요.")),
 dict(n=17, t=(31.5, 33.6), set="recycle", cam="M", chars=[("penguin", "좌2", [(0, "퇴근-서기-평온")]), ("panda", "우2", [(0, "내밀기-웃음")])],
      props=[("note-list", "hand", "panda", dict(grip="top", mag=1.8))] + [("note-list", "hand", "panda", dict(grip="top", mag=1.8, off=(0, 190 * 1.8 * i), vis=(31.6 + 0.6 * i, None))) for i in (1,)],
      line=("panda", 31.6, "이거 다 물어봐도 돼요?"), sfx=[("스윽", 31.7)]),
 dict(n=18, t=(33.6, 35.4), set="recycle", cam="CU", bg=CU_A, chars=[("penguin", "중", TALK("퇴근-상반신", 33.7))], line=("penguin", 33.7, "진료 3분이에요.")),
 dict(n=19, t=(35.4, 37.2), set="recycle", cam="CU", bg=CU_A, chars=[("penguin", "중", TALK("퇴근-상반신", 35.5))], line=("penguin", 35.5, "…하나만 고르세요.")),
 dict(n=20, t=(37.2, 39.0), set="recycle", cam="M", chars=[("bear", "좌2", [(0, "들기-웃음")], dict(move=[(37.2, -620), (37.75, 0)])), ("panda", "우2", [(0, "내밀기-웃음")])],   # 2차: 곰 아빠가 걸어 들어온다, 펭귄 뺌
      props=[("note-list-folded", "hand", "panda", dict(vis=(37.2, 38.6))), ("note-list-folded", "hand", "bear", dict(vis=(38.6, None), grip="top"))],
      line=("panda", 37.3, "아빠, 하나만 골라.")),
 dict(n=21, t=(39.0, 41.8), set="recycle", cam="CU", bg=CU_B, chars=[("bear", "중", TALK("상반신", 39.1, "웃음"))], line=("bear", 39.1, "허허허! 원 플러스 원은 안 되냐?")),
 dict(n=22, t=(41.8, 43.6), set="table", cam="판", ppm="note", bg=TEAL, line=("bear", 41.9, "이건 아빠도 알아."), sfx=[("사각", 41.95), ("사각", 42.45), ("사각", 42.95)]),
 dict(n=23, t=(43.6, 45.0), set="recycle", cam="CU", bg=CU_B, chars=[("panda", "중", [(0, "상반신-놀람")])], line=("panda", 43.7, "그걸 왜 지워!", {0: "놀람"})),
 dict(n=24, t=(45.0, 47.8), set="recycle", cam="M", chars=[("penguin", "좌2", [(0, "퇴근-서기-평온")]), ("panda", "우2", [(0, "서기-평온")])], line=("penguin", 45.1, "근데 따님은 검사 받아 봤어요?"), sfx=[("탁", 45.0)]),
 dict(n=25, t=(47.8, 49.2), set="recycle", cam="CU", bg=CU_B, chars=[("panda", "중", TALK("상반신", 47.9))], line=("panda", 47.9, "네?")),
 dict(n=26, t=(49.2, 51.6), set="recycle", cam="CU", bg=CU_A, chars=[("penguin", "중", TALK("퇴근-상반신", 49.3))], line=("penguin", 49.3, "아버님이 당뇨시잖아요.")),
 dict(n=27, t=(51.6, 52.9), set="recycle", cam="CU", bg=CU_B, chars=[("panda", "중", [(0, "상반신-놀람")])], still=True),
 dict(n=28, t=(52.9, 54.3), set="recycle", cam="CU", bg=CU_B, chars=[("bear", "중", TALK("상반신", 53.0))],   # 2차: 웃음 없는 곰 아빠 = 상반신 평온(평온 전신 든 그림 없음)
      props=[("note-list-folded", "on", "bear", dict(at=(0.74, 0.66), grip="bottom", mag=1.5, rot=15))], line=("bear", 53.0, "…너 안 받았어?", {0: "시무룩"})),
 dict(n=29, t=(54.3, 55.7), set="recycle", cam="CU", bg=CU_B, chars=[("panda", "중", [(0, "상반신-시무룩")])], line=("panda", 54.4, "아직.", {0: "속삭임"})),
 # S5 회사
 dict(n=30, t=(55.7, 60.2), set="company", cam="M", chars=[("panda", "좌2", [(0, "서기-말")]), ("hedgehog", "우2", [(0, "앉기-평온")])],
      title=(55.7, 56.9, "다음 날"), line=("panda", 56.0, "실장님, 반차 하나만 더요./이번엔 제 검사 받으려고요.")),
 dict(n=31, t=(60.2, 62.3), set="company", cam="CU", chars=[("hedgehog", "중", [(0, "상반신-당황"), (60.8, "상반신-가시")])],
      line=("hedgehog", 60.3, "(…무슨 검사지? 묻지 말자)", {0: "속마음"})),
 dict(n=32, t=(62.3, 63.8), set="company", cam="M", chars=[("panda", "좌2", [(0, "서기-평온")]), ("hedgehog", "우2", [(0, "앉기-말")])],
      line=("hedgehog", 62.4, "네. 잘 받고 와요."), sfx=[("톡", 63.4)]),
 # S6 대기실
 dict(n=33, t=(63.8, 65.9), set="clinic", cam="M", chars=[("bear", "좌2", [(0, "앉기-평온")]), ("panda", "우2", [(0, "앉기-평온")])],
      props=[("note-list-folded", "on", "bear", dict(at=(0.9, 0.5), mag=1.5, rot=-12))],   # 2차: 판다 쪽으로 내민 쪽지. 번호표는 스티커처럼 보여 뺐다
      title=(63.8, 65.0, "아빠 진료 날"), line=("panda", 63.9, "그거 아직 갖고 있었어?")),
 dict(n=34, t=(65.9, 67.7), set="clinic", cam="CU", chars=[("bear", "중", TALK("상반신", 66.0))], line=("bear", 66.0, "하나만 물으라며.")),
 dict(n=35, t=(67.7, 70.7), set="table", cam="판", ppm="end", bg=TEAL, sfx=[("스윽", 68.2)]),
 dict(n=36, t=(70.7, 73.7), set="end", cam="board", bg=TEAL, chars=[], end=True),
]
