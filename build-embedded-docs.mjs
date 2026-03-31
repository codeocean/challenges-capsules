import { promises as fs } from "node:fs";
import path from "node:path";

const root = process.cwd();
const reviewDir = path.join(root, "review-challanges-iteration-03");

async function fileExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function readIfExists(targetPath) {
  return (await fileExists(targetPath)) ? fs.readFile(targetPath, "utf8") : "";
}

async function build() {
  const entries = await fs.readdir(root, { withFileTypes: true });
  const challengeDirs = entries
    .filter((entry) => entry.isDirectory() && /^challenge_\d{2}_/.test(entry.name))
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b));

  const docs = {};

  for (const directory of challengeDirs) {
    const match = directory.match(/^challenge_(\d{2})_/);
    if (!match) continue;

    const number = match[1];
    const id = `challenge-${number}`;
    const readmePath = path.join(root, directory, "code", "README.md");
    const reviewPath = path.join(reviewDir, `${id}-review.md`);

    docs[id] = {
      readmeMarkdown: await readIfExists(readmePath),
      reviewMarkdown: await readIfExists(reviewPath)
    };
  }

  const output = `window.CAPSULE_DOCS = ${JSON.stringify(docs, null, 2)};\n`;
  await fs.writeFile(path.join(root, "capsule-docs.js"), output, "utf8");
}

await build();
