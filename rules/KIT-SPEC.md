# 모래언덕 빌라 제작 키트 사양 1판 (2026-11-11)

- 근거: `skills/winky-script/references/R-17-rule-based.md`(규칙 기반 제작), `skills/winky-script/references/R-16-shortdrama-pace.md`(호흡), `ep01/README.md`(2판 한계)
- 쓰임: 1화 6판(`episodes/ep01-fruit-juice/script-9c.md`)부터 모든 회차. 대본의 컷 표는 이 문서에 있는 이름만 쓴다.
- 기획은 Fable, 그림·코드·렌더는 Opus. 이 문서의 숫자는 `kit/size-registry.json`, `kit/sets.json`, `kit/kit.json`으로 옮겨 렌더가 읽는다. 컷마다 손으로 좌표를 적지 않는다.

## 0. 제작자 지적(11/11)과 대응

| 지적 | 원인 | 규칙 |
|---|---|---|
| 컵 크기가 컷마다 다르다 | 배경에 컵이 그려져 있고, 자세 그림 손에도 컵이 그려져 있었다 | 컵은 조각 하나(`cup`)뿐이다. 배경과 자세 그림에 소품을 그리지 않는다(1절, 3절) |
| 시계 숫자가 칸 밖으로 넘친다 | 글자 크기를 손으로 정했다 | 칸 글자는 칸 크기에서 계산한다(6절) |
| 의성어가 그림을 가린다 | 자리를 컷마다 눈대중으로 잡았다 | 글자 구역과 보호 상자를 두고 겹치면 빌드가 실패한다(2절, 6절) |
| 윙키가 사과를 밟고 선 것처럼 보인다 | 조각이 바닥·손이 아닌 곳에 떠 있었다 | 모든 조각은 「놓이는 곳」 넷 중 하나에만 붙는다(2절) |
| 음악이 내내 깔린다 | 배경음악을 전 구간에 깔았다 | 음악은 큐 시트에 있는 곳만, 대사와 겹치지 않는다(5절) |

## 1. 크기 레지스트리 (mm)

화면 크기는 언제나 「mm × 그 컷 프리셋의 px/mm」다. 다른 방법으로 크기를 정하지 않는다.

### 인물 9명

| 인물 | 키 | 비고 |
|---|---|---|
| 곰 아빠 | 1800 | 모자 끝까지 |
| 판다 | 1600 | |
| 고양이 사장 | 1450 | |
| 너구리 대리 | 1450 | |
| 다람쥐 코치 | 1300 | |
| 도치 실장 | 1250 | |
| 거북 여사 | 1200 | |
| 펭귄 선생님 | 1100 | |
| 윙키 | 650 | 귀 끝까지 |

- 값은 `chars.txt`와 같다. 바꾸지 않는다.
- 인물마다 **머리 폭(mm)** 을 차렷 그림에서 한 번 재서 레지스트리에 적는다. 자세가 달라도 머리 폭으로 배율을 맞춘다(숙인 자세는 키로 잴 수 없다).

### 공용 소품

| 이름 | 크기(mm) | 조각 | 비고 |
|---|---|---|---|
| `cup` 컵 | 높이 190(빨대 끝까지), 폭 106 | `cup-empty` `cup-third` `cup-twothird` `cup-full` (있음) | **시리즈의 컵은 이것 하나다.** 뚜껑 달린 하늘색 컵. 유리컵·머그는 쓰지 않는다 |
| `apple` 사과 | 높이 90(꼭지까지), 폭 80 | `apple-whole`, `apple-bite-1~3` (있음) | 초록 사과 |
| `jug` 주스 통 | 높이 200, 폭 213 | `jug` (있음) | 착즙기 옆에 둔다 |
| `box` 택배 상자 | 폭 500, 높이 300 | `box-closed`, `box-open` (새로) | 윙키 눈(바닥에서 330)이 상자 위로 겨우 나온다 |
| `note` 쪽지 | 폭 150, 높이 100 | `note` (새로) | 그 회의 강조색 소품 |
| `chair` 의자(발판) | 좌판 높이 450, 등받이 끝 900, 폭 420 | `chair` (새로) | 윙키 발판. 세트마다 가운데 자리에 둔다 |
| `clock` 탁상시계 | 폭 160, 높이 90 | (1화에 안 씀, 쓸 때 생성) | 화면은 비워 그리고 숫자는 6절 규칙으로 얹는다 |
| `card` 소개 카드 | 큰 카드 640×420px, 작은 카드 520×300px | `card`, `card-s`, `tape` (있음) | 화면 고정 크기(mm 아님) |

