import { cp, mkdir, writeFile } from "node:fs/promises";

await mkdir("public/matches", { recursive: true });
await cp("index.html", "public/index.html");
await cp("matches/jfl-preview.png", "public/matches/jfl-preview.png");
await writeFile("public/matches/published.js", "window.jflDynamicShares = true;\n");
