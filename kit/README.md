# kit/ — 공유 프리미티브 라이브러리

배우·소품·무대·음악을 **프리미티브**로 두고, 회차는 이것을 조합해 연출한다. 재료가 쌓이고 공유돼야 세계관이 유지·발전된다. 한 사람이 회차를 만들다 새 재료가 필요하면 만들어서(draft) 승인받아(approved) 여기 올리고, 다음 사람은 그걸 그대로 쓴다.

## 폴더

| 폴더 | 무엇 |
|---|---|
| `actors/<인물>/` | 인물 자세-표정 조각(`bear-상반신컵가득-웃음` → `bear-bustcupfull-smile.webp`), 손 조각(`bear-hand-flat`) |
| `props/` | 소품(컵 4단, 통, 사과, 기록장, 상자, 의자, 땀…) |
| `sets/<세트>/<W·M·CU·board>/` | 배경. `kitchen`·`office`·`door`·`table`(판)·`end`(끝 화면) |
| `ui/` | 종이 띠·이름표 카드·테이프·연필 줄 |
| `fx/` | 아이리스 전환 |
| `logo/` | 시리즈 로고(썸네일에만) |
| `music/` | 정식 음원 세트. **wav는 git에 없다**(아래) |
| `sfx/` | 효과음(합성, 설명만) |
| `fonts/` | 주아·도현·개구·Pretendard(OFL) |
| `gen/` | 생성 도구: `gen.py`(Codex Images 2.6), 프롬프트 조각, 기준 그림 2장. 생성 결과 `gen/out/`은 git에 없다 |

## registry.json (한 곳에 다 등록)

```jsonc
{
 "actors": { "bear": { "mm": {"h": 1800, "headW": 839}, "voice": {"semi": -7, "rate": 7}, "status": "approved" } },
 "sizes":  { "cup": {"h": 190, "w": 106}, "notebook-open": {"w": 300, "h": 210}, ... },   // 소품 실제 크기(mm, KIT-SPEC 1절)
 "items":  { "bear-상반신컵가득-웃음": {
      "kind": "actor", "actor": "bear", "file": "kit/actors/bear/bear-bustcupfull-smile.webp", "w": …, "h": …,
      "anchor": { "face": [...], "head": [...], "cx": …, "held": ["cup", …], "scale": "head" },   // 조각 px
      "family": "bear-상반신컵-평온", "status": "approved", "approved": "2026-11-11 ep01 9e판",
      "source": "...", "prompt": null, "ref": null } },
 "music":  { "theme-a": { "role": "theme", "file": "kit/music/theme-a.wav", "sha256": "...", "suno_clip": "...", "status": "approved" } },
 "sfx":    { "톡": { "source": "engine/sound.py SFX 합성", "status": "approved" } }
}
```

- 이름(열쇠)은 대본에 쓰는 이름 그대로(한글 자세·표정). 파일 이름은 ASCII.
- `status`: `draft`(생성됨, 아직 못 씀) → `approved`(사람이 승인 모음을 보고 승인). **engine은 approved만 쓴다.** draft를 쓰는 컷 표는 build에서 멈추고 check 16번에서 걸린다.
- 앵커 뜻: `cx` 몸 중심, `head` 머리 상자, `face` 이목구비(보호 상자), `torso` 몸통 x 범위, `hand` 소품 얹는 손, `held` 손에 그린 소품 상자, `paw`/`pawc`/`tip` 손 조각, `text` 칸 글자 상자(비율), `scale` 배율 기준(`h` 키, `head` 머리 폭). 자세한 것은 `rules/KIT-SPEC.md` 1·3·6절.
- 손으로 고치지 않는다. `python3 engine/register.py add|approve|music|sheet|list`.
- ep01 때 만든 프리미티브의 생성 프롬프트는 이전 제작 기록에만 있어 `prompt: null`이다. 새로 만드는 것부터 `prompt`·`ref`를 채운다.

## 음원 받기

정식 음원 wav 7개는 레포가 아니라 GitHub Release 「music-v1」의 `winky-music-v1.zip`에 있다. `engine/sound.py`가 처음 실행될 때 `engine/fetch_kit.py`로 받아 `kit/music/`에 둔다(직접 받으려면 `python engine/fetch_kit.py`). 레지스트리의 sha256으로 검증해서 다른 음원은 엔진이 거부한다. Suno 원본 clip id는 SOURCE.md에 있다. 새 음원이 승인되면 팩 버전을 올린다(music-v2).
