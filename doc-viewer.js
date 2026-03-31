(function () {
  const capsules = Array.isArray(window.CAPSULES) ? window.CAPSULES : [];
  const docs = window.CAPSULE_DOCS || {};
  const renderer = window.MarkdownRenderer || {};

  const titleEl = document.getElementById("doc-title");
  const subtitleEl = document.getElementById("doc-subtitle");
  const kickerEl = document.getElementById("doc-kicker");
  const typePillEl = document.getElementById("doc-type-pill");
  const statusPillEl = document.getElementById("doc-status-pill");
  const contentEl = document.getElementById("doc-content");
  const backLinkEl = document.querySelector(".doc-back");
  const atlasLinkEl = document.getElementById("doc-atlas-link");
  const relatedLinkEl = document.getElementById("doc-related-link");

  const pageConfig = window.DOC_PAGE || {};
  const params = new URLSearchParams(window.location.search);
  const capsuleId = pageConfig.capsuleId || params.get("capsule");
  const docType = (pageConfig.docType || params.get("doc")) === "review" ? "review" : "readme";
  const capsule = capsules.find((item) => item.id === capsuleId);

  function statusClass(status) {
    if (status === "completed") return "completed";
    if (status === "partial") return "partial";
    return "blocked";
  }

  if (!capsule || !renderer.renderMarkdown) {
    document.title = "Document not found";
    kickerEl.textContent = "Capsule document";
    titleEl.textContent = "Document not found";
    subtitleEl.textContent = "The requested capsule document could not be loaded.";
    typePillEl.textContent = "Missing";
    statusPillEl.textContent = "Unavailable";
    contentEl.innerHTML = "<p class=\"markdown-empty\">Check the capsule id and document type in the URL.</p>";
    return;
  }

  const capsuleDoc = docs[capsule.id] || {};
  const markdown = docType === "review" ? capsuleDoc.reviewMarkdown : capsuleDoc.readmeMarkdown;
  const docLabel = docType === "review" ? "Review summary" : "Local README";

  document.title = `${capsule.title} ${docLabel}`;
  kickerEl.textContent = `Challenge ${capsule.number}`;
  titleEl.textContent = `${capsule.title} ${docLabel}`;
  subtitleEl.textContent = capsule.directory;
  typePillEl.textContent = docLabel;
  statusPillEl.textContent = capsule.statusLabel;
  statusPillEl.classList.add(statusClass(capsule.status));
  contentEl.innerHTML = renderer.renderMarkdown(markdown);

  const defaultBackHref = `./index.html#${capsule.id}`;
  const defaultAtlasHref = `./index.html#${capsule.id}`;
  const relatedHref =
    pageConfig.relatedHref ||
    `./docs/${capsule.id}-${docType === "review" ? "readme" : "review"}.html`;
  const relatedLabel = pageConfig.relatedLabel || (docType === "review" ? "Open local README" : "Open review summary");

  if (backLinkEl) {
    backLinkEl.href = pageConfig.backHref || defaultBackHref;
  }

  if (atlasLinkEl) {
    atlasLinkEl.href = pageConfig.atlasHref || defaultAtlasHref;
  }

  if (relatedLinkEl) {
    relatedLinkEl.href = relatedHref;
    relatedLinkEl.textContent = relatedLabel;
  }
})();
