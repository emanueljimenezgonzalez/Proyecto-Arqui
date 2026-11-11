// Catálogo Hottest Deals (Integrante 2)
// Consume la API: /api/meta (filtros y fecha), /api/games (lista) y /api/games/{id} (detalle).
(() => {
  "use strict";

  const REFRESH_MS = 5 * 60 * 1000; // revisa si el scraper publicó datos nuevos
  const FILTER_KEYS = ["q", "platform", "format", "store", "sort", "on_sale"];
  const FORMAT_LABELS = { digital: "Digital", fisico: "Físico", otro: "Otro" };

  const $ = (sel) => document.querySelector(sel);
  const form = $("#filters");
  const grid = $("#grid");
  const dialog = $("#detail");

  let meta = null;
  let money = null;
  let listRequest = 0;

  // ---------- utilidades ----------
  const esc = (value) =>
    String(value ?? "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

  // Solo se aceptan enlaces http(s) que vienen del scraping
  const safeUrl = (url) => {
    if (typeof url !== "string" || !url.trim()) return null;
    try {
      const u = new URL(url); // solo URLs absolutas
      return u.protocol === "http:" || u.protocol === "https:" ? u.href : null;
    } catch { return null; }
  };

  const price = (n) => (n == null ? "—" : money.format(n));

  const hours = (h) => (h == null ? "Sin dato" : `${h.toLocaleString("es-CR")} h`);

  const dateTime = (iso) => {
    if (!iso) return "Sin dato";
    const d = new Date(iso);
    return isNaN(d) ? iso : d.toLocaleString("es-CR", { dateStyle: "medium", timeStyle: "short" });
  };

  // solo fecha: se lee en UTC para que en Costa Rica no salga un día antes
  const dateOnly = (iso) => {
    if (!iso) return "Sin dato";
    const d = new Date(iso);
    return isNaN(d) ? iso : d.toLocaleDateString("es-CR", { dateStyle: "medium", timeZone: "UTC" });
  };

  const scoreClass = (s) => (s == null ? "none" : s >= 75 ? "good" : s >= 50 ? "mixed" : "bad");

  const scoreBadge = (s, big = false) =>
    `<span class="score score-${scoreClass(s)}${big ? " score-big" : ""}" title="Metacritic">${
      s == null ? "–" : Math.round(s)}</span>`;

  const cover = (game, cls) => {
    const src = safeUrl(game.image_url);
    const placeholder = `<div class="${cls} placeholder" aria-hidden="true">${esc(game.name?.[0] || "?")}</div>`;
    if (!src) return placeholder;
    return `<img class="${cls}" src="${esc(src)}" alt="Portada de ${esc(game.name)}" loading="lazy"
      data-initial="${esc(game.name?.[0] || "?")}">`;
  };

  // Si una imagen falla (enlace roto), se cambia por el marcador con la inicial
  document.addEventListener("error", (e) => {
    const img = e.target;
    if (!(img instanceof HTMLImageElement) || !img.dataset.initial) return;
    const div = document.createElement("div");
    div.className = `${img.className} placeholder`;
    div.setAttribute("aria-hidden", "true");
    div.textContent = img.dataset.initial;
    img.replaceWith(div);
  }, true);

  async function getJSON(url) {
    const res = await fetch(url, { headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(`${res.status} ${url}`);
    return res.json();
  }

  // ---------- filtros <-> URL ----------
  function readForm() {
    const data = new FormData(form);
    const params = new URLSearchParams();
    for (const key of FILTER_KEYS) {
      const value = (data.get(key) || "").trim();
      if (value && !(key === "sort" && value === "name")) params.set(key, value);
    }
    return params;
  }

  function writeForm(params) {
    for (const key of FILTER_KEYS) {
      const el = form.elements[key];
      if (!el) continue;
      if (el.type === "checkbox") el.checked = params.get(key) === "true";
      else el.value = params.get(key) || (key === "sort" ? "name" : "");
    }
  }

  function fillSelect(name, options) {
    const select = form.elements[name];
    const first = select.options[0].outerHTML;
    select.innerHTML = first + options
      .map((o) => (typeof o === "string" ? { value: o, label: o } : o))
      .map((o) => `<option value="${esc(o.value)}"${o.disabled ? " disabled" : ""}>${esc(o.label)}</option>`).join("");
  }

  // ---------- meta ----------
  async function loadMeta() {
    meta = await getJSON("/api/meta");
    money = new Intl.NumberFormat("es-CR", { style: "currency", currency: meta.currency || "USD" });
    const f = meta.filters;
    fillSelect("platform", f.platforms);
    // Tipo: físico, digital u otro, con la cantidad de juegos de cada uno.
    // Las opciones sin juegos se ven pero no se pueden escoger.
    fillSelect("format", f.formats.map((o) => ({
      value: o.value, label: `${o.label} (${o.count})`, disabled: o.count === 0,
    })));
    fillSelect("store", f.stores);
    $("#last-updated").textContent = dateTime(meta.last_updated);
    $("#total-games").textContent = `${meta.total_games} juegos en el catálogo`;
  }

  // ---------- lista ----------
  function card(g) {
    const onSale = g.on_sale && g.regular_price != null;
    return `
      <article class="card" data-id="${esc(g.id)}" tabindex="0" role="button"
               aria-label="Ver detalle de ${esc(g.name)}">
        <div class="cover-wrap">
          ${cover(g, "cover")}
          ${onSale ? `<span class="badge-discount">-${g.discount_percent}%</span>` : ""}
        </div>
        <div class="card-content">
          <h2>${esc(g.name)}</h2>
          <ul class="chips" aria-label="Plataformas">
            ${g.platforms.map((p) => `<li class="chip">${esc(p)}</li>`).join("")}
          </ul>
          <div class="card-bottom">
            <div class="prices">
              ${g.best_price == null
                ? `<span class="price pending">Precio no disponible</span>`
                : `<span class="price">${price(g.best_price)}</span>
                   ${onSale ? `<s class="regular">${price(g.regular_price)}</s>` : ""}
                   <span class="store-name">en ${esc(g.best_store)}</span>`}
            </div>
            ${scoreBadge(g.metacritic_score)}
          </div>
        </div>
      </article>`;
  }

  async function loadGames({ pushState = true } = {}) {
    const params = readForm();
    if (pushState) {
      const qs = params.toString();
      const url = (qs ? `?${qs}` : location.pathname) + location.hash;
      history.replaceState(null, "", url);
    }
    const apiParams = new URLSearchParams(params);
    const [sort, order] = (apiParams.get("sort") || "name").split(":");
    apiParams.set("sort", sort);
    if (order) apiParams.set("order", order);

    const id = ++listRequest;
    grid.setAttribute("aria-busy", "true");
    try {
      const games = await getJSON(`/api/games?${apiParams}`);
      if (id !== listRequest) return; // llegó una respuesta más nueva
      grid.innerHTML = games.map(card).join("");
      $("#empty").hidden = games.length > 0;
      $("#error").hidden = true;
      $("#result-count").textContent =
        `${games.length} de ${meta.total_games} juego${meta.total_games === 1 ? "" : "s"}`;
    } catch (err) {
      console.error(err);
      $("#error").hidden = false;
    } finally {
      grid.removeAttribute("aria-busy");
    }
  }

  // ---------- detalle ----------
  function detailHTML(g) {
    const rows = g.offers.map((o) => {
      const url = safeUrl(o.url);
      const best = o.available && o.current_price === g.best_price;
      // si la tienda falló en la última corrida, su precio es de una fecha anterior
      const old = o.updated_at && o.updated_at !== g.updated_at;
      return `
        <tr class="${o.available ? "" : "unavailable"} ${best ? "best" : ""}">
          <td><strong>${esc(o.store)}</strong>${best ? ` <span class="tag-best">Mejor precio</span>` : ""}${
            old ? `<small class="sub">Precio del ${esc(dateTime(o.updated_at))}</small>` : ""}</td>
          <td>${esc(o.platform || "—")}</td>
          <td>${esc(FORMAT_LABELS[o.format] || o.format)}</td>
          <td class="num">${o.available ? price(o.current_price) : "No disponible"}</td>
          <td class="num">${o.regular_price != null && o.discount_percent > 0
            ? `<s>${price(o.regular_price)}</s> <span class="pct">-${o.discount_percent}%</span>` : "—"}</td>
          <td>${url ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Ir a la tienda ↗</a>` : "—"}</td>
        </tr>`;
    }).join("");

    const scores = Object.entries(g.metacritic_scores || {}).sort()
      .map(([platform, score]) => `${platform} ${score}`).join(" · ");
    const hltbMore = g.hltb_extra_hours != null || g.hltb_completionist_hours != null;
    return `
      <div class="detail-head">
        ${cover(g, "detail-cover")}
        <div>
          <h2 id="detail-title">${esc(g.name)}</h2>
          <ul class="chips">${g.platforms.map((p) => `<li class="chip">${esc(p)}</li>`).join("")}</ul>
          <div class="detail-best">
            ${g.best_price == null ? `<span class="price pending">Precio no disponible</span>` :
              `<span class="price">${price(g.best_price)}</span>
               ${g.on_sale ? `<s class="regular">${price(g.regular_price)}</s>
               <span class="badge-discount inline">-${g.discount_percent}%</span>` : ""}
               <span class="store-name">en ${esc(g.best_store)}</span>`}
          </div>
        </div>
      </div>

      <dl class="facts">
        <div><dt>Metacritic</dt><dd>${scoreBadge(g.metacritic_score, true)}${
          scores ? `<small class="sub">${esc(scores)}</small>` : ""}</dd></div>
        <div><dt>HowLongToBeat (historia)</dt><dd>${esc(hours(g.hltb_main_hours))}${
          hltbMore ? `<small class="sub">Con extras: ${esc(hours(g.hltb_extra_hours))}</small>
            <small class="sub">Al 100%: ${esc(hours(g.hltb_completionist_hours))}</small>` : ""}</dd></div>
        <div><dt>Precio sugerido</dt><dd>${price(g.reference_price)}</dd></div>
        <div><dt>Lanzamiento</dt><dd>${esc(dateOnly(g.release_date))}</dd></div>
        <div><dt>Tipo</dt><dd>${esc(g.formats.map((f) => FORMAT_LABELS[f] || f).join(", ") || "Sin dato")}</dd></div>
      </dl>

      <h3>Precios por tienda</h3>
      ${g.offers.length ? `
      <div class="table-wrap">
        <table class="offers">
          <thead><tr><th>Tienda</th><th>Plataforma</th><th>Formato</th>
            <th class="num">Precio</th><th class="num">Regular</th><th>Enlace</th></tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </div>` : `<p class="muted">No hay precios disponibles para este juego.</p>`}

      <p class="updated">Datos actualizados: <strong>${esc(dateTime(g.updated_at))}</strong></p>`;
  }

  async function openDetail(id) {
    $("#detail-body").innerHTML = `<p class="muted">Cargando…</p>`;
    if (!dialog.open) dialog.showModal();
    try {
      const game = await getJSON(`/api/games/${encodeURIComponent(id)}`);
      $("#detail-body").innerHTML = detailHTML(game);
    } catch {
      $("#detail-body").innerHTML = `<p class="error">No se encontró el juego.</p>`;
    }
  }

  function routeFromHash() {
    const m = location.hash.match(/^#juego\/(.+)$/);
    if (m) openDetail(decodeURIComponent(m[1]));
    else if (dialog.open) dialog.close();
  }

  // ---------- eventos ----------
  let searchTimer;
  form.addEventListener("input", (e) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(loadGames, e.target.name === "q" ? 250 : 0);
  });
  form.addEventListener("submit", (e) => e.preventDefault());
  form.addEventListener("reset", () => setTimeout(loadGames, 0));

  const openCard = (el) => { location.hash = `juego/${encodeURIComponent(el.dataset.id)}`; };
  grid.addEventListener("click", (e) => {
    const el = e.target.closest(".card");
    if (el) openCard(el);
  });
  grid.addEventListener("keydown", (e) => {
    const el = e.target.closest(".card");
    if (el && (e.key === "Enter" || e.key === " ")) { e.preventDefault(); openCard(el); }
  });

  window.addEventListener("hashchange", routeFromHash);
  dialog.addEventListener("close", () => {
    if (location.hash) history.replaceState(null, "", location.pathname + location.search);
  });
  dialog.addEventListener("click", (e) => {
    if (e.target === dialog || e.target.closest("[data-close]")) dialog.close();
  });

  // Actualización automática: si el scraper escribió datos nuevos, se recarga
  setInterval(async () => {
    try {
      const prev = meta?.data_version;
      const current = await getJSON("/api/meta");
      if (current.data_version !== prev) {
        const params = readForm();
        await loadMeta();
        writeForm(params);
        await loadGames({ pushState: false });
      }
    } catch (err) { console.warn("No se pudo revisar actualizaciones", err); }
  }, REFRESH_MS);

  // ---------- inicio ----------
  (async function init() {
    try {
      await loadMeta();
    } catch (err) {
      console.error(err);
      $("#error").hidden = false;
      $("#last-updated").textContent = "Sin conexión";
      return;
    }
    writeForm(new URLSearchParams(location.search));
    await loadGames({ pushState: false });
    routeFromHash();
  })();
})();
