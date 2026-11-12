"""진짜 대화 예문 꺼내기. 대사를 쓰기 전에 장면에 맞는 실제 한국어 대화를 몇 개 뽑아 옆에 둔다.
  python3 engine/realtalk.py 아빠 병원 -n 5        # 낱말이 모두 든 대화 5개
  python3 engine/realtalk.py --any 택배 반품 -n 5  # 하나라도 든 대화

자료: AI Hub 「한국어 대화 요약」(20~30대 친구끼리 메신저 대화 14,759개), HF 미러 lwef/aihub-ko-dialogue-2.
data/realtalk/dialogues.jsonl (git에 안 올림). 없으면 README의 받는 법대로 받는다.
사내 대사 작업의 참고용이다. 문장을 대본에 그대로 옮기지 않는다(재배포 금지 자료). 리듬·끊는 법·받아치는 법만 본다.
메신저 대화라 ㅋㅋ·오타·줄임이 많다. 그건 따라 하지 않는다.
"""
import json, random, re, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data/realtalk/dialogues.jsonl"

def clean(d):
    d = re.sub(r"#P0(\d)#:\s*", lambda m: "ABCDEFGHI"[int(m.group(1)) - 1] + ": ", d)
    return d.replace("#@이모티콘#", "(이모티콘)")

def search(rows, words, any_=False):
    hit = any if any_ else all
    return [r for r in rows if hit(w in r for w in words)]

assert search(["아빠 병원 갔대", "엄마"], ["아빠", "병원"]) == ["아빠 병원 갔대"]
assert search(["아빠", "엄마"], ["아빠", "엄마"], any_=True) == ["아빠", "엄마"]
assert clean("#P01#: 응\n#P02#: 웅") == "A: 응\nB: 웅"

if __name__ == "__main__":
    args = sys.argv[1:]
    n = int(args[args.index("-n") + 1]) if "-n" in args else 5
    any_ = "--any" in args
    words = [a for i, a in enumerate(args) if not a.startswith("-") and (i == 0 or args[i - 1] != "-n")]
    if not DATA.exists():
        sys.exit(f"{DATA} 없음. data/realtalk/README.md 참고")
    rows = [json.loads(l)["dialogue"] for l in DATA.open(encoding="utf-8")]
    hits = search(rows, words, any_)
    random.seed(" ".join(words))  # ponytail: 같은 낱말이면 같은 예문 — 재현용
    for d in random.sample(hits, min(n, len(hits))):
        print(clean(d), "\n---")
    print(f"[{len(hits)}개 중 {min(n, len(hits))}개] 리듬만 보고 문장은 옮기지 않는다.", file=sys.stderr)
