"""회차 폴더 준비: kit·fonts·lib·index.html 을 레포의 kit/·engine/ 에 잇는다. macOS·Linux·Windows 공통.
링크를 git에 올리지 않는다(Windows 기본 설정에서 깨진다). 심볼릭 링크를 만들고, Windows에서 권한이 없으면 폴더는 정션, index.html은 복사.
build.py가 시작할 때 부르므로 기존 회차는 따로 돌리지 않아도 된다.
새 회차: python engine/setup_episode.py episodes/ep02-<영문-짧게>  → 폴더를 만들고 ep01의 episode.py·sound_cues.py·thumb.html을 틀로 복사"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINKS = {"kit": "kit", "fonts": "kit/fonts", "lib": "engine/lib", "index.html": "engine/index.html"}
TEMPLATE = os.path.join(ROOT, "episodes/ep01-fruit-juice")

def link(ep):
    for name, rel in LINKS.items():
        dst, src = os.path.join(ep, name), os.path.join(ROOT, rel)
        if os.path.lexists(dst): continue                       # 이미 있으면(직접 복사해 고친 index.html 포함) 그대로 둔다
        try: os.symlink(os.path.relpath(src, ep), dst, target_is_directory=os.path.isdir(src))
        except OSError:                                         # Windows: 개발자 모드가 아니면 심볼릭 링크 권한이 없다
            if os.path.isdir(src): subprocess.run(["cmd", "/c", "mklink", "/J", dst, src], check=True, capture_output=True)
            else: shutil.copy(src, dst)                         # ponytail: 복사본은 engine/index.html을 고치면 지우고 다시 만든다

if __name__ == "__main__":
    if len(sys.argv) != 2: sys.exit(__doc__)
    ep = os.path.abspath(sys.argv[1]); os.makedirs(ep, exist_ok=True)
    for f in ("episode.py", "sound_cues.py", "thumb.html"):
        if not os.path.exists(os.path.join(ep, f)): shutil.copy(os.path.join(TEMPLATE, f), ep)
    link(ep); print("준비됨", ep)
