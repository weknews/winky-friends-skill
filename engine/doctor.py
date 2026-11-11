"""winky-friends 준비 점검. 표준 라이브러리만 쓰고 읽기만 한다(아무것도 설치·생성·전송하지 않는다).
API 키·로그인 파일은 「있다/없다」만 본다. 값은 읽지도 출력하지도 않는다.

  python engine/doctor.py                      사람이 보는 표
  python engine/doctor.py --host-tools suno    에이전트가 자기 도구 목록에서 보이는 것을 알려 줄 때(예: Suno MCP)
  python engine/doctor.py --json               에이전트가 읽기 좋게

상태: OK(준비됨) · WARN(되지만 주의) · FAIL(영상 만들기가 깨짐) · MISSING(선택 기능이 없음) · AGENT(에이전트만 안다)
FAIL과 MISSING에는 고치는 명령을 붙인다. FAIL이 하나라도 있으면 종료 코드 1.
설치는 하지 않는다. 고칠 명령은 에이전트가 사람에게 묻고 실행한다(docs/providers.md)."""
import argparse, hashlib, importlib.util, json, os, platform, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OS = {"Darwin": "mac", "Windows": "win"}.get(platform.system(), "linux")
FIX = {  # OS별 설치 명령(README 「준비물」과 같다)
    "python": {"mac": "brew install python", "win": "winget install -e --id Python.Python.3.12", "linux": "sudo apt install -y python3"},
    "numpy": {"mac": "pip3 install numpy pillow", "win": "py -m pip install numpy pillow", "linux": "sudo apt install -y python3-numpy python3-pil"},
    "node": {"mac": "brew install node", "win": "winget install -e --id OpenJS.NodeJS.LTS", "linux": "sudo apt install -y nodejs npm (22 미만이면 nodesource로 22 설치)"},
    "ffmpeg": {"mac": "brew install ffmpeg", "win": "winget install -e --id Gyan.FFmpeg", "linux": "sudo apt install -y ffmpeg"},
}
rows = []

def add(area, item, status, note="", fix=""):
    rows.append({"area": area, "item": item, "status": status, "note": note, "fix": fix})

def ver(cmd):
    try: return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout + ""
    except Exception: return ""

def num(s):
    m = re.search(r"(\d+)\.(\d+)", s or ""); return (int(m.group(1)), int(m.group(2))) if m else None

def check_runtime():
    v = sys.version_info
    add("실행", "Python", "OK" if v >= (3, 10) else "FAIL", f"{v.major}.{v.minor}", "" if v >= (3, 10) else FIX["python"][OS])
    for mod in ("numpy", "PIL"):
        ok = importlib.util.find_spec(mod) is not None
        add("실행", {"PIL": "Pillow"}.get(mod, mod), "OK" if ok else "FAIL", "", "" if ok else FIX["numpy"][OS])
    node = shutil.which("node")
    nv = num(ver([node, "--version"])) if node else None
    add("실행", "Node.js 22+", "OK" if nv and nv[0] >= 22 else "FAIL", f"{nv[0]}.{nv[1]}" if nv else "없음", "" if nv and nv[0] >= 22 else FIX["node"][OS])
    ff = shutil.which("ffmpeg")
    fv = num(ver([ff, "-version"])) if ff else None
    add("실행", "ffmpeg", "OK" if fv else "FAIL", f"{fv[0]}.{fv[1]}" if fv else "없음", "" if fv else FIX["ffmpeg"][OS])
    nm = os.path.isdir(os.path.join(ROOT, "engine", "node_modules", "hyperframes"))
    add("실행", "렌더 도구(hyperframes)", "OK" if nm else "FAIL", "", "" if nm else "cd engine && npm install")
    ch = os.path.isdir(os.path.join(os.path.expanduser("~"), ".cache", "hyperframes"))
    add("실행", "렌더용 크롬", "OK" if ch else "WARN", "" if ch else "첫 렌더 때 자동으로 받는다(몇 분 걸림)")
    pa = os.path.isdir(os.path.join(ROOT, "tools", "PyAnimalese"))
    add("실행", "목소리 녹음(PyAnimalese)", "OK" if pa else "FAIL", "", "" if pa else "git clone https://github.com/hwi-middle/PyAnimalese tools/PyAnimalese")

