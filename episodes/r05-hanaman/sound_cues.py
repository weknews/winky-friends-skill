"""r05 「하나만요」 소리 큐(engine/sound.py가 exec). 대본 2판 「큐 시트」 그대로. 정식 음원만(rules/music.md)."""
SCRATCH = [(0.3, 1)] * 3                     # 22번 줄 긋기 셋(한 획씩)
QT = lambda t, name: place(sting, t, stings, 15.50, 0.9, 0.06, 0.3, name, 10 ** ((REF - lufs_of(stings)) / 20))   # Q-TIME = ep01과 같은 밝은 스팅 앞 0.9초

# 1) 아침 1~3번: 썸네일부터 bed-bright
place(bed, -OFF, bright, 0.0, cut[4][0] + OFF + 0.2, 0.02, 0.3, "아침 bed-bright"); o_b = cut[4][0] + OFF + 0.2
# 2) 4번 아침 → 저녁 Q-TIME, 저녁 4~10번은 bed-bright 이어서(큐 시트에 따로 없음)
QT(cut[4][0], "Q-TIME 저녁")
t_a = cut[4][0] + 0.6; t_b = cut[11][0] + 0.2; place(bed, t_a, bright, o_b, t_b - t_a, 0.4, 0.3, "저녁 bed-bright"); o_b += t_b - t_a
# 3) 회사 11~13번
QT(cut[11][0], "Q-TIME 회사")
t_a = cut[11][0] + 0.6; t_b = cut[14][0] + 0.2; o_co = o_b; place(bed, t_a, bright, o_b, t_b - t_a, 0.4, 0.3, "회사 bed-bright"); o_b += t_b - t_a
# 4) 분리수거장 14~23번: bed-awkward. 24번 「근데 따님은…」 직전(44.9)에 뚝(30ms)
QT(cut[14][0], "Q-TIME 분리수거장")
t_a = cut[14][0] + 0.6; t_b = 44.9; place(bed, t_a, awk, 3.0, t_b - t_a, 0.4, 0.03, "분리수거장 bed-awkward")
# 5) 24~29번 무음(반전과 침묵)
# 6) 회사 30~32번(콜백)
QT(cut[30][0], "Q-TIME 회사 콜백")
t_a = cut[30][0] + 0.6; t_b = cut[33][0] + 0.2; place(bed, t_a, bright, o_co, t_b - t_a, 0.4, 0.3, "회사 bed-bright ②(11번과 같은 소절, 콜백)")   # bed-bright 30.8초라 이어 쓰면 모자란다
# 7) 대기실 33~34번: Q-DOWN → 낮게(배경 −8dB). 35번 쪽지는 정적
place(sting, cut[33][0], stings, 13.90, 0.8, 0.04, 0.25, "Q-DOWN stings-1", 10 ** ((REF - lufs_of(stings)) / 20))
t_a = cut[33][0] + 0.5; t_b = cut[35][0]; place(bed, t_a, bright, o_b, t_b - t_a, 0.4, 0.4, "대기실 bed-bright 낮게", 10 ** (-8 / 20))
# 8) 끝 화면 theme-a 끝맺음(ep01 Q-END와 같은 자리)
place(bed, cut[36][0], theme_n, 27.0, 2.9, 0.1, 0.3, "끝 theme-a")

SECTIONS = [("아침 대사 중(2번)", 2.1, 4.3), ("저녁 대사 없음(8번)", *cut[8]), ("회사 대사 중(11번)", 18.4, 22.3), ("분리수거장 대사 중(17번)", 31.6, 33.5),
            ("뚝 끊긴 뒤 무음(24~29번)", 45.0, 55.7), ("대기실 낮게(33번)", 63.9, 65.8), ("정적(35번)", *cut[35]), ("끝 theme-a", cut[36][0], cut[36][0] + 2.9)]
