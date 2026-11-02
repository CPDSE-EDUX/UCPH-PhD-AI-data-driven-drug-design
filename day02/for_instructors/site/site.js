(() => {
  "use strict";
  const body = document.body;
  const menu = document.querySelector(".menu-toggle");
  const backdrop = document.querySelector(".nav-backdrop");
  const sidebar = document.querySelector(".course-sidebar");
  function closeMenu() {
    body.classList.remove("nav-open");
    menu.setAttribute("aria-expanded", "false");
    menu.setAttribute("aria-label", "Open course navigation");
    backdrop.hidden = true;
  }
  menu.addEventListener("click", () => {
    const open = !body.classList.contains("nav-open");
    body.classList.toggle("nav-open", open);
    menu.setAttribute("aria-expanded", String(open));
    menu.setAttribute("aria-label", open ? "Close course navigation" : "Open course navigation");
    backdrop.hidden = !open;
    if (open) sidebar.querySelector("a").focus();
  });
  backdrop.addEventListener("click", closeMenu);
  sidebar.addEventListener("click", (event) => { if (event.target.closest("a")) closeMenu(); });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && body.classList.contains("nav-open")) { closeMenu(); menu.focus(); }
  });
  matchMedia("(min-width: 761px)").addEventListener("change", (event) => { if (event.matches) closeMenu(); });

  const storageKey = "ucph-drug-design-2026-workshop-progress";
  let completed = new Set();
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "[]");
    if (Array.isArray(saved)) completed = new Set(saved.filter(value => Number.isInteger(value) && value >= 1 && value <= 18));
  } catch (_) { /* Progress is optional when storage is unavailable. */ }
  const completionButton = document.querySelector(".completion-toggle");
  const currentStep = Number(body.dataset.step);
  function renderProgress() {
    document.querySelector("#progress-count").textContent = `${completed.size} / 18`;
    document.querySelector("#workshop-progress").value = completed.size;
    document.querySelectorAll("[data-step-link]").forEach(link => {
      const done = completed.has(Number(link.dataset.stepLink));
      link.querySelector(".step-check").hidden = !done;
    });
    if (completionButton) {
      const done = completed.has(currentStep);
      completionButton.setAttribute("aria-pressed", String(done));
      completionButton.textContent = done ? "✓ Step complete" : "○ Mark step complete";
    }
  }
  if (completionButton) completionButton.addEventListener("click", () => {
    completed.has(currentStep) ? completed.delete(currentStep) : completed.add(currentStep);
    try { localStorage.setItem(storageKey, JSON.stringify([...completed])); } catch (_) { /* Still reflect progress for this page. */ }
    renderProgress();
  });
  renderProgress();

  const dialog = document.querySelector(".search-dialog");
  const input = document.querySelector("#course-search");
  const results = document.querySelector("#search-results");
  const status = document.querySelector("#search-status");
  const siteRoot = new URL(body.dataset.siteRoot, location.href);
  let searchIndex;
  let loadPromise;
  async function loadSearch() {
    if (!loadPromise) loadPromise = fetch(body.dataset.searchIndex).then(response => {
      if (!response.ok) throw new Error("Search index unavailable");
      return response.json();
    }).then(index => { searchIndex = index; }).catch(() => {
      loadPromise = undefined;
      status.textContent = "Search could not load. Use the course navigation or try opening search again.";
    });
    await loadPromise;
  }
  function renderSearch() {
    results.replaceChildren();
    if (!searchIndex) return;
    const query = input.value.trim().toLowerCase();
    if (!query) { status.textContent = "Search across all course days and workshop steps."; return; }
    const words = query.split(/\s+/).filter(Boolean);
    const matches = searchIndex.map(page => {
      const title = `${page.section} ${page.title}`.toLowerCase();
      const text = `${title} ${page.text}`.toLowerCase();
      return { ...page, score: words.every(word => text.includes(word)) ? words.reduce((score, word) => score + (title.includes(word) ? 5 : 1), 0) : 0 };
    }).filter(page => page.score > 0).sort((a, b) => b.score - a.score).slice(0, 12);
    status.textContent = matches.length ? `${matches.length} matching page${matches.length === 1 ? "" : "s"}` : "No matching pages. Try a shorter phrase or a different term.";
    matches.forEach(page => {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = new URL(page.path, siteRoot).href;
      const section = document.createElement("small"); section.textContent = page.section;
      const title = document.createElement("strong"); title.textContent = page.title;
      const snippet = document.createElement("p");
      const position = page.text.toLowerCase().indexOf(words[0]);
      const start = Math.max(0, position - 45);
      snippet.textContent = (start ? "…" : "") + page.text.slice(start, start + 160) + (page.text.length > start + 160 ? "…" : "");
      link.append(section, title, snippet); item.append(link); results.append(item);
    });
  }
  async function openSearch() {
    closeMenu();
    if (!dialog.open) dialog.showModal();
    input.focus();
    await loadSearch();
    renderSearch();
  }
  document.querySelector(".search-toggle").addEventListener("click", openSearch);
  input.addEventListener("input", renderSearch);
  input.addEventListener("keydown", event => {
    if (event.key === "ArrowDown") { event.preventDefault(); results.querySelector("a")?.focus(); }
  });
  document.addEventListener("keydown", event => {
    const editing = event.target.matches("input, textarea, select, [contenteditable=true]");
    if (!editing && (event.key === "/" || ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k"))) { event.preventDefault(); openSearch(); }
  });
  dialog.addEventListener("click", event => { if (event.target === dialog) { const box = dialog.getBoundingClientRect(); if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close(); } });

  // The original submission app remains unchanged and runs at its existing URL.
  const frame = document.querySelector("#smiles-app");
  if (frame) frame.addEventListener("load", () => {
    try {
      const doc = frame.contentDocument;
      if (!doc?.body) return;
      const resize = () => { frame.style.height = `${Math.max(850, doc.documentElement.scrollHeight, doc.body.scrollHeight) + 8}px`; };
      resize();
      const observer = new MutationObserver(() => requestAnimationFrame(resize));
      observer.observe(doc.body, { childList: true, subtree: true });
      if (typeof ResizeObserver !== "undefined") new ResizeObserver(resize).observe(doc.body);
      window.addEventListener("resize", resize);
    } catch (_) { /* The standalone app link remains available if embedding is restricted. */ }
  });
})();
