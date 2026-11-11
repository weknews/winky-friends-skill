# 소리 규칙과 정식 음원 세트

## 1. 정식 음원 세트 (고정)

세계관의 소리 결이 같아야 한다. **모든 회차는 `kit/registry.json` `music`에 승인(approved)된 음원만 쓴다.** 엔진(`engine/sound.py`)은 파일의 sha256이 레지스트리와 다르면 멈춘다.

| 이름 | 역할 | 쓰는 곳 |
|---|---|---|
| `theme-a` | theme | 오프닝 앞 소절(썸네일과 함께), 끝 화면 끝맺음(원본 27.0~29.5초) |
| `bed-bright` | bed | 집·부엌 같은 밝은 장면의 배경 |
| `bed-awkward` | bed | 상담소 같은 어색한 긴장 장면의 배경(앞 3초 여린 도입부는 건너뛴다) |
| `stings-1` | stings | 이음새 묶음. Q-TIME(15.5~16.7, 「다음 날」), Q-DOWN(13.9~14.7, 돌아옴) |
| `sting-babam` · `sting-boing` · `sting-wahwah` | sting | 반전 얼굴(babam), 핑계 직후(boing), 판정 직후(wahwah) |

출처·Suno clip id는 `kit/music/SOURCE.md`와 레지스트리에 있다(Suno Pro, 상업 이용 가능 요금제).

## 2. 새 음원은 아무나 만들지 않는다

- 새 테마를 만들지 않는다. 시리즈 테마는 `theme-a` 하나다.
- 정식 세트로 안 되는 장면(새 무대의 배경 등)만 새 음원을 만든다. 순서:
  1. 이슈나 PR 설명에 「왜 정식 세트로 안 되나」를 적는다.
  2. Suno에서 **`theme-a`를 reference(커버·확장·스템)로** 만든다. 악기·조·빠르기를 테마에 맞춘다. 가사 없는 기악.
  3. `python3 engine/register.py music 이름 파일.wav --role bed --clip <Suno clip id>` → draft 등록(sha256 기록).
  4. `kit/music/SOURCE.md`에 한 줄 추가. PR에서 사람 귀로 듣고 승인자가 `register.py approve 이름 --by 이름`.
- 정식 음원을 바꾸거나 다시 만들지 않는다. 길이·자리는 회차 `sound_cues.py`에서 잘라 쓴다.

## 3. 숏폼 소리 원칙 (11/11, KIT-SPEC 5절 1~4 「대사 컷엔 음악 없음」을 대체)

- 장면 분위기마다 배경음악(bed)을 계속 깐다. 대사 중에는 덕킹(대사 첫 음절 0.08초 앞 ~ 끝 0.15초 뒤, −8dB, 0.15초 이동 평균).
- 반전 직전에 음악을 **뚝 끊고(30ms)** 정적, 펀치라인 직후 스팅. 웃음 자리는 무음·효과음으로 만든다.
- 장소·시간 전환은 이음새 큐(Q-TIME, Q-DOWN)와 「다음 날」·「그날 저녁」 글자가 같이 온다.
- 전환 큐(Q-OPEN·Q-UP·Q-DOWN·Q-TIME·Q-END)는 대사와 겹치지 않고 합이 길이의 20% 이하(check 10번). 큐 시트(`episode.py` `CUE_SHEET`) 밖의 큐는 없다.
- 섞기: 전체 −15 LUFS(−14~−16), 최대 −1.5 dBTP 이하. 배경음악은 목소리 통합 음량 −6 LU, 스팅 −2 LU, 효과음 최댓값은 목소리 최댓값 −4dB. 목소리는 2:1 가벼운 압축 + 앞보기 피크 리미터.
- 썸네일 0.4초가 맨 앞에 붙고 그동안 theme-a가 먼저 시작한다(장면 시각 t = 완성 파일 t + 0.4).

## 4. 효과음·목소리

- 효과음은 `engine/sound.py` 합성(레지스트리 `sfx`에 등록된 이름만, check 1번). 화면에 원인이 보이는 소리만, 소품·동작 하나에 소리 하나, 같은 순간 둘까지, 대사와 겹치면 −6dB.
- 새 효과음은 sound.py `SFX`에 합성 함수를 더하고 레지스트리 `sfx`에 등록한다.
- 목소리는 Animalese 방식: 자막 음절마다 초성 소리(PyAnimalese 녹음, MIT). 인물별 반음·빠르기는 레지스트리 `actors.*.voice`.
