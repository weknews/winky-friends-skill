# engine/ — 공통 제작 코드

원본은 1화 9e판 제작 폴더(`ep01-v9`). 회차 값은 `episodes/<회차>/episode.py`·`sound_cues.py`로 뺐고, 그림 목록은 `kit/registry.json`의 approved 항목에서 읽는다. ep01로 돌리면 원본과 scene.json이 같고(경로만 다름) audio.wav가 비트 단위로 같다.

| 파일 | 일 |
|---|---|
| `build.py` | 컷 표 → `scene.json`·`scene.js`(크기 = 레지스트리 mm × px/mm, 자리 = 놓이는 곳·앵커, 12fps 사건). 끝에서 `EP/episode.py`를 exec |
| `check.py` | 자동 검사 16항목(KIT-SPEC 7절 12 + 손에 그린 소품·판 소품·금지 표현·레지스트리). 실패 있으면 종료 코드 1 |
| `sound.py` | 목소리(Animalese) + 효과음(합성) + 정식 음원 큐 → `out/audio.wav`. 회차 큐는 `EP/sound_cues.py` |
| `register.py` | 프리미티브 등록(draft)·승인 모음·승인·음원 등록·목록 |
| `render.py` | hyperframes 렌더 + 썸네일 0.4초·소리·표지 붙이기 → `out/<회차>.mp4` |
| `setup_episode.py` | 회차 폴더 준비(kit·fonts·lib·index.html 링크, 새 회차 틀 복사). build.py가 시작할 때 부른다 |
| `index.html` | 렌더 화면(hyperframes 컴포지션). 회차 폴더에서 링크로 쓴다 |
| `textcheck.mjs` · `shot.mjs` · `thumbshot.mjs` | 렌더된 글자 검사 · 프레임 찍기 · 썸네일 찍기. 크롬은 `chrome.mjs`가 찾는다 |
| `lib/` | gsap(UMD, CustomEase) |

모든 스크립트는 회차 폴더에서 `python3 ../../engine/<파일>` / `node ../../engine/<파일>`로 돈다(Windows는 `python3` 대신 `py`). bash 없이 macOS·Linux·Windows에서 같게 돈다. 쓰는 법은 `skills/winky-episode/SKILL.md`.

한계: build.py의 판 컷(`table`)·기록장 칸 글자 처리는 ep01 소품(잔·기록장·연필) 기준이라, 판 컷 소품이 다른 회차는 episode.py에 회차 함수를 더해야 한다.
