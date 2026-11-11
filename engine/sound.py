"""윙키와 친구들 소리(엔진, 원본 ep01-v9 sound.py 9e판): 목소리(음절 소리) + 효과음(numpy 합성) + 음악 큐 3개(Q-TIME, Q-DOWN, Q-END) → out/audio.wav (48kHz 스테레오)
- 목소리: KIT-SPEC 5절. 자막 음절마다 초성에 맞는 짧은 소리. 음원은 tools/PyAnimalese/sources(MIT, 초성 19개 녹음).
  음절 시각·반음·음량은 build.py가 계산한 scene.json 그대로(자막과 같은 시계).
- 효과음: ep01/sfx.py 합성 함수를 옮겨 와 대본 효과음을 낸다. 9판에 톡·사각·스윽을 더했다(아래 SFX). 대사와 겹치면 −6dB.
  7b: 아이리스 아웃의 「띠로리」(슬라이드 휘슬)·「뿅」은 lemo-opuscar(MIT) 함수를 옮겼다(아래 주석).
- 9b 음악(숏폼 원칙, 제작자 11/11 — 「대사 컷엔 음악 없음」을 대체): 장면마다 배경음악을 계속 깔고 대사 중엔 덕킹(9b −11dB, 9c −8dB: 상담소 bed-awkward가 대사 중 너무 작아서).
  오프닝 theme-a 앞 소절, 부엌 bed-bright, 상담소 bed-awkward, 저녁 부엌 bed-bright. 이음새는 Q-TIME·Q-DOWN 스팅.
  윙키 「주스만 세 잔이요.」 뒤 뚝 끊고 babam, 곰 「두 잔이 한 잔이지.」 뒤 boing, 펭귄 「치죠.」 뒤 wahwah(18번까지 정적). 끝은 theme-a 끝.
- 음량: 전체 −15 LUFS(허용 −14~−16), 최대 −1.5 dBTP 이하. 목소리 압축은 가볍게(문턱 = 목소리 최댓값 −8dB에서 시작, 2:1).
- 장면 시각 0 앞에 썸네일 0.4초(OFF)가 붙는다. 그동안 theme-a가 먼저 시작한다.
- 음악은 kit/registry.json music의 「정식 음원 세트」만 쓴다. 파일의 sha256이 레지스트리와 다르면 멈춘다(사람마다 다른 음원 금지, rules/music.md).
- 회차마다 다른 것(음악 큐 배치, 사각 소리 길이, 구간별 음량을 잴 구간)은 EP/sound_cues.py에 있고 여기서 exec 한다.
사용: cd episodes/<회차> && python3 ../../engine/sound.py"""
import json, os, re, shutil, subprocess, sys, wave, random, hashlib
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EP = os.path.abspath(os.environ.get("EP", os.getcwd())); HERE = EP
sys.stdout.reconfigure(encoding="utf-8")                                 # Windows 콘솔·파이프에서도 한글 출력이 멈추지 않게
if not shutil.which("ffmpeg"): sys.exit("ffmpeg를 찾지 못했다. README 「준비물」대로 설치하고 새 터미널에서 다시 돈다")
REGISTRY = json.load(open(os.path.join(ROOT, "kit/registry.json"), encoding="utf-8"))
SR = 48000
S = json.load(open(os.path.join(HERE, "scene.json"), encoding="utf-8")); D = S["D"]
OFF = 0.4                                             # 9b: 맨 앞 썸네일 컷(0.4초). 장면 시각 t는 완성 파일에서 t + OFF
N = int(SR * (D + OFF))
VOX_SRC = os.path.join(ROOT, "tools/PyAnimalese/sources")             # git에 없다. README 「준비물」대로 클론
if not os.path.isdir(VOX_SRC): sys.exit("tools/PyAnimalese 가 없다. 레포 뿌리에서 git clone https://github.com/hwi-middle/PyAnimalese tools/PyAnimalese")
rng = np.random.default_rng(1111)
T = lambda d: np.arange(int(SR * d)) / SR

