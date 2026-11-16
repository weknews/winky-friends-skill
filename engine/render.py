"""렌더·붙이기(회차 폴더에서). macOS·Linux·Windows 공통. build → check → sound → thumbshot 뒤에 돈다.
hyperframes render → out/raw.mp4, 썸네일 0.4초 + 본편 + out/audio.wav + 표지(attached_pic) → out/<회차 폴더 이름>.mp4
미리 보기 장면(WINKY_PREVIEW_DRAFTS=1 로 build)은 out/<회차>-preview.mp4 로 나온다. 정식 파일 이름은 정식 렌더만 쓴다.
순서 관문: 산출물이 재료보다 오래됐거나 check에 실패가 있으면 멈추고 다시 돌릴 명령을 알려 준다(WINKY_RENDER_ANYWAY=1 이면 건너뜀).
사용: cd episodes/<회차> && python3 ../../engine/render.py   (Windows는 python3 대신 py)"""
import json, os, re, shutil, subprocess, sys

ENGINE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(os.environ.get("EP", os.getcwd()))
HF = os.path.join(ENGINE, "node_modules/hyperframes/bin/hyperframes.mjs")

def stale(ep=EP):
    """다시 돌려야 하는 단계 목록(없으면 []). 단계 상태는 파일 시각으로 본다: 결과가 재료보다 새것이어야 한다."""
    p = lambda f: os.path.join(ep, f); mt = lambda f: os.path.getmtime(p(f)) if os.path.exists(p(f)) else 0
    if not mt("scene.json"): return ["scene.json 이 없다 → python3 ../../engine/build.py"]
    out = []
    if mt("scene.json") < max(mt("episode.py"), os.path.getmtime(os.path.join(ENGINE, "../kit/registry.json"))):
        out.append("episode.py 나 레지스트리가 build 뒤에 바뀌었다 → python3 ../../engine/build.py (그 뒤 check·sound도 다시)")
    if not json.load(open(p("scene.json"), encoding="utf-8")).get("preview"):      # 미리 보기는 draft 때문에 check 16이 늘 실패한다
        c = open(p("out/check.txt"), encoding="utf-8").read() if mt("out/check.txt") else ""
        if mt("out/check.txt") < mt("scene.json") or re.search(r"/ 실패 [1-9]", c):
            out.append("지금 장면으로 통과한 check가 없다 → python3 ../../engine/check.py (실패 0)")
    if mt("out/audio.wav") < max(mt("scene.json"), mt("sound_cues.py")): out.append("소리가 장면·큐보다 오래됐다 → python3 ../../engine/sound.py")
    if mt("out/thumb.png") < mt("thumb.html"): out.append("썸네일이 thumb.html보다 오래됐다 → node ../../engine/thumbshot.mjs")
    return out

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    node, ffmpeg = shutil.which("node"), shutil.which("ffmpeg")
    if not (node and ffmpeg and os.path.exists(HF)): sys.exit("node·ffmpeg·hyperframes 중 없는 것이 있다. README 「준비물」과 engine 폴더 npm install 을 확인한다")
    for f in ("out/thumb.png", "out/audio.wav"):
        if not os.path.exists(os.path.join(EP, f)): sys.exit(f"{f} 가 없다. thumbshot.mjs·sound.py를 먼저 돈다")
    todo = stale()
    if todo and not os.environ.get("WINKY_RENDER_ANYWAY"): sys.exit("렌더하지 않았다. 먼저:\n  " + "\n  ".join(todo))

    run = lambda *a: subprocess.run(a, cwd=EP, check=True)
    # M2: hyperframes는 index.html의 data-duration(ep01 50.0)을 읽는다. 회차 길이(scene.json D)로 바꾼 사본을 렌더하고 지운다
    S = json.load(open(os.path.join(EP, "scene.json"), encoding="utf-8"))
    name = f"out/{os.path.basename(EP)}{'-preview' if S.get('preview') else ''}.mp4"
    html = re.sub(r'data-duration="[\d.]+"', f'data-duration="{S["D"]}"', open(os.path.join(EP, "index.html"), encoding="utf-8").read(), count=1)
    open(os.path.join(EP, "_render.html"), "w", encoding="utf-8").write(html)
    try: run(node, HF, "render", "-c", "_render.html", "--quality", "high", "--output", "out/raw.mp4")
    finally: os.remove(os.path.join(EP, "_render.html"))
    run(ffmpeg, "-y", "-loop", "1", "-framerate", "30", "-t", "0.4", "-i", "out/thumb.png", "-i", "out/raw.mp4", "-i", "out/audio.wav", "-i", "out/thumb.png",
        "-filter_complex", "[0:v]format=yuv420p,setsar=1,fps=30[t];[1:v]format=yuv420p,setsar=1[m];[t][m]concat=n=2:v=1:a=0[v]",
        "-map", "[v]", "-map", "2:a", "-map", "3:v", "-c:v:0", "libx264", "-crf", "18", "-preset", "slow", "-c:a", "aac", "-b:a", "192k",
        "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic", "-movflags", "+faststart", name)
    print("완성", name)
