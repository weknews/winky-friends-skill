---
name: winky-assets
description: 「윙키와 친구들」 공유 프리미티브(인물 자세-표정, 손, 소품, 세트 배경)를 새로 만들어 kit/registry.json에 draft로 등록하고 승인 모음을 만든다. 대본 「새로 만들 것」 표에 있는 그림만 만든다. 「새 자세 만들어」, 「소품 그림 생성」, 「세트 배경 만들기」, 「프리미티브 등록」 요청에 쓴다. Claude Code·Codex 전용(Codex CLI 이미지 생성 필요). 음원은 rules/music.md 절차, 영상 조립은 winky-episode.
---

# 프리미티브 만들기 (그림만)

> 모델 분업은 `rules/models.md`를 따른다(기획은 가장 좋은 추론 모델 하나, 외부 모델 검토, 제작 모델은 기획대로만).


없으면 생성 → draft 등록 → 승인 모음 → 사람 승인 → approved → PR로 공유 → 다음 사람은 재사용. **이미 있으면 만들지 않는다.** 시작 전에 레포 뿌리에서:

```bash
python3 engine/register.py list <이름 일부>       # 이미 있나
```

명령은 macOS·Linux 기준이다. Windows(PowerShell)에서는 `python3` 대신 `py`를 쓴다. `--anchor`·`--mm`의 JSON은 PowerShell 7에서는 그대로 되고, Windows PowerShell 5.1에서는 안의 큰따옴표를 `\"`로 쓴다.

## 1. 준비

- Codex CLI 로그인(구독 OAuth, Images 2.6 = 내장 `image_gen`). API 키를 쓰지 않는다.
- Python 3 + Pillow + numpy. OS별 설치는 README 「준비물」.
- 생성 결과(`kit/gen/out/`)와 승인 모음(`review/`)은 git에 올리지 않는다. 올리는 것은 등록된 프리미티브와 `kit/registry.json`뿐이다.

## 2. 무엇을 어떻게 만드나

| 종류 | `--kind` | 바탕 | 크기 기준(레지스트리 mm) | 요령 |
|---|---|---|---|---|
| 인물 자세-표정 | `actor` | 마젠타(`magenta`) | `actors.<인물>.mm` 키·머리 폭 | **그 인물의 기존 조각을 기준 그림으로 편집**한다(옷 색·종이결 유지). 같은 자세의 표정·말하기·눈감음은 한 가족(`--family 기준 이름`)으로, 얼굴 칸만 바꿔 몸이 떨리지 않게 한다 |
| 손에 소품을 쥔 자세 | `actor` | 마젠타 | 쥔 소품도 레지스트리 mm ±10% | 소품을 손 앵커에 얹지 않고 「실제로 쥔」 그림을 만든다. 잔이 찬 프레임은 편집으로 채우지 말고 빈 잔 그림의 창 색만 바꾼다(편집하면 컵이 매번 1.3~1.5배 커졌다) |
| 손 조각(판 컷) | `hand` | 마젠타 | `bear-paw` 165mm, `winky-paw` 95mm 손바닥 폭 | 인물 원본에서 손·소매를 잘라 마젠타 판에 놓은 그림을 기준으로 편집. 곰 손은 아래에서, 윙키 손은 위에서 들어오고 팔이 화면 끝까지 닿게 길게 |
| 소품 | `prop` | 마젠타 | `sizes.<종류>` | 위에서 내려다본 판 소품은 「top-down, flat, no perspective」. 글자를 그리지 않는다(칸만 비워 두고 글자는 렌더에서 얹는다) |
| 세트 배경 | `set` (`--set kitchen` 등) | 없음(`none`) | 기준 사물 높이(예: 조리대 850mm) | 1152×2048. 인물·소품·글자 없이. 판(`table`)은 흰 바탕·옅은 회청 그림자, 갈색 나무 금지 |