def rd(f):
    w = wave.open(f); n = w.getnframes(); sr = w.getframerate(); ch = w.getnchannels()
    a = np.frombuffer(w.readframes(n), dtype=np.int16).reshape(-1, ch).astype(float) / 32768
    assert sr == SR, (f, sr); return a if ch == 2 else np.repeat(a, 2, 1)
def mp3(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-f", "mp3", "-i", f, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(float)
def add(bus, t, x, g=1.0, pan=0.0):
    i = int(round(SR * (t + OFF))); x = x[: max(0, N - i)]; a = (pan + 1) * np.pi / 4
    if x.ndim == 1: bus[i:i + len(x), 0] += x * g * np.cos(a); bus[i:i + len(x), 1] += x * g * np.sin(a)
    else: bus[i:i + len(x)] += x * g
def resample(x, f):                                  # 재생 속도 f배(음높이 함께 오름)
    n = int(len(x) / f); return np.interp(np.arange(n) * f, np.arange(len(x)), x)

# ── ep01/sfx.py 에서 옮긴 합성 함수(필요한 것만)
def filt(x, lo=0.0, hi=SR / 2):
    X = np.fft.rfft(x); f = np.maximum(np.fft.rfftfreq(len(x), 1 / SR), 1.0)
    return np.fft.irfft(X / (1 + (lo / f) ** 4) / (1 + (f / hi) ** 4), len(x))
def noise(d, lo=0.0, hi=SR / 2): return filt(rng.standard_normal(int(SR * d)), lo, hi)
def ad(d, a=0.004, k=20.0): t = T(d); return np.minimum(t / a, 1) * np.exp(-k * t)
def sweep(f0, f1, d, h2=0.0):
    ph = 2 * np.pi * np.cumsum(f0 * (f1 / f0) ** (T(d) / d)) / SR
    return np.sin(ph) + h2 * np.sin(2 * ph)
def lay(*xs):
    out = np.zeros(max(map(len, xs)))
    for x in xs: out[: len(x)] += x
    return out
def thump(f0, f1, d, k=18): return sweep(f0, f1, d) * ad(d, 0.003, k)
def tick(d=0.03, lo=2000, hi=9000, k=140): return noise(d, lo, hi) * ad(d, 0.0005, k) * 4
def bell(f, d, k=4.0):
    t = T(d); return sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-k * m * t) for r, a, m in ((1, 1, 1), (2.76, .35, 2.2), (5.4, .15, 4), (8.9, .06, 7))) * np.minimum(t / .002, 1)
def pour(d):
    x = noise(d, 1500, 7000) * .5
    for t in np.sort(rng.uniform(0, d - .06, int(d * 70))):
        f = rng.uniform(450, 900) * (1 + 0.9 * t / d); g = sweep(f, f * 1.5, .04) * ad(.04, .003, 60); i = int(SR * t); x[i:i + len(g)] += g * rng.uniform(.3, 1)
    e = np.minimum(T(d) / .15, 1) * np.minimum((d - T(d)) / .2, 1); return x * e
def nz(x): return x / np.abs(x).max()
def crunch():                                        # 아삭(ep01/sfx.py 그대로): 짧은 알갱이 여러 개 + 낮은 몸통
    x = np.zeros(int(SR * .22))
    for t in np.sort(rng.uniform(0, .12, 11)):
        g = tick(.02, 1500, 9000, 220) * rng.uniform(.4, 1); i = int(SR * t); x[i:i + len(g)] += g
    return x + noise(.22, 300, 1200) * ad(.22, .002, 30) * 3
