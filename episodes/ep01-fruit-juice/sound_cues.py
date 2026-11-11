"""ep01 「주스 세 잔」 소리 큐(engine/sound.py가 exec). 원본 ep01-v9 sound.py 9e판에서 회차 부분만 옮겼다.
쓸 수 있는 것: place(bus, 장면시각, 원본, 원본시작, 길이, 페이드인, 페이드아웃, 이름, 이득), bed·sting 버스, theme_n·bright·awk·stings·ST(정규화된 정식 음원),
cut[n]=(t0,t1), line_end[n], onset2, lufs_of, REF, OFF, S(scene)."""
# 사각: 컷마다 쓰는 글자 수만큼 긁는다(15번 6자 0.9초, 17번 줄 한 획 0.3초 · 「세」 한 자 0.4초). 나오는 차례대로 쓴다(9c: 시각은 scene.json)
SCRATCH = [(0.9, 6), (0.3, 1), (0.4, 2)]


# 1) 오프닝: 썸네일과 함께 theme-a 앞 소절 1.9초(초인종은 장면 0.0), 부엌으로 0.3초 크로스페이드
place(bed, -OFF, theme_n, 0.0, 1.5 + OFF, 0.02, 0.3, "오프닝 theme-a")
# 2) 부엌 「어제」 2~9번: bed-bright. 끝은 Q-TIME 스팅에 넘긴다
t_a = cut[2][0]; t_b = cut[10][0] + 0.25; place(bed, t_a, bright, 0.0, t_b - t_a, 0.3, 0.35, "부엌 bed-bright")
s_bright = t_b - t_a
# 3) 이음새 Q-TIME(밝은 스팅 1.2초, 9판과 같은 자리)
s0 = 15.50; place(sting, cut[10][0], stings, s0, 1.2, 0.06, 0.35, "Q-TIME stings-1", 10 ** ((REF - lufs_of(stings)) / 20))
# 4) 상담소 10~12번: bed-awkward. 윙키 「주스만 세 잔이요.」 끝에서 뚝 끊는다(30ms)
t_a = cut[10][0] + 0.8; t_b = line_end[12] + 0.05; o_awk = 3.0   # 원본 앞 3초는 여린 도입부라 건너뛴다
place(bed, t_a, awk, o_awk, t_b - t_a, 0.4, 0.03, "상담소 bed-awkward ①"); o_awk += t_b - t_a
# 5) 13번 곰 아빠 표정 컷: 정적 → babam 앞 1.0초(꼬리 0.3초 페이드)
b = ST["babam"]; place(sting, cut[13][0], b, onset2(b) / SR, 1.0, 0.005, 0.3, "babam")
# 6) 8번 「두 잔이 한 잔이지.」 직후 boing 앞 0.75초
b = ST["boing"]; place(sting, line_end[8] + 0.05, b, onset2(b) / SR, 0.75, 0.005, 0.2, "boing")
# 7) 14번 「치죠.」 직후 wahwah 앞 1.4초. 15~17번(기록장 고치기)은 정적
b = ST["wahwah"]; place(sting, line_end[14] + 0.06, b, onset2(b) / SR, 1.4, 0.005, 0.45, "wahwah")
# 8) 18~19번: bed-awkward 이어서(①이 멈춘 자리부터). 끝은 Q-DOWN에 넘긴다
t_a = cut[18][0]; t_b = cut[20][0] + 0.2; place(bed, t_a, awk, o_awk, t_b - t_a, 0.5, 0.3, "상담소 bed-awkward ②")
# 9) 이음새 Q-DOWN(내려가는 0.8초, 9판과 같은 자리)
place(sting, cut[20][0], stings, 13.90, 0.8, 0.04, 0.25, "Q-DOWN stings-1", 10 ** ((REF - lufs_of(stings)) / 20))
# 10) 부엌 「그날 저녁」 20~22번: bed-bright 이어서. 아이리스 「띠로리」(45.8) 직전에 빠진다
t_a = cut[20][0] + 0.5; t_b = next(C for C in S["cuts"] if C.get("iris"))["iris"]["steps"][0][0] + 0.05; place(bed, t_a, bright, s_bright, t_b - t_a, 0.4, 0.35, "저녁 부엌 bed-bright")
# 11) 끝 화면: theme-a 끝맺음(9판 Q-END와 같다)
place(bed, cut[23][0], theme_n, 27.0, 2.5, 0.1, 0.05, "끝 theme-a")

# 구간별 음량을 잴 구간(audio.json sections)
SECTIONS = [("오프닝 theme-a(썸네일~1번)", -OFF, 1.2), ("부엌 대사 중(2번)", 1.3, 3.3), ("부엌 대사 없음(7번)", *cut[7]), ("boing", line_end[8] + 0.05, line_end[8] + 0.8),
     ("상담소 대사 중(11번)", cut[11][0] + 0.1, cut[11][0] + 1.8), ("뚝 끊긴 뒤 정적", line_end[12] + 0.1, cut[13][0]), ("babam", cut[13][0], cut[13][0] + 1.0), ("wahwah", line_end[14] + 0.06, line_end[14] + 1.46),
     ("정적(15~17번)", cut[15][0] + 0.7, cut[18][0]), ("상담소 대사 중(19번)", cut[19][0], cut[19][0] + 3.5), ("저녁 부엌 대사 없음(21번 앞)", cut[21][0], cut[21][0] + 1.8), ("끝 theme-a", cut[23][0], cut[23][0] + 2.5)]
