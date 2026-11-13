# 재사용 가능한 2D 캐릭터 프리미티브를 AI로 만드는 방법 (2025–2026 조사)

표기: 【확인】 = 1차 출처(공식 문서·논문 본문을 직접 열어 확인), 【2차】 = 벤더 블로그·비교 글·검색 요약, 【추정】 = 근거 부족한 판단.

## 1. 캐릭터 시트와 정체성 유지

- 【확인】 OpenAI 이미지 API 가이드: 편집 엔드포인트가 여러 입력 이미지를 참조로 받을 수 있고, 마스크는 첫 번째 이미지에 적용된다(알파 채널 필요). 현재 목록에는 `gpt-image-2.5-sunburst`(편집 정밀도), `gpt-image-2.5-flare`(빠른 생성), 2.6 변형이 나온다. 페이지 본문이 길어 input_fidelity 항목은 확인하지 못했다. https://developers.openai.com/api/docs/guides/image-generation
- 【확인】 Google AI Studio 이미지 문서: 현재 주력은 Nano Banana 2.1(`gemini-nano-banana-2.1`), 그 아래로 Nano Banana 2, Nano Banana Pro(`gemini-3-pro-image`), 레거시 Nano Banana(`gemini-2.5-flash-image`). 참조 이미지는 총 14장까지이며, 캐릭터 참조는 Nano Banana 2.1·2는 최대 4장, Pro는 최대 5장이다. 2.5 Flash Image는 이제 레거시다. https://aistudio.google.com/docs/image-generation
- 【2차】 Nano Banana 계열로 "정면·측면·후면·3/4 + 표정 + 포즈"를 한 장의 시트로 뽑는 방법이 여러 튜토리얼에 나온다. 표정을 이름으로 지정하고, 흰 배경과 스프라이트 시트 레이아웃을 명시하라는 식이다. 일관성 수치(95%, 98% 등)는 대부분 벤더·SEO 글이라 검증되지 않았다. https://selfielabstudio.com/blog/nano-banana-pro-consistent-character-sheets-guide-20260216 , https://www.morphstudio.com/article/efficient-character-design-with-nano-banana-pro
- 【2차】 공통 절차: 승인된 "골든 레퍼런스" 한 장을 고정하고, 거기서 시트(턴어라운드 + 표정 5종 + 의상 변형)를 파생시킨다. 드리프트가 생기면 레퍼런스를 다시 넣는다. https://invideo.io/blog/ai-character-consistency/ , https://easyviral.ai/blog/how-to-make-ai-animated-series
- 【2차】 Flux Kontext는 새로 시트를 만드는 용도보다 얼굴을 유지한 채 표정·의상만 바꾸는 편집 용도로 쓰인다고 설명된다. 벤더 주장이므로 자체 테스트가 필요하다. https://martini.art/en/workflows/character-consistency
- 【2차】 Sorceress 글은 정체성 보존에 Nano Banana Pro와 GPT Image 2를 꼽지만, 독립 벤치마크는 찾지 못했다. https://sorceress.games/blog/ai-character-generator-stay-on-model-with-reference-images-2026
- 【추정】 캐릭터별 LoRA는 이미지 모델 API만 쓰는 현재 파이프라인에 비해 학습·관리 비용이 크다. 9캐릭터 × 자세 수가 많지 않다면 레퍼런스 편집이 더 가볍다.

## 2. 모듈형·컷아웃 리그와 레이어 분해

- 【확인】 See-through 논문(arXiv 2602.03749, 2026-02-03 제출): 애니 일러스트 1장을 SDXL 기반 모델로 몸 부위별 RGBA 레이어(가려진 부분 인페인팅 포함)와 깊이 순서로 분해한다. 자체 수치는 FID 18.37(SAM+LaMa는 81.14). 한계로 몸 밖의 약간의 겹침, 깊이 레이어의 안정적 분리 어려움, 옷 경계 모호함을 명시한다. 주로 애니 인물 데이터에서 학습되었으므로 동물 캐릭터는 검증되지 않았다【추정】. https://arxiv.org/html/2602.03749
- 【확인】 Bunraku(arXiv 2607.27348, 2026-07): 일러스트 1장 → 레이어 분해 → 레이어 알파에서 메시 생성 → 키포즈 변위 예측까지 한 파이프라인. 저자들은 1단계 분해 오류를 2단계가 복구할 수 없다고 명시한다. 50개 캐릭터 평가에서 방향 코사인 0.768. 렌더 결과 평가는 아니다. https://www.alphaxiv.org/abs/2607.27348
- 【확인】 Live2D Cubism 자동 디포머 생성 매뉴얼: "동물 같은 비인간 모델은 적합하지 않다"고 명시하고, 사람이고 정면을 보며 똑바로 선 모델에서 가장 잘 된다고 한다. 우리 동물 캐릭터에는 이 기능을 쓸 수 없다. https://docs.live2d.com/en/cubism-editor-manual/auto-generation-of-deformer/
- 【2차】 Live2D 5.1(2024-07) 릴리스에서 AI 디포머 생성과 머리카락·액세서리 흔들림 자동 생성이 들어왔다. 2026년 AI 신기능은 찾지 못했다. https://automaton-media.com/articles/newsjp/20240730-303793/
- 【2차】 Spine은 AI 레이어 분해 기능이 확인되지 않았다. 대신 Scenario "2D Animation Rigging Sheet"가 부위(팔·몸통·머리)를 분리된 에셋 시트로 만들어 주는 방식을 제공한다. https://scenario.com/apps/2d-animation-rigging-sheet
- 【2차】 Qwen-Image-Layered에 LoRA를 붙여 얼굴 부위(눈·눈썹)를 레이어로 분리한 개인 테스트가 있다. 표정 교체를 얼굴 레이어만 바꾸는 방식이라 우리 엔진의 얼굴 플레이트 교체와 같은 발상이다. https://lilting.ch/en/articles/qwen-image-layered-live2d-face-parts
- 【추정】 현 엔진(Python 합성) 구조에 맞으려면 굳이 리그 툴이 필요 없다. 부위별 PNG(머리·눈썹·눈·입 모양·팔·손)를 AI로 만들고 합성 단계에서 조합하면 된다. Live2D·Spine은 움직임 보간이 필요할 때만 검토한다.

