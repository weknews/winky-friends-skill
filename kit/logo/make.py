"""로고 시안 묶기: A(그림 모델이 글자까지) 그대로, B(글자 없는 판 + 우리 글꼴 종이 글자) 합성 → cand/*.png, LOGO-REVIEW.png
사용: python3 make.py"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from papertext import paper_text, NAVY, CREAM, WHITE
H = os.path.dirname(os.path.abspath(__file__)); os.makedirs(f"{H}/cand", exist_ok=True)
G = lambda n: Image.open(f"{H}/gen/{n}.png").convert("RGBA")

def put(base, t, cx, cy, maxw=None):
    if maxw and t.width > maxw: t = t.resize((maxw, round(t.height * maxw / t.width)), Image.LANCZOS)
    base.alpha_composite(t, (round(cx - t.width / 2), round(cy - t.height / 2))); return base

def clean(im, f=4):
    """생성 그림 둘레의 반투명 부스러기(떨어진 작은 조각)를 지운다: 1/4 축소 마스크에서 덩어리를 세고 큰 덩어리만 남긴다."""
    import numpy as np
    from collections import deque
    a = np.asarray(im.getchannel("A")); m = np.asarray(im.getchannel("A").resize((im.width // f, im.height // f))) > 60
    lab = np.zeros(m.shape, int); sizes = [0]; h, w = m.shape
    for y0 in range(h):
        for x0 in range(w):
            if m[y0, x0] and not lab[y0, x0]:
                n = len(sizes); sizes.append(0); dq = deque([(y0, x0)]); lab[y0, x0] = n
                while dq:
                    y, x = dq.popleft(); sizes[n] += 1
                    for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                        if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not lab[yy, xx]: lab[yy, xx] = n; dq.append((yy, xx))
    big = max(sizes); keep = np.isin(lab, [i for i, s in enumerate(sizes) if i and s >= big * 0.02])
    k = Image.fromarray((keep * 255).astype("uint8")).resize(im.size).filter(ImageFilter.MaxFilter(9))
    out = im.copy(); out.putalpha(Image.fromarray(np.minimum(a, np.asarray(k)))); return out

def crop(im, pad=12):
    im = clean(im)
    x0, y0, x1, y1 = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))

# B1 가로형: 크림 판(x 200~1345, y 520~690)에 도현 제목, 모래 띠(y 690~750)에 주아 부제. 윙키가 판 왼쪽 위를 덮으니 제목은 오른쪽으로 비킨다
b1 = G("B1-wide-blank")
put(b1, paper_text("윙키와 친구들", "DoHyeon", 132, rim=WHITE, outer=CREAM, seed=3), 820, 598, maxw=940)
put(b1, paper_text("모래언덕 빌라", "Jua", 46, rim=WHITE, outer=WHITE, rim_w=4, seed=5), 690, 712)
# B2 세로 스택형: 판(y 490~830) 두 줄, 띠(y 900~1000) 부제
b2 = G("B2-stack-blank")
put(b2, paper_text("윙키와", "DoHyeon", 170, rim=WHITE, outer=CREAM, seed=7), 500, 600)
put(b2, paper_text("친구들", "DoHyeon", 170, rim=WHITE, outer=CREAM, seed=8), 500, 755)
put(b2, paper_text("모래언덕 빌라", "Jua", 58, rim=WHITE, outer=WHITE, rim_w=5, seed=9), 470, 952)

C = {"A1-wide": crop(G("A1-wide")), "A2-stack": crop(G("A2-stack")), "B1-wide": crop(b1), "B2-stack": crop(b2),
     "A3-inline": crop(G("A3-inline")), "A4-inline-under": crop(G("A4-inline-under"))}
for k, v in C.items(): v.save(f"{H}/cand/{k}.png")

# 비교판: 시안마다 큰 것 + 쇼츠 크기(폭 200·120px)를 밝은 배경(1화 편 색 연두)과 짙은 배경(남색)에 
NOTE = {"A1-wide": "A1 가로형, 그림 모델이 글자까지", "A2-stack": "A2 세로 스택형, 그림 모델이 글자까지",
        "B1-wide": "B1 가로형, 빈 판 + 도현+주아 종이 글자", "B2-stack": "B2 세로 스택형, 빈 판 + 도현+주아 종이 글자",
        "A3-inline": "A3 한 줄형(A1 편집), 영상 첫 컷용", "A4-inline-under": "A4 두 단 납작형(A1 편집)"}
PICK = "A1-wide"
F = lambda px: ImageFont.truetype(f"{H}/../ep01-v9/fonts/Jua-Regular.ttf", px)
CW, CH = 1100, 640; board = Image.new("RGB", (CW * 2, CH * 3 + 120), (250, 248, 242)); d = ImageDraw.Draw(board)
d.text((40, 30), "윙키와 친구들 / 모래언덕 빌라 시리즈 로고 시안 (2026-11-11)   ★ = 고른 것", font=F(54), fill=(16, 35, 63))
fit = lambda im, w, h: im.resize((max(1, round(im.width * min(w / im.width, h / im.height))), max(1, round(im.height * min(w / im.width, h / im.height)))), Image.LANCZOS)
for i, k in enumerate(NOTE):
    x, y = (i % 2) * CW, 120 + (i // 2) * CH; im = C[k]
    cell = Image.new("RGBA", (CW - 20, CH - 20), (221, 243, 206, 255)); cell.alpha_composite(Image.new("RGBA", (300, CH - 20), (16, 35, 63, 255)), (CW - 320, 0))
    big = fit(im, 720, 470); cell.alpha_composite(big, ((760 - big.width) // 2, 70 + (470 - big.height) // 2))
    for j, sw in enumerate((200, 120)):
        s1 = fit(im, sw, 200); cell.alpha_composite(s1, (CW - 320 + (300 - s1.width) // 2, 90 + j * 260))
    board.paste(cell.convert("RGB"), (x + 10, y + 10))
    d.text((x + 34, y + 22), ("★ " if k == PICK else "") + NOTE[k], font=F(40), fill=(16, 35, 63))
    d.text((x + CW - 300, y + 22), "폭 200 / 120px", font=F(30), fill=(250, 248, 242))
board.save(f"{H}/LOGO-REVIEW.png")

# 고른 것: 큰 로고 = A1, 한 줄형 = A3(README.md). 영상 키트에도 같은 파일을 둔다
C["A1-wide"].save(f"{H}/logo-main.png"); C["A3-inline"].save(f"{H}/logo-inline.png")
import shutil
for n in ("logo-main", "logo-inline"): shutil.copy(f"{H}/{n}.png", f"{H}/../ep01-v9/kit/{n}.png")
