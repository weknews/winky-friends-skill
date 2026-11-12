# 숏폼 스토리·시트콤 대본 작법 조사 (Claude/LLM)

조사일: 2026-11-12. 태그: 【확인】 = 이번 조사에서 실제 열어 본 SKILL.md·README·페이지 본문, 【2차】 = 웹검색 요약 스니펫만 본 것(원문 미확인). Reddit 스레드는 검색에서 나오지 않아 찾지 못함(아래 "빈 곳" 참고).

## 1. 파이프라인·레포·스킬 표

| 이름 | URL | 별·설치수 | 자동화 범위 | 대본 단계 처리 | 라이선스 |
|---|---|---|---|---|---|
| jakeschincariol/youtube-agent-skill | https://github.com/jakeschincariol/youtube-agent-skill | 5,619★ 【확인】 | YouTube 채널 11개 스킬(대본·제목/썸네일·편집목록·이탈 구간 분석·Shorts 컷·바이럴) | `yt-script`: 훅 21개 공식 중 5개 작성 → `hookscore.py`로 점수화 → 상위 2개 제시 → 본문은 "턴(0:15–0:45)"·비트별 `[ON SCREEN: …]` 표기. 음성 프로필(`voice.md`) 없으면 영상 3편 요구. 숫자·결과 날조 금지 【확인】 | MIT 【확인】 |
| social-media-skills/skills (short-form-video-script 포함) | https://github.com/social-media-skills/skills | 298★ 【확인】; npx 설치 1.9K 【확인】 | 소셜 전략·글쓰기 106개 스킬 묶음 | `short-form-video-script`: WATCH 프레임(3초 훅·아크·음소거 트랙·약속 이행·루프). 시각/화면글자/대사 3트랙 비트 표 【확인】 | MIT 【확인】 |
| agricidaniel/claude-shorts | https://github.com/agricidaniel/claude-shorts | 377★ 【확인】; 설치 351 【확인】 | 롱폼→숏폼 편집(Remotion 자막, 구간 점수) | 대본 생성이 아니라 기존 영상 자르기 중심 【2차: 설명문 기준】 | MIT 【확인】 |
| melvynx/video-agent-skills | https://github.com/melvynx/video-agent-skills | 149★ 【확인】; studio-script 설치 1.4K 【확인】 | 숏폼 대본·리서치·편집, 마크다운만 | `studio-script` 본문은 이번에 못 읽음 【미확인】 | MIT 【확인】 |
| jtydhr88/screenwriting-skills | https://github.com/jtydhr88/screenwriting-skills | 2,042★ 【확인】 | 각본·시트콤·대사 작법 스킬 | **이미 이 레포에 `.claude/skills`로 설치됨**(sw-dialogue, sw-sitcom-comedy, sw-workflow) 【확인: 프로젝트 git log d5c4695】 | MIT 【확인】 |
| diamond-one/hybrid-AI-animated-shorts-pipeline | https://github.com/diamond-one/hybrid-AI-animated-shorts-pipeline | 0★, 라이선스 없음 【확인】 | 애니 단편 제작 문서(에셋·모션캡처·조명·편집) | 대본은 "범위 밖"이라고 명시 【확인】 → 쓸모 없음 | 없음 |
| outscal/video-generator (shorts-script-personality) | https://github.com/outscal/video-generator | 69★ 【확인】; 325 설치 【확인】 | AI 영상 생성 | 대본 스킬 본문 미확인 【미확인】 | 라이선스 없음 【확인】 |
| samuraigpt/generative-media-skills | https://github.com/samuraigpt/generative-media-skills | 38★ 【확인】; 2.8K 설치(shorts) 【확인】 | 이미지·영상·음성 생성(muapi.ai 기반) | 생성 도구 래퍼. 대본 작법 없음 【2차】 | MIT 【확인】 |
| social-media-skills/remotion-shorts-skill, neosapience/create-typecast-shorts, anil-matcha/youtube-shorts-generator 등 | skills.sh 목록 | 31~63 설치 【확인】 | 쇼츠 생성 | 본문 미확인 | 미확인 |
| mirage-hq/tesseract-video | skills.sh | 4.3K 설치 【확인】 | 영상 | 본문 미확인 | 미확인 |
| zenstory-ai/video-recap-skills@video-script | skills.sh | 57 설치 【확인】 | 영상 리캡 대본 | 본문 미확인 | 미확인 |
| agentara/skills@video-storyboard | skills.sh | 965 설치 【확인】 | 스토리보드 | 본문 미확인 | 미확인 |
| melvynx `studio-script` | skills.sh | 1.4K 설치 【확인】 | 스튜디오형 대본 | 본문 미확인 | 미확인 |