def check_kit():
    try: reg = json.load(open(os.path.join(ROOT, "kit", "registry.json"), encoding="utf-8"))
    except Exception as e: add("재료", "registry.json", "FAIL", str(e)[:60], "git pull 로 레포를 다시 받는다"); return
    items = [e for e in reg.get("items", {}).values() if e.get("status") == "approved"]
    lost = [e.get("file") for e in items if not os.path.exists(os.path.join(ROOT, e.get("file", "")))]
    add("재료", f"승인된 그림 {len(items)}개", "OK" if not lost else "FAIL", f"없는 파일 {len(lost)}개" if lost else "", "git pull (또는 git checkout -- kit)" if lost else "")
    bad = []
    for n, e in reg.get("music", {}).items():
        if e.get("status") != "approved": continue
        f = os.path.join(ROOT, e["file"])
        if not os.path.exists(f) or hashlib.sha256(open(f, "rb").read()).hexdigest() != e["sha256"]: bad.append(n)
    add("재료", "정식 음원", "OK" if not bad else "MISSING", f"{len(bad)}개 없음·다름" if bad else "", "python engine/fetch_kit.py (첫 소리 작업 때 자동으로도 받는다)" if bad else "")
    fonts = os.listdir(os.path.join(ROOT, "kit", "fonts")) if os.path.isdir(os.path.join(ROOT, "kit", "fonts")) else []
    ok = any(f.lower().endswith((".ttf", ".woff2")) for f in fonts)
    add("재료", "글꼴", "OK" if ok else "FAIL", "", "" if ok else "git pull")

def check_routes(host):
    backend = os.environ.get("WINKY_IMAGE_BACKEND", "codex")
    codex = shutil.which("codex")
    if backend == "openai":
        key = bool(os.environ.get("OPENAI_API_KEY")); pkg = importlib.util.find_spec("openai") is not None
        add("새 그림(선택)", "OpenAI Images API", "OK" if key and pkg else "MISSING",
            f"키 {'있음' if key else '없음'}, openai 패키지 {'있음' if pkg else '없음'}", "" if key and pkg else "docs/providers.md 「OpenAI API 키로 그림 그리기」")
    else:
        add("새 그림(선택)", "Codex CLI", "OK" if codex else "MISSING", (ver([codex, "--version"]).strip()[:30] if codex else "없음"),
            "" if codex else "npm install -g @openai/codex && codex login (docs/providers.md)")
        if codex: add("새 그림(선택)", "Codex 로그인", "WARN", "로그인 여부는 실제 생성 때 확인된다. 안 되면 codex login")
    if "suno" in host: add("새 음악(선택)", "Suno MCP", "OK", "에이전트가 도구 목록에서 확인")
    else: add("새 음악(선택)", "Suno MCP", "AGENT", "에이전트가 자기 도구에 suno가 보이면 --host-tools suno 로 다시 돈다. 없으면 docs/providers.md 「Suno」(구독·얼리 액세스·연결)")

def check_claude():
    if os.environ.get("CLAUDE_CODE_USE_BEDROCK"): p = f"Bedrock(리전 {os.environ.get('AWS_REGION', '설정 없음')})"
    elif os.environ.get("ANTHROPIC_API_KEY"): p = "Claude API 키"
    else: p = "Claude 구독 로그인 또는 Codex(환경변수 없음)"
    add("에이전트", "Claude 연결 방식", "OK", p)

if __name__ == "__main__":
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host-tools", default="", help="에이전트가 쓸 수 있는 도구(쉼표). 예: suno,image_gen")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(); host = {t.strip().lower() for t in a.host_tools.split(",") if t.strip()}
    check_runtime(); check_kit(); check_routes(host); check_claude()
    fail = any(r["status"] == "FAIL" for r in rows)
    if a.json: print(json.dumps({"os": OS, "ok": not fail, "checks": rows}, ensure_ascii=False, indent=1))
    else:
        mark = {"OK": "OK  ", "WARN": "주의", "FAIL": "실패", "MISSING": "없음", "AGENT": "확인", "UNKNOWN": "모름"}
        print(f"winky-friends 준비 점검 ({OS})\n")
        for r in rows:
            print(f"[{mark[r['status']]}] {r['area']} · {r['item']}" + (f"  ({r['note']})" if r["note"] else ""))
            if r["fix"]: print(f"        고치기: {r['fix']}")
        print("\n영상을 만들 준비가 됐습니다." if not fail else "\n「실패」 항목을 고쳐야 영상을 만들 수 있습니다. 「없음」은 선택 기능입니다.")
    sys.exit(1 if fail else 0)