금지(모든 그림): 빨강 큰 면, 그림 안 글자·숫자, 혈당 측정기 화면 숫자, 다른 인물의 옷 색 섞임. 사과는 초록.

## 3. 순서

1. **프롬프트 쓰기.** 영어 IMAGE 문장 하나. 예시는 `kit/registry.json`의 `set-table`, `notebook-open`, `bear-hand-flat`, `bear-hand-pencil`, `winky-hand`, `notebook-closed`의 `prompt`. 공통 문단(그림체·키 색·9인 설정·색 잠금)은 `gen.py`가 붙인다.
2. **생성.**
   ```bash
   python3 kit/gen/gen.py 이름 1024x1536 magenta "IMAGE ..." [기준 그림.png ...]
   ```
   → `kit/gen/out/이름.png`, `.log`, `.prompt.txt`. 한 번에 여러 장은 백그라운드로 나란히 돌린다(한 장 최대 15분).
3. **크기 재기 → 줄이기(편집 회차).** 생성 모델은 크기를 자주 틀린다. 키를 빼고 재서(손바닥 폭, 연필 길이, 기록장 가로세로 비율) 레지스트리 mm와 ±10% 안인지 본다. 벗어나면 다시 뽑지 말고 **잰 그림을 목표 비율로 줄이거나 늘여 마젠타 판에 놓은 「안내 그림」을 만들어 그것을 편집**한다(「소매를 아래 끝까지」, 「연필만 73%로」처럼 고칠 것 하나만). ep01 예: 기록장 2.05:1 → 1.70:1 → 안내 그림 편집으로 1.52:1(목표 1.43, −5.7%), 연필 240mm → 「연필만 73%」 → 172mm(−1.7%). 회차 기록은 `episodes/ep01-fruit-juice/legacy/gen9.py`.
4. **등록(draft).**
   ```bash
   python3 engine/register.py add 'bear-들기컵-웃음' kit/gen/out/bear-들기컵-웃음.png --kind actor --actor bear --key magenta \
     --anchor '{"cx":490,"head":[136,10,826,600],"face":[310,280,670,560],"torso":[100,820],"hand":[866,650],"scale":"h"}' \
     --prompt-file kit/gen/out/bear-들기컵-웃음.prompt.txt --ref kit/actors/bear/bear-lift-smile.webp
   ```
   키 색을 빼고 알파 둘레로 잘라 `kit/<종류>/`에 webp(배경은 jpg)로 넣는다. 앵커(조각 px)는 잘린 그림을 눈금판에 놓고 잰다: `cx` 몸 중심, `head` 머리 상자(귀 빼고), `face` 이목구비, `torso` 몸통 x 범위, `hand` 소품 얹는 곳, `held` 손에 그린 소품 상자 `[종류,x0,y0,x1,y1]`, 손 조각은 `paw`·`pawc`·`tip`, 칸 글자 자리는 `text`(비율). 새 소품 종류면 `--mm '{"h":190}' --size-class cup`.
5. **승인 모음.** `python3 engine/register.py sheet` → `review/drafts.jpg`(draft 전부, 이름·px·mm). 쓸 회차 화면에 놓아 본 컷(`winky-episode`의 shot)도 같이 보여 준다.
6. **사람 승인.** 사람이 보고 승인한 것만 `python3 engine/register.py approve 이름 ... --by 승인자`. 에이전트가 스스로 approve 하지 않는다.
7. **공유.** `feature/assets-<무엇>` 브랜치 → 커밋(그림 + registry.json) → PR(승인 모음 그림을 PR 본문에 첨부, 무엇을 왜 만들었나) → 리뷰 → 머지. `CONTRIBUTING.md`.

## 4. 이미 승인된 것을 고칠 때

`--replace`가 필요하다. 같은 이름을 쓰는 지난 회차가 달라지므로 PR에 이유와 영향 회차를 적고, 지난 회차 `check.py`를 다시 돌린다.
