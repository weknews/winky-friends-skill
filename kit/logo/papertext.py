"""글꼴 글자를 래스터화해 종이 오린 글자 PNG로 만든다(B 방식). CSS 그림자가 아니라 그림이다.
겹: 짙은 종이 그림자(아래로 비킨 흐린 남색) → 흰 종이 테두리(넓게 팽창) → 크림 테두리 → 남색 글자. 각 겹에 종이 섬유 잡음.
사용: from papertext import paper_text; paper_text("윙키와 친구들", "DoHyeon", 200) → RGBA Image"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../ep01-v9/fonts")
FF = {"DoHyeon": "DoHyeon-Regular.ttf", "Jua": "Jua-Regular.ttf"}
NAVY, CREAM, WHITE, SHADOW = (16, 35, 63), (243, 227, 200), (252, 250, 244), (16, 35, 63)

def _mask(s, font, px, pad):
    f = ImageFont.truetype(os.path.join(FONTS, FF[font]), px)
    l, t, r, b = f.getbbox(s)
    im = Image.new("L", (r - l + 2 * pad, b - t + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - l, pad - t), s, font=f, fill=255)
    return im

def _grow(m, r):                                   # 둥근 팽창(오린 종이 가장자리처럼 모서리가 둥글다)
    return m.filter(ImageFilter.GaussianBlur(r * 0.55)).point(lambda v: 255 if v > 22 else 0) if r else m

def _paper(size, rgb, seed, amp=4):               # 섬유 잡음: 가는 결 + 넓은 얼룩
    rnd = np.random.default_rng(seed); h, w = size[1], size[0]
    fine = rnd.normal(0, 1, (h, w)); fine = np.asarray(Image.fromarray(((fine * 40) + 128).clip(0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.6)), float) - 128
    blot = np.asarray(Image.fromarray((rnd.normal(0, 1, (h // 16 + 1, w // 16 + 1)) * 40 + 128).clip(0, 255).astype("uint8")).resize((w, h), Image.BICUBIC), float) - 128
    n = (fine * 0.12 + blot * 0.08) * amp / 7
    a = np.stack([np.full((h, w), c, float) + n for c in rgb], -1).clip(0, 255).astype("uint8")
    return Image.fromarray(a, "RGB")

def paper_text(s, font, px, fill=NAVY, rim=CREAM, outer=WHITE, rim_w=None, seed=1):
    rw = rim_w or max(4, round(px * 0.11)); pad = rw * 3 + px // 6
    m = _mask(s, font, px, pad)
    m_rim = _grow(m, rw); m_out = _grow(m, round(rw * 1.6))
    W, H = m.size; out = Image.new("RGBA", (W, H + pad // 2), (0, 0, 0, 0))
    sh = m_out.filter(ImageFilter.GaussianBlur(rw * 0.5)).point(lambda v: v * 0.32)    # 겹 그림자: 아래로 비킨 흐린 남색
    out.paste(Image.new("RGB", m.size, SHADOW), (round(rw * 0.25), round(rw * 0.55)), sh)
    for msk, col, sd, off in ((m_out, outer, seed, 0), (m_rim, rim, seed + 1, 0), (m, fill, seed + 2, 0)):
        if msk is not m_out:                                                         # 겹 사이 얇은 그림자
            out.paste(Image.new("RGB", m.size, SHADOW), (0, round(rw * 0.2)), msk.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: v * 0.22))
        out.paste(_paper(m.size, col, sd), (0, off), msk.filter(ImageFilter.GaussianBlur(0.7)))
    return out.crop(out.getbbox())

if __name__ == "__main__":
    t = paper_text("윙키와 친구들", "DoHyeon", 200); assert t.size[0] > 1000 and t.getbbox()
    t.save("/tmp/pt-test.png") if False else None
    print("ok", t.size)
