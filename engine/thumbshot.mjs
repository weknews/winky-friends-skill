// 썸네일 찍기(회차 폴더에서): thumb.html → out/thumb.png, 글자 상자가 안전 여백(좌우 60, 위 200, 아래 220) 안인지 잰다. 사용: node thumbshot.mjs
import puppeteer from "puppeteer-core";
import { CHROME } from "./chrome.mjs";
import { pathToFileURL } from "node:url";
const b = await puppeteer.launch({ executablePath: CHROME, headless: "shell", args: ["--allow-file-access-from-files"] });
const p = await b.newPage(); await p.setViewport({ width: 1080, height: 1920 }); p.on("pageerror", (e) => console.log("PAGEERROR", e.message));
await p.goto(pathToFileURL("thumb.html").href, { waitUntil: "load" });
const r = await p.evaluate(async () => { await document.fonts.ready; await Promise.all([...document.images].map((i) => i.decode())); return [...document.querySelectorAll(".t, #logo")].map((d) => { const g = document.createRange(); g.selectNodeContents(d); const q = d.id === "logo" ? d.getBoundingClientRect() : g.getBoundingClientRect(); return { s: d.textContent || d.id, px: parseFloat(d.style.fontSize), x0: q.left, x1: q.right, y0: q.top, y1: q.bottom }; }); });
await p.screenshot({ path: "out/thumb.png" }); await b.close();
let fail = 0; for (const t of r) { const ok = t.x0 >= 60 && t.x1 <= 1020 && t.y0 >= 200 && t.y1 <= 1700; if (!ok) fail++; console.log(ok ? "통과" : "실패", t.s, t.px + "px", [t.x0, t.y0, t.x1, t.y1].map(Math.round)); }
process.exit(fail ? 1 : 0);