`npx skills find` 결과 자체는 【확인】(검색 명령 출력). 이번에 `gh search repos`로 나온 "시트콤·숏폼 AI 대본" 전용 레포는 거의 없었다(검색 결과 1~2개, 대부분 문서 전용).

## 2. 대본 작법 기법 (사람들이 쓴다고 보고된 것)

출처 등급을 표기. 번호는 근거 원문에 따른 것.

1. **훅을 여러 개 쓰고 점수로 고른다.** yt-script는 훅 5개 → 점수화 → 상위 2개를 보여 주고, "하나만 주지 않는다" 【확인: jakeschincariol/youtube-agent-skill yt-script/SKILL.md】.
2. **첫 15초 = 약속 확인 + 열린 질문 + 보상 예고.** 채널 소개·구독 요청을 빼라(0:30 이탈의 가장 흔한 원인으로 꼽음) 【확인: 같은 파일】.
3. **비트마다 "화면에 무엇이 있는지"를 적는다.** 말만 있으면 팟캐스트가 된다 【확인: 같은 파일】.
4. **음소거 버전을 먼저 쓴다.** "약 80%가 무음으로 본다"는 주장과 함께, 화면 글자만으로 줄거리가 서는지 먼저 확인 【확인: short-form-video-script SKILL.md. 단, 통계는 스킬이 인용한 2차 수치】.
5. **루프 엔딩.** 끝이 첫 장면으로 이어지도록 설계 【확인: 같은 파일】.
6. **약속한 것을 정확히 이행(미끼-후 교체 금지).** 【확인: 같은 파일】.
7. **패턴이 아니라 "자기 목소리 파일"을 먼저.** 음성 프로필을 만들고 그 뒤에 씀. 목소리가 틀리면 대본 자체가 틀린 것 【확인: yt-script】.
8. **출력 전 소리 내 읽기 기준.** 150단어/분으로 길이 추정 【확인: yt-script】.
9. **대량 생성 후 선별.** 농담은 양이 많아야 몇 개가 나온다는 주장 【2차: promptoptimizer.tools 스니펫, 원문 미확인】.
10. **셋업 확장 원칙.** 농담 설정을 장면마다 "같거나 더 세게" 확장하고 한 단계 물러나지 않는다 【2차: 같은 스니펫】.
11. **3분 이상 굴릴 수 있는 전제인지 테스트.** 【2차: 같은 스니펫】.
12. **시험용 낭독.** 원고를 소리 내 읽고 리듬이 맞는지 확인 【2차 & 확인: 조사 중 본 여러 글 공통】.
13. **대사 교환(톤 샘플 기법).** 아래 3번 참고.
14. **시트콤 형식:** 콜드오프·액트·태그 구조를 명시하면 모델이 형식을 따른다는 튜토리얼 주장 【2차: vidmuse/dtptips 등 튜토리얼 스니펫】.
15. **대사 길이 제한.** "약 5초 분량 대사, 짧은 대사" 프롬프트 규칙을 매 에피소드 고정 【2차: tutorialsdojo 스니펫】.
16. **사람 편집이 최종 30%.** "ChatGPT가 70%, 나머지 30%는 편집" 【2차: 블로그 스니펫】.

## 3. AI 티가 나는 대사·농담을 덜 AI답게 하는 방법

