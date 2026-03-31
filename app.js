(function () {
  const capsules = Array.isArray(window.CAPSULES) ? window.CAPSULES : [];
  const capsuleDocs = window.CAPSULE_DOCS || {};
  const renderer = window.MarkdownRenderer || {};
  const escapeHtml = renderer.escapeHtml || ((value) => String(value ?? ""));
  const renderMarkdown = renderer.renderMarkdown || ((value) => value);

  const DOC_TYPES = [
    {
      key: "results",
      label: "RESULTS",
      pageSuffix: "results",
      availabilityKey: "results",
      sourcePath: (capsule) => capsule.resultsPath
    },
    {
      key: "readme",
      label: "README",
      pageSuffix: "readme",
      availabilityKey: "readme",
      sourcePath: (capsule) => capsule.readmePath
    },
    {
      key: "aquaPrompt",
      label: "AQUA PROMPT",
      pageSuffix: "aqua-prompt",
      availabilityKey: "aquaPrompt",
      sourcePath: (capsule) => capsule.aquaPromptPath
    },
    {
      key: "howToImplement",
      label: "HOW TO IMPLEMENT",
      pageSuffix: "how-to-implement",
      availabilityKey: "howToImplement",
      sourcePath: (capsule) => capsule.howToImplementPath
    },
    {
      key: "review",
      label: "REVIEW",
      pageSuffix: "review",
      availabilityKey: "review",
      sourcePath: (capsule) => capsule.reviewPath
    }
  ];

  const state = {
    search: "",
    status: "all",
    flags: new Set(),
    sortKey: "challenge",
    sortDirection: "asc"
  };

  const statusOptions = [
    { id: "all", label: "All" },
    { id: "completed", label: "Completed" },
    { id: "partial", label: "Partial" },
    { id: "blocked", label: "Blocked" }
  ];

  const flagOptions = [
    { id: "self-contained", label: "Self-contained" },
    { id: "data-asset", label: "Needs data asset" },
    { id: "aqua", label: "Aqua" },
    { id: "app-panel", label: "App Panel" },
    { id: "bedrock", label: "Bedrock" },
    { id: "real-data", label: "Real data" },
    { id: "synthetic-data", label: "Synthetic fallback" }
  ];

  const statsGrid = document.getElementById("stats-grid");
  const capsuleNav = document.getElementById("capsule-nav");
  const overviewBody = document.getElementById("overview-body");
  const capsulesContainer = document.getElementById("capsules-container");
  const resultsNote = document.getElementById("results-note");
  const searchInput = document.getElementById("search-input");
  const statusFilters = document.getElementById("status-filters");
  const flagFilters = document.getElementById("flag-filters");
  const tableHead = document.querySelector(".capsule-table thead");

  let observer;

  function statusClass(status) {
    if (status === "completed") return "completed";
    if (status === "partial") return "partial";
    return "blocked";
  }

  function normalizeRelativePath(value) {
    return String(value || "").replace(/^\.\//, "");
  }

  async function copyTextToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return;
    }

    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "true");
    textarea.style.position = "absolute";
    textarea.style.left = "-9999px";
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }

  function markButtonCopied(button, defaultLabel) {
    const original = defaultLabel || button.textContent || "Copy";
    button.textContent = "Copied";
    button.classList.add("is-copied");

    window.setTimeout(() => {
      button.textContent = original;
      button.classList.remove("is-copied");
    }, 1600);
  }

  function getArtifactHref(relativePath, prefix = "./") {
    return `${prefix}${normalizeRelativePath(relativePath)}`;
  }

  function getDocPageHref(capsule, docType, prefix = "./docs/") {
    return `${prefix}${capsule.id}-${docType.pageSuffix}.html`;
  }

  function getDocEntries(capsule) {
    const availability = capsule.docAvailability || {};
    return DOC_TYPES.filter((docType) => availability[docType.availabilityKey]);
  }

  function getResultsArtifacts(capsule) {
    const capsuleDoc = capsuleDocs[capsule.id] || {};
    return Array.isArray(capsuleDoc.resultsArtifacts) ? capsuleDoc.resultsArtifacts : [];
  }

  function getFeaturedArtifacts(capsule) {
    const artifacts = getResultsArtifacts(capsule);
    const featuredPaths = Array.isArray(capsule.featuredArtifacts) ? capsule.featuredArtifacts : [];

    if (!featuredPaths.length) {
      return artifacts.slice(0, 3);
    }

    return featuredPaths
      .map((relativePath) =>
        artifacts.find((artifact) => normalizeRelativePath(artifact.path) === normalizeRelativePath(relativePath))
      )
      .filter(Boolean);
  }

  function getSearchHaystack(capsule) {
    const artifacts = getResultsArtifacts(capsule);

    return [
      capsule.number,
      capsule.title,
      capsule.directory,
      capsule.problem,
      capsule.capsuleSummary,
      capsule.primaryUseCase,
      capsule.usageMode,
      capsule.notes,
      (capsule.usageHighlights || []).join(" "),
      (capsule.resultsHighlights || []).join(" "),
      capsule.inputs.join(" "),
      capsule.outputs.join(" "),
      capsule.runModes.join(" "),
      artifacts.map((artifact) => `${artifact.name} ${artifact.path} ${artifact.type}`).join(" ")
    ]
      .join(" ")
      .toLowerCase();
  }

  function getFilteredCapsules() {
    const query = state.search.trim().toLowerCase();

    return capsules.filter((capsule) => {
      if (state.status !== "all" && capsule.status !== state.status) {
        return false;
      }

      const capsuleFlags = Array.isArray(capsule.flags) ? capsule.flags : [];
      const hasAllFlags = [...state.flags].every((flag) => capsuleFlags.includes(flag));
      if (!hasAllFlags) {
        return false;
      }

      if (!query) {
        return true;
      }

      return getSearchHaystack(capsule).includes(query);
    });
  }

  function getSortValue(capsule, sortKey) {
    switch (sortKey) {
      case "challenge":
        return Number(capsule.number);
      case "status": {
        const order = { completed: 0, partial: 1, blocked: 2 };
        return order[capsule.status] ?? 99;
      }
      case "useCase":
        return capsule.primaryUseCase || capsule.capsuleSummary;
      case "usage":
        return (capsule.usageHighlights || [])[0] || capsule.usageSteps[0] || capsule.usageMode;
      case "result":
        return (capsule.resultsHighlights || [])[0] || capsule.outputs.join(" ");
      case "docs":
        return getDocEntries(capsule).length * 100 + getResultsArtifacts(capsule).length;
      default:
        return capsule.title;
    }
  }

  function sortCapsules(items) {
    return items
      .map((capsule, index) => ({ capsule, index }))
      .sort((left, right) => {
        const leftValue = getSortValue(left.capsule, state.sortKey);
        const rightValue = getSortValue(right.capsule, state.sortKey);

        let result = 0;

        if (typeof leftValue === "number" && typeof rightValue === "number") {
          result = leftValue - rightValue;
        } else {
          result = String(leftValue).localeCompare(String(rightValue), undefined, {
            numeric: true,
            sensitivity: "base"
          });
        }

        if (result === 0) {
          result = Number(left.capsule.number) - Number(right.capsule.number);
        }

        if (result === 0) {
          result = left.index - right.index;
        }

        return state.sortDirection === "asc" ? result : -result;
      })
      .map((entry) => entry.capsule);
  }

  function formatSortLabel() {
    const labels = {
      challenge: "Challenge",
      status: "Status",
      useCase: "Best for",
      usage: "How to run",
      result: "Key result",
      docs: "Docs and artifacts"
    };

    return `${labels[state.sortKey] || "Challenge"} ${state.sortDirection === "asc" ? "↑" : "↓"}`;
  }

  function renderSortHeaders() {
    if (!tableHead) return;

    const buttons = tableHead.querySelectorAll("[data-sort-key]");
    buttons.forEach((button) => {
      const key = button.getAttribute("data-sort-key");
      const th = button.closest("th");
      const indicator = button.querySelector(".sort-indicator");
      const isActive = key === state.sortKey;

      if (th) {
        th.setAttribute(
          "aria-sort",
          isActive ? (state.sortDirection === "asc" ? "ascending" : "descending") : "none"
        );
      }

      button.classList.toggle("is-active", isActive);
      if (indicator) {
        indicator.textContent = isActive ? (state.sortDirection === "asc" ? "↑" : "↓") : "↕";
      }
    });
  }

  function renderStats() {
    const completed = capsules.filter((item) => item.status === "completed").length;
    const partial = capsules.filter((item) => item.status === "partial").length;
    const blocked = capsules.filter((item) => item.status === "blocked").length;

    statsGrid.innerHTML = `
      <article class="stat-card">
        <p class="stat-value">${capsules.length}</p>
        <p class="stat-label">Capsules indexed</p>
      </article>
      <article class="stat-card">
        <p class="stat-value">${completed}</p>
        <p class="stat-label">Completed</p>
      </article>
      <article class="stat-card">
        <p class="stat-value">${partial}</p>
        <p class="stat-label">Partial</p>
      </article>
      <article class="stat-card">
        <p class="stat-value">${blocked}</p>
        <p class="stat-label">Blocked</p>
      </article>
    `;
  }

  function renderStatusFilters() {
    statusFilters.innerHTML = statusOptions
      .map((option) => {
        const active = state.status === option.id ? "is-active" : "";
        return `<button class="filter-chip ${active}" type="button" data-status="${option.id}">${option.label}</button>`;
      })
      .join("");
  }

  function renderFlagFilters() {
    flagFilters.innerHTML = flagOptions
      .map((option) => {
        const active = state.flags.has(option.id) ? "is-active" : "";
        return `<button class="filter-chip subtle ${active}" type="button" data-flag="${option.id}">${option.label}</button>`;
      })
      .join("");
  }

  function renderNav(filtered) {
    capsuleNav.innerHTML = filtered
      .map(
        (capsule) => `
          <a class="nav-link reveal" href="#${capsule.id}" data-nav-target="${capsule.id}">
            <span class="nav-number">${capsule.number}</span>
            <span class="nav-text">${escapeHtml(capsule.title)}</span>
          </a>
        `
      )
      .join("");
  }

  function renderInlineList(items, fallbackText) {
    if (!Array.isArray(items) || items.length === 0) {
      return `<p class="supporting-note">${escapeHtml(fallbackText)}</p>`;
    }

    return `
      <ul class="compact-list">
        ${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    `;
  }

  function renderArtifactList(artifacts, assetPrefix = "./", compact = false) {
    if (!artifacts.length) {
      return `<p class="supporting-note">No result artifacts were indexed for this capsule.</p>`;
    }

    const listClass = compact ? "artifact-list compact-artifact-list" : "artifact-list";
    const itemClass = compact ? "artifact-item compact" : "artifact-item";

    return `
      <ul class="${listClass}">
        ${artifacts
          .map(
            (artifact) => `
              <li class="${itemClass}">
                <div>
                  <a href="${getArtifactHref(artifact.path, assetPrefix)}">${escapeHtml(artifact.name)}</a>
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

  function renderDocsHub(capsule, options = {}) {
    const { docPrefix = "./docs/", assetPrefix = "./", compact = false } = options;
    const entries = getDocEntries(capsule);
    const classes = compact ? "docs-hub compact" : "docs-hub";

    return `
      <div class="${classes}">
        ${entries
          .map(
            (docType) => `
              <a class="doc-chip ${docType.key === "results" ? "is-primary" : ""}" href="${getDocPageHref(
                capsule,
                docType,
                docPrefix
              )}">
                ${escapeHtml(docType.label)}
              </a>
            `
          )
          .join("")}
        <a class="doc-chip is-raw" href="${getArtifactHref(capsule.aquaPromptPath, assetPrefix)}">Raw AQUA_PROMPT.md</a>
      </div>
    `;
  }

  function renderEmbeddedDoc(title, markdown, options = {}) {
    if (!markdown) {
      return "";
    }

    const openAttr = options.open ? " open" : "";

    return `
      <details class="doc-disclosure"${openAttr}>
        <summary>${escapeHtml(title)}</summary>
        <div class="markdown-body">${renderMarkdown(markdown)}</div>
      </details>
    `;
  }

  function renderTable(filtered) {
    overviewBody.innerHTML = filtered
      .map((capsule) => {
        const featuredArtifacts = getFeaturedArtifacts(capsule);
        const resultsArtifacts = getResultsArtifacts(capsule);
        const docsCount = getDocEntries(capsule).length;

        return `
          <tr class="reveal">
            <td>
              <a class="table-anchor" href="#${capsule.id}">
                <span class="challenge-number">Ch${capsule.number}</span>
                <strong>${escapeHtml(capsule.title)}</strong>
              </a>
              <div class="table-subtext">${escapeHtml(capsule.directory)}</div>
            </td>
            <td>
              <span class="status-pill ${statusClass(capsule.status)}">${escapeHtml(capsule.statusLabel)}</span>
            </td>
            <td>
              <p class="table-emphasis">${escapeHtml(capsule.primaryUseCase || capsule.capsuleSummary)}</p>
              <div class="table-subtext">${escapeHtml(capsule.problem)}</div>
            </td>
            <td>
              <p class="table-mode">${escapeHtml(capsule.usageMode)}</p>
              ${renderInlineList((capsule.usageHighlights || []).slice(0, 2), capsule.usageSteps[0] || "See capsule section")}
            </td>
            <td>
              ${renderInlineList((capsule.resultsHighlights || []).slice(0, 2), capsule.notes || "See results documentation")}
              <div class="table-subtext">Featured artifacts: ${featuredArtifacts.length || resultsArtifacts.length}</div>
            </td>
            <td>
              ${renderDocsHub(capsule, { compact: true })}
              <div class="table-subtext">Docs ${docsCount} · Artifacts ${resultsArtifacts.length}</div>
            </td>
          </tr>
        `;
      })
      .join("");
  }

  function renderCapsules(filtered) {
    if (filtered.length === 0) {
      capsulesContainer.innerHTML = `
        <article class="surface-card empty-state">
          <p class="section-kicker">No matches</p>
          <h2>Nothing matches the current filters.</h2>
          <p>Try clearing the search or removing one of the active capability filters.</p>
          <button class="filter-chip is-active" type="button" data-clear-filters="true">Reset filters</button>
        </article>
      `;
      return;
    }

    capsulesContainer.innerHTML = filtered
      .map((capsule, index) => {
        const previous = filtered[index - 1];
        const next = filtered[index + 1];
        const docs = capsuleDocs[capsule.id] || {};
        const featuredArtifacts = getFeaturedArtifacts(capsule);
        const allArtifacts = getResultsArtifacts(capsule);

        return `
          <article id="${capsule.id}" class="capsule-card reveal surface-card" data-section="${capsule.id}">
            <div class="capsule-head">
              <div>
                <p class="section-kicker">Challenge ${escapeHtml(capsule.number)}</p>
                <h2>${escapeHtml(capsule.title)}</h2>
              </div>
              <span class="status-pill ${statusClass(capsule.status)}">${escapeHtml(capsule.statusLabel)}</span>
            </div>

            <p class="capsule-subtitle">${escapeHtml(capsule.primaryUseCase || capsule.capsuleSummary)}</p>
            <p class="lead-text">${escapeHtml(capsule.problem)}</p>

            <div class="detail-grid summary-grid">
              <section class="detail-block accent-block">
                <h3>How to use</h3>
                <p class="mode-line">${escapeHtml(capsule.usageMode)}</p>
                <ol class="step-list">
                  ${capsule.usageSteps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}
                </ol>
                <ul class="highlight-list">
                  ${(capsule.usageHighlights || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                </ul>
                <div class="pill-row">
                  ${capsule.runModes.map((mode) => `<span class="meta-pill">${escapeHtml(mode)}</span>`).join("")}
                </div>
              </section>

              <section class="detail-block accent-block results-block">
                <h3>Results at a glance</h3>
                <ul class="highlight-list">
                  ${(capsule.resultsHighlights || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                </ul>
                <p class="supporting-note">${escapeHtml(capsule.notes)}</p>
              </section>
            </div>

            <div class="detail-grid">
              <section class="detail-block">
                <h3>Key artifacts</h3>
                <p class="supporting-note">
                  Start with the featured files below. They are the fastest route to the strongest machine-readable evidence for this capsule.
                </p>
                ${renderArtifactList(featuredArtifacts, "./")}
                <details class="artifact-disclosure">
                  <summary>See all result artifacts (${allArtifacts.length})</summary>
                  ${renderArtifactList(allArtifacts, "./", true)}
                </details>
              </section>

              <section class="detail-block">
                <h3>Docs hub</h3>
                <p class="supporting-note">
                  Open RESULTS for proof, README for scope, HOW TO IMPLEMENT for adaptation, and AQUA PROMPT when you want copy-ready instructions for Aqua.
                </p>
                ${renderDocsHub(capsule, { docPrefix: "./docs/", assetPrefix: "./" })}
                <div class="prompt-actions">
                  <button class="secondary-link action-button copy-button" type="button" data-copy-aqua="${capsule.id}">
                    Copy AQUA prompt
                  </button>
                  <a class="secondary-link" href="${getDocPageHref(capsule, DOC_TYPES[2], "./docs/")}">Open AQUA prompt page</a>
                  <a class="secondary-link" href="${getArtifactHref(capsule.aquaPromptPath, "./")}">Open raw AQUA_PROMPT.md</a>
                </div>
              </section>
            </div>

            <div class="detail-grid">
              <section class="detail-block">
                <h3>Implementation approach</h3>
                ${capsule.solution.map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`).join("")}
              </section>

              <section class="detail-block">
                <h3>Inputs and outputs</h3>
                <div class="io-columns">
                  <section>
                    <p class="mini-label">Inputs</p>
                    <ul class="data-list">
                      ${capsule.inputs.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                    </ul>
                  </section>
                  <section>
                    <p class="mini-label">Outputs</p>
                    <ul class="data-list">
                      ${capsule.outputs.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                    </ul>
                  </section>
                </div>
              </section>
            </div>

            <div class="embedded-docs">
              ${renderEmbeddedDoc("Embedded RESULTS", docs.resultsMarkdown, { open: true })}
              ${renderEmbeddedDoc("Embedded HOW TO IMPLEMENT", docs.howToImplementMarkdown, { open: true })}
              ${renderEmbeddedDoc("Embedded AQUA PROMPT", docs.aquaPromptMarkdown)}
              ${renderEmbeddedDoc("Embedded README", docs.readmeMarkdown)}
              ${renderEmbeddedDoc("Embedded REVIEW", docs.reviewMarkdown)}
            </div>

            <div class="capsule-actions">
              <div class="link-pair">
                <a href="#overview">Back to table</a>
                <a href="${getDocPageHref(capsule, DOC_TYPES[0], "./docs/")}">Open RESULTS</a>
                <a href="${getArtifactHref(capsule.aquaPromptPath, "./")}">Open raw AQUA_PROMPT.md</a>
              </div>
              <div class="pager-links">
                ${
                  previous
                    ? `<a href="#${previous.id}">Previous: Ch${previous.number}</a>`
                    : `<span class="pager-spacer"></span>`
                }
                ${next ? `<a href="#${next.id}">Next: Ch${next.number}</a>` : ""}
              </div>
            </div>
          </article>
        `;
      })
      .join("");
  }

  function renderResultsNote(filtered) {
    const capsulesCount = filtered.length;
    const label = capsulesCount === 1 ? "capsule" : "capsules";
    resultsNote.textContent = `${capsulesCount} ${label} shown · sorted by ${formatSortLabel()}`;
  }

  function bindFilterEvents() {
    statusFilters.addEventListener("click", (event) => {
      const target = event.target.closest("[data-status]");
      if (!target) return;
      state.status = target.getAttribute("data-status");
      render();
    });

    flagFilters.addEventListener("click", (event) => {
      const target = event.target.closest("[data-flag]");
      if (!target) return;
      const flag = target.getAttribute("data-flag");
      if (state.flags.has(flag)) {
        state.flags.delete(flag);
      } else {
        state.flags.add(flag);
      }
      render();
    });

    searchInput.addEventListener("input", (event) => {
      state.search = event.target.value;
      render();
    });

    if (tableHead) {
      tableHead.addEventListener("click", (event) => {
        const button = event.target.closest("[data-sort-key]");
        if (!button) return;

        const nextKey = button.getAttribute("data-sort-key");
        if (state.sortKey === nextKey) {
          state.sortDirection = state.sortDirection === "asc" ? "desc" : "asc";
        } else {
          state.sortKey = nextKey;
          state.sortDirection = "asc";
        }

        render();
      });
    }

    capsulesContainer.addEventListener("click", (event) => {
      const copyButton = event.target.closest("[data-copy-aqua]");
      if (copyButton) {
        const capsuleId = copyButton.getAttribute("data-copy-aqua");
        const capsuleDoc = capsuleDocs[capsuleId] || {};
        const aquaPrompt = capsuleDoc.aquaPromptMarkdown;

        if (!aquaPrompt) {
          return;
        }

        copyTextToClipboard(aquaPrompt)
          .then(() => markButtonCopied(copyButton, "Copy AQUA prompt"))
          .catch(() => {
            copyButton.textContent = "Copy failed";
          });
        return;
      }

      const target = event.target.closest("[data-clear-filters]");
      if (!target) return;
      state.search = "";
      state.status = "all";
      state.flags.clear();
      searchInput.value = "";
      render();
    });
  }

  function activateNavOnScroll() {
    if (observer) {
      observer.disconnect();
    }

    const sections = document.querySelectorAll("[data-section]");
    const navLinks = [...document.querySelectorAll("[data-nav-target]")];

    observer = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries
          .filter((entry) => entry.isIntersecting)
          .sort((left, right) => right.intersectionRatio - left.intersectionRatio)[0];

        if (!visibleEntry) return;

        const currentId = visibleEntry.target.getAttribute("data-section");
        navLinks.forEach((link) => {
          link.classList.toggle("is-current", link.getAttribute("data-nav-target") === currentId);
        });
      },
      {
        rootMargin: "-20% 0px -55% 0px",
        threshold: [0.15, 0.3, 0.6]
      }
    );

    sections.forEach((section) => observer.observe(section));
  }

  function render() {
    const filtered = getFilteredCapsules();
    const sorted = sortCapsules(filtered);
    renderStatusFilters();
    renderFlagFilters();
    renderSortHeaders();
    renderNav(sorted);
    renderTable(sorted);
    renderCapsules(sorted);
    renderResultsNote(sorted);
    activateNavOnScroll();
  }

  renderStats();
  bindFilterEvents();
  render();
})();
