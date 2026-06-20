/**
 * SentimentAI — History Page JS
 * Handles: client-side table filtering and row deletion via API.
 */

// ── DOM References ──────────────────────────────────────────────────────────
const filterInput  = document.getElementById("filterInput");
const labelFilter  = document.getElementById("labelFilter");
const recordsTable = document.getElementById("recordsTable");

// ── Filtering ────────────────────────────────────────────────────────────────
function applyFilters() {
  if (!recordsTable) return;

  const textQ  = (filterInput?.value || "").toLowerCase();
  const labelQ = (labelFilter?.value || "").toUpperCase();
  const rows   = recordsTable.querySelectorAll("tbody tr");

  rows.forEach(row => {
    const rowText  = row.querySelector(".text-cell")?.textContent?.toLowerCase() || "";
    const rowLabel = row.dataset.label?.toUpperCase() || "";

    const matchText  = !textQ  || rowText.includes(textQ) || rowLabel.toLowerCase().includes(textQ);
    const matchLabel = !labelQ || rowLabel === labelQ;

    row.style.display = matchText && matchLabel ? "" : "none";
  });
}

filterInput?.addEventListener("input", applyFilters);
labelFilter?.addEventListener("change", applyFilters);

// ── Delete ────────────────────────────────────────────────────────────────────
document.addEventListener("click", async (e) => {
  const btn = e.target.closest(".btn-delete");
  if (!btn) return;

  const docId = btn.dataset.id;
  const row   = btn.closest("tr");

  if (!confirm("Delete this analysis record?")) return;

  try {
    const res = await fetch(`/delete/${docId}`, { method: "DELETE" });
    if (res.ok) {
      row.style.transition = "opacity 0.3s, transform 0.3s";
      row.style.opacity    = "0";
      row.style.transform  = "translateX(20px)";
      setTimeout(() => row.remove(), 300);
    } else {
      const err = await res.json();
      alert(`Delete failed: ${err.error || "Unknown error"}`);
    }
  } catch (error) {
    alert(`Network error: ${error.message}`);
  }
});