### 세트 고정물 (배경에 그려 두는 것)

| 이름 | 크기(mm) |
|---|---|
| 현관문·문틀 | 높이 2100, 폭 900 |
| 식탁 | 높이 750, 폭 680 |
| 조리대 | 높이 850 |
| 착즙기 | 높이 400, 폭 250 (조리대 위) |
| 상담소 책상 | 높이 750 |
| 계단 한 단 | 높이 170, 깊이 270 |

### 손에 든 소품

- **자세 그림의 손은 비워 그린다.** 컵·사과·상자·쪽지를 손에 그려 넣지 않는다. 인물이 원래 지닌 것만 예외다(펭귄 선생님 부채, 청진기).
- 자세 조각마다 `hand` 앵커(조각 안의 손바닥 중심 좌표)를 `kit.json`에 적는다. 소품은 그 앵커에 레지스트리 크기로 얹는다. 손바닥이 소품 뒤에 3분의 1쯤 가려지게 놓는다(종이 인형 방식).
- 소품 크기는 손 크기에 맞춰 바꾸지 않는다. 곰 아빠가 들어도 윙키가 들어도 컵은 190mm다. 그 차이가 그림이다.

### 놓이는 곳 (네 가지뿐)

모든 조각은 다음 중 하나에 붙는다. 그 밖의 자리는 없다.

1. **바닥선:** 인물 발끝, 상자, 의자.
2. **윗면:** 식탁·조리대·책상·의자 좌판·상자 윗면. y는 「바닥선 − 높이 × px/mm」로 나온다.
3. **손 앵커:** 손에 든 소품.
4. **판:** 그림판·끝 화면 위(실제 크기가 아닌 도해. 사과와 컵의 상대 크기만 지킨다).

## 2. 세트와 카메라

### 공통 틀 (1080×1920)

세트가 달라도 프리셋 숫자는 같다. 세트마다 다른 것은 도면(가구 자리)과 배경 그림뿐이다.

| 프리셋 | px/mm | 바닥선 y | 인물 자리 x | 쓰임 |
|---|---|---|---|---|
| `W` 와이드 | 0.50 | 1420 | 좌 230 · 중 540 · 우 850 | 세 사람, 방 전체. 곰 아빠 머리끝 y 520 |
| `M` 미디엄 | 0.80 | 1840 | 좌 200 · 중 540 · 우 880 | 두 사람과 가운데 윙키. 곰 아빠 머리끝 y 400 |
| `CU` 클로즈업 | 1.40 | 300 + 키 × 1.4 | 중 540 | 한 사람. 머리끝(귀·모자 포함)을 y 300에 맞춘다 |

- 화면 좌표는 계산한다. `x = 540 + (X − 세트 중심) × px/mm`, `y = 바닥선 − 높이 × px/mm`.
- 뒷벽 가구(조리대·식탁·책상)의 밑선은 바닥선보다 80mm 위다(W 40px, M 64px). 인물은 가구 앞에 선다.
- **윙키 발판 규칙:** 윙키는 `M`에서 늘 가운데 자리 의자 위에 선다. 머리끝이 y 960으로 펭귄 선생님과 같다. 바닥에 서면 자막 띠에 가려진다. `W`에서도 가운데 자리면 의자 위다.
- 인물끼리 겹침은 폭의 15%까지다. 얼굴 상자는 겹치지 않는다.
- 카메라는 프리셋 안에서 움직이지 않는다. 바꾸려면 컷을 나눈다. 옆모습 구도는 쓰지 않는다(정면·평면).
- 조각 확대는 1.3배, 배경 확대는 1.15배까지다. 넘으면 그 프리셋용 그림을 따로 만든다. 그래서 곰 아빠·판다·펭귄 선생님의 `CU`는 상반신 그림을 쓴다.

### 글자 구역

| 구역 | 자리 | 규칙 |
|---|---|---|
| 안전 여백 | 좌우 60, 위 200, 아래 220 | 글자와 얼굴을 두지 않는다 |
| 대사 자막 띠 | y 1500~1700, 폭 960 | 68px, 두 줄까지. 다리와 바닥은 가려도 된다. 얼굴·손·소품은 가리지 못한다(프리셋 바닥선이 이걸 보장한다) |
| 의성어 | 후보 자리 넷: 좌상(280, 300) · 우상(800, 300) · 좌중(200, 760) · 우중(880, 760) | 보호 상자와 안 겹치는 첫 자리에 놓는다. 다 겹치면 110 → 88 → 72px로 줄이고, 그래도 겹치면 빌드 실패. 한 컷에 하나 |
| 소개 카드 | 좌하(350, 1250) · 우하(730, 1250) · 지정 소품 위 | 손에 든 소품의 반대쪽. 얼굴과 그 컷의 핵심 소품을 가리지 못한다 |
| 근거 자막·제목 | y 220~290 | 56px |

