"""9판 새 그림 6장(대본 「새로 만들 것」): table 판, 손 셋(bear-hand-flat, bear-hand-pencil, winky-hand), 기록장 둘.
생성은 series-kit/gen.sh(Codex Images 2.6, 기준 그림 편집). 손은 그 인물 원본 그림의 손·소매를 잘라 마젠타 바탕에 놓은
기준 그림(series-kit/gen/ref-v9/*.png)을 편집해 털색·종이결을 맞춘다. 크기는 prep.py가 재고 build.py가 mm로 맞춘다.
사용: python3 gen9.py refs | gen1(판·기록장 펼침·손 셋) | gen2(기록장 닫힘: 펼침을 기준으로) | fix 이름 "고칠 말" [기준...]"""
import os, sys, subprocess, glob, unicodedata
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
KITS = os.path.join(HERE, "../series-kit"); GEN = os.path.join(KITS, "gen")
REF = os.path.join(GEN, "ref-v9"); os.makedirs(REF, exist_ok=True)
MAG = (255, 0, 255)

def src(n):
    return [f for f in glob.glob(os.path.join(GEN, "*.png")) if unicodedata.normalize("NFC", os.path.basename(f))[:-4] == n][0]

def keyed(n):
    sys.path.insert(0, HERE); import prep
    im = np.asarray(Image.open(src(n)).convert("RGB")); px = im[4, 4]
    a = prep.key(im, "m" if (px[0] > 200 and px[2] > 200 and px[1] < 90) else "b"); a[..., 3][a[..., 3] < 24] = 0
    return Image.fromarray(a, "RGBA")