# ── 9판 새 효과음(같은 합성 함수로): 톡 = 플라스틱 잔·사과를 판에 놓는 짧은 소리(밝은 딸깍 + 낮고 짧은 몸통),
#    사각 = 연필이 종이를 긁는 소리(높은 대역 잡음 알갱이를 글자 박자로), 스윽 = 잔을 판 위로 미는 소리(마찰 잡음, 대역이 천천히 오른다)
def tok(): return lay(tick(.025, 1800, 7000, 180) * 1.2, thump(420, 260, .07, 45) * .9)
def scratch(d, n):
    x = np.zeros(int(SR * d)); 
    for k in range(n):
        t0 = k * d / n; g = noise(d / n * .8, 2500, 9000) * ad(d / n * .8, .004, 9) * rng.uniform(.6, 1); i = int(SR * t0); x[i:i + len(g)] += g
    return x
def swish(d):
    n = int(SR * d); u = np.linspace(0, 1, n)
    return (noise(d, 600, 2500) * (1 - u) + noise(d, 1500, 5000) * u) * np.sin(np.pi * u) ** 0.7
card = np.zeros(int(SR * .25))
for t, g in ((0, .6), (.035, 1)):
    c = tick(.03, 2500, 10000, 160) * g; i = int(SR * t); card[i:i + len(c)] += c
card[: int(SR * .12)] += noise(.12, 500, 4000) * ad(.12, .001, 45) * 3 + thump(150, 60, .12, 30) * 1.2
# ── 7b 아이리스 효과음: lemo-opuscar (https://github.com/lemomo-ai/lemo-opuscar, MIT License, © Lemomo)
#    styles/rubber-hose/demo/mix.py 의 slide_whistle·boing, core/audio/sfx.py 의 pop 을 옮겼다.
#    scipy 대역 필터(bp)만 이 파일의 noise(d, lo, hi)로 바꿨다. 나머지 식은 그대로.
def slide_whistle(f0, f1, d, vib=0):
    tt = T(d); f = f0 * (f1 / f0) ** (tt / d) * (1 + vib * np.sin(2 * np.pi * 6 * tt)); x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    x = x + .15 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR); e = np.minimum(1, tt / .03) * np.minimum(1, (d - tt) / .06)
    return nz(x * e + noise(d, 1500, 5000) * .03 * e)
def boing(f=210, d=.6, depth=.35):
    tt = T(d); f_ = f * (1 + depth * np.sin(2 * np.pi * 13 * tt) * np.exp(-tt * 4)); ph = 2 * np.pi * np.cumsum(f_) / SR
    return nz((np.sin(ph) + .4 * np.sin(2 * ph) + .2 * np.sin(3 * ph)) * np.exp(-tt * 4.5))
def pop_(v=1.0):
    d = .18; tt = T(d); f = 500 + 1400 * tt / d
    return nz(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / .05)) * v
SFX = {   # 이름: (소리, 상대 음량). 모두 최댓값 1로 맞춘 뒤 음량을 곱한다
 "띵동": (nz(lay(bell(659, 1.0, 3), np.pad(bell(523, 1.3, 2.5), (int(SR * .35), 0)))), .55),
 "탁": (nz(card), .55),
 "쿵": (nz(lay(thump(120, 45, .35, 9), noise(.12, 200, 1500) * ad(.12, .002, 40) * 2)), .7),
 "꿀꺽": (nz(lay(thump(200, 90, .12, 20), np.pad(thump(260, 110, .12, 20), (int(SR * .22), 0)) * .8)), .55),
 "쪼르륵": (nz(pour(0.5)), .4),
 "띠로리": (nz(slide_whistle(1250, 420, 0.42, 0.02)), .5),      # 아이리스가 줄 때 내려가는 슬라이드 휘슬
 "뿅": (nz(lay(boing(430, 0.32, 0.3), pop_(0.6) * 0.5)), .55),     # 닫히는 순간
 "삐질": (nz(sweep(1700, 850, .22) * ad(.22, .004, 12) + .3 * bell(2200, .22, 14)), .3),
 "아삭": (nz(crunch()), .5),
 "톡": (nz(tok()), .45),
 "스윽": (nz(swish(0.45)), .35),
}
# ── 목소리
CHO = 19
SRC = [mp3(os.path.join(VOX_SRC, f"{i:02d}.padata")) for i in range(1, CHO + 1)]
def onset(x): return int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max()))
SRC = [x[onset(x):] / np.abs(x).max() for x in SRC]
VOICE = {"bear": dict(semi=-7, jit=1.0), "panda": dict(semi=2, jit=1.0), "penguin": dict(semi=-2, jit=0.5), "winky": dict(semi=9, jit=1.0)}
RATE = {"bear": 7, "panda": 9, "penguin": 6, "winky": 10}
BASE = 12                                             # 기준 음높이: 녹음을 한 옥타브 올린 소리
def syl_sound(ch, semi, dur):
    cho = (ord(ch) - 0xAC00) // 588; f = 2 ** ((BASE + semi) / 12)
    src = SRC[cho]; L = int(SR * dur); x = resample(np.pad(src, (0, int(L * f) + 8)), f)[:L]
    env = np.minimum(np.arange(L) / (SR * .005), 1) * np.minimum((L - np.arange(L)) / (SR * .02), 1)
    x = x * env; rms = np.sqrt((x ** 2).mean()) + 1e-9
    x = x * (0.25 / rms); pk = np.abs(x).max()          # 음절마다 세기를 고르게(초성마다 녹음 크기가 다르다)
    return x * (0.9 / pk) if pk > 0.9 else x
