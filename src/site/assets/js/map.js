/**
 * map.js
 * ------
 * Interroge data/map_state.json en boucle (ecrit par
 * src/MJ_application/map_sync.py) et dessine la carte sur un <canvas>.
 *
 * La camera (pan/zoom) du site est INDEPENDANTE de celle du MJ : on
 * reproduit le CONTENU de la carte (cases, images) en quasi temps reel,
 * mais chaque spectateur navigue la carte a son rythme (glisser pour
 * deplacer, molette / pincement pour zoomer, bouton "Recentrer" pour tout
 * revoir).
 */

(() => {
  "use strict";

  const POLL_INTERVAL_MS = 1000;
  const OFFLINE_AFTER_MISSES = 3;
  const ZOOM_MIN = 0.1;
  const ZOOM_MAX = 6;
  const ZOOM_STEP = 1.18;

  const canvas = document.getElementById("mapCanvas");
  const ctx = canvas.getContext("2d");
  const statusEl = document.getElementById("status");
  const statusLabel = document.getElementById("statusLabel");
  const hudCoords = document.getElementById("hudCoords");
  const zoomReadout = document.getElementById("zoomReadout");

  /** @type {{n: number, s_cell: number, cells: Array<{col:number,row:number,image:string}>}} */
  let mapData = { n: 0, s_cell: 64, cells: [] };
  let cellImageByKey = new Map(); // "col,row" -> image url
  const imageCache = new Map();   // url -> HTMLImageElement
  let lastVersion = null;
  let hasReceivedData = false;
  let consecutiveMisses = 0;

  // Camera : transforme des coordonnees "monde" (en pixels de grille,
  // 0..n*s_cell) en coordonnees ecran. screen = world * zoom + offset.
  const camera = { x: 0, y: 0, zoom: 1 };

  let dpr = Math.max(1, window.devicePixelRatio || 1);

  // -------------------------------------------------------------- canvas

  function resizeCanvas() {
    dpr = Math.max(1, window.devicePixelRatio || 1);
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = Math.round(rect.width * dpr);
    canvas.height = Math.round(rect.height * dpr);
    canvas.style.width = rect.width + "px";
    canvas.style.height = rect.height + "px";
    draw();
  }

  function worldToScreen(wx, wy) {
    return [wx * camera.zoom + camera.x, wy * camera.zoom + camera.y];
  }

  function screenToWorld(sx, sy) {
    return [(sx - camera.x) / camera.zoom, (sy - camera.y) / camera.zoom];
  }

  function fitToView() {
    const n = mapData.n || 1;
    const s = mapData.s_cell || 64;
    const worldSize = n * s;
    const viewW = canvas.width;
    const viewH = canvas.height;
    const scale = Math.min(viewW / worldSize, viewH / worldSize) * 0.92;
    camera.zoom = Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, scale));
    camera.x = (viewW - worldSize * camera.zoom) / 2;
    camera.y = (viewH - worldSize * camera.zoom) / 2;
  }

  function clampZoom(z) {
    return Math.min(ZOOM_MAX, Math.max(ZOOM_MIN, z));
  }

  function zoomAround(screenX, screenY, factor) {
    const [wx, wy] = screenToWorld(screenX, screenY);
    camera.zoom = clampZoom(camera.zoom * factor);
    camera.x = screenX - wx * camera.zoom;
    camera.y = screenY - wy * camera.zoom;
    draw();
  }

  // --------------------------------------------------------------- draw

  function ensureImageLoaded(url) {
    if (imageCache.has(url)) return imageCache.get(url);
    const img = new Image();
    img.decoding = "async";
    img.onload = () => draw();
    img.src = url;
    imageCache.set(url, img);
    return img;
  }

  function draw() {
    const n = mapData.n || 0;
    const s = mapData.s_cell || 64;

    ctx.save();
    ctx.scale(dpr, dpr);
    const w = canvas.width / dpr;
    const h = canvas.height / dpr;
    ctx.clearRect(0, 0, w, h);

    if (n > 0) {
      ctx.save();
      ctx.translate(camera.x, camera.y);
      ctx.scale(camera.zoom, camera.zoom);

      // Fond + cases vides, dans le style de l'app (case grise unie).
      ctx.fillStyle = "#4a4540";
      ctx.fillRect(0, 0, n * s, n * s);

      for (let row = 0; row < n; row++) {
        for (let col = 0; col < n; col++) {
          const key = col + "," + row;
          const url = cellImageByKey.get(key);
          if (url) {
            const img = ensureImageLoaded(url);
            if (img.complete && img.naturalWidth > 0) {
              ctx.drawImage(img, col * s, row * s, s, s);
            }
          }
        }
      }

      // Quadrillage discret par dessus.
      ctx.strokeStyle = "rgba(232, 149, 74, 0.16)";
      ctx.lineWidth = 1 / camera.zoom;
      ctx.beginPath();
      for (let i = 0; i <= n; i++) {
        ctx.moveTo(i * s, 0);
        ctx.lineTo(i * s, n * s);
        ctx.moveTo(0, i * s);
        ctx.lineTo(n * s, i * s);
      }
      ctx.stroke();

      ctx.restore();
    }

    ctx.restore();

    zoomReadout.textContent = Math.round(camera.zoom * 100) + "%";
    hudCoords.textContent = n + " × " + n;
  }

  // ----------------------------------------------------------- polling

  function setOnline(online) {
    statusEl.classList.toggle("status--offline", !online);
    statusLabel.textContent = online ? "En direct" : "Hors ligne";
  }

  function applyData(data) {
    const firstLoad = !hasReceivedData;
    const hasGrid = (data.n || 0) > 0;
    if (hasGrid) hasReceivedData = true;
    mapData = data;

    cellImageByKey.clear();
    for (const c of data.cells || []) {
      cellImageByKey.set(c.col + "," + c.row, c.image);
    }
    for (const url of new Set((data.cells || []).map((c) => c.image))) {
      ensureImageLoaded(url);
    }

    if (firstLoad) {
      fitToView();
    }
    draw();
  }

  async function poll() {
    try {
      const res = await fetch("data/map_state.json?t=" + Date.now(), {
        cache: "no-store",
      });
      if (!res.ok) throw new Error("http " + res.status);
      const data = await res.json();
      consecutiveMisses = 0;
      setOnline(true);
      if (data.version !== lastVersion) {
        lastVersion = data.version;
        applyData(data);
      }
    } catch (err) {
      consecutiveMisses += 1;
      if (consecutiveMisses >= OFFLINE_AFTER_MISSES) {
        setOnline(false);
      }
    }
  }

  // --------------------------------------------------------- interaction

  let dragging = false;
  let lastX = 0;
  let lastY = 0;
  const activePointers = new Map(); // pointerId -> {x, y}
  let pinchStartDist = null;
  let pinchStartZoom = 1;

  function pointerPos(e) {
    const rect = canvas.getBoundingClientRect();
    return [e.clientX - rect.left, e.clientY - rect.top];
  }

  canvas.addEventListener("pointerdown", (e) => {
    canvas.setPointerCapture(e.pointerId);
    const [x, y] = pointerPos(e);
    activePointers.set(e.pointerId, { x, y });
    if (activePointers.size === 1) {
      dragging = true;
      lastX = x;
      lastY = y;
    } else if (activePointers.size === 2) {
      dragging = false;
      const pts = [...activePointers.values()];
      pinchStartDist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
      pinchStartZoom = camera.zoom;
    }
  });

  canvas.addEventListener("pointermove", (e) => {
    if (!activePointers.has(e.pointerId)) return;
    const [x, y] = pointerPos(e);
    activePointers.set(e.pointerId, { x, y });

    if (activePointers.size === 2) {
      const pts = [...activePointers.values()];
      const dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
      if (pinchStartDist) {
        const midX = (pts[0].x + pts[1].x) / 2;
        const midY = (pts[0].y + pts[1].y) / 2;
        const targetZoom = clampZoom(pinchStartZoom * (dist / pinchStartDist));
        const factor = targetZoom / camera.zoom;
        zoomAround(midX, midY, factor);
      }
      return;
    }

    if (dragging) {
      camera.x += x - lastX;
      camera.y += y - lastY;
      lastX = x;
      lastY = y;
      draw();
    }
  });

  function releasePointer(e) {
    activePointers.delete(e.pointerId);
    pinchStartDist = null;
    dragging = activePointers.size === 1;
    if (dragging) {
      const remaining = [...activePointers.values()][0];
      lastX = remaining.x;
      lastY = remaining.y;
    }
  }

  canvas.addEventListener("pointerup", releasePointer);
  canvas.addEventListener("pointercancel", releasePointer);
  canvas.addEventListener("pointerleave", (e) => {
    if (e.pointerType !== "touch") releasePointer(e);
  });

  canvas.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      const [x, y] = pointerPos(e);
      const factor = e.deltaY < 0 ? ZOOM_STEP : 1 / ZOOM_STEP;
      zoomAround(x, y, factor);
    },
    { passive: false }
  );

  document.getElementById("zoomInBtn").addEventListener("click", () => {
    zoomAround(canvas.clientWidth / 2, canvas.clientHeight / 2, ZOOM_STEP);
  });
  document.getElementById("zoomOutBtn").addEventListener("click", () => {
    zoomAround(canvas.clientWidth / 2, canvas.clientHeight / 2, 1 / ZOOM_STEP);
  });
  document.getElementById("recenterBtn").addEventListener("click", () => {
    fitToView();
    draw();
  });

  window.addEventListener("resize", resizeCanvas);

  // ------------------------------------------------------------------ go

  resizeCanvas();
  poll();
  setInterval(poll, POLL_INTERVAL_MS);
})();
