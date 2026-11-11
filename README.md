<div align="center">

<img src="kit/logo/logo-main.png" alt="윙키와 친구들 · 모래언덕 빌라" width="420" />

**당뇨 오해를 50초 시트콤으로 바로잡는 숏폼 제작 스킬**

Claude Code · Codex 플러그인

</div>

---

<table><tr>
<td width="38%"><img src="docs/thumb-ep01.jpg" alt="샘플 회차 썸네일: 과일주스는 건강식이니까 괜찮다?" /></td>
<td valign="top">

### 이런 영상을 만듭니다

모래언덕 빌라에 사는 윙키와 이웃들이 매 회 작은 소동을 벌입니다. 소동은 늘 당뇨 환자가 실제로 하는 오해에서 시작하고, 끝에서 대한당뇨병학회 진료지침 한 줄로 바로잡힙니다.

샘플 회차 **「과일주스는 건강식이니까 괜찮다?」**
곰 아빠는 「과일인데 뭐~」 하며 사과주스를 세 잔 마십니다. 다음 날 상담소에서 윙키가 편들어 준다는 게 그만 실토가 되고, 곰 아빠는 결국 주스 대신 사과를 집어 듭니다.

- 세로 1080×1920, 50초 안팎
- 내용은 진료지침 범위 안에서만 쓰고 의료진 검수를 거칩니다
- 회차 번호는 쓰지 않습니다. 환자마다 받는 순서가 달라서입니다
- 샘플 회차는 의료진 검수 전 시안입니다

</td>
</tr></table>

> **교육용 콘텐츠 제작 도구입니다. 진료를 대신하지 않습니다.** 만든 영상은 게시 전에 반드시 의료진 검수를 받아야 합니다. 샘플 ep01도 의료진 검수 전 시안입니다.

## 어떻게 다른가

카드뉴스는 「우리가 알려 줄 정보」에서 출발했습니다. 이 스킬은 **「환자가 실제로 하는 오해」에서 출발합니다.** 공급자의 설명을 소비자의 일상으로 바꾼 것이 핵심입니다.

만드는 방식은 시트콤 촬영과 같습니다. 배우, 소품, 무대, 음악을 **재료(프리미티브)** 로 정해 두고, 회차는 그 재료를 조합해 연출합니다. 없는 재료만 새로 만들고, 사람이 승인하면 모두가 다시 씁니다. 회차가 쌓일수록 재료도 쌓이고, 누가 만들어도 같은 그림체와 같은 소리가 납니다.

## 어디서 쓰나요

개발자가 아니어도 됩니다. 가장 쉬운 곳은 **Claude 데스크톱 앱의 Code 탭**입니다. 터미널을 열 필요가 없습니다.

| 어디서 | 할 수 있는 것 | 이런 분께 |
|---|---|---|
| **Claude 데스크톱 앱 → Code 탭** (Mac·Windows) | 대본부터 영상까지 전부 | 대부분의 분께 권합니다 |
| Claude Code(터미널), Codex | 대본부터 영상까지 전부 | 터미널이 익숙한 분 |
| Claude 데스크톱·웹의 일반 채팅, ChatGPT | 대본까지 | 기획만 하실 분 |

**데스크톱 앱에서 시작하는 법**

