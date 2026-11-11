---
id: R-17
title: 규칙 기반 시트콤 제작 (재사용 체계, 음악 큐, 크기 레지스트리)
date: 2026-11-11
question: 시트콤·TV 애니처럼 배우·소품·세트·음악을 재사용하고 크기·위치·음악을 규칙으로 잡는 방법
tags: [재사용, 레지스트리, 세트, 카메라프리셋, 음악큐, 스팅어, Harmony, Bluey, Remotion]
related: [R-04, R-13, R-16]
applied_in: []
---

사용자 지적(11/11): 1화 2판에서 컵 크기·인물 위치가 깨지고 음악이 내내 깔림. Haiku 조사(웹 13회).

## 1. 재사용 체계 (애니·시트콤 제작)

- **Harmony 라이브러리 템플릿.** 리그 전체를 마스터 템플릿으로, 동작을 액션 템플릿으로 저장한다. 리그는 첫 프레임에 키를 찍고 접은 뒤 저장한다. 【확인】 https://docs.toonboom.com/help/harmony-20/premium/library/create-template.html 액션 템플릿은 레이어 순서가 같아야 들어간다. 【2차】 https://docs.toonboom.com/help/harmony-12-2/premium/cut-out-animation/action-templates.html
- **Bluey(게임 쪽 자료).** 손·발 형태를 캐릭터끼리 공유했다. 8개 방향 중 주 방향을 그리고 나머지는 복사했다. 크기 기준은 공식 시트가 아니라 팬 토론(「토마토 소스병」 비교)에서 왔다. 【확인】 https://80.lv/articles/bluey-s-simple-2d-look-required-gameloft-s-most-technically-challenging-art-pipeline
- **Bluey 설정 바이블.** 카메라는 대부분 정면·평면이다. 배경은 2점 투시로 그리되 가장자리는 평면으로 둔다. 배경은 단순하게 하고, 소품은 둥글고 통통한 직사각형 계열로 맞춘다. 【확인】 https://www.itsnicethat.com/features/how-we-built-bluey-s-world-cartoon-background-scenery-art-director-catriona-drummond-animation-090725 세트 재사용 여부는 기사에 없다.
- **South Park.** 6일 제작 주기가 확인된다. 【확인】 https://cartoonbrew.com/documentary-2/6-days-to-air-reveals-south-parks-insane-production-schedule-67657.html 세트·캐릭터 재사용과 도구 세부는 이 기사에 없다. 9일 주기·Kawaja 발언은 못 찾았다. 【미확인】
- **모델 시트.** 키 비교표(height/scale chart)가 표준 요소다. 턴어라운드는 같은 축척으로 그린다. 소품은 주인공 손이나 몸 옆에 놓고 크기를 정한다. 【2차】 https://tropedia.fandom.com/wiki/Model_Sheet · Toon Boom learn 「relative size of characters」 검색 요약
- **Adobe Character Animator.** 스왑 세트로 입·표정 트리거를 바꾼다. 트리거는 두 퍼펫에서 이름이 같아야 붙여넣기가 된다. 립싱크 테이크는 퍼펫끼리 복사할 수 있다. 【2차】 https://helpx.adobe.com/adobe-character-animator/using/triggering-and-controlling-puppets.html

## 2. 시트콤 음악 규칙

- **스팅어.** 짧은 전환 음악으로, 음원 라이브러리 기준 4~13초 편집본이 흔하다. 끝을 해결하지 않은 화음으로 끝내 다음 장면으로 넘긴다. 본편 테마를 잘라 쓴다. 【2차】 https://artlist.io/sfx/track/serious-rock-segments---sitcom-stinger-/118814 (음원 사이트 설명)
- **큐 체크.** 큐마다 「어디서 시작·어디서 끝·왜 넣나」를 적는다. 한 큐가 장면 전환 컷에서 끝나는 경우가 있다. 스포팅 세션은 60~90분이다. 【2차】 https://simpsonswiki.com/wiki/Spotting_notes (팬 위키, 원 인터뷰는 Ledesma 인용)
- **편당 큐 수.** Clausen(1997) 「한 회 30 큐 이하」가 유일한 수치다. 오래된 장편 기준이라 상한 근거로는 약하다. 【2차】 같은 위키
- **웃음 트랙.** 실사 시트콤에서 방청 효과음이 웃음 박자를 만들었다. 【2차】 https://www.rochester.edu/college/ugresearch/jur/crafting-comedy-sound-silence-and-framing-in-sitcoms/
- **【공백】** 장면 안 무음 관행, 회당 음악 길이, 현대 애니 시트콤 큐 수 실측.

## 3. 코드·데이터 기반 제작

