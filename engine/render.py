"""렌더·붙이기(회차 폴더에서). macOS·Linux·Windows 공통. check·sound·thumbshot을 통과한 뒤에 돈다.
hyperframes render → out/raw.mp4, 썸네일 0.4초 + 본편 + out/audio.wav + 표지(attached_pic) → out/<회차 폴더 이름>.mp4
사용: cd episodes/<회차> && python3 ../../engine/render.py   (Windows는 python3 대신 py)"""
import os, shutil, subprocess, sys

ENGINE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.abspath(os.environ.get("EP", os.getcwd()))
HF = os.path.join(ENGINE, "node_modules/hyperframes/bin/hyperframes.mjs")
node, ffmpeg = shutil.which("node"), shutil.which("ffmpeg")
if not (node and ffmpeg and os.path.exists(HF)): sys.exit("node·ffmpeg·hyperframes 중 없는 것이 있다. README 「준비물」과 engine 폴더 npm install 을 확인한다")
for f in ("out/thumb.png", "out/audio.wav"):
    if not os.path.exists(os.path.join(EP, f)): sys.exit(f"{f} 가 없다. thumbshot.mjs·sound.py를 먼저 돈다")

run = lambda *a: subprocess.run(a, cwd=EP, check=True)
run(node, HF, "render", "--quality", "high", "--output", "out/raw.mp4")
run(ffmpeg, "-y", "-loop", "1", "-framerate", "30", "-t", "0.4", "-i", "out/thumb.png", "-i", "out/raw.mp4", "-i", "out/audio.wav", "-i", "out/thumb.png",
    "-filter_complex", "[0:v]format=yuv420p,setsar=1,fps=30[t];[1:v]format=yuv420p,setsar=1[m];[t][m]concat=n=2:v=1:a=0[v]",
    "-map", "[v]", "-map", "2:a", "-map", "3:v", "-c:v:0", "libx264", "-crf", "18", "-preset", "slow", "-c:a", "aac", "-b:a", "192k",
    "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic", "-movflags", "+faststart", f"out/{os.path.basename(EP)}.mp4")
print("완성", os.path.join("out", os.path.basename(EP) + ".mp4"))
