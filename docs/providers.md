# 계정·API별 설정

회사 안에서도 쓰는 계정이 다릅니다. Claude 구독, 회사 AWS의 Bedrock, Claude API 키, ChatGPT 구독, OpenAI API 키 가운데 가진 것에 맞춰 아래만 해 두면 됩니다. 설정은 한 번만 하면 됩니다.

## 한눈에 보기

| 가진 것 | 대본 | 영상 | 새 그림 | 설정 |
|---|---|---|---|---|
| Claude 구독(Pro·Max·Team) | O | O | Codex가 있으면 | 없음. 데스크톱 앱 Code 탭에 로그인 |
| AWS Bedrock(회사 계정) | O | O | Codex나 OpenAI API가 있으면 | 아래 「Bedrock」 |
| Claude API 키(Console) | O | O | Codex나 OpenAI API가 있으면 | 아래 「Claude API 키」 |
| ChatGPT 구독 | O(채팅에 붙여 넣기) | Codex에서 O | O(Codex 내장 그림) | 아래 「Codex」 |
| OpenAI API 키 | Codex에서 O | Codex에서 O | O(OpenAI Images API) | 아래 「OpenAI API 키」 |

영상 만들기는 Claude Code나 Codex 중 하나만 있으면 됩니다. 새 그림은 Codex(ChatGPT 구독) 또는 OpenAI API 키 중 하나가 있어야 합니다. 이미 있는 재료만 쓸 때는 필요 없습니다.

## Bedrock (Claude Code)

회사 AWS 계정으로 Claude를 쓰는 경우입니다. 먼저 `aws sso login`(또는 `aws configure`)으로 AWS에 로그인해 둡니다.

`~/.claude/settings.json`에 아래를 넣으면 데스크톱 앱 Code 탭과 터미널 Claude Code에 함께 적용됩니다. 파일이 없으면 새로 만듭니다.

```json
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_REGION": "ap-northeast-2",
    "AWS_PROFILE": "회사-프로필-이름",
    "ANTHROPIC_MODEL": "global.anthropic.claude-opus-5-5"
  }
}
```

- `AWS_REGION`과 모델 ID는 회사 Bedrock에서 열려 있는 것으로 바꿉니다. 모델 목록은 AWS 콘솔 Bedrock 「모델 액세스」에서 봅니다.
- Windows에서 파일 위치는 `%USERPROFILE%\.claude\settings.json`입니다.
- 기획 단계에 쓰는 가장 좋은 추론 모델이 Bedrock에 없으면 Opus로 합니다(`rules/models.md`).

## Claude API 키 (Claude Code)

Claude Console에서 받은 API 키로 쓰는 경우입니다. Claude Code를 처음 열 때 「Console 계정으로 로그인」을 고르면 됩니다. 키를 직접 넣으려면 `~/.claude/settings.json`에 이렇게 둡니다.

```json
{ "env": { "ANTHROPIC_API_KEY": "sk-ant-..." } }
```

키는 이 파일에만 두고 레포나 대화에 붙여 넣지 않습니다.

## Codex (ChatGPT 구독 또는 OpenAI API 키)

Codex CLI를 설치합니다.

```bash
npm install -g @openai/codex
codex login
```

- ChatGPT 구독이면 `codex login`에서 ChatGPT 계정으로 로그인합니다. 새 그림은 Codex 내장 그림 도구로 그립니다(기본 설정).
- OpenAI API 키만 있으면 `codex login --with-api-key`로 로그인합니다. 이 경우 내장 그림 도구가 없을 수 있으니, 새 그림은 아래 「OpenAI API 키로 그림 그리기」를 씁니다.
- Codex에서는 레포의 `skills/*/SKILL.md`를 스킬로 읽게 하면 됩니다(README 「빠른 설치」 글이 해 줍니다).

## OpenAI API 키로 그림 그리기

Codex 구독 없이 OpenAI API 키로 새 그림을 만들 수 있습니다. 결과는 같은 승인 절차를 거칩니다.

```bash
pip install openai
# macOS·Linux
export OPENAI_API_KEY=sk-...
export WINKY_IMAGE_BACKEND=openai
# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."; $env:WINKY_IMAGE_BACKEND="openai"
```

- 모델은 `WINKY_IMAGE_MODEL`로 바꿀 수 있습니다(기본 `gpt-image-1`). 계정에 열린 최신 그림 모델 이름을 넣으면 됩니다.
- API가 받는 크기(1024×1024, 1536×1024, 1024×1536)로 맞춰 그리고, 배경은 투명으로 받습니다. 등록할 때는 `--key none`을 씁니다. 크기는 엔진이 mm로 다시 맞추니 신경 쓰지 않아도 됩니다.
- API 사용료가 듭니다. 한 장에 여러 번 고쳐 그릴 수 있으니 회사 API 한도를 먼저 확인합니다.

## Suno (새 음악 큐를 만들 때만)

정식 음원은 Release 팩으로 받으니 대부분은 Suno가 없어도 됩니다. 새 음악 큐가 필요할 때만 아래가 필요합니다. 그 경우에도 새 테마는 만들지 않고 정식 테마를 기준으로만 만듭니다(`rules/music.md`).

Suno MCP는 가입과 구독만으로는 쓸 수 없습니다. 지금은 얼리 액세스라 세 단계가 필요합니다.

1. **Suno 유료 구독**(Pro 이상). 상업 이용 권리 때문에 위뉴 자산은 Pro 이상 계정으로 만듭니다.
2. **얼리 액세스 신청.** 구독자가 Suno에 MCP(API) 얼리 액세스를 따로 신청하고 승인을 받아야 합니다.
3. **MCP 수동 연결.** 승인된 뒤 Claude Code에 연결합니다.

```bash
claude mcp add --transport http --scope user suno https://api.suno.com/mcp
```

- 데스크톱 앱 Code 탭이라면 이 명령을 에이전트에게 실행해 달라고 하면 됩니다.
- 연결한 다음 대화 창에 `/mcp`를 입력하고 `suno`를 골라 **Authenticate**를 누릅니다. 브라우저에서 suno.com에 로그인하면 끝납니다.
- 연결은 **새 세션부터** 보입니다. 연결 후 앱이나 Claude Code를 한 번 다시 열어 주세요.
- 확인: 새 세션에서 「Suno 계정 사용량 확인해 줘」라고 하면 요금제와 남은 크레딧을 알려 줍니다.

얼리 액세스 승인 전이라면 정식 음원 관리자(위뉴 콘텐츠팀)에게 새 큐를 요청해 주세요.

## ChatGPT나 Claude 웹에서 대본만

설정이 필요 없습니다. [`skills/winky-script/SKILL.md`](../skills/winky-script/SKILL.md) 내용을 붙여 넣고 시작합니다.
