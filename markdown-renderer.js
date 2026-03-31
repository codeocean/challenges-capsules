(function () {
  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function renderInlineMarkdown(text) {
    return escapeHtml(text)
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>")
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  }

  function isTableSeparator(line) {
    return /^\|?[\s:-]+(?:\|[\s:-]+)+\|?$/.test(line.trim());
  }

  function splitTableRow(line) {
    return line
      .trim()
      .replace(/^\|/, "")
      .replace(/\|$/, "")
      .split("|")
      .map((cell) => cell.trim());
  }

  function renderMarkdown(markdown) {
    if (!markdown || !markdown.trim()) {
      return "<p class=\"markdown-empty\">Not available in this repository snapshot.</p>";
    }

    const lines = markdown.replace(/\r\n/g, "\n").split("\n");
    const html = [];
    let index = 0;

    while (index < lines.length) {
      const line = lines[index];
      const trimmed = line.trim();

      if (!trimmed) {
        index += 1;
        continue;
      }

      if (trimmed.startsWith("```")) {
        const language = trimmed.slice(3).trim();
        const codeLines = [];
        index += 1;

        while (index < lines.length && !lines[index].trim().startsWith("```")) {
          codeLines.push(lines[index]);
          index += 1;
        }

        if (index < lines.length) {
          index += 1;
        }

        html.push(
          `<pre class="markdown-code"><code class="language-${escapeHtml(language || "plain")}">${escapeHtml(
            codeLines.join("\n")
          )}</code></pre>`
        );
        continue;
      }

      const heading = trimmed.match(/^(#{1,6})\s+(.+)$/);
      if (heading) {
        const level = Math.min(6, heading[1].length + 1);
        html.push(`<h${level} class="markdown-heading">${renderInlineMarkdown(heading[2])}</h${level}>`);
        index += 1;
        continue;
      }

      if (trimmed.startsWith("|") && index + 1 < lines.length && isTableSeparator(lines[index + 1])) {
        const headerCells = splitTableRow(lines[index]);
        const rowHtml = [];
        index += 2;

        while (index < lines.length && lines[index].trim().startsWith("|")) {
          const cells = splitTableRow(lines[index]);
          rowHtml.push(
            `<tr>${cells.map((cell) => `<td>${renderInlineMarkdown(cell)}</td>`).join("")}</tr>`
          );
          index += 1;
        }

        html.push(`
          <div class="markdown-table-wrap">
            <table class="markdown-table">
              <thead><tr>${headerCells
                .map((cell) => `<th>${renderInlineMarkdown(cell)}</th>`)
                .join("")}</tr></thead>
              <tbody>${rowHtml.join("")}</tbody>
            </table>
          </div>
        `);
        continue;
      }

      if (/^[-*]\s+/.test(trimmed)) {
        const items = [];
        while (index < lines.length && /^[-*]\s+/.test(lines[index].trim())) {
          items.push(lines[index].trim().replace(/^[-*]\s+/, ""));
          index += 1;
        }
        html.push(`<ul class="markdown-list">${items.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join("")}</ul>`);
        continue;
      }

      if (/^\d+\.\s+/.test(trimmed)) {
        const items = [];
        while (index < lines.length && /^\d+\.\s+/.test(lines[index].trim())) {
          items.push(lines[index].trim().replace(/^\d+\.\s+/, ""));
          index += 1;
        }
        html.push(`<ol class="markdown-list ordered">${items.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join("")}</ol>`);
        continue;
      }

      const paragraphLines = [];
      while (index < lines.length) {
        const current = lines[index].trim();
        const nextLine = lines[index + 1] ? lines[index + 1].trim() : "";
        if (
          !current ||
          current.startsWith("```") ||
          /^(#{1,6})\s+/.test(current) ||
          /^[-*]\s+/.test(current) ||
          /^\d+\.\s+/.test(current) ||
          (current.startsWith("|") && nextLine && isTableSeparator(nextLine))
        ) {
          break;
        }
        paragraphLines.push(current);
        index += 1;
      }

      html.push(`<p>${renderInlineMarkdown(paragraphLines.join(" "))}</p>`);
    }

    return html.join("");
  }

  window.MarkdownRenderer = {
    escapeHtml,
    renderInlineMarkdown,
    renderMarkdown
  };
})();
