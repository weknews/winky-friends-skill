# NOTICE: 서드파티 자원

이 레포의 코드는 MIT([`LICENSE`](LICENSE)), 위뉴 자산은 CC BY-NC-ND 4.0([`LICENSE-ASSETS.md`](LICENSE-ASSETS.md))이다. 아래 자원은 각자의 라이선스를 따른다.

## 글꼴 (SIL Open Font License 1.1): `kit/fonts/`

| 글꼴 | 파일 | 라이선스 전문 |
|---|---|---|
| 주아(Jua) | `Jua-Regular.ttf` | `kit/fonts/OFL-Jua.txt` |
| 도현(Do Hyeon) | `DoHyeon-Regular.ttf` | `kit/fonts/OFL-DoHyeon.txt` |
| 개구(Gaegu) Bold | `Gaegu-Bold.ttf` | `kit/fonts/OFL-Gaegu.txt` |
| Pretendard Bold·ExtraBold | `Pretendard-*.woff2` | `kit/fonts/OFL.txt` |

주아·도현·개구는 Google Fonts 저장소(github.com/google/fonts `ofl/`) 원본 그대로다. 글꼴 자체를 따로 팔지 않는 한 영상·문서에 넣어 쓸 수 있다.

## MIT License

- **PyAnimalese** (© 2022 Ju Hwijung, https://github.com/hwi-middle/PyAnimalese): 초성 19개 녹음(`sources/*.padata`)을 목소리 음원으로 쓴다(`engine/sound.py`). 레포에는 넣지 않고 `tools/PyAnimalese`에 클론한다.
- **lemo-opuscar** (© 2026 LemoLab, https://github.com/lemomo-ai/lemo-opuscar): `styles/rubber-hose/demo/mix.py`의 `slide_whistle`·`boing`, `core/audio/sfx.py`의 `pop` 식을 `engine/sound.py`에 옮겼다(대역 필터만 바꿈). 「띠로리」·「뿅」 효과음. 아이리스 전환 마스크 기법(`engine/index.html`)도 같은 레포의 `styles/rubber-hose/demo/scenes.js`에서 왔다.

MIT 고지: Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

## 그 밖

- **GSAP** (`engine/lib/gsap.min.js`, `CustomEase.min.js`): GreenSock 표준 라이선스(https://gsap.com/standard-license). 파일 머리의 고지를 그대로 둔다.
- **hyperframes, puppeteer-core** 등 `engine/package.json` 의존성: `npm install`로 받으며 각자의 라이선스를 따른다. 레포에 넣지 않는다.
- **음원**: Suno(위뉴 계정, 상업 이용 가능 요금제)로 생성했다. 출처는 `kit/music/SOURCE.md`. 위뉴 자산이다.
- **그림**: OpenAI Images(Codex CLI 내장 image_gen)로 생성한 뒤 사람이 승인했다. 위뉴 자산이다. 화면에 「AI로 만든 그림입니다」를 표시한다(`rules/ai-basic-act.md`).