## 3. 이미지→영상 (짧은 모션)

- 【2차】 Kling 3.0과 Veo 3.1 비교는 대부분 벤더 글이고, 정체성 드리프트를 분리 측정한 독립 테스트는 찾지 못했다. Kling은 다인물 긴 테이크와 요소(Element) 참조에, Veo는 장면마다 참조 얼굴을 넣는 방식에 강하다고 주장된다. Veo 클립은 약 8초, Kling 3.0 Pro는 최대 15초로 보고된다. https://invideo.io/blog/kling-3-vs-veo-3-1/ , https://www.gradually.ai/en/ai-video-model-comparison/veo-3.1-vs-kling-3-pro/
- 【2차】 종이공예풍 스토리북 제작자는 컷 전환과 줌에 Kling을, 장면 움직임에 Veo 3.1을 쓰는 단계별 파이프라인을 설명한다. 캐릭터 시트 자체는 이미지 모델로 만든다. https://glennwilliams.beehiiv.com/p/how-i-make-ai-paper-cut-out-storybook-videos-complete-production-guide
- 【2차】 한 벤더의 Arcane풍 사례는 164 클립 생성 중 41개만 사용했다고 보고한다(폐기율 약 75%). 검증 불가. https://invideo.io/faq/what-is-the-best-ai-workflow-for-producing-an-arcane/
- 【추정】 입을 움직이는 대사는 영상 생성보다 입 모양 레이어 교체가 통제하기 쉽다. 영상 생성은 걷기·문 열기 같은 긴 모션이나 한 번뿐인 연출에만 쓰는 편이 비용과 드리프트 면에서 낫다.

## 4. 실제 제작 사례

- 【2차】 AI 애니메이션 시리즈 가이드들은 공통적으로 "승인 게이트를 단계마다 둘 것", "캐스트 단계의 캐릭터 시트가 기준 이미지가 된다"고 말한다. 종이공예 AI 시트콤의 구체적 제작 기록은 찾지 못했다. https://easyviral.ai/blog/how-to-make-ai-animated-series

## 5. 권장 최소 에셋 세트 (캐릭터 1명 기준, 【추정】)

기준 원칙: 몸은 고정 하나, 바뀌는 것은 머리·얼굴·팔·손·소품으로 쪼갠다. 현재 파이프라인(자세 PNG 통째 생성)에서 부위 PNG로 옮기는 것이 핵심이다.

- 몸: 정면 서기 1, 앉기 1(정면), 3/4 서기 1, 측면 서기 1, 뒷모습 1.
- 머리: 정면, 3/4, 측면, 뒷머리 각 1 (몸과 분리). 얼굴 플레이트는 머리 정면 기준으로 교체.
- 표정 플레이트 7–8종: 평온, 웃음, 화남, 슬픔, 놀람, 당황, 민망, 능청 (눈썹 포함).
- 입 모양 5종: 닫힘, 아(크게), 오(둥글게), 이(좁게), 음(M·닫힘 이빨). 기존 "까딱" 흔들림은 입 모양 사이를 바꾸는 대체로 둔다.
- 팔·손: 팔은 상완·하완 분리. 손은 빈손, 펴진 손(가리킴), 주먹, 소품 쥔 손 4종, 소품은 별도 PNG와 손 위치 앵커.
- 소품: 공용 소품 라이브러리로 두고 캐릭터별 복제는 하지 않는다.
- 합계: 캐릭터당 약 25–30장(부위). 9캐릭터면 약 230–270장. 자세 PNG를 매번 새로 만드는 것보다 부위 재사용이 훨씬 많은 상황을 덮는다.

## 6. 바로 실행할 권고

1. 캐릭터별 골든 레퍼런스 1장을 고정하고, 모든 부위 생성을 그 레퍼런스 편집으로 한다(현재 파이프라인과 같은 마젠타 키 유지).
2. 자세 전체 생성을 멈추고, 머리·얼굴·입·팔·손을 각각 별도 프롬프트로 뽑는다.
3. 동물 캐릭터는 Live2D 자동 디포머와 See-through 계열이 검증되지 않았으므로 자동 분해는 시험 1–2캐릭터만 한다.
4. 영상 생성(Kling/Veo)은 컷 전환이나 긴 모션 연출에만 쓴다. 대사 장면은 레이어 합성으로 간다.
5. 드리프트 측정: 같은 레퍼런스로 얼굴 유사도를 장면마다 기록하는 간단한 체크를 만든다(독립 벤치마크가 없어서 직접 해야 함).

## 한계

- 제작 사례와 모델 순위는 대부분 벤더 글이다. 독립 비교는 찾지 못했다.
- 모델 이름과 버전은 공식 문서 페이지 본문 기준이며, 실제 API 가용성은 계정에서 확인해야 한다.
