# 효과음

효과음은 파일이 아니라 `engine/sound.py`의 `SFX` 합성 함수다(numpy, 시드 고정이라 늘 같은 소리). 등록 이름은 `kit/registry.json` `sfx`.

띵동 · 탁 · 쿵 · 꿀꺽 · 쪼르륵 · 띠로리 · 뿅 · 삐질 · 아삭 · 톡 · 스윽 · 사각(그 컷에서 쓰는 글자 수만큼 긁는다)

새 효과음: sound.py `SFX`에 합성 함수를 더하고 → registry `sfx`에 이름을 넣고(status approved는 PR 리뷰 뒤) → 회차 컷 표의 `sfx`에서 쓴다. 띠로리·뿅은 lemo-opuscar(MIT) 함수를 옮겼다(NOTICE.md).
