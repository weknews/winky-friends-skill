"""정식 음원 팩 받기. 음원은 레포가 아니라 GitHub Release에 둔다(레포를 가볍게, 공개 레포 LFS 전송량 걱정 없이).
처음 실행할 때 sound.py가 자동으로 부른다. 직접 받으려면: python engine/fetch_kit.py
받은 파일은 kit/registry.json 의 sha256으로 검증한다. 다르면 지우고 멈춘다(정식 음원만 쓴다, rules/music.md)."""
import hashlib, io, json, os, sys, urllib.request, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = json.load(open(os.path.join(ROOT, "kit", "registry.json"), encoding="utf-8"))
PACK = REG.get("music_pack", {})
URL = PACK.get("url")

def missing():
    out = []
    for n, e in REG["music"].items():
        if e.get("status") != "approved": continue
        f = os.path.join(ROOT, e["file"])
        if not os.path.exists(f) or hashlib.sha256(open(f, "rb").read()).hexdigest() != e["sha256"]: out.append((n, e))
    return out

def fetch():
    need = missing()
    if not need: return 0
    if not URL: raise SystemExit("registry.json 에 music_pack.url 이 없다")
    print(f"정식 음원 팩 받는 중: {URL}")
    data = urllib.request.urlopen(URL, timeout=120).read()
    if PACK.get("sha256") and hashlib.sha256(data).hexdigest() != PACK["sha256"]:
        raise SystemExit("음원 팩 sha256이 레지스트리와 다르다. 받지 않았다")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for n, e in need:
            name = os.path.basename(e["file"])
            blob = z.read(name)
            if hashlib.sha256(blob).hexdigest() != e["sha256"]: raise SystemExit(f"{name}: sha256 불일치")
            dst = os.path.join(ROOT, e["file"]); os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, "wb").write(blob)
            print("  받음", e["file"])
    return len(need)

if __name__ == "__main__":
    n = fetch(); print("정식 음원 준비 완료" if n == 0 else f"정식 음원 {n}개 받음")