**보호 상자**는 얼굴(`kit.json`의 `face`), 손과 손에 든 소품, 그 컷의 핵심 소품(컷 표 「소품」 칸 첫 번째), 떠 있는 카드다.

### 세트 1. 곰네 부엌 `kitchen` (1화)

도면(X는 왼쪽 벽에서 mm, 세트 중심 1080):

| 고정물·자리 | X | 높이 |
|---|---|---|
| 식탁 | 80~760 | 750 |
| 의자(윙키 발판, 조각) | 1080 | 좌판 450 |
| 상자 자리(바닥) | 1380 | |
| 조리대 | 1300~2160 | 850 |
| 주스 통 자리(조리대 위) | 1400 | |
| 착즙기(조리대 위) | 1620 | 400 |
| 컵 자리(조리대 위) | 1500 | |
| 창 | 250~750, 바닥에서 1100~1900 | |

| 프리셋 | 배경 | 보이는 범위 | 배경 기준 사물(그림 높이의 %) |
|---|---|---|---|
| `W` | `set-kitchen-w` | X 0~2160 | 바닥선 74%, 조리대 윗면 50%, 식탁 윗면 52% |
| `M` | `set-kitchen-m` | X 405~1755 | 바닥선 96%, 조리대 윗면 57%, 식탁 윗면 61% |
| `CU` | `set-kitchen-cu` | 벽면 | 연두 벽과 창틀 한쪽만. 기준 사물 없음 |
| `TOP` 조리대 근접 | `bg-juicer` (있음) | 착즙기 투입구 | 투입구 지름 110mm로 px/mm를 잰다. 사과가 들어가는 컷 전용 |

### 세트 2. 곰네 현관 `door` (1화)

도면: 문틀 X 630~1530(중심 1080, 높이 2100). 신발장 X 1600~2100(높이 900). 상자 자리 X 1080.

| 프리셋 | 배경 | 비고 |
|---|---|---|
| `W` | `bg-door-out` (있음, 1화에 안 씀) | 문틀 윗선이 y 370에 오게 한 값으로 맞춘다 |
| `M` | (쓸 때 생성) | |
| `CU` | `set-door-cu` | 문턱 높이에서 본 열린 문간. 문틀 두 기둥과 바닥 매트만 |

### 세트 3. 건강상담소 `office` (1화)

도면(세트 중심 1080):

| 고정물·자리 | X | 높이 |
|---|---|---|
| 선반(뒷벽) | 200~900 | 1800 |
| 명패 「위뉴 건강상담소」(뒷벽, 칸 글자) | 400~900, 바닥에서 1500~1650 | |
| 의자(윙키 발판, 조각) | 1080 | 좌판 450 |
| 책상(오른쪽 벽) | 1400~2160 | 750 |
| 선풍기(책상 위) | 1700 | 350 |

| 프리셋 | 배경 | 배경 기준 사물 |
|---|---|---|
| `W` | `bg-office` (있음, 1화에 안 씀) | 책상이 앞에 있어 인물이 가려진다. 쓸 때 다시 만든다 |
| `M` | `set-office-m` | 바닥선 96%, 책상 윗면 61% |
| `CU` | `set-office-cu` | 연노랑 벽과 선반 한쪽만 |

### 세트 4. 계단참 `stairs` (2화 이후, 지금은 만들지 않는다)

도면: 계단이 왼쪽 위에서 가운데 참으로 내려온다. 참 폭 1200, 층 표시 숫자판(칸 글자). `W`만 쓴다. 인물 자리는 계단 위(좌), 참(중·우)이다.

### 판 2종 (세트가 아님)

| 이름 | 배경 | 쓰임 |
|---|---|---|
| `board` 그림판 | `bg-diagram` (있음) | 쪽지 확대, 도해. 글자 칸은 x 140~940, y 420~1380 |
| `end` 끝 화면 | `bg-end` (있음) | 검수·근거·AI 표시 |

### 배경 생성 원칙

