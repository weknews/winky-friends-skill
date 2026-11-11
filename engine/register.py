"""프리미티브 등록·승인 도구. kit/registry.json 을 손으로 고치지 않고 이걸로 고친다.

  python3 engine/register.py add NAME SRC.png --kind actor|hand|prop|set|ui|fx --actor bear --key magenta|blue|none \
          --mm '{"h":190}' --anchor '{"cx":400,"head":[..]}' --prompt-file kit/gen/out/NAME.prompt.txt --ref kit/gen/refs/x.png
      → 키 색 제거·알파 둘레로 자르기 → kit/<종류 폴더>/NAME.webp(배경은 .jpg), status=draft 로 등록
  python3 engine/register.py sheet [--out review/drafts.jpg]      → draft 전부를 한 장 승인 모음으로(이름·크기·mm 표기)
  python3 engine/register.py approve NAME [NAME...] --by 이름        → status=approved (사람이 승인 모음을 보고 나서만)
  python3 engine/register.py music NAME SRC.wav --role bed --clip SUNO_CLIP_ID   → 정식 음원 draft 등록(sha256 기록, rules/music.md)
  python3 engine/register.py list [이름 일부] [--status draft]

engine(build·check·sound)은 approved만 쓴다. draft 그림을 쓰는 회차는 build에서 멈추고 check 16번에서 걸린다."""
import argparse, datetime, hashlib, json, os, shutil, sys, unicodedata
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "kit/registry.json")
ASSET_LICENSE = "CC-BY-NC-ND-4.0 (위뉴, LICENSE-ASSETS.md)"   # 그림·음원은 위뉴 자산. 효과음은 코드 합성이라 MIT
DIR = {"actor": "actors/{actor}", "hand": "actors/{actor}", "prop": "props", "set": "sets/{set}", "ui": "ui", "fx": "fx"}

def load(): return json.load(open(REG, encoding="utf-8"))
def save(r): json.dump(r, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def key(a, k):                                   # ep01-v9 prep.py key() 그대로(k: "m" 마젠타, 그 밖 파랑)
    r, g, b = [a[..., i].astype(np.float32) for i in range(3)]
    spill = (np.minimum(r, b) - g) if k == "m" else (b - np.maximum(r, g))
    alpha = 1 - np.clip((spill - 30) / 60, 0, 1)
    ex = np.clip(spill, 0, None) * 0.85
    if k == "m": r, b = r - ex, b - ex
    else: b = b - ex
    return np.dstack([r, g, b, alpha * 255]).clip(0, 255).astype(np.uint8)

def add(o):
    r = load()
    if o.name in r["items"] and r["items"][o.name]["status"] == "approved" and not o.replace:
        sys.exit(f"{o.name} 은 이미 승인된 프리미티브다. 고쳐 만들려면 --replace (PR에서 이유를 적는다)")
    im = Image.open(o.src).convert("RGBA"); a = np.asarray(im)
    if o.key != "none": a = key(a, "m" if o.key == "magenta" else "b")
    if o.kind != "set":
        bb = Image.fromarray(a[..., 3]).point(lambda v: 255 if v > 40 else 0).getbbox(); a = a[bb[1]:bb[3], bb[0]:bb[2]]
    sub = DIR[o.kind].format(actor=o.actor or "", set=o.set or "")
    ext = ".jpg" if o.kind == "set" else ".webp"; rel = f"kit/{sub}/{o.file or o.name}{ext}"
    os.makedirs(os.path.dirname(os.path.join(ROOT, rel)), exist_ok=True)
    out = Image.fromarray(a, "RGBA")
    (out.convert("RGB").save(os.path.join(ROOT, rel), quality=90) if ext == ".jpg" else out.save(os.path.join(ROOT, rel), quality=92, method=6))
    e = dict(kind=o.kind, file=rel, w=out.width, h=out.height, anchor=json.loads(o.anchor or "{}"), status="draft",
             source=o.source or "Codex Images 2.6 (kit/gen/gen.py)", prompt=open(o.prompt_file, encoding="utf-8").read().strip() if o.prompt_file else None,
             ref=o.ref, created=datetime.date.today().isoformat(), license=ASSET_LICENSE)
    if o.actor: e["actor"] = o.actor
    if o.family: e["family"] = o.family
    if o.mm: e["mm"] = json.loads(o.mm)
    if o.size_class and o.mm: r["sizes"][o.size_class] = json.loads(o.mm)
    r["items"][o.name] = e; save(r); print("draft 등록", o.name, rel, f"{out.width}×{out.height}")

def music(o):
    r = load(); rel = f"kit/music/{o.name}.wav"; shutil.copy(o.src, os.path.join(ROOT, rel))
    r["music"][o.name] = dict(kind="music", role=o.role, file=rel, sha256=hashlib.sha256(open(o.src, "rb").read()).hexdigest(), bytes=os.path.getsize(o.src),
                              suno_clip=o.clip, status="draft", source="Suno Pro, 정식 테마 theme-a를 reference로(rules/music.md)", created=datetime.date.today().isoformat(), license=ASSET_LICENSE)
    save(r); print("음원 draft 등록", o.name)

def approve(o):
    r = load()
    for n in o.names:
        e = r["items"].get(n) or r["music"].get(n)
        if not e: sys.exit(f"{n} 없음")
        e["status"] = "approved"; e["approved"] = f"{datetime.date.today().isoformat()} {o.by}"
    save(r); print("승인", *o.names)

def sheet(o):
    r = load(); ds = [(n, e) for n, e in r["items"].items() if e["status"] == "draft"]
    if not ds: print("draft 없음"); return
    C, cw, ch = 4, 480, 620; rows = (len(ds) + C - 1) // C
    S = Image.new("RGB", (C * cw, rows * ch), (238, 238, 238)); d = ImageDraw.Draw(S)
    try: f = ImageFont.truetype(os.path.join(ROOT, "kit/fonts/Jua-Regular.ttf"), 26)
    except OSError: f = None
    for i, (n, e) in enumerate(ds):
        x, y = i % C * cw, i // C * ch; im = Image.open(os.path.join(ROOT, e["file"])).convert("RGBA"); im.thumbnail((cw - 40, ch - 120))
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); S.paste(bg.convert("RGB"), (x + 20, y + 20))
        d.text((x + 20, y + ch - 90), n, fill=(16, 35, 63), font=f); d.text((x + 20, y + ch - 55), f"{e['w']}×{e['h']}px  mm {e.get('mm', '-')}", fill=(60, 60, 60), font=f)
    os.makedirs(os.path.dirname(os.path.join(ROOT, o.out)), exist_ok=True); S.save(os.path.join(ROOT, o.out), quality=88); print("승인 모음", o.out, len(ds), "장")

