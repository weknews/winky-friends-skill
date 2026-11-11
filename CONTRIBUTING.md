# 기여 절차

`main`에 직접 커밋하지 않는다. 작업 하나 = PR 하나. 커밋은 conventional commits(`feat(kit): …`, `docs(rules): …`).

## 새 프리미티브(그림·음원)

1. **브랜치** `feature/assets-<무엇>` (예: `feature/assets-turtle-stand`).
2. **생성** `skills/winky-assets` 대로 `kit/gen/gen.py` → 크기 재기·줄이기 → `engine/register.py add` (status `draft`). 음원은 `rules/music.md` 절차(정식 테마 reference) → `register.py music`.
3. **승인 모음** `engine/register.py sheet` → `review/drafts.jpg`. 쓸 회차 화면에 놓아 본 프레임도 같이.
4. **PR** 그림 파일 + `kit/registry.json`. 본문에 무엇을 왜(어느 대본 「새로 만들 것」), 승인 모음 그림 첨부. `review/`·`kit/gen/out/`은 올리지 않는다.
5. **리뷰** 담당자가 그림(옷 색·그림체·크기·글자 없음)과 레지스트리 값(mm·앵커)을 본다. 음원은 귀로 듣는다.
6. **승인·머지** 승인자가 `register.py approve 이름 --by 승인자` 커밋을 PR에 더한 뒤 머지. 이때부터 모든 회차가 쓸 수 있다.

## 새 회차

`feature/ep<번호>-<영문>` → `episodes/<회차>/`(script.md, episode.py, sound_cues.py, thumb.html, README.md) → `check.py` 실패 0 → PR(확인판 몇 장 첨부). 영상·wav·scene.*·out/은 올리지 않는다.

## 규칙·엔진을 고칠 때

`rules/`나 `engine/`를 바꾸면 기존 회차를 모두 다시 build·check 해서 실패 0인지 PR에 적는다. 승인된 프리미티브를 바꾸는 것(`--replace`)도 같다.
