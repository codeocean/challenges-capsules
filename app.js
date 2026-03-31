(function () {
  const capsules = Array.isArray(window.CAPSULES) ? window.CAPSULES : [];
  const capsuleDocs = window.CAPSULE_DOCS || {};
  const renderer = window.MarkdownRenderer || {};
  const escapeHtml = renderer.escapeHtml || ((value) => String(value));
  const renderMarkdown = renderer.renderMarkdown || ((value) => value);

  const state = {
    search: "",
    status: "all",
    flags: new Set()
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
    { id: "app-panel", label: "App Panel" },
    { id: "aqua", label: "Aqua ready" },
    { id: "interactive", label: "Interactive UI" }
  ];

  const statsGrid = document.getElementById("stats-grid");
  const capsuleNav = document.getElementById("capsule-nav");
  const overviewBody = document.getElementById("overview-body");
  const capsulesContainer = document.getElementById("capsules-container");
  const resultsNote = document.getElementById("results-note");
  const searchInput = document.getElementById("search-input");
  const statusFilters = document.getElementById("status-filters");
  const flagFilters = document.getElementById("flag-filters");

  let observer;

  function titleToStatusClass(status) {
    if (status === "completed") return "completed";
    if (status === "partial") return "partial";
    return "blocked";
  }

  function getFilteredCapsules() {
    const query = state.search.trim().toLowerCase();

    return capsules.filter((capsule) => {
      if (state.status !== "all" && capsule.status !== state.status) {
        return false;
      }

      const hasAllFlags = [...state.flags].every((flag) => capsule.flags.includes(flag));
      if (!hasAllFlags) {
        return false;
      }

      if (!query) {
        return true;
      }

      const haystack = [
        capsule.number,
        capsule.title,
        capsule.directory,
        capsule.problem,
        capsule.capsuleSummary,
        capsule.usageMode,
        capsule.notes,
        capsule.inputs.join(" "),
        capsule.outputs.join(" "),
        capsule.runModes.join(" ")
      ]
        .join(" ")
        .toLowerCase();

      return haystack.includes(query);
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

  function renderTable(filtered) {
    overviewBody.innerHTML = filtered
      .map(
        (capsule) => `
          <tr class="reveal">
            <td>
              <a class="table-anchor" href="#${capsule.id}">
                <span class="challenge-number">Ch${capsule.number}</span>
                <strong>${escapeHtml(capsule.title)}</strong>
              </a>
              <div class="table-subtext">${escapeHtml(capsule.directory)}</div>
            </td>
            <td>
              <span class="status-pill ${titleToStatusClass(capsule.status)}">${escapeHtml(capsule.statusLabel)}</span>
            </td>
            <td>${escapeHtml(capsule.capsuleSummary)}</td>
            <td>${escapeHtml(capsule.usageSteps[0])}</td>
            <td>
              <ul class="compact-list">
                ${capsule.inputs
                  .slice(0, 3)
                  .map((item) => `<li>${escapeHtml(item)}</li>`)
                  .join("")}
              </ul>
            </td>
            <td>
              <div class="link-stack">
                <a href="#${capsule.id}">Open section</a>
                <a href="./docs/${capsule.id}-readme.html">README</a>
                <a href="./docs/${capsule.id}-review.html">Review</a>
              </div>
            </td>
          </tr>
        `
      )
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

        return `
          <article id="${capsule.id}" class="capsule-card reveal surface-card" data-section="${capsule.id}">
            <div class="capsule-head">
              <div>
                <p class="section-kicker">Challenge ${escapeHtml(capsule.number)}</p>
                <h2>${escapeHtml(capsule.title)}</h2>
              </div>
              <span class="status-pill ${titleToStatusClass(capsule.status)}">${escapeHtml(capsule.statusLabel)}</span>
            </div>

            <p class="lead-text">${escapeHtml(capsule.problem)}</p>

            <div class="detail-grid">
              <section class="detail-block">
                <h3>What the capsule does</h3>
                <p>${escapeHtml(capsule.capsuleSummary)}</p>
              </section>

              <section class="detail-block">
                <h3>How this codebase solves it</h3>
                ${capsule.solution.map((paragraph) => `<p>${escapeHtml(paragraph)}</p>`).join("")}
              </section>
            </div>

            <div class="detail-grid">
              <section class="detail-block">
                <h3>How to use it in Code Ocean</h3>
                <p class="mode-line">${escapeHtml(capsule.usageMode)}</p>
                <ol class="step-list">
                  ${capsule.usageSteps.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}
                </ol>
              </section>

              <section class="detail-block">
                <h3>Run profile</h3>
                <div class="pill-row">
                  ${capsule.runModes.map((mode) => `<span class="meta-pill">${escapeHtml(mode)}</span>`).join("")}
                </div>
                <p class="supporting-note">${escapeHtml(capsule.notes)}</p>
              </section>
            </div>

            <div class="detail-grid">
              <section class="detail-block">
                <h3>Inputs to prepare</h3>
                <ul class="data-list">
                  ${capsule.inputs.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                </ul>
              </section>

              <section class="detail-block">
                <h3>Outputs to inspect</h3>
                <ul class="data-list">
                  ${capsule.outputs.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
                </ul>
              </section>
            </div>

            <div class="embedded-docs">
              <details class="doc-disclosure">
                <summary>Embedded review summary</summary>
                <div class="markdown-body">${renderMarkdown(docs.reviewMarkdown)}</div>
              </details>
              <details class="doc-disclosure">
                <summary>Embedded README</summary>
                <div class="markdown-body">${renderMarkdown(docs.readmeMarkdown)}</div>
              </details>
            </div>

            <div class="capsule-actions">
              <div class="link-pair">
                <a href="#overview">Back to table</a>
                <a href="./docs/${capsule.id}-readme.html">Open local README</a>
                <a href="./docs/${capsule.id}-review.html">Open review summary</a>
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
    resultsNote.textContent = `${capsulesCount} ${label} shown`;
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

    capsulesContainer.addEventListener("click", (event) => {
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
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

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
    renderStatusFilters();
    renderFlagFilters();
    renderNav(filtered);
    renderTable(filtered);
    renderCapsules(filtered);
    renderResultsNote(filtered);
    activateNavOnScroll();
  }

  renderStats();
  bindFilterEvents();
  render();
})();
