# 색 조합·명도 대비 리서치 (페이퍼 크래프트 1분 숏츠용)

표기: 【확인】 = 원문을 직접 열어 확인함 / 【2차】 = 블로그·튜토리얼 요약 기준 / 【추정】 = 출처 부족, 우리 맥락으로 옮긴 판단

## 0. 리서치 한계
- Tearaway 색 설계는 찾지 못했다. 2025–2026 페이퍼 컷·디오라마 애니메이션의 색 사용을 다룬 독립 분석도 없었다. 나온 것은 벤더 페이지와 프롬프트 갤러리 위주다.
- 아래 근거 대부분은 모션그래픽·3D 조명 글이다. 페이퍼 컷 2D 캐릭터에 그대로 옮기는 것은 【추정】이다.

## 1. 명도 구조와 채도 (근거 있음)
- 명도 차이가 클수록 대비가 크다. 명도가 비슷한 두 형태는 하나로 뭉친다. 흑백으로 보거나 눈을 가늘게 떠서 확인한다. 【2차】 https://schoolofmotion.com/blog/design-value-structure-color-theory (날짜 미표기)
- 채도는 분위기를 정한다. 고채도는 선명하고 저채도는 회색빛으로 가라앉는다. 팔레트 기반을 파스텔로 잡으면 "washed out"이 된다는 경고가 있다. 【2차】 https://www.animateyour.science/post/colour-mastery-in-animation-dos-and-don-ts-for-creating-vibrant-animations (2024-08)
- 같은 글은 명도나 채도가 같은 색끼리 붙이면 대비가 가장 나쁘다고 한다. 보색 쌍은 "자연스러운 반대"로 쓰되, 순색 대신 살짝 누그러뜨리라고 한다(색약 시청자 고려). 【2차】 위와 같음
- 60-30-10은 모션 디자인 글에서도 가이드라인으로 소개된다. 정확한 공식은 아니라고 명시한다. 【2차】 https://lottiefiles.com/blog/tips-and-tutorials/color-theory-for-motion-design (2022-06)
- 같은 글: 검정·회색을 배경이나 외곽선으로 쓰면 주인공이 살아난다. 색 불협화(주변과 어긋나는 한 색)로 시선을 끈다. 【2차】 위와 같음

