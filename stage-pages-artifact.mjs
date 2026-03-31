import { execFileSync } from "node:child_process";
import { promises as fs } from "node:fs";
import path from "node:path";

const root = process.cwd();
const outputDir = path.join(root, ".site");

function getVersionToken() {
  const envSha = String(process.env.GITHUB_SHA || "").trim();
  if (envSha) {
    return envSha.slice(0, 12);
  }

  return execFileSync("git", ["rev-parse", "--short=12", "HEAD"], {
    cwd: root,
    encoding: "utf8"
  }).trim();
}

function shouldIgnore(relativePath) {
  if (!relativePath) return false;

  const parts = relativePath.split(path.sep);
  return parts[0] === ".git" || parts[0] === ".github" || parts[0] === ".site";
}

async function copyRepoTree(versionToken) {
  await fs.rm(outputDir, { recursive: true, force: true });
  await fs.mkdir(outputDir, { recursive: true });

  const entries = await fs.readdir(root, { withFileTypes: true });
  for (const entry of entries) {
    const sourcePath = path.join(root, entry.name);
    const relativePath = entry.name;

    if (shouldIgnore(relativePath)) {
      continue;
    }

    await fs.cp(sourcePath, path.join(outputDir, entry.name), {
      recursive: true,
      filter: (nestedSourcePath) => {
        const nestedRelativePath = path.relative(root, nestedSourcePath);
        return !shouldIgnore(nestedRelativePath);
      }
    });
  }

  await fs.writeFile(
    path.join(outputDir, "version.json"),
    JSON.stringify({ version: versionToken }, null, 2) + "\n",
    "utf8"
  );
}

async function collectHtmlFiles(directory) {
  const entries = await fs.readdir(directory, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(directory, entry.name);

    if (entry.isDirectory()) {
      files.push(...(await collectHtmlFiles(fullPath)));
      continue;
    }

    if (entry.isFile() && entry.name.endsWith(".html")) {
      files.push(fullPath);
    }
  }

  return files;
}

function rewriteAssetUrls(html, versionToken) {
  const assetRefs = [
    "./styles.css",
    "./code-ocean-logo.svg",
    "./Aqua-nautilex-process.png",
    "./capsules-data.js",
    "./capsule-docs.js",
    "./markdown-renderer.js",
    "./app.js",
    "./doc-viewer.js",
    "../styles.css",
    "../code-ocean-logo.svg",
    "../capsules-data.js",
    "../capsule-docs.js",
    "../markdown-renderer.js",
    "../doc-viewer.js"
  ];

  const rewritten = assetRefs.reduce((content, ref) => {
    const escapedRef = ref.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`(["'])${escapedRef}\\1`, "g");
    return content.replace(regex, `$1${ref}?v=${versionToken}$1`);
  }, html);

  const duplicateVersionRegex = new RegExp(`\\?v=${versionToken}\\?v=${versionToken}`, "g");
  return rewritten.replace(duplicateVersionRegex, `?v=${versionToken}`);
}

function getRelativeVersionPath(filePath) {
  const relativeDir = path.relative(path.dirname(filePath), outputDir) || ".";
  return path.join(relativeDir, "version.json").split(path.sep).join("/");
}

function injectVersionGuard(html, versionToken, filePath) {
  if (!html.includes("</head>")) {
    return html;
  }

  const versionPath = getRelativeVersionPath(filePath);
  const guard = `
    <meta name="site-version" content="${versionToken}" />
    <script>
      (function () {
        if (window.location.protocol === "file:") {
          return;
        }

        const currentVersion = ${JSON.stringify(versionToken)};
        const versionUrl = new URL(${JSON.stringify(versionPath)}, window.location.href);
        versionUrl.searchParams.set("ts", String(Date.now()));

        fetch(versionUrl, { cache: "no-store" })
          .then((response) => (response.ok ? response.json() : null))
          .then((data) => {
            if (!data || !data.version || data.version === currentVersion) {
              return;
            }

            const nextUrl = new URL(window.location.href);
            if (nextUrl.searchParams.get("v") === data.version) {
              return;
            }

            nextUrl.searchParams.set("v", data.version);
            window.location.replace(nextUrl.toString());
          })
          .catch(() => {});
      })();
    </script>
`;

  return html.replace("</head>", `${guard}\n  </head>`);
}

async function rewriteHtml(versionToken) {
  const htmlFiles = await collectHtmlFiles(outputDir);

  await Promise.all(
    htmlFiles.map(async (filePath) => {
      const html = await fs.readFile(filePath, "utf8");
      const rewrittenAssets = rewriteAssetUrls(html, versionToken);
      const rewritten = injectVersionGuard(rewrittenAssets, versionToken, filePath);
      await fs.writeFile(filePath, rewritten, "utf8");
    })
  );
}

async function main() {
  const versionToken = getVersionToken();
  await copyRepoTree(versionToken);
  await rewriteHtml(versionToken);
  console.log(`Staged GitHub Pages artifact in .site with asset version ${versionToken}`);
}

await main();
