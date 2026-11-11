// 확인 스크립트(shot·textcheck·thumbshot)가 쓰는 크롬 경로. CHROME 환경 변수가 있으면 그것을, 없으면 hyperframes가 받아 둔
// chrome-headless-shell을 쓴다(없으면 받는다). OS마다 다른 경로를 직접 적지 않는다.
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
const hf = fileURLToPath(new URL("node_modules/hyperframes/bin/hyperframes.mjs", import.meta.url));
const run = (sub) => execFileSync(process.execPath, [hf, "browser", sub], { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim().split(/\r?\n/).pop();
function find() {
  try { return run("path"); } catch {}
  try { run("ensure"); return run("path"); } catch {}
  console.error("크롬을 찾지 못했다. engine 폴더에서 npm install 을 했는지 보고, 안 되면 CHROME 환경 변수에 크롬 실행 파일 경로를 준다.");
  process.exit(1);
}
export const CHROME = process.env.CHROME || find();
