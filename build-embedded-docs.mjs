import { promises as fs } from "node:fs";
import path from "node:path";
import vm from "node:vm";

const root = process.cwd();

const DOC_FILE_MAP = {
  readmeMarkdown: "README.md",
  resultsMarkdown: "RESULTS.md",
  howToImplementMarkdown: "HOW_TO_IMPLEMENT.md",
  aquaPromptMarkdown: "AQUA_PROMPT.md"
};

function toPosix(value) {
  return value.split(path.sep).join("/");
}

function normalizeRelativePath(value) {
  return toPosix(String(value || "").replace(/^\.\//, ""));
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function inferArtifactType(fileName) {
  const extension = path.extname(fileName).slice(1).toLowerCase();
  return extension || "file";
}

async function readRequiredFile(filePath, label) {
  try {
    return await fs.readFile(filePath, "utf8");
  } catch (error) {
    throw new Error(`Missing required ${label}: ${toPosix(path.relative(root, filePath))}`);
  }
}

async function collectFilesRecursively(directory) {
  const entries = await fs.readdir(directory, { withFileTypes: true });
  const files = [];

  for (const entry of entries.sort((left, right) => left.name.localeCompare(right.name))) {
    const fullPath = path.join(directory, entry.name);

    if (entry.isDirectory()) {
      files.push(...(await collectFilesRecursively(fullPath)));
      continue;
    }

    if (entry.isFile()) {
      files.push(fullPath);
    }
  }

  return files;
}

async function collectResultsArtifacts(directory) {
  const files = await collectFilesRecursively(directory);

  return Promise.all(
    files.map(async (filePath) => {
      const stats = await fs.stat(filePath);
      const relativePath = toPosix(path.relative(root, filePath));

      return {
        path: relativePath,
        name: path.basename(filePath),
        type: inferArtifactType(filePath),
        sizeBytes: stats.size,
        sizeLabel: formatBytes(stats.size)
      };
    })
  );
}

async function loadCapsulesFromDataFile() {
  const source = await fs.readFile(path.join(root, "capsules-data.js"), "utf8");
  const context = { window: {}, console };
  vm.createContext(context);
  vm.runInContext(source, context, { filename: "capsules-data.js" });

  if (!Array.isArray(context.window.CAPSULES)) {
    throw new Error("capsules-data.js did not define window.CAPSULES");
  }

  return context.window.CAPSULES;
}

async function build() {
  const capsules = await loadCapsulesFromDataFile();
  const bundledDocs = {};

  for (const capsule of capsules) {
    const capsuleCodeDir = path.join(root, capsule.directory, "code");
    const reviewPath = path.join(root, normalizeRelativePath(capsule.reviewPath));
    const resultsDir = path.join(capsuleCodeDir, "results");

    const docPayload = {};
    for (const [field, fileName] of Object.entries(DOC_FILE_MAP)) {
      docPayload[field] = await readRequiredFile(
        path.join(capsuleCodeDir, fileName),
        `${capsule.id} ${fileName}`
      );
    }

    docPayload.reviewMarkdown = await readRequiredFile(reviewPath, `${capsule.id} review markdown`);
    docPayload.resultsArtifacts = await collectResultsArtifacts(resultsDir);

    const inventoryPaths = new Set(docPayload.resultsArtifacts.map((artifact) => normalizeRelativePath(artifact.path)));
    for (const featuredArtifact of capsule.featuredArtifacts || []) {
      const normalized = normalizeRelativePath(featuredArtifact);
      if (!inventoryPaths.has(normalized)) {
        throw new Error(
          `Featured artifact "${featuredArtifact}" for ${capsule.id} was not found under ${toPosix(
            path.relative(root, resultsDir)
          )}`
        );
      }
    }

    bundledDocs[capsule.id] = docPayload;
  }

  const serialized = JSON.stringify(bundledDocs, null, 2)
    .replace(/\u2028/g, "\\u2028")
    .replace(/\u2029/g, "\\u2029");

  await fs.writeFile(path.join(root, "capsule-docs.js"), `window.CAPSULE_DOCS = ${serialized};\n`, "utf8");
}

await build();