PAN = {"좌": -0.25, "중": 0.0, "우": 0.25}
vox = np.zeros((N, 2)); sfx = np.zeros((N, 2)); mus = np.zeros((N, 2)); speech = []
for C in S["cuts"]:
    L = C["line"]
    if not L: continue
    who = L["who"]; v = VOICE[who]; r = random.Random(L["text"])          # 같은 대사는 늘 같은 소리
    lay_ = next((l for l in C["layers"] if l.get("who") == who), None); pan = PAN.get(lay_["at"], 0) if lay_ and C["cam"] != "CU" else 0
    for s in L["syl"]:
        emo = s.get("emo", ""); semi = v["semi"] + s["semi"] + r.uniform(-v["jit"], v["jit"]); db = s["db"]
        dur = min(0.09, 0.8 / RATE[who]) + (0.16 if s.get("long") else 0)      # 9판: 「~」 앞 음절은 늘인다
        if emo == "놀람": semi += 2
        if emo == "시무룩": semi -= 2; db -= 4
        if emo == "당황": semi += r.uniform(-2, 2); dur *= 0.7
        add(vox, s["t"], syl_sound(s["ch"], semi, max(dur, 0.06)), 10 ** (db / 20), pan)
    speech.append((L["syl"][0]["t"], L["end"]))
# ── 음악(9b): 버스 둘. bed = 오프닝·배경·끝 테마(덕킹 받음), sting = 스팅(덕킹 받음, 배경보다 크다)
def rdm(n):                                            # 정식 음원만: 레지스트리 approved + sha256 일치
    e = REGISTRY["music"].get(n)
    if not e or e.get("status") != "approved": raise SystemExit(f"음원 {n}: 레지스트리에 승인된 항목이 없다(rules/music.md)")
    f = os.path.join(ROOT, e["file"])
    if not os.path.exists(f):                          # 처음 실행: Release의 정식 음원 팩을 받는다
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import fetch_kit; fetch_kit.fetch()
    if hashlib.sha256(open(f, "rb").read()).hexdigest() != e["sha256"]: raise SystemExit(f"음원 {n}: sha256이 정식 음원과 다르다(바꾼 음원은 등록 절차를 거친다)")
    return rd(f)
theme, stings = rdm("theme-a"), rdm("stings-1")
def fade(x, fi, fo):
    n = len(x); e = np.ones(n); a, b = int(SR * fi), int(SR * fo)
    if a: e[:a] = np.linspace(0, 1, a)
    if b: e[n - b:] = np.minimum(e[n - b:], np.linspace(1, 0, b))
    return x * e[:, None]
def lufs_of(x):
    tmp = os.path.join(HERE, "out/_l.wav"); wr(tmp, x / (np.abs(x).max() + 1e-9) * 0.5)
    o = subprocess.run(["ffmpeg", "-nostats", "-i", tmp, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr; os.remove(tmp)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]) - 20 * np.log10(0.5 / (np.abs(x).max() + 1e-9))
