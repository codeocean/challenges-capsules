import { promises as fs } from "node:fs";
import path from "node:path";

const root = process.cwd();
const docsDir = path.join(root, "docs");

const DOC_TYPES = [
  { slug: "readme", title: "README", description: "Usage, scope, and repository overview." },
  { slug: "results", title: "RESULTS", description: "Evidence, metrics, and result artifacts." },
  {
    slug: "how-to-implement",
    title: "HOW TO IMPLEMENT",
    description: "Technical implementation notes and adaptation guidance."
  },
  {
    slug: "aqua-prompt",
    title: "AQUA PROMPT",
    description: "Copy-ready prompt instructions for Aqua."
  },
  { slug: "review", title: "REVIEW", description: "Independent review summary for the capsule." }
];

function buildHtml({ capsuleId, docType }) {
  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Capsule document</title>
    <meta
      name="description"
      content="Styled local document page for Code Ocean challenge capsule markdown and results artifacts."
    />
    <link rel="icon" type="image/svg+xml" href="../code-ocean-logo.svg" />
    <link rel="stylesheet" href="../styles.css" />
  </head>
  <body>
    <div class="background-shell" aria-hidden="true">
      <div class="background-orb orb-a"></div>
      <div class="background-orb orb-b"></div>
      <div class="background-grid"></div>
    </div>

    <main class="doc-page">
      <div class="doc-shell surface-card">
        <div class="doc-header">
          <a class="secondary-link doc-back" href="../index.html#${capsuleId}">Back to atlas</a>
          <div class="doc-title-block">
            <p class="section-kicker" id="doc-kicker">Capsule document</p>
            <h1 id="doc-title">Loading document</h1>
            <p class="doc-subtitle" id="doc-subtitle"></p>
            <div class="doc-meta-row">
              <span class="meta-pill" id="doc-type-pill"></span>
              <span class="meta-pill" id="doc-status-pill"></span>
            </div>
            <div class="doc-action-row">
              <a class="primary-link" id="doc-atlas-link" href="../index.html#${capsuleId}">Open atlas section</a>
              <a class="secondary-link" id="doc-source-link" href="../index.html#${capsuleId}">Open raw source file</a>
            </div>
          </div>
        </div>

        <section class="doc-summary-grid" id="doc-summary-grid" aria-label="Capsule summary"></section>
        <nav class="doc-nav" id="doc-nav" aria-label="Capsule document navigation"></nav>
        <section class="doc-artifacts" id="doc-artifacts" hidden></section>

        <article class="doc-content markdown-body" id="doc-content">
          <p>Loading document content.</p>
        </article>
      </div>
    </main>

    <script>
      window.DOC_PAGE = {
        capsuleId: "${capsuleId}",
        docType: "${docType}",
        atlasPrefix: "../",
        docsPrefix: "./",
        assetPrefix: "../"
      };
    </script>
    <script src="../capsules-data.js"></script>
    <script src="../capsule-docs.js"></script>
    <script src="../markdown-renderer.js"></script>
    <script src="../doc-viewer.js"></script>
  </body>
</html>
`;
}

async function build() {
  await fs.mkdir(docsDir, { recursive: true });

  const entries = await fs.readdir(root, { withFileTypes: true });
  const challengeDirs = entries
    .filter((entry) => entry.isDirectory() && /^challenge_\d{2}_/.test(entry.name))
    .map((entry) => entry.name)
    .sort((left, right) => left.localeCompare(right));

  for (const directory of challengeDirs) {
    const match = directory.match(/^challenge_(\d{2})_/);
    if (!match) continue;

    const capsuleId = `challenge-${match[1]}`;

    for (const docType of DOC_TYPES) {
      const filePath = path.join(docsDir, `${capsuleId}-${docType.slug}.html`);
      await fs.writeFile(filePath, buildHtml({ capsuleId, docType: docType.slug }), "utf8");
    }
  }
}

await build();