- **Remotion.** 데이터를 props로 받는 템플릿, 루트 파일의 중앙 등록, `staticFile` 에셋 관리가 기본 구조다. 【2차】 https://www.remotion.dev/docs/reusability 크기 레지스트리 사례는 없었다. 【공백】
- **Motion Canvas 비교.** Remotion 쪽 자료라 한쪽 시각이다. 컴포넌트 props·앵커 배치 세부는 확인하지 못했다. 【미확인】
- **AI 시리즈 일관성.** 정면·측면·3/4·뒷면 턴어라운드와 얼굴 클로즈업을 만들고, 모든 컷 프롬프트에 참조를 붙인다. 한 장짜리 시트를 시리즈 전체에 쓰면 드리프트가 난다. 【2차】 https://invideo.io/faq/how-do-you-create-a-character-reference-sheet-for-ai/ (벤더 사례, 수치 불확실)
- **Frames-first.** 캐릭터·환경·소품 정지 참조를 전부 승인한 뒤에만 영상을 만든다. 【2차】 https://invideo.io/faq/what-is-the-frames-first-pipeline-for-ai-video/
- **2D 리그 혼합.** 에셋 팩(캐릭터·표정·소품·배경)을 AI로 만들고 퍼펫 리그로 움직인다. 【2차】 https://www.neolemon.com/blog/ai-storyboard-to-animation-pipeline-workflow
- **Disenchanted.** 배경은 포토샵, 캐릭터는 Harmony, 효과는 Harmony에서 그려 애프터이펙트에서 합성한다. 레이어로 나눈 구조다. 【2차】 https://www.toonboom.com/?p=17372

## 4. 세트 + 카메라 프리셋 + 표정 교체

- **멀티캠.** 카메라 3대에 역할을 나눈다(와이드·미디엄·클로즈업). 인물이 움직이면 카메라 배정을 바꾼다. 바닥 표시(마크)로 자리를 맞춘다. 【2차】 https://jk.media.indiana.edu/C228/3_camera_blocking_ex.shtml 세트 재사용 방식은 못 찾았다. 【공백】
- **표정 교체.** 입·눈썹을 표정 세트로 바꾼다(스왑 세트 개념). 입 모양 교체는 리그 문제를 만들기도 해서, 태그와 트리거를 같이 쓴다는 커뮤니티 의견이 있다. 【2차】

## 우리 제작 규칙 제안 (10개 이내)

1. **크기 레지스트리 1파일.** `size-registry.json`에 사람·윙키·문·식탁·컵·수첩의 mm 값과 px/mm 환산을 둔다. 렌더는 이 값만 읽는다. 기존 R-04 기준표를 여기로 옮긴다.
2. **컵은 손 기준 1개.** 컵 크기는 캐릭터 손 너비 대비 한 값으로만 정한다. 컷마다 따로 정하지 않는다. 【추정】
3. **바닥선 고정.** 발끝 y는 장면별 바닥선 값에서만 나온다. 인물 x는 좌·중·우 3슬롯만 쓴다. 【추정】
4. **세트 5곳 이하.** 거실·주방·현관·병원 대기실·공원 벤치처럼 장소를 고정하고, 세트마다 소품 좌표를 미리 정한다.
5. **세트별 카메라 프리셋 3개.** 와이드·미디엄·클로즈업. 각 프리셋에 바닥선·소품 좌표를 묶는다. 정면·평면을 기본으로 하고 측면 샷은 한 화 2회 이하.
6. **표정 6종 고정.** 중립·웃음·당황·짜증·놀람·말하기 입. 캐릭터별 파일로 두고 컷에서는 이름으로만 고른다.
7. **생성 순서.** 세트 플레이트·캐릭터 시트·소품 시트를 먼저 승인하고, 컷은 승인 에셋 합성만 한다(frames-first). 컷마다 참조 시트 세트를 붙인다.
8. **음악 큐 규칙.** 오프닝 테마 1개, 엔딩 1개, 장면 전환 스팅어 한 화 최대 4개, 길이 4~8초. 대사가 있는 컷 안에서는 음악을 깔지 않는다. 웃음 박자는 효과음이나 무음으로 만든다. 【추정】
9. **큐 시트.** 큐마다 시작 컷·끝 컷·「왜」 한 줄을 적는다. 기록 없는 큐는 넣지 않는다. 【추정】
10. **자동 검사.** 발끝 y 오차, 머리 높이 ±10%(R-04 기준), 소품 bbox의 mm 환산 ±10%. 넘으면 렌더 실패로 처리한다.

## 공백

- 시트콤 세트 재사용과 카메라 배치의 실제 제작 자료 (멀티캠 세트 재사용 방식)
- South Park 9일 주기, Kawaja 발언, 제작 도구 세부
- Peppa Pig 등 반복 세트 애니의 배경 재사용 방식
- Bluey 쇼 본편의 에셋 라이브러리 (공개 자료 없음)
- 시트콤 장면 안 무음 관행, 회당 음악 길이, 현대 애니 큐 수 실측
- 스팅어 길이·위치의 공식 규칙
- Remotion 크기 레지스트리·앵커 배치 사례, Motion Canvas 컴포넌트 API
- Character Animator 공식 표정 스왑 가이드
- AI 시리즈에서 레이어 고정 플레이트를 쓴 실측 사례