def wr(f, x):
    with wave.open(f, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
def onset2(a, th=0.05): m = np.abs(a).max(1); return int(np.argmax(m > th * m.max()))
REF = -16.0                                           # 원본마다 통합 음량을 이 값으로 맞춘 뒤 버스 이득을 곱한다
def norm(a): return a * 10 ** ((REF - lufs_of(a)) / 20)
bright, awk = norm(rdm("bed-bright")), norm(rdm("bed-awkward")); theme_n = norm(theme)
ST = {k: norm(rdm("sting-" + k)) for k in ("babam", "boing", "wahwah")}
bed = np.zeros((N, 2)); sting = np.zeros((N, 2)); CUE_SRC = {}
def place(bus, t, src, s0, d, fi, fo, name, g=1.0):
    seg = fade(src[int(SR * s0): int(SR * (s0 + d))], fi, fo); add(bus, t, seg, g); CUE_SRC[name] = f"{t:.2f}~{t + d:.2f}초(장면 시각) ← 원본 {s0:.2f}~{s0 + d:.2f}초"
line_end = {C["n"]: C["line"]["end"] for C in S["cuts"] if C["line"]}
cut = {C["n"]: (C["t0"], C["t1"]) for C in S["cuts"]}
exec(compile(open(os.path.join(EP, "sound_cues.py"), encoding="utf-8").read(), os.path.join(EP, "sound_cues.py"), "exec"))   # 회차 음악 큐·SCRATCH·SECTIONS
# ── 효과음(대사와 겹치면 −6dB)
for C in S["cuts"]:
    for name, t in C["sfx"]:
        if name == "사각": d_, n_ = SCRATCH.pop(0); x, g = nz(scratch(d_, n_)), .3
        else: x, g = SFX[name]
        duck = any(a - 0.05 <= t <= b for a, b in speech)
        add(sfx, t, x, g * (0.5 if duck else 1.0))
# ── 덕킹: 목소리 구간(첫 음절 0.08초 앞 ~ 끝 0.15초 뒤)에서 −8dB(9b −11), 0.15초 이동 평균으로 붙고 떨어지게
DUCK_DB = -8.0
m = np.zeros(N)
for a, b in speech: m[max(0, int(SR * (a + OFF - 0.08))): int(SR * (b + OFF + 0.15))] = 1
k = int(SR * 0.15); m = np.convolve(m, np.ones(k) / k, "same"); duck = 10 ** (DUCK_DB * m / 20)
bed *= duck[:, None]; sting *= duck[:, None]
# ── 섞기
def loud(x):
    tmp = os.path.join(HERE, "out/_mix.wav"); wr(tmp, x)
    o = subprocess.run(["ffmpeg", "-nostats", "-i", tmp, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); P = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", o)[-1]); os.remove(tmp); return I, P
def bus_peak(x): return 20 * np.log10(np.abs(x).max() + 1e-9)
def comp(x, thr_db, ratio=2.0, win=0.005):              # 목소리 버스 압축: 5ms 창 RMS, 문턱 위를 ratio:1로
    mm = np.sqrt((x ** 2).mean(1)); n = int(SR * win); kk = len(mm) // n
    e = np.sqrt((mm[: kk * n] ** 2).reshape(kk, n).mean(1)) + 1e-9; db = 20 * np.log10(e)
    gdb = np.where(db > thr_db, (thr_db + (db - thr_db) / ratio) - db, 0.0)
    for i in range(1, kk): gdb[i] = min(gdb[i], gdb[i - 1] + 0.35)       # 풀림 약 70ms
    g = np.interp(np.arange(len(mm)), np.arange(kk) * n + n / 2, 10 ** (gdb / 20)); return x * g[:, None]
def plim(x, ceil_db, la=0.004, rel=0.06):            # 목소리 버스 앞보기 피크 리미터: 음절 머리의 짧은 튐(수 ms)만 깎는다
    c = 10 ** (ceil_db / 20); need = np.minimum(1.0, c / (np.abs(x).max(1) + 1e-12)); n = int(SR * la)
    from numpy.lib.stride_tricks import sliding_window_view as sw
    gmin = sw(np.pad(need, (n, n), constant_values=1.0), 2 * n + 1).min(1)        # 앞뒤 la 안의 최소 이득
    k = int(SR * rel); gs_ = np.convolve(np.pad(gmin, (k // 2, k - k // 2 - 1), constant_values=1.0), np.ones(k) / k, "valid")
    return x * np.minimum(gmin, gs_)[:, None]
gv = 0.5 / np.abs(vox).max(); vx = vox * gv
Iv = lufs_of(vx)
# 버스 이득(목소리 통합 음량 기준): 배경음악 −6 LU(덕킹되면 −17), 스팅 −2 LU, 효과음 최댓값은 목소리 최댓값 −4dB
gb = 10 ** ((Iv - 6 - REF) / 20); gst = 10 ** ((Iv - 2 - REF) / 20)
TARGET = -15.0; thr0 = bus_peak(vx) - 8; thr = thr0; lim = 0.0     # lim = 목소리 피크 리미터가 깎는 양(dB)
for it in range(16):
    v2 = comp(vx, thr); v2 = plim(v2, bus_peak(v2) - lim) if lim else v2
    gs = 10 ** ((bus_peak(v2) - 4 - bus_peak(sfx)) / 20)
    mix = v2 + sfx * gs + bed * gb + sting * gst
    I, P = loud(mix); g = 10 ** ((TARGET - I) / 20); I2, P2 = loud(mix * g)
    print(f"  목표 {TARGET} · 목소리 압축 문턱 {thr:.1f} dBFS · 피크 리미터 {lim:.0f}dB → {I2:.1f} LUFS, 최대 {P2:.1f} dBTP")
    if P2 <= -1.5: break
    if lim < 6: lim += 1.0                                 # 먼저 음절 머리 튐만 1dB씩(최대 6dB) 깎는다
    elif TARGET > -15.9: TARGET -= 0.5; lim = 0.0
    else: thr -= 1.5                                       # −16에서도 넘을 때만 압축을 더
mix *= g
wr(os.path.join(HERE, "out/audio.wav"), mix)
# ── 구간별 음량(버스별로 따로 잰다, 완성 음량 기준). 구간은 장면 시각
BUS = dict(voice=v2 * g, sfx=sfx * gs * g, music=(bed * gb + sting * gst) * g)
def win_lufs(x, a, b):
    seg = x[int(SR * (a + OFF)): int(SR * (b + OFF))]
    if np.abs(seg).max() < 1e-5: return None
    tmp = os.path.join(HERE, "out/_w.wav"); wr(tmp, seg)
    o = subprocess.run(["ffmpeg", "-nostats", "-i", tmp, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace").stderr; os.remove(tmp)
    v = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", o)[-1]); return None if v < -70 else v
sec = []
for name, a, b in SECTIONS:
    r = {k: win_lufs(x, a, b) for k, x in BUS.items()}; r = {k: (round(v, 1) if v is not None else None) for k, v in r.items()}
    sec.append(dict(구간=name, 장면시각=[round(a, 2), round(b, 2)], LUFS=r)); print(" ", name, r)
rep = dict(LUFS=I2, truePeak=P2, target=TARGET, offset=OFF, duck_dB=DUCK_DB, voice_comp=dict(thr_dBFS=round(thr, 1), ratio=2.0, start=round(thr0, 1), peak_limiter_dB=lim),
           cues=CUE_SRC, buses_dBFS={k: round(bus_peak(x), 1) for k, x in BUS.items()}, sections=sec)
json.dump(rep, open(os.path.join(HERE, "out/audio.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: rep[k] for k in ("LUFS", "truePeak", "target", "voice_comp", "buses_dBFS")}, ensure_ascii=False))
