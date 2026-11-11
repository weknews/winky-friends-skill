// 빠른 확인용: 지정한 시각의 프레임을 찍는다.  node shot.mjs 0.5 1.0 ...  → out/shots/t0050.jpg
// 시각을 안 주면 2초 간격(0, 2, …)과 끝 0.5초 전을 찍는다. 저장 폴더는 OUT 환경 변수(기본 out/shots)
import puppeteer from "puppeteer-core";
import { CHROME } from "./chrome.mjs";
import { pathToFileURL } from "node:url";
import fs from "node:fs";
let times = process.argv.slice(2).map(Number);
fs.mkdirSync((process.env.OUT || "out/shots"), { recursive: true });
const b = await puppeteer.launch({ executablePath: CHROME, headless: "shell", args: ["--allow-file-access-from-files"] });
const p = await b.newPage(); await p.setViewport({ width: 1080, height: 1920 });
p.on("pageerror", (e) => console.log("PAGEERROR", e.message)); p.on("console", (m) => m.type() === "error" && console.log("CONSOLE", m.text()));
await p.goto(pathToFileURL("index.html").href + "?still", { waitUntil: "load" });
await p.evaluate(async () => { await document.fonts.ready; return 1; });
if (!times.length) { const D = await p.evaluate(() => window.__timelines.main.duration()); for (let t = 0; t < D - 1; t += 2) times.push(t); times.push(D - 0.5); }
for (const t of times) { await p.evaluate((t) => { window.__timelines.main.seek(t); return 1; }, t); await p.screenshot({ path: `${process.env.OUT || "out/shots"}/t${String(Math.round(t * 100)).padStart(4, "0")}.jpg`, quality: 80 }); }
await b.close();
