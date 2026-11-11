"""새 프리미티브 그림 한 장 생성. macOS·Linux·Windows 공통.
그리는 곳은 환경변수 WINKY_IMAGE_BACKEND 로 고른다(docs/providers.md).
  codex  (기본) Codex CLI 내장 image_gen. ChatGPT 구독으로 로그인한 Codex
  openai OpenAI Images API(이미지 편집). OPENAI_API_KEY, 모델은 WINKY_IMAGE_MODEL(기본 gpt-image-1). `pip install openai`
사용: python3 kit/gen/gen.py 이름 크기 키(magenta|blue|none) "IMAGE 문장" [기준 그림...] → kit/gen/out/이름.png (+ .log, .prompt.txt)
ep01-v9 시기 series-kit/gen.sh 와 같은 프롬프트 조립. kit/gen/out/ 은 git에 올리지 않는다.
편 색 문단은 넣지 않는다(옷 색이 덮인다). 윙키 원본·9인 줄 세우기를 매번 붙인다."""
import os, shutil, subprocess, sys

W = os.path.dirname(os.path.abspath(__file__)); P_ = os.path.join(W, "prompts"); R = os.path.join(W, "refs"); OUT = os.path.join(W, "out")
LOCK = "COLOR LOCK: Bear Dad brown fur, SKY-BLUE hoodie jacket with white zipper, GRAY cap, gray-brown cargo shorts, beige boots. Panda SKY-BLUE knit cardigan over white shirt, COBALT trousers. Penguin Doctor black head and back, white front, pure white coat, blue lanyard with blank card, silver stethoscope, paper fan. Winky exactly as the attached Winky reference, no clothes. EMPTY HANDS: never draw cups, apples, boxes or notes in any hand unless the prompt says so."

def part(n): return open(os.path.join(P_, n + ".txt"), encoding="utf-8").read().strip()  # ponytail: bash $(cat) 처럼 끝 줄바꿈을 뗀다

API_SIZES = {"1024x1024", "1536x1024", "1024x1536"}

def openai_backend(name, size, key, prompt, refs):
    """OpenAI Images API로 기준 그림을 편집해 그린다. 키 색 배경 대신 투명 배경으로 받는다(key가 none이 아니면)."""
    import base64
    try: from openai import OpenAI
    except ImportError: return "openai 패키지가 없다: pip install openai"
    if not os.environ.get("OPENAI_API_KEY"): return "OPENAI_API_KEY 환경변수가 없다(docs/providers.md)"
    os.makedirs(OUT, exist_ok=True); png = os.path.join(OUT, name + ".png")
    w, h = (int(x) for x in size.lower().split("x"))
    api_size = size if size in API_SIZES else ("1024x1536" if h > w else "1536x1024" if w > h else "1024x1024")  # ponytail: API가 받는 세 크기로 맞춤. 배율은 build가 mm로 다시 맞춘다
    P = f"{part('style-base')} {part('key-none') if key == 'none' else 'Transparent background, no floor, no shadow on the background.'} CHARACTERS: {part('chars')} {LOCK} IMAGE: {prompt}"
    files = [open(f, "rb") for f in [os.path.join(R, "s8-winky.png"), os.path.join(R, "lineup.png"), *refs]]
    try:
        r = OpenAI().images.edit(model=os.environ.get("WINKY_IMAGE_MODEL", "gpt-image-1"), image=files, prompt=P, size=api_size,
                                 quality="high", **({} if key == "none" else {"background": "transparent"}))
    finally:
        for f in files: f.close()
    open(png, "wb").write(base64.b64decode(r.data[0].b64_json))
    open(os.path.join(OUT, name + ".prompt.txt"), "w", encoding="utf-8").write(prompt + "\n")
    print("OK", name, "(openai", api_size + ")"); return 0

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 5: sys.exit(__doc__)
    name, size, key, prompt, *refs = sys.argv[1:]
    if os.environ.get("WINKY_IMAGE_BACKEND", "codex") == "openai":
        sys.exit(openai_backend(name, size, key, prompt, refs))
    codex = shutil.which("codex") or sys.exit("codex 명령을 찾지 못했다. Codex CLI를 설치하고 로그인한 뒤 새 터미널에서 다시 돈다(npm install -g @openai/codex)")
    os.makedirs(OUT, exist_ok=True); png = os.path.join(OUT, name + ".png")
    args = [a for r in [os.path.join(R, "s8-winky.png"), os.path.join(R, "lineup.png"), *refs] for a in ("-i", r)]
    P = f"{part('style-base')} {part('key-' + key)} CHARACTERS: {part('chars')} {LOCK} IMAGE: {prompt}"
    ask = f"내장 image_gen 도구로 quality high, 크기 {size} 그림을 한 장 만들어 {png} 에 저장하라. 코드로 그리지 말고 반드시 image_gen 도구를 써라. 첨부한 그림은 기준 그림이다(그림체, 캐릭터 생김새). 저장 뒤 파일 경로만 한 줄로 답하라. 프롬프트는 아래를 그대로 쓴다. {P}"
    with open(os.path.join(OUT, name + ".log"), "w", encoding="utf-8") as log:
        try: subprocess.run([codex, "exec", "--skip-git-repo-check", "-s", "workspace-write", "-C", W, *args, "--", ask], stdin=subprocess.DEVNULL, stdout=log, stderr=log, timeout=900)
        except subprocess.TimeoutExpired: log.write("\n시간 초과(900초)\n")
    open(os.path.join(OUT, name + ".prompt.txt"), "w", encoding="utf-8").write(prompt + "\n")
    if os.path.exists(png): print("OK", name)
    else: print("FAIL", name); print("".join(open(os.path.join(OUT, name + ".log"), encoding="utf-8", errors="replace").readlines()[-3:])); sys.exit(1)