- 인물 없이 세트만 그린다. **컵, 과일, 그릇, 시계 숫자, 글자를 그리지 않는다.** 움직이거나 바뀌는 것은 전부 조각이다.
- 기준 사물의 높이를 프롬프트에 %로 적는다(위 표). 받은 그림에서 기준 사물을 재고, ±5%를 벗어나면 한 값으로 키우거나 줄여 맞춘다. 그 값을 `sets.json`에 적는다.
- 같은 세트의 `M`·`CU`는 `W` 그림을 참조로 붙여 만든다.

## 3. 인물 자세와 표정

### 원칙

- **인물별 세로 단독 한 장씩** 만든다. 1024×1536, 마젠타 키(윙키는 귀 분홍 때문에 파랑 키). 한 장에 한 인물, 한 자세다. 여러 자세를 한 장에 모으지 않는다.
- 전신은 발끝을 아래 5%, 머리끝을 위 5% 선에 맞춘다. 상반신은 머리 폭이 그림 폭의 60%다.
- 새 자세는 그 인물의 차렷 그림을 참조로 붙인다. 표정만 다른 그림은 기본 그림을 참조로 「얼굴만 바꾼다」로 만든다.
- 편 색 문단은 인물 프롬프트에 넣지 않는다(옷 색이 덮인다, README).
- 이름은 `인물-자세-표정`이다. 컷 표에는 이 이름만 쓴다.

### 표정 6종

| 이름 | 뜻 |
|---|---|
| `평온` | 기본 |
| `웃음` | 환하게 |
| `놀람` | 눈이 커진다 |
| `당황` | 눈을 피한다. 땀은 `sweat` 조각으로 따로 붙인다 |
| `시무룩` | 삐침, 풀 죽음(윙키는 귀가 처진다) |
| `말하기` | 입을 벌린다. `CU`에서 `평온`과 번갈아 12fps로 입을 움직인다 |

화내는 표정은 두지 않는다. 이 세계에는 혼내는 인물이 없다. `W`·`M`에서는 입 움직임 없이 조각이 살짝 까딱인다.

### 자세 12종 (인물 공통 이름)

| 이름 | 뜻 | 손 앵커 |
|---|---|---|
| `서기` | 차렷. 배율 기준 | |
| `내밀기` | 한 손을 앞으로 뻗는다 | 있음 |
| `들기` | 한 손을 가슴 높이로 | 있음 |
| `양손들기` | 두 손을 앞으로 모은다 | 있음 |
| `숙이기` | 허리를 굽혀 아래를 본다(속삭임) | 있음(내린 손) |
| `뒤돌기` | 뒷모습 | 등 앵커(쪽지) |
| `달리기` | 뛰는 한 장. 12fps로 위아래 까딱 | |
| `앉기` | 의자·평상 | |
| `가리키기` | 한 손으로 가리킨다 | |
| `상반신` | `CU`용. 손 하나가 가슴 높이에 보인다 | 있음 |
| `부채질` | 펭귄 선생님 고유(기본 `서기`가 부채를 들고 있다) | |
| `붙어서기` | 두 인물이 닿는 자세. 한 덩어리로 만든다 | |

### 1화 6판에 필요한 것 (22장: 새로 18, 있음 4)

| 인물 | 이름 | 상태 |
|---|---|---|
| 윙키 | `winky-서기-평온` | 새로(지금 것은 600px라 `CU`에 못 쓴다) |
| 윙키 | `winky-서기-말하기` · `-당황` · `-시무룩` | 새로 3 |
| 윙키 | `winky-달리기-당황` | 새로 |
| 윙키 | `winky-뒤돌기` | 새로 |
| 윙키 | `winky-양손들기-웃음` | 새로 |
| 곰 아빠 | `bear-서기-웃음` | 있음(`bear-stand`) |
| 곰 아빠 | `bear-내밀기-웃음` | 있음(`bear-handoff`, 빈 손) |
| 곰 아빠 | `bear-숙이기-당황` | 새로 |
| 곰 아빠 | `bear-들기-당황` | 새로 |
| 곰 아빠 | `bear-상반신-평온` · `-말하기` · `-당황` | 새로 3 |
| 판다 | `panda-양손들기-놀람` | 있음(`panda-recv`, 빈 손) |
| 판다 | `panda-내밀기-웃음` · `-시무룩` | 새로 2 |
| 판다 | `panda-뒤돌기` | 새로 |
| 펭귄 선생님 | `penguin-서기-평온` | 있음(`penguin-stand`, 부채) |
| 펭귄 선생님 | `penguin-내밀기-평온` | 새로 |
| 펭귄 선생님 | `penguin-상반신-평온` · `-말하기` | 새로 2 |

