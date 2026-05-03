async function getJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

function card(title, body, meta = "") {
  const el = document.createElement("div");
  el.className = "card";
  el.innerHTML = `<strong>${title}</strong><div>${body}</div>${meta ? `<div class="meta">${meta}</div>` : ""}`;
  return el;
}

async function refresh() {
  const dashboard = await getJson("/api/dashboard");
  document.getElementById("health").textContent = JSON.stringify(dashboard.health, null, 2);

  const positions = document.getElementById("positions");
  positions.innerHTML = "";
  (dashboard.positions || []).forEach((position) => {
    positions.appendChild(card(position.symbol, `Net: ${position.net_quantity} | PnL: ${position.unrealized_pnl}`));
  });

  const orders = document.getElementById("orders");
  orders.innerHTML = "";
  const orderCards = (dashboard.open_orders || []).length ? dashboard.open_orders : dashboard.recent_orders || [];
  orderCards.forEach((entry) => {
    const payload = entry.payload || entry;
    orders.appendChild(card(payload.symbol || "Order", `${payload.side} ${payload.quantity}`, payload.state || payload.created_at || ""));
  });

  const timeline = document.getElementById("timeline");
  timeline.innerHTML = "";
  (dashboard.timeline || []).forEach((event) => {
    timeline.appendChild(card(event.event_type, JSON.stringify(event.payload), event.created_at));
  });
}

document.getElementById("seedCycle").addEventListener("click", async () => {
  await getJson("/api/seed-cycle", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
  await refresh();
});

document.getElementById("venueSelect").addEventListener("change", async (event) => {
  await getJson("/api/select-venue", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ venue: event.target.value }),
  });
  await refresh();
});

document.getElementById("killOn").addEventListener("click", async () => {
  await getJson("/api/kill-switch/toggle", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ engage: true }),
  });
  await refresh();
});

document.getElementById("killOff").addEventListener("click", async () => {
  await getJson("/api/kill-switch/toggle", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ engage: false }),
  });
  await refresh();
});

refresh().catch((error) => {
  document.getElementById("health").textContent = error.message;
});