def lst(o):
    r = load()
    for n, e in list(r["items"].items()) + list(r["music"].items()):
        if (not o.status or e["status"] == o.status) and (not o.part or o.part in n): print(f"{e['status']:9} {e['kind']:6} {n:28} {e['file']}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("add"); a.add_argument("name"); a.add_argument("src"); a.add_argument("--kind", required=True, choices=list(DIR))
    a.add_argument("--actor"); a.add_argument("--set"); a.add_argument("--key", default="magenta", choices=["magenta", "blue", "none"])
    a.add_argument("--mm"); a.add_argument("--size-class"); a.add_argument("--anchor"); a.add_argument("--family"); a.add_argument("--file")
    a.add_argument("--prompt-file"); a.add_argument("--ref"); a.add_argument("--source"); a.add_argument("--replace", action="store_true"); a.set_defaults(f=add)
    m = sp.add_parser("music"); m.add_argument("name"); m.add_argument("src"); m.add_argument("--role", required=True, choices=["theme", "bed", "stings", "sting", "end"]); m.add_argument("--clip", required=True); m.set_defaults(f=music)
    v = sp.add_parser("approve"); v.add_argument("names", nargs="+"); v.add_argument("--by", required=True); v.set_defaults(f=approve)
    s = sp.add_parser("sheet"); s.add_argument("--out", default="review/drafts.jpg"); s.set_defaults(f=sheet)
    l = sp.add_parser("list"); l.add_argument("part", nargs="?"); l.add_argument("--status"); l.set_defaults(f=lst)
    o = p.parse_args(); sys.stdout.reconfigure(encoding="utf-8")
    nfc = lambda s: s and unicodedata.normalize("NFC", s)                 # 한글 이름·파일 이름은 NFC로(macOS 입력이 NFD일 때가 있다)
    for k in ("name", "file"): hasattr(o, k) and setattr(o, k, nfc(getattr(o, k)))
    if hasattr(o, "part"): o.part = nfc(o.part)
    if hasattr(o, "names"): o.names = [nfc(n) for n in o.names]
    o.f(o)