def crop_ref(out, n, box):
    """원본 그림에서 손·소매 칸을 잘라 마젠타 바탕 1024×1024 가운데에 놓는다(배율 바꾸지 않음)."""
    im = keyed(n).crop(box); C = Image.new("RGBA", (1024, 1024), MAG + (255,))
    C.alpha_composite(im, ((1024 - im.width) // 2, (1024 - im.height) // 2)); C.convert("RGB").save(os.path.join(REF, out)); return os.path.join(REF, out)

def refs():
    return dict(
        bear=crop_ref("bear-paw-src.png", "bear-들기-웃음", (640, 640, 1010, 1010)),          # 든 손 + 하늘색 소매
        winky=crop_ref("winky-paw-src.png", "winky-양손들기-웃음", (230, 700, 760, 960)),     # 두 앞발 + 크림색 털
    )

ALPHA = (" If your image tool offers a transparent background option, turn it on and keep the alpha; otherwise use the plain flat magenta background.")
TOP = "Seen from DIRECTLY ABOVE (top-down, flat, no perspective), like a paper cut-out lying on a table."
P = {
 "set-table": ("1152x2048", "none",
   "BACKGROUND PLATE, top-down: looking straight down at a plain WHITE paper tabletop that fills the entire frame edge to edge. "
   "Clean matte white paper surface with very faint paper fiber; the only other tone is a soft pale blue-gray (#DCE3EC) used for a gentle shadow "
   "along the edges and one or two large layered white paper sheets with thin pale blue-gray shadows between layers. "
   "It is a white table or desk top: NEVER brown, no wood, no wood grain, no beige, no tablecloth pattern. "
   "Nothing on it at all: no objects, no cups, no notebook, no hands, no text, no lines, no numbers."),
 "notebook-open": ("1536x1024", "magenta",
   "ONE prop only, no characters: an open paper notebook (a meal diary) lying flat, " + TOP + " Landscape 300:210 (two pages side by side, "
   "a soft fold in the middle, no spiral), thin pale sky-blue paper cover edges peeking around the white pages. "
   "The RIGHT page has a simple table drawn with thin pale gray-blue lines: FOUR equal horizontal rows filling the page; each row has a small "
   "BLANK label box at its left (about one fifth of the row width) and a wide writing area to its right. In the top three rows the writing "
   "area holds only a few faint light-gray pencil scribble lines (illegible squiggles, never letters). The BOTTOM (fourth) row is completely "
   "EMPTY: two thin pale ruled lines, lots of white space, nothing written. The LEFT page is blank white with a few faint pale ruled lines. "
   "No letters, no numbers, no text anywhere." + ALPHA),
 "bear-hand-flat": ("1024x1536", "magenta",
   "EDIT the attached bear paw reference (BEAR DAD's raised paw and sky-blue sleeve). ONE body part only: BEAR DAD's right forearm and paw, "
   + TOP + " The arm comes UP from the BOTTOM edge of the picture: the SKY-BLUE hoodie jacket sleeve (same blue paper and cuff as the reference) "
   "runs straight down and is cut off by the bottom edge. At the top of the arm, the brown paw lies FLAT, PALM DOWN, fingers pointing up, "
   "four short thick rounded fingers slightly apart, the same brown paper color and rounded shape as the reference paw. The paw is about 30% of "
   "the picture width, its fingertips near the top (about 6% from the top edge). The arm is vertical and centered, long (it fills the height). "
   "No body, no head, no other paw, nothing in the paw." + ALPHA),
 "bear-hand-pencil": ("1024x1536", "magenta",
   "EDIT the attached bear paw reference (BEAR DAD's raised paw and sky-blue sleeve). ONE body part plus one pencil: BEAR DAD's right forearm and "
   "paw, " + TOP + " The arm comes UP from the BOTTOM edge of the picture: the SKY-BLUE hoodie jacket sleeve (same blue paper and cuff as the reference) "
   "runs straight down and is cut off by the bottom edge. The brown paw (same brown paper as the reference) holds a plain unpainted pale-wood "
   "pencil the way you write: fingers curled around it, the pencil leaning so its sharpened gray graphite TIP points to the UPPER-LEFT and is "
   "the top-left-most point of the whole picture, a small white eraser end at the other side. The pencil is about as long as the paw is wide "
   "(pencil length about 1.05 times the paw width). No red anywhere. The paw is about 30% of the picture width, near the top. Arm vertical, "
   "centered, long (it fills the height). No body, no head, no paper, no writing." + ALPHA),
 "winky-hand": ("1024x1536", "magenta",
   "EDIT the attached Winky paw reference (WINKY's cream front paws). ONE body part only: WINKY's right front leg and paw, " + TOP +
   " The arm comes DOWN from the TOP edge of the picture: a cream fur foreleg (same cream paper as the reference, no clothes) runs straight "
   "down from the top edge (cut off by the top edge) and ends in a small round cream paw lying FLAT, PALM DOWN, three little toe slits at its "
   "bottom edge, the same paw shape as the reference. The paw is about 30% of the picture width; its bottom tip about 6% above the bottom edge. "
   "Leg vertical, centered, long (it fills the height). No body, no head, no ears, no tail, nothing in the paw." + ALPHA),
 "notebook-closed": ("1024x1536", "magenta",
   "The SAME notebook as the attached open notebook picture, now CLOSED, lying flat, " + TOP + " Portrait 150:210. The front cover is the same "
   "pale sky-blue paper as the cover edges of the open notebook, with one BLANK white rectangular label panel in the upper middle of the cover "
   "(about 60% of the cover width). No letters, no numbers, no text, no spiral." + ALPHA),
}

def gen(name, *refs_):
    size, key, prompt = P[name]
    log = open(os.path.join(REF, name + ".run.log"), "w")
    return subprocess.Popen([os.path.join(KITS, "gen.sh"), name, size, key, prompt, *refs_], stdout=log, stderr=log)

def run(jobs):
    ps = [gen(*j) for j in jobs]
    for p in ps: p.wait()
    for j in jobs: print("OK" if os.path.exists(os.path.join(GEN, j[0] + ".png")) else "FAIL", j[0])

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "refs": print(refs())
    elif cmd == "gen1":
        R = refs()
        run([("set-table", src("set-office-m")), ("notebook-open",), ("bear-hand-flat", R["bear"], src("bear-들기-웃음")),
             ("bear-hand-pencil", R["bear"], src("bear-들기-웃음")), ("winky-hand", R["winky"], src("winky-양손들기-웃음"))])
    elif cmd == "gen2": run([("notebook-closed", src("notebook-open"))])

# ── 2회차(크기 고침): 곰 손은 손바닥이 그림 폭의 50%(515px)라 팔이 짧다(판 1.75 px/mm에서 화면 아래 끝에서 잔 줄까지 못 닿음).
#    1회차 그림을 0.6배(가로세로 같은 배율)로 줄여 손끝을 위 60px에 놓은 기준 그림을 만들고 「소매를 아래 끝까지 이어라」로 편집한다.
#    기록장 펼침은 2.05:1로 나와(레지스트리 300×210 = 1.43:1) 비율을 고쳐 다시 그린다.
def shrink_ref(n, s=0.6, top=60):
    im = Image.open(os.path.join(GEN, n + ".png")).convert("RGBA"); bb = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox(); im = im.crop(bb)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS); C = Image.new("RGBA", (1024, 1536), MAG + (255,))
    C.alpha_composite(im, ((1024 - im.width) // 2, top)); out = os.path.join(REF, n + "-small.png"); C.convert("RGB").save(out); os.makedirs(os.path.join(REF, "v1"), exist_ok=True)
    os.replace(os.path.join(GEN, n + ".png"), os.path.join(REF, "v1", n + ".png")); return out
EXT = ("EDIT the attached first picture (the arm on magenta). Keep the paw{p} EXACTLY as it is: same size, same position at the top, same shape, colors and paper texture. "
       "Change only: the sky-blue sleeve must continue straight down, same width and same paper, all the way to the BOTTOM edge of the picture and be cut off by it "
       "(no end of the sleeve visible). Nothing else in the picture. Top-down flat view." + ALPHA)
P["bear-hand-flat2"] = ("1024x1536", "magenta", EXT.format(p=""))
P["bear-hand-pencil2"] = ("1024x1536", "magenta", EXT.format(p=" and the pencil it holds"))
P["notebook-open2"] = ("1536x1024", "magenta",
   "Redraw the attached open notebook (same style, colors, paper, same table on the right page) with the RIGHT PROPORTIONS: the whole open notebook is "
   "1300 px wide and 910 px tall (ratio 10:7), centered; each page is a tall PORTRAIT page (5:7). " + TOP + " The RIGHT page holds the table: FOUR equal "
   "tall rows filling the page; in each row a BLANK label box on the left that is a wide rectangle (about 30% of the row width, nearly as tall as the row) and "
   "a wide writing area to its right. Rows 1-3 writing areas: only a few faint light-gray squiggle lines (never letters). Row 4 writing area: completely EMPTY, "
   "just two thin pale ruled lines low in the area with lots of white space above. LEFT page: blank white with a few faint pale ruled lines. "
   "No letters, no numbers, no text anywhere." + ALPHA)
def gen3():
    jobs = [("bear-hand-flat", shrink_ref("bear-hand-flat")), ("bear-hand-pencil", shrink_ref("bear-hand-pencil"))]
    os.makedirs(os.path.join(REF, "v1"), exist_ok=True); nb = os.path.join(REF, "v1", "notebook-open.png"); os.replace(os.path.join(GEN, "notebook-open.png"), nb)
    ps = []
    for n, r in jobs + [("notebook-open", nb)]:
        size, key, prompt = P[n + "2"]; log = open(os.path.join(REF, n + "-2.run.log"), "w")
        ps.append(subprocess.Popen([os.path.join(KITS, "gen.sh"), n, size, key, prompt, r], stdout=log, stderr=log))
    for p in ps: p.wait()
    for n in ("bear-hand-flat", "bear-hand-pencil", "notebook-open"): print("OK" if os.path.exists(os.path.join(GEN, n + ".png")) else "FAIL", n)
if __name__ == "__main__" and sys.argv[1] == "gen3": gen3()

# ── 3회차: 기록장 펼침이 1.70:1로 나왔다(레지스트리 1.43:1, 폭에 맞추면 높이 −16%). 지금 그림을 목표 비율 칸(1300×910)에 맞춰 늘린
#    배치 안내 그림(렌더에는 안 씀)을 붙여 「이 칸을 꼭 채워 다시 그려라」로 편집한다.
def gen4():
    v2 = os.path.join(REF, "v2"); os.makedirs(v2, exist_ok=True); cur = os.path.join(v2, "notebook-open.png"); os.replace(os.path.join(GEN, "notebook-open.png"), cur)
    im = Image.open(cur).convert("RGBA"); im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()).resize((1300, 910), Image.LANCZOS)
    C = Image.new("RGBA", (1536, 1024), MAG + (255,)); C.alpha_composite(im, (118, 57)); guide = os.path.join(REF, "notebook-open-guide.png"); C.convert("RGB").save(guide)
    pr = ("EDIT the attached first picture: it shows the open notebook already at the CORRECT outline size and position (1300 x 910 px, ratio 10:7), but stretched. "
          "Redraw it cleanly at exactly that outline (same outer edges, same position), with undistorted round corners, the same pale sky-blue cover edge, white pages, "
          "the same table on the right page (four rows, blank rounded label boxes on the left, faint gray squiggles in rows 1-3, row 4 empty with two thin ruled lines "
          "low in the area) and faint ruled lines on the left page. " + TOP + " No letters, no numbers, no text anywhere." + ALPHA)
    log = open(os.path.join(REF, "notebook-open-3.run.log"), "w")
    subprocess.run([os.path.join(KITS, "gen.sh"), "notebook-open", "1536x1024", "magenta", pr, guide], stdout=log, stderr=log)
    print("OK" if os.path.exists(os.path.join(GEN, "notebook-open.png")) else "FAIL", "notebook-open")
if __name__ == "__main__" and sys.argv[1] == "gen4": gen4()

# ── 연필 크기 고침(재기 → 줄이기): 2회차 그림에서 연필 408px, 손바닥 폭 280px → 165mm 손에 240mm 연필(레지스트리 175mm, +37%).
#    「연필만 73%로 줄여라」 편집. 기준 그림 = 지금 그림 + 목표 길이 연필 자리(같은 그림을 0.73배로 줄인 연필 영역은 못 오려 내므로 말로만 준다).
def gen5(scale=73, now=408, want=298):
    v = os.path.join(REF, "v2"); os.makedirs(v, exist_ok=True); cur = os.path.join(v, "bear-hand-pencil.png"); os.replace(os.path.join(GEN, "bear-hand-pencil.png"), cur)
    pr = ("EDIT the attached first picture. Keep EVERYTHING identical (the bear paw size, shape, position, the sky-blue sleeve down to the bottom edge, colors, paper texture); "
          f"change ONLY the pencil: make the pencil SHORTER and a bit thinner, scaled down to {scale}% of its current size (total length from the gray tip to the white eraser "
          f"about {want} px instead of {now} px), still held the same way in the paw, the sharpened gray TIP still pointing to the UPPER-LEFT and sticking out beyond the "
          "paw's upper-left edge so the tip is the top-left-most point of the picture. The paw now covers more of the pencil." + ALPHA)
    log = open(os.path.join(REF, "bear-hand-pencil-3.run.log"), "w")
    subprocess.run([os.path.join(KITS, "gen.sh"), "bear-hand-pencil", "1024x1536", "magenta", pr, cur], stdout=log, stderr=log)
    print("OK" if os.path.exists(os.path.join(GEN, "bear-hand-pencil.png")) else "FAIL", "bear-hand-pencil")
if __name__ == "__main__" and sys.argv[1] == "gen5": gen5()

# ── 연필 손 큰 판(15·17번용): 기록장 칸 글자가 판 2.3 px/mm에서 27px로 너무 작다. 글자를 읽히게 15·17번만 4.0 px/mm로 잡으면
#    손바닥 660px가 되어 지금 그림(손바닥 300px)으로는 확대 2.2배라 한도(1.3)를 넘는다. 지금 그림을 1.85배로 키운 배치 안내 그림을 붙여
#    「이 크기로 또렷하게 다시 그려라」로 편집한다(연필 길이 비율·쥔 모양 그대로).
def gen6(s=1.85):
    v = os.path.join(REF, "v3"); os.makedirs(v, exist_ok=True); cur = os.path.join(v, "bear-hand-pencil.png"); import shutil; shutil.copy(os.path.join(GEN, "bear-hand-pencil.png"), cur)
    a = np.asarray(Image.open(cur)).copy(); haze = (a[..., 3] < 230) & (a[..., :3].max(-1) < 40); a[..., 3][haze] = 0
    im = Image.fromarray(a); im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox())
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS); C = Image.new("RGBA", (1024, 1536), MAG + (255,)); C.alpha_composite(im, ((1024 - im.width) // 2, 40))
    guide = os.path.join(REF, "bear-hand-pencil-big-guide.png"); C.convert("RGB").save(guide)
    pr = ("EDIT the attached first picture: a bear paw holding a pencil, already at the CORRECT size and position but blurry because it was enlarged. Redraw it crisp and clean "
          "at exactly this size and position: the same brown paw (same shape, same fingers), the same pale-wood pencil with gray tip pointing to the upper-left and white eraser, "
          "same pencil length relative to the paw, the same sky-blue sleeve running straight down to the bottom edge and cut off by it. " + TOP + " Nothing else." + ALPHA)
    log = open(os.path.join(REF, "bear-hand-pencil-big.run.log"), "w")
    subprocess.run([os.path.join(KITS, "gen.sh"), "bear-hand-pencil-big", "1024x1536", "magenta", pr, guide], stdout=log, stderr=log)
    print("OK" if os.path.exists(os.path.join(GEN, "bear-hand-pencil-big.png")) else "FAIL", "bear-hand-pencil-big")
if __name__ == "__main__" and sys.argv[1] == "gen6": gen6()