1. [Claude 데스크톱 앱](https://claude.ai/download)을 설치하고 로그인합니다.
2. 왼쪽 위에서 **Code** 탭을 고릅니다. 작업할 폴더를 하나 고르라고 하면 문서 폴더처럼 아무 폴더나 고르면 됩니다.
3. 아래 「빠른 설치」의 글을 그대로 붙여 넣습니다. 필요한 프로그램(Node, ffmpeg, Python)이 없으면 에이전트가 무엇을 설치할지 먼저 물어봅니다. 허락하면 알아서 설치합니다.
4. 설치가 끝나면 「Quick Start」의 문장으로 바로 시작합니다.

중간에 에이전트가 명령을 실행해도 되는지 물으면 내용을 읽어 보고 허락하면 됩니다. 영상이 다 만들어지면 파일 위치를 알려 줍니다.

**Bedrock, Claude API 키, ChatGPT, OpenAI API 키를 쓰신다면** [`docs/providers.md`](docs/providers.md)를 먼저 봐 주세요. 가진 계정에 맞춰 한 번만 설정하면 됩니다.

**일반 채팅이나 ChatGPT에서 대본만 쓰려면** [`skills/winky-script/SKILL.md`](skills/winky-script/SKILL.md) 내용을 붙여 넣고 「「꿀은 설탕이 아니니까 괜찮다」는 오해로 윙키와 친구들 대본 써 줘」라고 보내면 됩니다. 만든 대본은 Code 탭을 쓰는 분께 넘기면 영상으로 만들 수 있습니다.

## 빠른 설치

Claude 데스크톱 앱의 Code 탭(또는 Claude Code, Codex)에 아래 글을 그대로 붙여 넣으면 설치와 점검이 끝납니다.

```text
weknews/winky-friends-skill 스킬을 설치해 줘.
1. 내 OS(macOS, Windows, Linux)를 먼저 확인하고, 설치 명령은 README 「준비물」의 그 OS 명령을 써 줘. Windows는 PowerShell 기준, Python은 python3 대신 py.
2. 레포(https://github.com/weknews/winky-friends-skill)를 내가 고른 폴더에 클론해 줘. 이미 있으면 git pull.
3. Claude Code라면 /plugin marketplace add weknews/winky-friends-skill 과 /plugin install winky-friends@winky-friends-skill 로 플러그인을 설치해 줘. Codex라면 레포의 skills/*/SKILL.md 를 스킬로 읽게 설정해 줘.
4. 준비물을 확인하고 없는 것만 알려 줘(설치 전 나에게 물어볼 것): Node 22+, ffmpeg, Python 3(numpy, Pillow), Codex 구독(새 그림용, 없어도 됨), Suno MCP 연결(새 음악 큐용, 없어도 됨).
5. episodes/ep01-fruit-juice 폴더에서 engine/build.py 와 engine/check.py 를 차례로 돌려서 통과하는지 확인하고, 결과를 짧게 알려 줘.
6. 마지막에 「대본만 쓸 때는 winky-script, 영상까지 만들 때는 winky-episode」 사용법을 세 줄로 알려 줘.
```

직접 설치하려면 이렇게 합니다.

```
/plugin marketplace add weknews/winky-friends-skill
/plugin install winky-friends@winky-friends-skill
```

정식 음원은 레포가 아니라 GitHub Release에 있습니다. 처음 영상을 만들 때 자동으로 받으니 따로 할 일은 없습니다.

## Quick Start

설치가 끝나면 같은 Code 탭(또는 Claude Code, Codex) 대화에서 바로 시작합니다. 레포 폴더에서 세션을 여는 것이 가장 편합니다.

**1. 대본 쓰기**

```text
/winky-script 「꿀은 설탕이 아니니까 괜찮다」는 오해로 윙키와 친구들 대본 써 줘
```

주제가 아직 없으면 `/winky-script 오해 주제 후보 보여 줘`로 시작합니다. ChatGPT나 Claude 웹에서는 `skills/winky-script/SKILL.md`를 붙여 넣은 뒤 같은 문장을 보냅니다(슬래시 없이).

**2. 영상 만들기**

```text
/winky-episode 방금 대본으로 영상 만들어 줘
```

새 그림이 필요한 대본이면 에이전트가 승인 모음을 먼저 보여 주고 기다립니다. 승인해야 다음 단계로 넘어갑니다.

**연습:** 샘플 회차를 다시 만들어 보면 흐름을 익히기 좋습니다.

```text
/winky-episode episodes/ep01-fruit-juice 를 다시 렌더해 줘
```

Claude Code에서 다른 플러그인과 스킬 이름이 겹치면 `/winky-friends:winky-script`처럼 플러그인 이름을 붙여 부릅니다. Codex에서는 슬래시 명령 대신 문장 앞에 「winky-script 스킬로」라고 적습니다.

**결과 위치**

| 무엇 | 어디 |
|---|---|
| 대본 | `episodes/<회차>/script.md` (대본만 쓸 때는 대화 창에 마크다운으로) |
| 영상 | `episodes/<회차>/out/<회차>.mp4` |
| 썸네일 | `episodes/<회차>/out/thumb.png` |
| 승인 모음(새 그림) | `review/drafts.jpg` |

결과 영상과 `out/`은 git에 올리지 않습니다. 다 만든 뒤에는 아래 「사람이 꼭 할 일」 네 가지가 남습니다. 대사 소리 내 읽기, 그림 승인, 의료진 검수, 소리 듣기입니다.

## 스킬 셋

| 스킬 | 어디서 쓰나 | 하는 일 |
|---|---|---|
| `winky-script` | 어디서나. ChatGPT나 Claude 웹에는 `SKILL.md`와 `references/`를 붙여 넣으면 됩니다 | 오해 고르기 → 대본·컷 표 → 지침 대조 → 대사·화면 문구 점검 → 낙인 점검 → 썸네일 훅 |
| `winky-episode` | Claude Code, Codex | 컷 표를 받아 합성 → 자동 검사 → 소리 → 썸네일 → 렌더 |
| `winky-assets` | Claude Code, Codex | 새 자세·소품·세트를 만들고, 크기를 맞추고, 승인 모음을 만듭니다 |

기획하는 분은 대본까지만, 제작하는 분은 영상까지 만들면 됩니다. 시트콤의 재미를 가르는 건 결국 대본입니다.

## 한 회 만드는 순서

1. **대본** (`winky-script`): 오해 하나를 골라 대본과 컷 표를 씁니다.
2. **검토**: 다른 회사 모델(ChatGPT, Codex)에게 이야기의 인과, 재미, 교육 메시지를 따로 물어봅니다. 1화는 이 단계를 다섯 번 거쳤습니다.
3. **사람**: 대사를 소리 내 읽습니다. 번역투는 여기서 걸러집니다.
4. **재료** (`winky-assets`): 대본에 새로 필요한 것만 만들고, 사람이 승인 모음을 보고 승인합니다.
5. **제작** (`winky-episode`): 합성하고 자동 검사(16항목)를 통과하면 소리를 섞고 렌더합니다.
6. **사람**: 영상을 보고 소리를 듣습니다. 의료진 검수를 받고 검수자 이름(○○○)을 채운 뒤 게시합니다.

어느 단계에 어떤 모델을 쓰는지는 [`rules/models.md`](rules/models.md)에 있습니다. 기획은 가장 좋은 추론 모델 하나가 맡고, 제작 모델은 기획서대로만 만듭니다.

## 사람이 꼭 할 일

에이전트가 대신할 수 없는 일이 네 가지 있습니다.

- **대사를 소리 내 읽기.** 모델이 고른 말은 문법은 맞아도 사람이 실제로 하는 말이 아닐 때가 많습니다.
- **그림 승인.** 새 재료는 사람이 승인해야 다음 사람이 씁니다. 에이전트는 스스로 승인하지 않습니다.
- **의료진 검수.** 지침 대조표의 「지침 밖」 줄과 검수 질문에 답을 받기 전에는 게시하지 않습니다.
- **소리 듣기.** 모델은 음량 수치만 맞출 뿐 듣지는 못합니다.

## 준비물

| 무엇 | 언제 필요한가 |
|---|---|
| Node 22 이상, ffmpeg, Python 3(numpy, Pillow) | 영상을 만들 때 |
| PyAnimalese(MIT) | 인물 목소리. `git clone https://github.com/hwi-middle/PyAnimalese tools/PyAnimalese` |
| Codex 구독(Images 2.6) | 새 그림을 만들 때만 |
| Suno(상업 이용이 되는 Pro 이상 요금제)와 MCP 연결 | 새 음악 큐를 만들 때만. 정식 테마를 기준으로만 만듭니다 |

### OS별 설치

대본만 쓸 때는 설치할 것이 없습니다. 영상을 만들 때 아래를 한 번 설치합니다.

macOS (Homebrew)

```bash
brew install node ffmpeg python numpy pillow
```

Windows (PowerShell)

```powershell
winget install -e --id Git.Git
winget install -e --id OpenJS.NodeJS.LTS
winget install -e --id Python.Python.3.12
winget install -e --id Gyan.FFmpeg
```

설치가 끝나면 PowerShell 창을 새로 열고 아래를 실행합니다. Windows에서는 명령의 `python3`를 `py`로 바꿔 씁니다.

```powershell
py -m pip install numpy pillow
```

PowerShell에서 npm이 「스크립트를 실행할 수 없습니다」라며 멈추면 `npm` 대신 `npm.cmd`로 실행합니다.

Linux (Ubuntu·Debian, apt)

```bash
sudo apt install -y git ffmpeg python3 python3-numpy python3-pil
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs
```

Fedora는 `sudo dnf install -y git nodejs ffmpeg python3-numpy python3-pillow` 한 줄입니다(ffmpeg는 RPM Fusion을 켠 상태에서).

어느 OS든 그다음은 같습니다. 레포 뿌리에서 `cd engine`, `npm install`을 하고, 위 표의 PyAnimalese를 클론합니다. 렌더용 크롬은 처음 쓸 때 자동으로 받습니다.

**Codex가 없으면** 승인된 재료만으로 만듭니다. 코드로 그린 대체 그림은 그림체가 깨져서 쓰지 않습니다.
**Suno가 없으면** 레포에 있는 정식 음원을 그대로 씁니다.

## 폴더

```
skills/      스킬 셋
kit/         공유 재료(배우·소품·무대·로고·글꼴·음악)와 registry.json
engine/      회차와 상관없는 공통 제작 코드
rules/       세계관, 제작 사양, 지침 관문, 문구 점검, 낙인, 음악, 모델 분업
episodes/    회차별 대본·컷 표·소리 큐·썸네일
```

올리지 않은 것도 있습니다. 그림 생성 원본과 회차 결과 영상은 크기 때문에 뺐습니다(필요하면 위뉴 콘텐츠팀에 요청). 진료지침 PDF 원문은 판매 자료라 어디에도 올리지 않습니다.

## 기여

새 재료를 만들었다면 `feature/assets-*` 브랜치에서 승인 모음과 함께 PR을 올려 주세요. 자세한 순서는 [`CONTRIBUTING.md`](CONTRIBUTING.md)에 있습니다.

## 라이선스

코드와 위뉴 자산의 라이선스가 다릅니다.

| 무엇 | 라이선스 |
|---|---|
| 코드·스킬·규칙: `engine/`(`engine/lib` 제외), `skills/`, `rules/`, `kit/gen/`의 스크립트·프롬프트, `kit/logo/`의 스크립트, `kit/registry.json`, `episodes/`의 코드와 문서 | MIT ([`LICENSE`](LICENSE)), Copyright 위뉴(Weknew) |
| 위뉴 자산: `kit/`의 인물·세트·소품·UI·전환 그림, `kit/gen/refs/` 기준 그림, `kit/logo/` 로고 그림, `kit/music/` 음원, `docs/` 썸네일 | CC BY-NC-ND 4.0 ([`LICENSE-ASSETS.md`](LICENSE-ASSETS.md)) |
| 「윙키」 「윙키와 친구들」 「모래언덕 빌라」 「위뉴 건강상담소」 이름과 인물 | 위뉴 상표. 라이선스로 주지 않습니다([`LICENSE-ASSETS.md`](LICENSE-ASSETS.md)) |
| 글꼴 `kit/fonts/`(주아·도현·개구·Pretendard) | SIL OFL 1.1 |
| `engine/lib/` GSAP | GreenSock 표준 라이선스 |
| PyAnimalese 녹음(클론해서 씀), lemo-opuscar에서 옮긴 효과음 식 | MIT |

서드파티 자원은 [`NOTICE.md`](NOTICE.md)에 정리했습니다. 위뉴 구성원과 위뉴가 허락한 사람은 위뉴 자산을 고치거나 상업적으로 쓸 수 있습니다. 엔진과 스킬로 자기 인물과 그림을 넣어 새 시리즈를 만드는 것은 MIT 범위라 자유입니다.
