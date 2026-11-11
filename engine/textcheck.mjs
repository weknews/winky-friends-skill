// KIT-SPEC 6·7절 8번: 렌더된 칸 글자(상자 라벨·소개 카드)의 글자 상자를 브라우저에서 재서 칸 밖으로 1px이라도 나가면 실패.
// 또 모든 글자 요소가 화면 안전 여백(좌우 60, 위 200, 아래 220) 안인지 잰다. 사용: node textcheck.mjs
import puppeteer from "puppeteer-core";
import { CHROME } from "./chrome.mjs";
import { pathToFileURL } from "node:url";
const b = await puppeteer.launch({ executablePath: CHROME, headless: "shell", args: ["--allow-file-access-from-files"] });
const p = await b.newPage(); await p.setViewport({ width: 1080, height: 1920 });
await p.goto(pathToFileURL("index.html").href + "?still", { waitUntil: "load" });
const res = await p.evaluate(async () => {
  await document.fonts.ready; const out = [];
  document.querySelectorAll(".txt").forEach((d) => {
    const r = document.createRange(); r.selectNodeContents(d);
    const L = d.offsetLeft, T = d.offsetTop, W = d.scrollWidth, H = d.offsetHeight;        // 변환 전 배치(카드 기울임·흔들림 제외)
    const row = { s: d.textContent, x0: L, y0: T, x1: L + W, y1: T + H };
    if (d.dataset.box) { const [a, bb, c, e] = d.dataset.box.split(",").map(Number); row.box = [a, bb, c, e]; row.inBox = L >= a - 1 && T >= bb - 1 && L + W <= c + 1 && T + H <= e + 1; }
    row.safe = L >= 59 && L + W <= 1021 && T >= 199 && T + H <= 1701;
    out.push(row);
  });
  return out;
});
await b.close();
let fail = 0;
for (const r of res) {
  if (r.box && !r.inBox) { fail++; console.log("칸 밖", r.s, r); }
  if (!r.safe) { fail++; console.log("안전 여백 밖", r.s, [r.x0, r.y0, r.x1, r.y1].map(Math.round)); }
}
console.log(`글자 ${res.length}개, 칸 글자 ${res.filter((r) => r.box).length}개, 실패 ${fail}`);
process.exit(fail ? 1 : 0);