## 2. 캐릭터 가독성과 배경 분리 (근거 있음)
- 캐릭터와 배경의 명도가 비슷하면 실루엣이 사라진다. 배경 명도를 조정하고 얼굴·상체 주변에 의도된 대비를 준다. 【확인】 https://80.lv/articles/lighting-in-3d-art-why-it-matters-how-to-improve-it/ (2026-05, 3D 조명 인터뷰)
- 어두운 셋업에서는 림 라이트로 실루엣을 분리한다. 림 라이트는 최종 조명 패스에 넣는다. 【확인】 위와 같음
- 큰 배경 면은 명도 높고 채도 낮게, 채도 높은 대비는 얼굴이나 핵심 아이콘에만 쓴다. 시선 경로가 생긴다. 【2차】 StudyRaid 가이드(https://app.studyraid.com/en/read/79471/3736150/maintaining-high-contrast-readability, 날짜 미확인). 이 글은 3D 기준이다.
- 배경이 밝으면 림 대신 어두운 할로(halo)로 분리한다. 【2차】 위와 같음
- 캐릭터 색이 배경을 "방해"하면 배경 색을 바꾼다. 【2차】 SoM 위와 같음

## 3. 색 스크립트 (Pixar 계열, 60초 6씬 적용)
- 색 스크립트는 스토리가 어느 정도 잡힌 뒤 만들고, 초기 단계 내내 스토리와 함께 갱신된다. 【2차】 Pixar 관련 설명을 모은 검색 요약. 원출처 미확인.
- 한 장면에 지배색 하나, 명도 한 단계를 적는 방식은 여러 블로그가 설명한다. 【2차】 https://pixune.com/?p=37699 류. 신뢰도 낮음.
- 실무 팁: 색을 기억에 의존하지 말고 HEX를 기록한다. 【2차】 animateyour.science 위와 같음.

우리 6씬 적용 (【추정】):
| 씬 | 감정어 | 지배색 | 명도 | 강조 포인트 |
|---|---|---|---|---|
| 1 훅 | 불안·긴장 | 어두운 배경 + 보색 1점 | 저 | 얼굴 주변만 밝게 |
| 2 | 부딪힘 | 에피소드 키 오브젝트 색 | 중 | 캐릭터 림 |
| 3 | 갈등 고조 | 지배색 60%, 보조 30% | 중 | 순간 불협화 1점 |
| 4 | 반전 | 채도 낮춘 배경 | 중 | 핵심 소품 |
| 5 | 몸 | 밝은 본체 | 고 | 표정 명도 차 |
| 6 | 따뜻한 마무리 | 웜톤 키 | 고 | 얼굴 가장 밝음 |

## 4. 이미지 모델 프롬프트 (약한 근거)
- 커뮤니티 갤러리 프롬프트는 "bold black outlines, bright, saturated colors"나 "limit the dominant palette to a few colors"를 쓴다. 【2차】 https://carat.im/en/prompt-gallery/paper-cut-style (커뮤니티 예시, 검증 안 됨)
- 파스텔·저채도 용어를 넣으면 흐려진다는 점은 갤러리 예시들이 반대로 보여준다. 정확한 출처 URL은 검색 결과에서 특정하지 못했다. 【추정】
- 실패 모드(추정): "pastel", "airy", "soft", "elegant" 같은 단어가 채도를 낮춘다. 페이퍼 질감 단어("layered cardstock", "clean cut edges", "subtle shadows between layers")는 채도를 살려 두는 데 도움이 된다. 【2차】 위 갤러리.
- 권장 구조: 지배색·보조색·포인트색 HEX를 명시하고, 포인트 면적을 8–10%로 적고, "high value contrast, saturated main color, muted background"를 넣는다. 금지어에 pastel·washed out을 넣는다. 【추정】
- 모델 비교나 Nano Banana·FLUX 전용 실험 근거는 찾지 못했다.

## 5. 우리 원칙과의 대조
- 기존 원칙(60-30-10, 보색 포인트 ≤8–10%, 키 오브젝트 색, 45° 이상 색상 분리, 훅 어둡게)은 외부 근거와 맞는다. 그대로 두고 아래를 보완한다.
- 보완 1: "밝은 본체"는 배경과 명도 차가 있을 때만 성립한다. 흰 벽과 옅은 캐릭터는 실패 패턴이다. 【추정】
- 보완 2: 배경은 밝게 하더라도 저채도로 두고, 채도는 캐릭터 얼굴이나 키 소품에만 준다. 【2차】
- 보완 3: 파스텔을 기본 팔레트로 쓰지 않는다. 【2차】 animateyour.science.
- 보완 4: 명도 차이가 작은 파랑-보라, 연노랑-연두 조합은 노인층이 구분하지 못한다는 기존 원칙은 명도 대비로 해결하는 방향이 맞다. 외부 근거는 찾지 못함. 【추정】

## 6. 체크리스트 (규칙화 후보)
1. 씬별 흑백 캡처(또는 눈 가늘게 뜨기)에서 캐릭터 실루엣이 배경과 구분되는가? 아니면 배경 명도를 먼저 바꾼다.
2. 얼굴 주변 명도 차가 충분한가? 배경이 얼굴보다 어둡거나 밝아야 한다.
3. 큰 배경 면은 저채도인가? 고채도는 키 소품·얼굴 포인트에만 있는가?
4. 보색 포인트 면적이 8–10% 이하인가?
5. 지배색 60 / 보조 30 / 포인트 10이 맞는가?
6. 파스텔·저채도 단어가 프롬프트에 들어 있지 않은가?
7. 씬 HEX가 색 스크립트에 기록되어 있고, 인접 씬과 지배색이 다른가?
8. 색약 시뮬레이션에서 포인트색이 살아 있는가?

## 출처 목록
- https://schoolofmotion.com/blog/design-value-structure-color-theory
- https://www.animateyour.science/post/colour-mastery-in-animation-dos-and-don-ts-for-creating-vibrant-animations
- https://80.lv/articles/lighting-in-3d-art-why-it-matters-how-to-improve-it/
- https://lottiefiles.com/blog/tips-and-tutorials/color-theory-for-motion-design
- https://app.studyraid.com/en/read/79471/3736150/maintaining-high-contrast-readability
- https://carat.im/en/prompt-gallery/paper-cut-style
- https://www.moma.org/audio/playlist/192/2575 (Pixar 색 스크립트 읽는 순서, 약함)
