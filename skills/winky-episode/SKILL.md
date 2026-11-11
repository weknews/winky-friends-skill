---
name: winky-episode
description: 승인된 「윙키와 친구들」 대본(winky-script 결과)을 50초 세로 숏폼 영상(1080×1920 mp4)으로 만든다. 컷 표 → episode.py → 새 프리미티브(winky-assets) → 승인 모음 → 합성(build) → 자동 검사(check·textcheck) → 숏폼 소리(sound) → 썸네일 → 렌더 → 썸네일 0.4초+표지 붙이기 → Stream 썸네일 지정 안내. 「영상 만들어」, 「회차 렌더」, 「윙키 에피소드 제작」 요청에 쓴다. Claude Code·Codex 전용.
---

# 회차 영상 만들기

> 모델 분업은 `rules/models.md`를 따른다(기획은 가장 좋은 추론 모델 하나, 외부 모델 검토, 제작 모델은 기획대로만).


프리미티브(`kit/`)를 회차 컷 표로 조합한다. 좌표를 손으로 적지 않는다. 크기는 레지스트리 mm × 컷의 px/mm, 자리는 놓이는 곳 넷(바닥·가구 윗면·손·판)과 앵커에서 나온다. 기준 회차는 `episodes/ep01-fruit-juice/`(9e판, check 실패 0).

## 0. 준비 (레포 뿌리)

Node 22+, ffmpeg, Python 3(numpy, Pillow)는 README 「준비물」의 OS별 명령으로 설치한다. 아래 명령은 macOS·Linux·Windows(PowerShell)에서 같다. Windows에서는 `python3` 대신 `py`를 쓴다.

```bash
cd engine
npm install                                                        # hyperframes, puppeteer-core, gsap
cd ..
git clone https://github.com/hwi-middle/PyAnimalese tools/PyAnimalese   # 목소리 녹음(MIT). tools/는 git에 없다
# 정식 음원 wav 7개는 sound.py가 처음 실행될 때 Release에서 받는다(engine/fetch_kit.py). sha256이 다르면 멈춘다
```

크롬은 따로 준비하지 않는다. 확인 스크립트(`textcheck`·`shot`·`thumbshot`)가 hyperframes가 받아 둔 크롬을 찾고, 없으면 받는다. 다른 크롬을 쓰려면 `CHROME` 환경 변수에 경로를 준다.

## 1. 회차 폴더

```bash
python3 engine/setup_episode.py episodes/ep02-<영문-짧게>    # 폴더를 만들고 ep01의 episode.py·sound_cues.py·thumb.html을 틀로 복사
cd episodes/ep02-<영문-짧게>
# 승인된 대본을 script.md 로 복사해 둔다
```

회차 폴더의 `kit`·`fonts`·`lib`·`index.html`은 git에 없다. `setup_episode.py`가 만들고, `build.py`도 시작할 때 없으면 만든다(macOS·Linux는 심볼릭 링크, Windows는 링크 권한이 없으면 폴더 정션과 index.html 복사).

모든 명령은 회차 폴더에서 `python3 ../../engine/<스크립트>`로 돈다(`EP` 환경 변수로 다른 폴더를 줄 수도 있다).

## 2. 컷 표 → episode.py

대본 컷 표를 `CUTS`로 옮긴다(형식은 ep01 `episode.py` 그대로):

- `dict(n, t=(시작, 끝), set, cam, chars=[(인물, 자리, [(시각, "자세-표정")])], props=[(조각, 놓이는 곳, 대상, 옵션)], line=(인물, 시작, "대사/둘째 줄"), tag=(인물, "좌하|우하"), sfx=[(이름, 시각)], title=(t0, t1, "다음 날"), source="근거 자막", iris=True, end=True)`.
- `'말'`로 끝나는 상태는 대사 중 평온↔말하기를 번갈아 쓴다. `"끝"`은 목소리 끝 시각.
- 판 컷(`cam="판"`)은 `board_cut(n)`에 조각과 움직임 열쇠 `(시각, X mm, Y mm[, 기울기])`를 적는다(원점 화면 가운데, 12fps 계단). 손은 화면 끝에서 들어온다.
- `TAGS`(이름표), `END`(끝 화면 줄·크기), `CUES`/`CUE_SHEET`(큐 시트), `IRIS`, `D`(전체 길이), `TPPM`(판 배율)을 회차 값으로 바꾼다. 기록장처럼 회차 전용 칸 글자는 `prebuild()`·`notebook_texts()`처럼 회차 파일에 함수로 둔다.
- 제작하며 시각을 옮겨야 하면 ep01처럼 원래 시각을 두고 `W()` 구간 선형 시계로 옮긴다. 대본과 다르게 한 것은 회차 `README.md` 「기획과 다르게 한 것」에 이유와 함께 적는다.
- `index.html`의 `data-duration`(지금 50.0)이 `D`와 다르면 회차 폴더의 index.html 링크를 지우고 `engine/index.html`을 복사해 고친다. 이 파일은 .gitignore에 걸리므로 `git add -f`로 올린다.

