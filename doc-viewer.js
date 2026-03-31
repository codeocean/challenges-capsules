(function () {
  const capsules = Array.isArray(window.CAPSULES) ? window.CAPSULES : [];
  const docs = window.CAPSULE_DOCS || {};
  const renderer = window.MarkdownRenderer || {};
  const escapeHtml = renderer.escapeHtml || ((value) => String(value ?? ""));

  const DOC_TYPES = [
    {
      slug: "results",
      key: "results",
      label: "RESULTS",
      field: "resultsMarkdown",
      availabilityKey: "results",
      description: "Run evidence, metrics, and result artifacts.",
      sourcePath: (capsule) => capsule.resultsPath
    },
    {
      slug: "readme",
      key: "readme",
      label: "README",
      field: "readmeMarkdown",
      availabilityKey: "readme",
      description: "Usage, scope, and repository overview.",
      sourcePath: (capsule) => capsule.readmePath
    },
    {
      slug: "aqua-prompt",
      key: "aquaPrompt",
      label: "AQUA PROMPT",
      field: "aquaPromptMarkdown",
      availabilityKey: "aquaPrompt",
      description: "Copy-ready instructions you can paste into Aqua.",
      sourcePath: (capsule) => capsule.aquaPromptPath
    },
    {
      slug: "how-to-implement",
      key: "howToImplement",
      label: "HOW TO IMPLEMENT",
      field: "howToImplementMarkdown",
      availabilityKey: "howToImplement",
      description: "Technical implementation notes and adaptation guidance.",
      sourcePath: (capsule) => capsule.howToImplementPath
    },
    {
      slug: "review",
      key: "review",
      label: "REVIEW",
      field: "reviewMarkdown",
      availabilityKey: "review",
      description: "Independent review summary of the current capsule state.",
      sourcePath: (capsule) => capsule.reviewPath
    }
  ];

  const titleEl = document.getElementById("doc-title");
  const subtitleEl = document.getElementById("doc-subtitle");
  const kickerEl = document.getElementById("doc-kicker");
  const typePillEl = document.getElementById("doc-type-pill");
  const statusPillEl = document.getElementById("doc-status-pill");
  const contentEl = document.getElementById("doc-content");
  const backLinkEl = document.querySelector(".doc-back");
  const atlasLinkEl = document.getElementById("doc-atlas-link");
  const sourceLinkEl = document.getElementById("doc-source-link");
  const summaryGridEl = document.getElementById("doc-summary-grid");
  const docNavEl = document.getElementById("doc-nav");
  const artifactsEl = document.getElementById("doc-artifacts");

  const pageConfig = window.DOC_PAGE || {};
  const params = new URLSearchParams(window.location.search);
  const capsuleId = pageConfig.capsuleId || params.get("capsule");
  const requestedDocType = pageConfig.docType || params.get("doc") || "readme";
  const docType = DOC_TYPES.find((entry) => entry.slug === requestedDocType) || DOC_TYPES[1];
  const capsule = capsules.find((item) => item.id === capsuleId);

  function statusClass(status) {
    if (status === "completed") return "completed";
    if (status === "partial") return "partial";
    return "blocked";
  }

  function normalizeRelativePath(value) {
    return String(value || "").replace(/^\.\//, "");
  }

  function getAtlasHref() {
    const prefix = pageConfig.atlasPrefix || "./";
    return `${prefix}index.html#${capsule.id}`;
  }

  function getDocsPrefix() {
    return pageConfig.docsPrefix || "./docs/";
  }

  function getAssetPrefix() {
    return pageConfig.assetPrefix || "./";
  }

  function getDocHref(entry) {
    return `${getDocsPrefix()}${capsule.id}-${entry.slug}.html`;
  }

  function getSourceHref() {
    const sourcePath = docType.sourcePath(capsule);
    return `${getAssetPrefix()}${normalizeRelativePath(sourcePath)}`;
  }

  function getResultsArtifacts() {
    return Array.isArray((docs[capsule.id] || {}).resultsArtifacts)
      ? (docs[capsule.id] || {}).resultsArtifacts
      : [];
  }

  function getFeaturedArtifacts() {
    const artifacts = getResultsArtifacts();
    const featuredPaths = Array.isArray(capsule.featuredArtifacts) ? capsule.featuredArtifacts : [];

    if (!featuredPaths.length) {
      return artifacts.slice(0, 4);
    }

    return featuredPaths
      .map((relativePath) =>
        artifacts.find((artifact) => normalizeRelativePath(artifact.path) === normalizeRelativePath(relativePath))
      )
      .filter(Boolean);
  }

  function renderList(items) {
    if (!Array.isArray(items) || items.length === 0) {
      return `<p class="supporting-note">No summary bullets were provided for this capsule.</p>`;
    }

    return `
      <ul class="highlight-list">
        ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    `;
  }

  function renderArtifactList(artifacts) {
    if (!artifacts.length) {
      return `<p class="supporting-note">No result artifacts were indexed for this capsule.</p>`;
    }

    return `
      <ul class="artifact-list compact-artifact-list">
        ${artifacts
          .map(
            (artifact) => `
              <li class="artifact-item compact">
                <div>
                  <a href="${getAssetPrefix()}${normalizeRelativePath(artifact.path)}">${escapeHtml(artifact.name)}</a>
                  <p class="artifact-note">${escapeHtml(artifact.path)}</p>
                </div>
                <div class="artifact-meta">
                  <span class="artifact-type">${escapeHtml(String(artifact.type).toUpperCase())}</span>
                  <span class="artifact-size">${escapeHtml(artifact.sizeLabel || "")}</span>
                </div>
              </li>
            `
          )
          .join("")}
      </ul>
    `;
  }

  function renderSummaryCards() {
    summaryGridEl.innerHTML = `
      <section class="summary-card">
        <p class="mini-label">Best for</p>
        <p class="summary-card-copy">${escapeHtml(capsule.primaryUseCase || capsule.capsuleSummary)}</p>
      </section>
      <section class="summary-card">
        <p class="mini-label">How to use</p>
        <p class="summary-card-copy"><strong>${escapeHtml(capsule.usageMode)}</strong></p>
        ${renderList(capsule.usageHighlights)}
      </section>
      <section class="summary-card">
        <p class="mini-label">Results snapshot</p>
        ${renderList(capsule.resultsHighlights)}
      </section>
      <section class="summary-card">
        <p class="mini-label">Primary outputs</p>
        ${renderList(capsule.outputs)}
      </section>
    `;
  }

  function renderDocNav() {
    const availability = capsule.docAvailability || {};

    docNavEl.innerHTML = DOC_TYPES.filter((entry) => availability[entry.availabilityKey])
      .map((entry) => {
        const classes = ["doc-nav-link"];
        if (entry.slug === docType.slug) {
          classes.push("is-current");
        }

        return `<a class="${classes.join(" ")}" href="${getDocHref(entry)}">${escapeHtml(entry.label)}</a>`;
      })
      .join("");
  }

  function renderArtifactsPanel() {
    const allArtifacts = getResultsArtifacts();
    const featuredArtifacts = getFeaturedArtifacts();

    if (docType.slug !== "results" || !artifactsEl) {
      return;
    }

    artifactsEl.hidden = false;
    artifactsEl.innerHTML = `
      <div class="doc-artifacts-copy">
        <p class="section-kicker">Result artifacts</p>
        <h2>Open the evidence files that back this capsule</h2>
        <p class="supporting-note">
          Start with the featured artifacts, then open the full inventory if you need every machine-readable result file.
        </p>
      </div>
      <div class="doc-artifacts-grid">
        <section>
          <p class="mini-label">Featured artifacts</p>
          ${renderArtifactList(featuredArtifacts)}
        </section>
        <section>
          <p class="mini-label">All indexed artifacts</p>
          ${renderArtifactList(allArtifacts)}
        </section>
      </div>
    `;
  }

  function renderMissingState() {
    document.title = "Document not found";
    kickerEl.textContent = "Capsule document";
    titleEl.textContent = "Document not found";
    subtitleEl.textContent = "The requested capsule document could not be loaded.";
    typePillEl.textContent = "Missing";
    statusPillEl.textContent = "Unavailable";
    contentEl.innerHTML = "<p class=\"markdown-empty\">Check the capsule id and document type in the URL.</p>";
    if (summaryGridEl) summaryGridEl.innerHTML = "";
    if (docNavEl) docNavEl.innerHTML = "";
    if (artifactsEl) artifactsEl.hidden = true;
  }

  if (!capsule || !renderer.renderMarkdown) {
    renderMissingState();
    return;
  }

  const capsuleDoc = docs[capsule.id] || {};
  const markdown = capsuleDoc[docType.field];

  if (!markdown) {
    renderMissingState();
    return;
  }

  document.title = `${capsule.title} ${docType.label}`;
  kickerEl.textContent = `Challenge ${capsule.number}`;
  titleEl.textContent = `${capsule.title} ${docType.label}`;
  subtitleEl.textContent = capsule.directory;
  typePillEl.textContent = docType.label;
  statusPillEl.textContent = capsule.statusLabel;
  statusPillEl.classList.add(statusClass(capsule.status));
  contentEl.innerHTML = renderer.renderMarkdown(markdown);

  if (backLinkEl) {
    backLinkEl.href = getAtlasHref();
  }

  if (atlasLinkEl) {
    atlasLinkEl.href = getAtlasHref();
  }

  if (sourceLinkEl) {
    sourceLinkEl.href = getSourceHref();
    sourceLinkEl.textContent =
      docType.slug === "aqua-prompt" ? "Open raw AQUA_PROMPT.md" : "Open raw source file";
  }

  renderSummaryCards();
  renderDocNav();
  renderArtifactsPanel();
})();
