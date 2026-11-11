"""대한당뇨병학회 「2025 당뇨병 진료지침」 원문을 각자 컴퓨터에 받아 두고 찾아 쓰는 도구. 원문은 학회 저작물이라 레포에 올리지 않는다.
  python engine/guideline.py fetch            학회 홈페이지에서 PDF를 받아 local/guideline/ 에 둔다(약 5MB)
  python engine/guideline.py text             쪽별 텍스트를 뽑는다(pypdf 필요: pip install pypdf)
  python engine/guideline.py search 주스 과일   낱말이 나오는 쪽과 문장을 찾는다(대본 지침 대조용)
받는 곳: 학회 홈페이지 진료지침 게시판의 「2025 당뇨병 진료지침_전문_최종본.pdf」. 주소가 바뀌면 WINKY_GUIDELINE_URL 로 바꾼다."""
import json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "local", "guideline")
PDF = os.environ.get("WINKY_GUIDELINE_PDF") or os.path.join(DIR, "kda-2025.pdf")
TXT = os.path.splitext(PDF)[0] + ".pages.json"
URL = os.environ.get("WINKY_GUIDELINE_URL", "https://diabetes.or.kr/bbs/download.php?code=guide&number=1522")

def fetch():
    os.makedirs(os.path.dirname(PDF), exist_ok=True)
    if os.path.exists(PDF): print("이미 있다:", PDF); return
    print("받는 중:", URL)
    data = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
    if not data.startswith(b"%PDF"): sys.exit("PDF가 아닌 응답이다. 학회 홈페이지에서 직접 받아 " + PDF + " 로 저장한다")
    open(PDF, "wb").write(data); print("저장:", PDF, f"{len(data)/1048576:.1f}MB")

def text():
    try: from pypdf import PdfReader
    except ImportError: sys.exit("pypdf가 없다: pip install pypdf (Windows는 py -m pip install pypdf)")
    if not os.path.exists(PDF): sys.exit("원문이 없다: python engine/guideline.py fetch")
    pages = [p.extract_text() or "" for p in PdfReader(PDF).pages]
    json.dump(pages, open(TXT, "w", encoding="utf-8"), ensure_ascii=False); print(f"{len(pages)}쪽 →", TXT)

def search(words):
    if not os.path.exists(TXT): text()
    pages = json.load(open(TXT, encoding="utf-8"))
    for i, t in enumerate(pages, 1):
        flat = re.sub(r"\s+", " ", t)
        for w in words:
            for m in re.finditer(re.escape(w), flat):
                print(f"[PDF {i}쪽] …{flat[max(0, m.start() - 70):m.end() + 70]}…")

if __name__ == "__main__":
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fetch": fetch()
    elif cmd == "text": text()
    elif cmd == "search" and len(sys.argv) > 2: search(sys.argv[2:])
    else: sys.exit(__doc__)