`ep01/kit`의 나머지 자세(`panda-pour`, `panda-tada`, `panda-thrust`, `m-*`, `cu-*`, `duo-*`, `bear-sneak-*`, `penguin-pj-*`, `winky-*`)는 손에 소품이 그려져 있거나 해상도가 낮아 6판에 쓰지 않는다. 지우지는 않는다.

## 4. 그림 목록 (새로 28, 있음 24)

프롬프트는 `style-base.txt`와 `chars.txt`의 해당 인물 줄 뒤에 붙인다.

### 새로 만드는 것

| # | 이름 | 크기 | 키 | 프롬프트 한 줄 |
|---|---|---|---|---|
| 1 | `set-kitchen-w` | 1152×2048 | 없음 | Bright morning apartment kitchen, flat front view, wide: white dining table on the left, white counter along the right back wall with a white slow juicer on it, window upper left, pale green #DDF3CE wall; floor line at 74% of image height, counter top at 50%, table top at 52%. No people, no cups, no fruit, no bowls, no clock, no text. |
| 2 | `set-kitchen-m` | 1152×2048 | 없음 | The same kitchen as the attached image, closer: floor line at 96% of image height, counter top at 57%, table edge at the far left with its top at 61%, juicer near the right edge. No people, no cups, no fruit, no text. (참조 #1) |
| 3 | `set-kitchen-cu` | 1152×2048 | 없음 | Plain pale green #DDF3CE layered paper wall of the same kitchen with only one edge of the white window frame at the far left. Nothing else. (참조 #1) |
| 4 | `set-door-cu` | 1152×2048 | 없음 | Low view at doorstep height of an open apartment doorway seen from inside: two white door-frame posts at the left and right edges, a green doormat on the floor, hallway in mid green #A0DD88 behind; floor line at 63% of image height. No people, no objects. |
| 5 | `set-office-m` | 1152×2048 | 없음 | Small friendly health counseling office, flat front view: pale shelves on the back wall at the left with a blank white name plate, a white desk against the right wall with a small desk fan on it, warm pale yellow-green #E9EDC0 wall; floor line at 96% of image height, desk top at 61%; the center floor is empty. No people, no cups, no text. |
| 6 | `set-office-cu` | 1152×2048 | 없음 | Plain warm pale yellow-green #E9EDC0 layered paper wall of the same office with only one edge of the pale shelf at the far right. Nothing else. (참조 #5) |
| 7 | `box-closed` | 1024×1024 | 마젠타 | A closed kraft cardboard parcel box, front view, 5:3 wide, with one blank white label on the front. No text. |
| 8 | `box-open` | 1024×1024 | 마젠타 | The same box with its top flaps open and green apples heaped inside, front view, blank white label. No text. (참조 #7) |
| 9 | `note` | 1024×1024 | 마젠타 | A blank pale blue #9EC4FA paper memo, 3:2 wide, one small strip of tape at the top. No text. |
| 10 | `chair` | 1024×1536 | 마젠타 | A plain white wooden dining chair, flat front view, seat at half of the backrest height. |
| 11 | `winky-서기-평온` | 1024×1536 | 파랑 | WINKY standing straight, facing front, arms at sides, calm small smile. Full body, empty hands. (참조: 윙키 원본) |
| 12 | `winky-서기-말하기` | 1024×1536 | 파랑 | The same image, nothing moved, only the mouth open as if talking. (참조 #11) |
| 13 | `winky-서기-당황` | 1024×1536 | 파랑 | The same image, only the face changes: eyes looking away, tight wobbly mouth. (참조 #11) |
| 14 | `winky-서기-시무룩` | 1024×1536 | 파랑 | The same pose, both ears drooping down, eyes lowered, small pout. (참조 #11) |
| 15 | `winky-달리기-당황` | 1024×1536 | 파랑 | WINKY running, facing front, arms pumping, one foot off the ground, flustered face. Empty hands. (참조 #11) |
| 16 | `winky-뒤돌기` | 1024×1536 | 파랑 | WINKY seen from behind, standing straight, plain back, tail to one side. (참조 #11) |
| 17 | `winky-양손들기-웃음` | 1024×1536 | 파랑 | WINKY standing, both open paws held together in front of the chest as if holding something, happy grin. Empty hands. (참조 #11) |
| 18 | `bear-숙이기-당황` | 1024×1536 | 마젠타 | BEAR DAD bending forward at the waist to whisper downward, one paw beside his mouth, the other open paw held low at his side, worried eyes. Empty hands. (참조: `bear-stand`) |
| 19 | `bear-들기-당황` | 1024×1536 | 마젠타 | BEAR DAD standing, one open paw raised at chest height as if holding a cup, worried stiff smile. Empty hands. (참조: `bear-stand`) |
| 20 | `bear-상반신-평온` | 1024×1536 | 마젠타 | BEAR DAD bust shot from the belly up, facing front, one open paw at chest height, blank calm face; the head is 60% of the image width. Empty hands. (참조: `bear-stand`) |
| 21 | `bear-상반신-말하기` | 1024×1536 | 마젠타 | The same image, only the mouth slightly open. (참조 #20) |
| 22 | `bear-상반신-당황` | 1024×1536 | 마젠타 | The same image, only the face changes: eyes looking sideways, stiff smile. (참조 #20) |
| 23 | `panda-내밀기-웃음` | 1024×1536 | 마젠타 | PANDA standing, one arm stretched forward with an open paw as if offering something, big proud smile. Empty hands. (참조: `panda-recv`) |
| 24 | `panda-내밀기-시무룩` | 1024×1536 | 마젠타 | The same pose, head turned away, small pout. (참조 #23) |
| 25 | `panda-뒤돌기` | 1024×1536 | 마젠타 | PANDA seen from behind, standing, arms forward as if wiping a counter. (참조: `panda-recv`) |
| 26 | `penguin-내밀기-평온` | 1024×1536 | 마젠타 | PENGUIN DOCTOR standing, one flipper stretched forward with the tip flat as if sticking a note, calm face, fan in the other flipper. (참조: `penguin-stand`) |
| 27 | `penguin-상반신-평온` | 1024×1536 | 마젠타 | PENGUIN DOCTOR bust shot from the belly up, facing front, fan held at the side, calm half-closed eyes, one sweat drop; the head is 60% of the image width. (참조: `penguin-stand`) |
| 28 | `penguin-상반신-말하기` | 1024×1536 | 마젠타 | The same image, only the beak slightly open. (참조 #27) |

### 그대로 쓰는 것 (`ep01/kit`)

| 종류 | 조각 | 수 |
|---|---|---|
| 인물 | `bear-stand`, `bear-handoff`, `panda-recv`, `penguin-stand` | 4 |
| 소품 | `cup-empty` `cup-third` `cup-twothird` `cup-full`, `apple-whole`, `apple-bite-1~3`, `jug` | 9 |
| 카드·효과 | `card`, `card-s`, `tape`, `sweat`, `puff`, `dash`, `strip-w-short` `-mid` `-long` | 9 |
| 배경 | `bg-juicer`, `bg-diagram`, `bg-end` | 3 |

`bg-kitchen`, `bg-kitchen-cu`, `bg-office`, `bg-door-in`, `bg-bedroom-*`는 6판에 쓰지 않는다. `bg-kitchen`에는 사과 그릇과 컵이 그려져 있어 컵 크기가 어긋난 원인이었다.

### 승인 순서

세트 → 인물 차렷 → 자세·표정 → 소품 순으로 제작자가 정지 그림을 먼저 본다. 승인 뒤에만 컷을 합성한다(R-17 제안 7).

## 5. 소리

### 음악 큐 규칙

1. 음악은 **큐 시트에 있는 곳에만** 낸다. 깔아 두는 배경음악은 없다.
2. 큐는 다섯 가지뿐이고, 전부 테마 한 곡(8초)을 잘라 만든다.
3. **대사(목소리와 자막)가 나오는 동안에는 음악이 없다.** 큐는 대사 사이, 멈춤, 장소 전환에만 온다. 카드 멈춤이 시작되면 자막을 내린다.
4. 한 회의 음악 합은 길이의 20%를 넘지 않는다. 전환 큐는 한 회 4번까지다.
5. 큐마다 시작·끝·이유를 대본 컷 표에 적는다. 적히지 않은 음악은 넣지 않는다.
6. 웃음 박자는 무음과 효과음으로 만든다. 쪽지·반전 컷은 조용히 둔다.

| 큐 | 길이 | 내용 | 쓰는 곳 |
|---|---|---|---|
| `Q-OPEN` | 1.5초 | 테마 첫 동기. 제목 「모래언덕 빌라」가 y 220~290에 같이 뜬다 | 첫 소개 카드 멈춤 |
| `Q-UP` | 0.8초 | 테마 끝 두 마디, 올라가다 멈춘다(해결 안 함) | 장소 전환: 급히 가는 쪽 |
| `Q-DOWN` | 0.8초 | 같은 마디, 내려가다 멈춘다 | 장소 전환: 돌아오는 쪽 |
| `Q-TIME` | 1.2초 | 느린 두 음 | 시간 경과(「다음 날」) |
| `Q-END` | 2.5초 | 테마 끝맺음(해결) | 끝 화면 |

악기는 2판과 같다(우쿨렐레 스트럼, 베이스, 셰이커). `sfx.py` 합성을 그대로 쓰고 구간만 자른다.

### 효과음 규칙

- 화면에 원인이 보이는 소리만 낸다. 소품·동작 하나에 소리 하나다.
- 같은 순간에 둘까지다. 대사 목소리와 겹칠 때는 효과음을 6dB 낮춘다.
- 의성어 글자는 그 컷의 요점이 소리일 때만, 한 컷에 하나다.
- 이름은 `sfx.py`의 것을 쓴다: `띵동`, `탁`(카드), `위이잉`(착즙기), `쪼르륵`(따르기), `다다다`, `삐질`, `찍`(쪽지 떼기), `쿵`(상자), `뽀득`, `아삭`.
- 음량 목표는 2판과 같다(−16 LUFS, 최대 −2dBTP).

### 인물별 목소리 규칙 (Animalese 방식)

대사 글자를 음절별 짧은 소리로 빠르게 이어 붙인다. 참고는 PyAnimalese(https://github.com/hwi-middle/PyAnimalese)다. 음원과 코드의 라이선스는 Opus가 확인하고, 쓸 수 없으면 같은 방식으로 직접 합성한다.

**만드는 법**

- 자막 글자를 음절로 나눈다. 음절마다 초성·중성에 맞는 짧은 소리(60~90ms) 하나를 낸다. 받침은 무시한다.
- 숫자와 영문은 읽는 소리로 바꾼다(「2층」 → 이층).
- 뜻이 들리지 않아도 된다. 뜻은 자막이 전한다.

**인물별 값**

| 인물 | 음높이(기준 대비) | 속도(음절/초) | 느낌 |
|---|---|---|---|
| 곰 아빠 | −7반음 | 7 | 낮고 둥글다 |
| 판다 | +2반음 | 9 | 밝고 빠르다 |
| 펭귄 선생님 | −2반음 | 6 | 차분하고 고르다. 음높이 흔들림을 가장 적게 |
| 윙키 | +9반음 | 10 | 높고 가장 빠르다 |
| 거북 여사 | −4반음 | 5 | 가장 느리다 |
| 너구리 대리 | −1반음 | 8 | 끝이 흐려진다 |
| 고양이 사장 | +4반음 | 8 | 끝을 길게 끈다 |
| 다람쥐 코치 | +6반음 | 11 | 크고 짧게 끊는다 |
| 도치 실장 | +1반음 | 7 | 작고 조심스럽다 |

음절마다 ±1반음 안에서 흔든다(시드 고정). 같은 대사는 늘 같은 소리가 난다.

**문장 부호와 감정**

| 경우 | 변화 |
|---|---|
| 물음표 | 마지막 두 음절을 +3, +5반음으로 올린다 |
| 느낌표 | 마지막 음절 +2반음, 음량 +3dB |
| 말줄임표 「…」 | 0.3초 쉰다. 소리 없음 |
| 쉼표 | 0.15초 쉰다 |
| `놀람` | 전체 +2반음, 속도 1.2배 |
| `당황` | 음절 흔들림 ±3반음, 사이사이 짧게 끊긴다 |
| `시무룩` | 전체 −2반음, 속도 0.8배, 음량 −4dB |
| 속삭임(컷 표에 표시) | 음량 −8dB, 높은 소리 성분을 줄인다 |

**자막과 맞추기**

- 목소리는 자막이 뜨는 순간 시작한다. 자막은 목소리가 끝난 뒤에도 그 컷이 끝나거나 카드 멈춤이 시작될 때까지 남는다(읽는 속도 초당 5음절 기준).
- `CU`에서는 목소리가 나는 동안만 `말하기` 표정을 번갈아 낸다. `W`·`M`에서는 말하는 인물 조각이 까딱인다. 누가 말하는지 그림으로 보인다.
- 소개 카드 멈춤, 쪽지·카드에 적힌 글, 화면 밖 인물의 글에는 목소리를 내지 않는다.
- 목소리가 나는 동안 음악은 없다(음악 큐 규칙 3과 같은 말이다).
- 컷 표 대사 칸에 목소리 적용을 적는다: `목소리`, `목소리(속삭임)`, `없음`.

## 6. 글자 규칙

- 글꼴과 크기는 2판과 같다: 대사 68px, 의성어 110px(겹치면 88, 72), 카드 이름 92px·특징 60px, 근거·끝 화면 56px.
- 대사 자막은 한 줄 14자까지다. 넘으면 뜻이 끊기는 곳에서 두 줄로 나눈다. 세 줄은 대사를 줄인다.
- **칸 글자:** 그림 안의 칸에 들어가는 글자(시계 숫자, 상자 라벨, 쪽지, 명패, 층 숫자판, 소개 카드)는 손으로 크기를 정하지 않는다.
  - 조각마다 `textBox`(조각 안의 칸 좌표, 비율)를 `kit.json`에 적는다.
  - 글자 크기 = 둘 중 작은 값. 「칸 높이 × 0.7 ÷ 줄 수」와 「칸 폭 × 0.9 ÷ 가장 긴 줄의 글자 폭」.
  - 숫자는 폭이 같은 숫자 글꼴을 쓴다. 시계는 「88:88」 폭으로 계산해 어떤 시각이든 같은 크기다.
  - 렌더 뒤 글자 상자를 재서 칸 밖으로 1px이라도 나가면 실패다.
- 배경과 조각 그림에는 글자를 그리지 않는다. 글자는 전부 렌더에서 얹는다.
- 끝 화면 네 줄(담당 선생님, 의학 검수, 근거, 「AI로 만든 그림입니다」)은 모든 회차에 둔다.

## 7. 자동 검사

렌더 전에 돌리고, 하나라도 걸리면 렌더하지 않는다.

| # | 검사 | 기준 |
|---|---|---|
| 1 | 이름 | 컷 표의 세트·프리셋·자세·소품·큐·효과음 이름이 키트에 있다 |
| 2 | 크기 | 소품의 화면 높이 ÷ px/mm가 레지스트리 값 ±5%. 인물은 머리 폭 ±5% |
| 3 | 놓이는 곳 | 모든 조각이 바닥선·윗면·손 앵커·판 중 하나에 붙어 있다. 발끝 y 오차 4px |
| 4 | 자리 | 인물 x가 프리셋의 자리 값이다. `M`의 윙키는 의자 위다 |
| 5 | 겹침 | 인물끼리 폭의 15% 이하, 얼굴 상자 겹침 0. 소품이 남의 얼굴 상자에 닿지 않는다 |
| 6 | 확대 | 조각 1.3배, 배경 1.15배 이하. 가로세로 배율이 같다 |
| 7 | 글자 구역 | 자막·의성어·카드가 보호 상자와 겹치지 않고 안전 여백 안이다 |
| 8 | 칸 글자 | 칸 밖으로 나간 글자 0 |
| 9 | 호흡 | 한 컷에 대사 한 줄, 초당 5음절 이하, 자막 1.2초 이상 |
| 10 | 음악 | 음악 구간과 대사(목소리·자막) 구간이 겹치지 않는다. 합이 길이의 20% 이하. 큐 시트 밖 음악 0 |
| 11 | 표기 | 끝 화면에 검수·근거·AI 표시 문자열이 있다 |
| 12 | 컵 | 화면에 나온 컵 조각이 `cup-*`뿐이다 |

검사가 못 보는 것은 사람이 본다. 컷마다 정지 화면 한 장씩 모은 확인판을 만들어 제작자가 한 번에 본다. 볼 것은 배경에 소품·글자가 그려지지 않았는지, 손과 소품이 어색하지 않은지, 옷 색이 맞는지다.

## 8. 규모

| 항목 | 키트 전체 | 1화에 쓰는 것 |
|---|---|---|
| 세트 | 4곳 + 판 2종 | 3곳 + 판 2종 |
| 카메라 프리셋 | 세트마다 `W`·`M`·`CU`, 부엌에 `TOP` 하나 더 | 7개(부엌 4, 현관 1, 상담소 2) |
| 표정 | 6종 | 6종 |
| 자세 | 12종 | 8종 |
| 소품 | 8종 | 6종(컵, 사과, 주스 통, 상자, 쪽지, 의자)과 카드 |
| 음악 큐 | 5개 | 4번(`Q-OPEN`, `Q-UP`, `Q-DOWN`, `Q-END`) |
| 그림 | | 새로 28장, 있는 것 24장 |