## 3. 새 프리미티브

컷 표에 레지스트리에 없는 이름이 있으면 build가 멈춘다. 대본 「새로 만들 것」대로 **winky-assets**로 만들고 draft 등록 → 승인 모음 → **사람 승인** 뒤에 진행한다. 판 배율에서 조각 확대가 1.3배를 넘으면 그 조각만 큰 판으로 다시 뽑는다(check 6번).

## 4. 합성·자동 검사

```bash
python3 ../../engine/build.py       # → scene.json, scene.js
python3 ../../engine/check.py       # 16항목. 실패가 하나라도 있으면 렌더하지 않는다 → out/check.txt
node ../../engine/textcheck.mjs     # 렌더된 글자가 칸·안전 여백 안인지
node ../../engine/shot.mjs           # 2초 간격 확인판 + 끝 0.5초 전 → out/shots/. 시각을 주면 그 시각만(node ../../engine/shot.mjs 12.5 13)
```

check 항목: 1 이름(레지스트리 approved·효과음 등록) · 2 크기 ±5% · 3 놓이는 곳 · 4 자리 · 5 겹침(얼굴 0, 몸통 15%) · 6 확대(조각 1.3, 배경 1.15, CSS 금지 표현) · 7 글자 구역(안전 여백, 보호 상자, 자막 56px 이상) · 8 칸 글자 · 9 호흡(한 컷 한 줄, 1.2초, 초당 5음절, 14자) · 10 음악 큐 · 11 표기(끝 화면 4줄, 본편 로고 없음, 썸네일 로고, 「1화」 없음) · 12 컵 · 13 손에 그린 소품 ±10% · 14 판 소품·팔 · 15 혈당·판정 표현 없음 · 16 레지스트리.

검사가 못 보는 것은 확인판을 직접 본다: 자막이 손의 소품을 가리나, 이름표가 얼굴을 덮나, 손과 소품이 어색한가, 옷 색이 맞나, 배경에 글자가 그려졌나. 고친 것은 회차 README에 적는다.

## 5. 숏폼 소리

`sound_cues.py`에 회차 음악 큐를 적는다(정식 음원만, `rules/music.md`): 장면별 bed, 이음새 Q-TIME·Q-DOWN, 반전 직전 뚝 끊고 스팅, 끝 theme-a. 사각 소리 길이 `SCRATCH`, 잴 구간 `SECTIONS`.

```bash
python3 ../../engine/sound.py       # → out/audio.wav(−15 LUFS, ≤−1.5 dBTP), out/audio.json(구간별 버스 음량)
```

수치만 맞춘 것이다. **사람이 귀로 듣고** 대사 중 음악 크기를 확인한다.

## 6. 썸네일 (로고는 썸네일에만)

`thumb.html`: 오해하는 인물 얼굴(기존 조각) + 위 띠 「당뇨 오해 바로잡기」 + 훅 두 줄(그 회 오해를 묻는 질문, 도현) + 오른쪽 아래 `kit/logo/logo-main.png`(폭 540). 회차 번호 없음.

```bash
node ../../engine/thumbshot.mjs     # → out/thumb.png, 글자·로고가 안전 여백 안인지
```

## 7. 렌더·붙이기

```bash
python3 ../../engine/render.py      # hyperframes render → out/raw.mp4, 썸네일·소리·표지를 붙여 out/<회차 폴더 이름>.mp4 (50초 영상이면 렌더·붙이기 약 50초, 맥)
```

맨 앞 0.4초가 썸네일이라 첫 프레임 = 썸네일이고, 같은 그림이 mp4 표지(attached_pic)로 들어간다. 완성 파일에서 프레임을 다시 뽑아(`ffmpeg -ss`) 확인판을 만들고, 음량을 다시 잰다.

## 8. 올릴 때 (Stream 썸네일)

Teams·Stream은 첫 프레임이 아니라 중간 프레임을 미리보기로 고를 수 있다. 올린 뒤 **영상 설정 → 썸네일 → 「이미지 업로드」로 `out/thumb.png`를 지정**한다(또는 0.0초 프레임 선택). 유튜브 쇼츠는 업로드 화면에서 0초 프레임을 고른다. 게시물 설명란은 대본의 것을 쓰고, 끝 화면·설명란의 ○○○(검수자)를 실제 표기로 바꾼 판인지 확인한다.

## 9. 레포에 올리는 것

`episode.py`, `sound_cues.py`, `thumb.html`, `script.md`, 회차 `README.md`(결과 수치·기획과 다르게 한 것·남은 한계). **영상·wav·scene.*·out/·확인판은 올리지 않는다**(.gitignore). 새 프리미티브는 winky-assets 절차로 따로 PR.

## 사람이 꼭 할 일

대사 소리 내 읽기 · 새 그림 승인 · 소리 귀로 듣기 · 의료진 검수와 ○○○ 채우기 · 게시 전 확인판 보기.