- **톤 샘플 제시.** 원하는 문체의 글을 샘플로 주고 그 목소리로 쓰게 한다. 다만 이 기법은 "조금 나아짐" 수준이라는 보고 【확인: Daniel Nest, "5 Ways to Help AI Chatbots Not Sound Like AI Chatbots", 2024-05-02 — WebFetch로 본문 확인】.
- **인물 페르소나 부여.** 전문성이 아니라 "말투가 있는 사람"으로 지정. 같은 글에서 Homer Simpson 예시를 씀 【확인: 같은 글】.
- **여러 문체 중 고르기.** 5가지 문체로 쓰게 한 뒤 하나를 골라 이어 쓰게 함 【확인: 같은 글】.
- **완벽한 문법·균형 잡힌 문장 깨기.** AI 대사는 문법이 너무 깔끔하고 문장 균형이 좋아 딱딱하다. 끊기·말 흐리기·단편 문장 허용 【2차: 검색 스니펫, 원문 미확인】.
- **리듬을 의도적으로 섞기.** 짧은 치기 대사 뒤에 긴 우회 문장 【2차】.
- **군더더기 상투구 제거.** "Furthermore", "It is worth noting" 같은 전환어 【2차: 프리랜서 구인 글 스니펫】.
- **여러 목소리로 주고받기.** TTS 여러 명을 쓰면 대화가 살아난다는 주장. 단 중간에 목소리를 바꾸면 한 사람이 낭독한 것처럼 들림 【2차】.
- **갈등·서브텍스트·짧은 대사.** 같은 주장 【2차: 대화 소설 가이드 스니펫】.
- **방언·사투리는 가볍게.** 과하면 캐리커처 【2차】.

**중요한 빈 곳:** 조사 범위 안에서 "AI로 쓴 유머 대사가 덜 웃긴 이유"를 근거와 함께 분석한 글은 찾지 못했다. 검색 결과 대부분은 "AI 티 없애기" 일반 가이드였다. 따라서 이 항목은 전부 2차 또는 일반론이다. 우리 프로젝트의 sw-dialogue·sw-sitcom-comedy 스킬(jtydhr88 레포, 이미 설치됨)이 가장 가까운 직접 자료다 【확인: 프로젝트 스킬 목록】.

## 4. 우리(윙키 프렌즈, 1분 세로 시트콤)에 대한 추천 3가지

1. **대사 전에 "말투 샘플"을 우리 캐릭터별로 만든다 — 근거: Nest의 톤 샘플·페르소나 기법 【확인】, yt-script의 voice.md 개념 【확인】.** 윙키·너구리·도치 각자 짧은 실제 대화 샘플 10줄씩을 사람이 쓰고, 모델에게 그 샘플을 주고 쓰게 한다. 이미 `characters.md`(인물 바이블)가 있으니 그 안에 "말버릇·금지어·웃음 유형"을 넣는 식으로 붙이면 된다. 우리 의도(가스 없는 가벼운 말소리+자막)에 맞게, 대사는 말소리가 아니라 자막 길이 제한을 같이 둔다.
2. **훅 여러 개 → 점수 → 고르기, 그리고 비트마다 화면 설명을 붙인다 — 근거: yt-script의 "5개 작성·상위 2개" 규칙과 `[ON SCREEN]` 비트 표기 【확인】, short-form-video-script의 "음소거 버전 먼저" 【확인】.** 우리 시트콤은 말소리가 아니라 자막이 주 전달 수단이므로, 대본 단계에서 "자막만 읽어도 웃음 구조가 서는지"를 체크 항목으로 넣는다.
3. **AI 초안은 "농담 설정 → 펀치 후보 여러 개 → 사람이 소리 내 읽고 고르기" 순서로, 설정을 장면마다 확장하는지 검사 — 근거: 프롬프트 스니펫의 volume·확장 원칙 【2차】, 그리고 프로젝트에 이미 있는 sw-sitcom-comedy/sw-dialogue 스킬 【확인】.** 새 스킬을 설치하기보다 이미 설치된 jtydhr88 스킬의 점검 기준(웃음 설계표·서브텍스트)을 쓰는 편이 낫다. 설치된 스킬을 우선하라는 제안이며, 외부 스킬 추가는 하지 않았다.

**한계:** Reddit(r/ClaudeAI·r/NewTubers·r/aivideo) 스레드는 검색에서 찾지 못했다. 웹 검색의 "reddit" 질의도 블로그·광고 페이지만 반환. 출처 대부분이 블로그·구인 광고·튜토리얼이다. 우리 같은 "애니 시트콤 단편" 실사례 중 웃음 품질이 검증된 것은 찾지 못했다.
