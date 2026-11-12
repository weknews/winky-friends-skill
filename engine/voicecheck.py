"""대사 말투 자동 검사 (rules/wording.md 4절 1단계). 대본·인물 문서 md에서 「」 안 대사와 `> **인물** 대사` 줄을 뽑아 AI 티 패턴을 찾는다.
  python3 engine/voicecheck.py <파일.md> [...]
기계가 잡는 건 일부다(경구체·비유·설명 대사는 못 잡는다). 통과해도 사람이 소리 내 읽는다.
"""
import re, sys

TELLS = [  # (이름, 패턴) — rules/wording.md 1·2절
    ("대명사", r"(그녀|당신|그것은|그것이|그것을|이것은)"),
    ("번역투 「때문에」", r"기 때문에|때문에"),
    ("번역투 「에 대해」", r"에 대해|에 대하여"),
    ("번역투 「를 통해」", r"[을를] 통해"),
    ("번역투 「에 의해」", r"에 의해"),
    ("번역투 「에 있어서」", r"에 있어서"),
    ("번역투 「하게 되다」", r"하게 되(었|었다|다|ㄴ다)|하게 됐"),
    ("번역투 「가지고 있다」", r"가지고 있"),
    ("「~것이다」", r"것이다|것입니다"),
    ("대칭 「A가 아니라 B」", r"[가이]? ?아니라 .+(다|야|예요|이다)"),
    ("결산어", r"결론적으로|중요한 (건|것은)|핵심은|요컨대"),
    ("과한 맞장구", r"(그랬군요|힘드셨겠네요|좋은 질문|충분히 이해)"),
    ("과공손 요청", r"(주시기 바랍니다|부탁드립니다)"),
]

def lines_of(text):
    out = re.findall(r"「([^」]+)」", text)
    out += [m.group(1) for m in re.finditer(r"^\s*>\s*\*\*.+?\*\*\s*(.+)$", text, re.M)]
    return out

def check(lines):
    hits = []
    for l in lines:
        for name, pat in TELLS:
            if re.search(pat, l): hits.append((name, l))
    return hits

# 자체 시험: 잡아야 할 것과 잡으면 안 되는 것
assert check(["그것은 제가 해결하겠습니다."]) and check(["비가 왔기 때문에 취소되었습니다."])
assert check(["이건 실패가 아니라 과정이다."]) and check(["확인하신 후 회신 부탁드립니다."])
assert not check(["바로 옆에 있어~"]) and check(["건강에 있어서 중요"])
assert not check(["알았어 알았어."]) and not check(["근데 뭐래?"]) and not check(["거기 문 닫았던데?"])

if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        hits = check(lines_of(open(f, encoding="utf-8").read()))
        for name, l in hits: print(f"{f}: [{name}] {l}")
        bad += len(hits)
    print(f"걸린 줄 {bad}. 기계 검사는 일부뿐이다. 이름 가리고 읽기·소리 내 읽기를 이어서 한다(rules/wording.md 4절).")
