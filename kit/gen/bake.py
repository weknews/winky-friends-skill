"""얼굴판 굽기: 표정만 바꾼 편집본에서 얼굴 칸만 잘라 기준 몸에 붙인다(rules/color.md와 같은 날, Fable 디렉터 안 2026-11-13).
몸은 기준 그림 그대로라 떨리지 않는다. 편집본이 몇 px 밀려 나와도 얼굴 칸 바깥(머리 테두리)으로 맞춰 붙인다.
사용: python3 kit/gen/bake.py 기준.png 편집본.png x0,y0,x1,y1 결과.png
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

def shift_of(base, edit, box, r=24):
    """얼굴 칸 둘레 띠(머리·가시)가 가장 잘 겹치는 (dx, dy). ponytail: 무식한 전수 탐색, 4배 줄여서 ±r px."""
    x0, y0, x1, y1 = box; k = 4
    g = lambda im: np.asarray(im.convert("L").resize((im.width // k, im.height // k)), dtype=float)
    a, b = g(base), g(edit)
    m = np.zeros_like(a, bool); m[max(0, (y0 - 80) // k):(y1 + 80) // k, max(0, (x0 - 80) // k):(x1 + 80) // k] = True
    m[y0 // k:y1 // k, x0 // k:x1 // k] = False  # 얼굴 칸은 표정이 달라서 빼고 둘레만 본다
    best = (1e18, 0, 0)
    for dy in range(-r // k, r // k + 1):
        for dx in range(-r // k, r // k + 1):
            e = np.roll(np.roll(b, dy, 0), dx, 1)
            best = min(best, (float(((a - e)[m] ** 2).mean()), dx * k, dy * k))
    return best[1], best[2]

def bake(base, edit, box):
    dx, dy = shift_of(base, edit, box)
    edit = Image.fromarray(np.roll(np.roll(np.asarray(edit.convert("RGB")), dy, 0), dx, 1))
    x0, y0, x1, y1 = box
    mask = Image.new("L", base.size, 0); mask.paste(255, (x0 + 12, y0 + 12, x1 - 12, y1 - 12))
    mask = mask.filter(ImageFilter.GaussianBlur(10))  # 이음매를 10px로 녹인다
    out = base.convert("RGB").copy(); out.paste(edit, (0, 0), mask)
    return out, (dx, dy)

def _check():
    base = Image.new("RGB", (200, 200), "white"); base.paste((0, 0, 0), (40, 40, 160, 160))
    edit = Image.fromarray(np.roll(np.asarray(base), 8, 1)); edit.paste((255, 0, 0), (90, 90, 110, 110))
    out, d = bake(base, edit, (70, 70, 130, 130))
    assert d == (-8, 0), d
    assert out.getpixel((10, 10)) == (255, 255, 255) and out.getpixel((100, 100))[0] > 200  # 바깥은 기준 그대로, 칸 안은 편집본

if __name__ == "__main__":
    _check()
    if len(sys.argv) == 5:
        b, e, box, o = sys.argv[1:]
        out, d = bake(Image.open(b), Image.open(e), tuple(int(v) for v in box.split(",")))
        out.save(o); print("구움", o, "밀림 보정", d)
