import streamlit as st

_HTML = """
<canvas id="kroky" aria-label="لوحة كروكي الحادث"></canvas>
"""

_CSS = """
:host { display: block; }
canvas {
  width: 100%;
  height: 640px;
  display: block;
  border-radius: 12px;
  background: #f6f1e6;
  touch-action: none;
}
"""

_JS = """
export default function (component) {
  const { data, parentElement, setStateValue } = component;
  const canvas = parentElement.querySelector("#kroky");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const colors = ["#0f766e","#0369a1","#b45309","#7c3aed","#be123c","#047857","#1d4ed8","#a16207","#4338ca","#9f1239"];

  const signature = JSON.stringify((data && data.marks) || []);
  if (!canvas._drag && canvas._sig !== signature) {
    canvas._sig = signature;
    canvas._items = JSON.parse(signature);
  }
  if (!canvas._items) canvas._items = [];
  canvas._tool = (data && data.tool) || "1";

  function size() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const width = Math.max(canvas.clientWidth || parentElement.clientWidth || 800, 320);
    const height = 640;
    const bitmapW = Math.floor(width * dpr);
    const bitmapH = Math.floor(height * dpr);
    if (canvas.width !== bitmapW || canvas.height !== bitmapH) {
      canvas.width = bitmapW;
      canvas.height = bitmapH;
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { width, height };
  }

  function drawPaper(width, height) {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#f6f1e6";
    ctx.fillRect(0, 0, width, height);
    ctx.fillStyle = "#e7dcc4";
    ctx.fillRect(0, height * 0.28, width, height * 0.44);
    ctx.fillStyle = "#3f4854";
    ctx.fillRect(0, height * 0.34, width, height * 0.32);
    ctx.strokeStyle = "#f8fafc";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, height * 0.36);
    ctx.lineTo(width, height * 0.36);
    ctx.moveTo(0, height * 0.64);
    ctx.lineTo(width, height * 0.64);
    ctx.stroke();
    ctx.save();
    ctx.strokeStyle = "#f5d90a";
    ctx.lineWidth = 3;
    ctx.setLineDash([22, 16]);
    ctx.beginPath();
    ctx.moveTo(0, height * 0.5);
    ctx.lineTo(width, height * 0.5);
    ctx.stroke();
    ctx.restore();
    ctx.fillStyle = "#0f2744";
    ctx.beginPath();
    ctx.arc(width - 46, 46, 22, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#f8fafc";
    ctx.font = "700 18px Tahoma, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("ش", width - 46, 48);
  }

  function drawItem(item, width, height) {
    const x = item.x * width;
    const y = item.y * height;
    if (item.kind === "tree") {
      ctx.fillStyle = "#7c4a21";
      ctx.fillRect(x - 3, y - 2, 6, 18);
      ctx.fillStyle = "#15803d";
      ctx.beginPath();
      ctx.arc(x, y - 16, 12, 0, Math.PI * 2);
      ctx.arc(x - 10, y - 8, 9, 0, Math.PI * 2);
      ctx.arc(x + 10, y - 8, 9, 0, Math.PI * 2);
      ctx.fill();
      return;
    }
    if (item.kind === "pole") {
      ctx.strokeStyle = "#374151";
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(x, y - 28);
      ctx.lineTo(x, y + 16);
      ctx.stroke();
      ctx.strokeStyle = "#f5d90a";
      ctx.beginPath();
      ctx.moveTo(x, y - 2);
      ctx.lineTo(x, y + 6);
      ctx.stroke();
      ctx.fillStyle = "#e5e7eb";
      ctx.fillRect(x - 8, y - 32, 16, 6);
      return;
    }
    if (item.kind === "hole") {
      ctx.save();
      ctx.translate(x, y);
      ctx.scale(1.15, 0.72);
      ctx.beginPath();
      ctx.arc(0, 0, 16, 0, Math.PI * 2);
      ctx.fillStyle = "#6b3f24";
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = "#3f2414";
      ctx.stroke();
      ctx.restore();
      ctx.fillStyle = "#f8f1e6";
      ctx.font = "700 11px Tahoma, sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("حفرة", x, y + 1);
      return;
    }
    const color = colors[(Number(item.n) - 1) % colors.length] || colors[0];
    ctx.beginPath();
    ctx.arc(x, y, 16, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.lineWidth = 2;
    ctx.strokeStyle = "#ffffff";
    ctx.stroke();
    ctx.fillStyle = "#ffffff";
    ctx.font = "700 16px Tahoma, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(String(item.n), x, y + 1);
  }

  function draw() {
    const box = size();
    drawPaper(box.width, box.height);
    canvas._items.forEach((item) => drawItem(item, box.width, box.height));
    const tool = canvas._tool;
    canvas.style.cursor = tool === "select" ? "grab" : tool === "erase" ? "cell" : "crosshair";
    return box;
  }

  function point(ev, box) {
    const rect = canvas.getBoundingClientRect();
    const x = ((ev.clientX - rect.left) / rect.width) * box.width;
    const y = ((ev.clientY - rect.top) / rect.height) * box.height;
    return {
      x: Math.min(0.98, Math.max(0.02, x / box.width)),
      y: Math.min(0.98, Math.max(0.02, y / box.height)),
      px: x,
      py: y,
    };
  }

  function nearest(px, py, box) {
    let found = null;
    let best = 28;
    canvas._items.forEach((item) => {
      const distance = Math.hypot(item.x * box.width - px, item.y * box.height - py);
      if (distance < best) {
        best = distance;
        found = item;
      }
    });
    return found;
  }

  function commit() {
    const plain = canvas._items.map((item) => ({
      id: item.id,
      kind: item.kind,
      n: item.n || 0,
      x: Math.round(item.x * 1000) / 1000,
      y: Math.round(item.y * 1000) / 1000,
    }));
    canvas._sig = JSON.stringify(plain);
    setStateValue("marks", plain);
    setStateValue("snapshot", canvas.toDataURL("image/png"));
  }

  draw();

  canvas.onpointerdown = (ev) => {
    const box = size();
    const spot = point(ev, box);
    const tool = canvas._tool;
    const hit = nearest(spot.px, spot.py, box);
    if (tool === "select") {
      if (!hit) return;
      canvas._drag = hit;
      canvas.setPointerCapture(ev.pointerId);
      return;
    }
    if (tool === "erase") {
      if (!hit) return;
      canvas._items = canvas._items.filter((item) => item !== hit);
      draw();
      commit();
      return;
    }
    if (tool === "tree" || tool === "pole" || tool === "hole") {
      canvas._seq = (canvas._seq || 0) + 1;
      canvas._items.push({
        id: tool + "-" + Date.now() + "-" + canvas._seq,
        kind: tool,
        n: 0,
        x: spot.x,
        y: spot.y,
      });
      draw();
      commit();
      return;
    }
    const number = Number(tool);
    if (!number) return;
    const existing = canvas._items.find((item) => item.kind === "vehicle" && item.n === number);
    if (existing) {
      existing.x = spot.x;
      existing.y = spot.y;
    } else {
      canvas._items.push({
        id: "v-" + number,
        kind: "vehicle",
        n: number,
        x: spot.x,
        y: spot.y,
      });
    }
    draw();
    commit();
  };

  canvas.onpointermove = (ev) => {
    if (!canvas._drag) return;
    const box = size();
    const spot = point(ev, box);
    canvas._drag.x = spot.x;
    canvas._drag.y = spot.y;
    draw();
  };

  canvas.onpointerup = () => {
    if (!canvas._drag) return;
    canvas._drag = null;
    commit();
  };

  return () => {
    canvas.onpointerdown = null;
    canvas.onpointermove = null;
    canvas.onpointerup = null;
  };
}
"""

_BOARD = st.components.v2.component(
    "bayyinah_kroky_board",
    html=_HTML,
    css=_CSS,
    js=_JS,
)


def kroky_board(*, marks: list, tool: str, key: str):
    return _BOARD(
        key=key,
        data={"marks": marks, "tool": tool},
        default={"marks": [], "snapshot": ""},
        on_marks_change=lambda: None,
        on_snapshot_change=lambda: None,
        width="stretch",
        height=648,
    )
