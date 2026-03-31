import { promises as fs } from "node:fs";
import path from "node:path";

const root = process.cwd();
const docsDir = path.join(root, "docs");

function buildHtml({ capsuleId, docType }) {
  const otherType = docType === "review" ? "readme" : "review";
  const otherLabel = docType === "review" ? "Open local README" : "Open review summary";

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Capsule document</title>
    <meta
      name="description"
      content="Styled local document page for Code Ocean challenge capsule markdown."
    />
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
              <a class="secondary-link" id="doc-related-link" href="./${capsuleId}-${otherType}.html">${otherLabel}</a>
            </div>
          </div>
        </div>

        <article class="doc-content markdown-body" id="doc-content">
          <p>Loading document content.</p>
        </article>
      </div>
    </main>

    <script>
      window.DOC_PAGE = {
        capsuleId: "${capsuleId}",
        docType: "${docType}",
        backHref: "../index.html#${capsuleId}",
        atlasHref: "../index.html#${capsuleId}",
        relatedHref: "./${capsuleId}-${otherType}.html",
        relatedLabel: "${otherLabel}"
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
    .sort((a, b) => a.localeCompare(b));

  for (const directory of challengeDirs) {
    const match = directory.match(/^challenge_(\d{2})_/);
    if (!match) continue;

    const capsuleId = `challenge-${match[1]}`;
    await fs.writeFile(path.join(docsDir, `${capsuleId}-readme.html`), buildHtml({ capsuleId, docType: "readme" }), "utf8");
    await fs.writeFile(path.join(docsDir, `${capsuleId}-review.html`), buildHtml({ capsuleId, docType: "review" }), "utf8");
  }
}

await build();
