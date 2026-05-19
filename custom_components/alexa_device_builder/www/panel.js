/**
 * Alexa Device Builder – Custom Sidebar Panel
 *
 * Registers the <alexa-device-panel> web component which is served by HA
 * under the "Alexa Devices" sidebar entry (Amazon account management mode).
 *
 * No build step required – plain ES-module compatible vanilla JS.
 */

// ---------------------------------------------------------------------------
// Styles (Shadow DOM – uses HA CSS custom-properties where available)
// ---------------------------------------------------------------------------
const STYLES = /* css */ `
  :host {
    display: block;
    padding: 16px;
    background: var(--lovelace-background, var(--primary-background-color, #fafafa));
    color: var(--primary-text-color, #212121);
    font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
    min-height: 100vh;
    box-sizing: border-box;
  }

  /* ── Header ─────────────────────────────────────────────── */
  .header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }
  .header h1 {
    margin: 0;
    font-size: 22px;
    font-weight: 400;
    flex: 1;
    min-width: 200px;
  }
  .pending-badge {
    padding: 3px 10px;
    border-radius: 12px;
    background: var(--warning-color, #f59b00);
    color: #fff;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
  }

  /* ── Cards ──────────────────────────────────────────────── */
  .card {
    background: var(--card-background-color, #fff);
    border-radius: 8px;
    box-shadow: var(--ha-card-box-shadow, 0 2px 6px rgba(0,0,0,.1));
    padding: 16px;
    margin-bottom: 16px;
  }

  /* ── Buttons ────────────────────────────────────────────── */
  button.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    white-space: nowrap;
    transition: opacity .15s;
  }
  button.btn:hover  { opacity: .85; }
  button.btn:active { opacity: .70; }
  button.btn:disabled { opacity: .4; cursor: not-allowed; }
  .btn-primary   { background: var(--primary-color, #03a9f4); color: #fff; }
  .btn-danger    { background: var(--error-color, #db4437);   color: #fff; }
  .btn-secondary {
    background: var(--secondary-background-color, #f0f0f0);
    color: var(--primary-text-color, #212121);
    border: 1px solid var(--divider-color, #ddd);
  }

  /* ── Filters ────────────────────────────────────────────── */
  .filters {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
  }
  .filter-input,
  .filter-select {
    padding: 7px 11px;
    border: 1px solid var(--divider-color, #ddd);
    border-radius: 4px;
    background: var(--input-fill-color, #fff);
    color: var(--primary-text-color, #212121);
    font-size: 13px;
  }
  .filter-input  { flex: 1; min-width: 180px; }
  .filter-select { min-width: 130px; }

  /* ── Bulk action bar ────────────────────────────────────── */
  .bulk-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    background: var(--primary-color, #03a9f4);
    color: #fff;
    border-radius: 6px;
    margin-bottom: 10px;
    flex-wrap: wrap;
  }
  .bulk-bar .lbl { flex: 1; font-weight: 500; font-size: 13px; }
  .bulk-bar .btn-secondary {
    background: rgba(255,255,255,.2);
    color: #fff;
    border-color: rgba(255,255,255,.4);
  }

  /* ── Table ──────────────────────────────────────────────── */
  .table-wrap { overflow-x: auto; }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }
  th {
    text-align: left;
    padding: 9px 8px;
    border-bottom: 2px solid var(--divider-color, #e0e0e0);
    font-weight: 500;
    white-space: nowrap;
    color: var(--secondary-text-color, #757575);
  }
  td {
    padding: 9px 8px;
    border-bottom: 1px solid var(--divider-color, #e0e0e0);
    vertical-align: middle;
  }
  tr:hover td { background: var(--secondary-background-color, #f5f5f5); }
  tr.row-selected td { background: rgba(3,169,244,.08); }
  tr.row-rename  td:nth-child(2) { font-style: italic; }
  tr.row-delete  td { opacity: .5; text-decoration: line-through; }

  .name-cell small { color: var(--secondary-text-color, #757575); margin-left: 4px; }

  /* ── Badges ─────────────────────────────────────────────── */
  .badge {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: 500;
    background: var(--secondary-background-color, #f0f0f0);
    color: var(--secondary-text-color, #757575);
    margin: 1px 2px 1px 0;
  }
  .badge.rename { background: #e3f2fd; color: #1565c0; }
  .badge.delete { background: #fce4ec; color: #b71c1c; }

  /* ── Row action buttons ─────────────────────────────────── */
  .act-cell { white-space: nowrap; }
  .act-cell button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 3px 6px;
    border-radius: 3px;
    color: var(--secondary-text-color, #757575);
    font-size: 16px;
    line-height: 1;
  }
  .act-cell button:hover { background: var(--secondary-background-color, #f0f0f0); }
  .act-cell button.edit:hover { color: var(--primary-color, #03a9f4); }
  .act-cell button.del:hover  { color: var(--error-color, #db4437); }
  .act-cell button.undo:hover { color: var(--warning-color, #f59b00); }

  /* ── Status / empty states ──────────────────────────────── */
  .loading, .empty {
    text-align: center;
    padding: 40px 16px;
    color: var(--secondary-text-color, #757575);
    font-size: 14px;
  }
  .error-box {
    padding: 12px 16px;
    border-radius: 6px;
    background: #fce4ec;
    color: #b71c1c;
    font-size: 13px;
    margin-bottom: 14px;
  }
  .info-box {
    padding: 12px 16px;
    border-radius: 6px;
    background: #e8f5e9;
    color: #2e7d32;
    font-size: 13px;
    margin-bottom: 14px;
  }

  /* ── Modal ──────────────────────────────────────────────── */
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.45);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  .modal {
    background: var(--card-background-color, #fff);
    border-radius: 10px;
    padding: 24px;
    width: min(560px, 92vw);
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 10px 40px rgba(0,0,0,.25);
  }
  .modal h2 {
    margin: 0 0 16px;
    font-size: 18px;
    font-weight: 500;
  }
  .form-row { margin-bottom: 12px; }
  .form-row label {
    display: block;
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: .05em;
    color: var(--secondary-text-color, #757575);
    margin-bottom: 5px;
  }
  .form-row input[type=text] {
    width: 100%;
    padding: 8px 11px;
    border: 1px solid var(--divider-color, #ddd);
    border-radius: 4px;
    font-size: 13px;
    background: var(--input-fill-color, #fff);
    color: var(--primary-text-color, #212121);
    box-sizing: border-box;
  }
  .form-row code {
    background: var(--secondary-background-color, #f0f0f0);
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 12px;
  }
  .form-row small { color: var(--secondary-text-color, #757575); font-size: 11px; }
  .modal-footer {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
    margin-top: 18px;
  }

  /* ── Preview / result list ──────────────────────────────── */
  .change-list {
    max-height: 280px;
    overflow-y: auto;
    border: 1px solid var(--divider-color, #ddd);
    border-radius: 4px;
    margin: 8px 0;
  }
  .change-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-bottom: 1px solid var(--divider-color, #ddd);
    font-size: 13px;
  }
  .change-item:last-child { border-bottom: none; }
  .change-item .arrow { color: var(--secondary-text-color, #757575); }
  .icon-ok   { color: var(--success-color, #43a047); font-size: 16px; }
  .icon-fail { color: var(--error-color,   #db4437); font-size: 16px; }

  .warn-box {
    padding: 10px 14px;
    border-radius: 4px;
    background: #fff8e1;
    color: #795548;
    font-size: 12px;
    margin-top: 10px;
  }
`;

// ---------------------------------------------------------------------------
// Helper – HTML-escape a value for safe injection into innerHTML
// ---------------------------------------------------------------------------
function esc(v) {
  if (v == null) return "";
  return String(v)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
class AlexaDevicePanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._initialized = false;

    /** @type {{
     *   loading: boolean,
     *   error: string|null,
     *   devices: Array,
     *   selected: Set<string>,
     *   changes: Map<string,{action:string,newName?:string,originalName:string}>,
     *   search: string,
     *   filterType: string,
     *   filterGroup: string,
     *   modal: string|null,
     *   editDevice: object|null,
     *   editName: string,
     *   bulkPattern: string,
     *   results: Array|null,
     * }} */
    this._s = {
      loading: false,
      error: null,
      devices: [],
      selected: new Set(),
      changes: new Map(),
      search: "",
      filterType: "",
      filterGroup: "",
      modal: null,
      editDevice: null,
      editName: "",
      bulkPattern: "",
      results: null,
    };
    this._render();
  }

  // ── HA lifecycle ──────────────────────────────────────────

  set hass(hass) {
    this._hass = hass;
    if (!this._initialized) {
      this._initialized = true;
      this._loadDevices();
    }
  }

  setConfig(config) {
    this._config = config;
  }

  // ── State helpers ─────────────────────────────────────────

  _setState(patch) {
    Object.assign(this._s, patch);
    this._render();
  }

  // ── Data fetching ─────────────────────────────────────────

  async _loadDevices() {
    this._setState({ loading: true, error: null });
    try {
      const resp = await this._fetch("/api/alexa_device_builder/devices");
      const data = await resp.json();
      if (data.error) {
        this._setState({ loading: false, error: data.error, devices: [] });
      } else {
        this._setState({
          loading: false,
          devices: data.devices || [],
          selected: new Set(),
          changes: new Map(),
        });
      }
    } catch (e) {
      this._setState({ loading: false, error: e.message });
    }
  }

  async _applyChanges() {
    const actions = [];
    for (const [applianceId, change] of this._s.changes) {
      if (change.action === "delete") {
        actions.push({ applianceId, action: "delete" });
      } else if (change.action === "rename") {
        actions.push({ applianceId, action: "rename", newName: change.newName });
      }
    }
    this._setState({ loading: true, modal: null });
    try {
      const resp = await this._fetch("/api/alexa_device_builder/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ actions }),
      });
      const data = await resp.json();
      this._setState({
        loading: false,
        modal: "results",
        results: data.results || [],
      });
    } catch (e) {
      this._setState({ loading: false, error: e.message });
    }
  }

  _fetch(url, opts = {}) {
    const token = this._hass?.auth?.data?.access_token;
    return fetch(url, {
      ...opts,
      headers: {
        ...(opts.headers || {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
  }

  // ── Derived data ──────────────────────────────────────────

  _getFiltered() {
    const { devices, search, filterType, filterGroup } = this._s;
    const q = search.toLowerCase();
    return devices.filter((d) => {
      if (
        q &&
        !d.friendlyName.toLowerCase().includes(q) &&
        !d.applianceId.toLowerCase().includes(q)
      )
        return false;
      if (
        filterType &&
        !(d.applianceTypes || []).some(
          (t) => t.toLowerCase() === filterType.toLowerCase()
        )
      )
        return false;
      if (filterGroup && d.groupName !== filterGroup) return false;
      return true;
    });
  }

  _getTypes() {
    const set = new Set();
    for (const d of this._s.devices)
      for (const t of d.applianceTypes || []) set.add(t);
    return [...set].sort();
  }

  _getGroups() {
    const set = new Set();
    for (const d of this._s.devices) if (d.groupName) set.add(d.groupName);
    return [...set].sort();
  }

  // ── Actions ───────────────────────────────────────────────

  _toggleSelect(id) {
    const sel = new Set(this._s.selected);
    if (sel.has(id)) sel.delete(id);
    else sel.add(id);
    this._setState({ selected: sel });
  }

  _toggleSelectAll(checked) {
    const filtered = this._getFiltered();
    const sel = checked
      ? new Set(filtered.map((d) => d.applianceId))
      : new Set();
    this._setState({ selected: sel });
  }

  _markDelete(id) {
    const changes = new Map(this._s.changes);
    const dev = this._s.devices.find((d) => d.applianceId === id);
    if (changes.has(id) && changes.get(id).action === "delete") {
      changes.delete(id); // toggle off
    } else {
      changes.set(id, {
        action: "delete",
        originalName: dev?.friendlyName || id,
      });
    }
    this._setState({ changes });
  }

  _undoChange(id) {
    const changes = new Map(this._s.changes);
    changes.delete(id);
    this._setState({ changes });
  }

  _openEdit(device) {
    const existing = this._s.changes.get(device.applianceId);
    const editName =
      existing?.action === "rename"
        ? existing.newName
        : device.friendlyName;
    this._setState({ modal: "edit", editDevice: device, editName });
  }

  _saveEdit() {
    const { editDevice, editName, changes } = this._s;
    if (!editDevice) return;
    const newChanges = new Map(changes);
    const trimmed = (editName || "").trim();
    if (trimmed && trimmed !== editDevice.friendlyName) {
      newChanges.set(editDevice.applianceId, {
        action: "rename",
        newName: trimmed,
        originalName: editDevice.friendlyName,
      });
    } else {
      newChanges.delete(editDevice.applianceId);
    }
    this._setState({ changes: newChanges, modal: null, editDevice: null });
  }

  _applyBulkRename() {
    const { selected, bulkPattern, changes, devices } = this._s;
    const pattern = (bulkPattern || "").trim();
    if (!pattern) return;
    const newChanges = new Map(changes);
    for (const id of selected) {
      const dev = devices.find((d) => d.applianceId === id);
      if (!dev) continue;
      const newName = pattern.replace(/\{name\}/g, dev.friendlyName);
      if (newName !== dev.friendlyName) {
        newChanges.set(id, {
          action: "rename",
          newName,
          originalName: dev.friendlyName,
        });
      }
    }
    this._setState({ changes: newChanges, modal: null, bulkPattern: "" });
  }

  _bulkDelete() {
    const { selected, changes, devices } = this._s;
    const newChanges = new Map(changes);
    for (const id of selected) {
      const dev = devices.find((d) => d.applianceId === id);
      newChanges.set(id, {
        action: "delete",
        originalName: dev?.friendlyName || id,
      });
    }
    this._setState({ changes: newChanges, selected: new Set() });
  }

  // ── Render ────────────────────────────────────────────────

  _render() {
    // Preserve focused element id across re-renders
    const focusedId = this.shadowRoot.activeElement?.id;
    const selStart = this.shadowRoot.activeElement?.selectionStart;

    const s = this._s;
    const filtered = this._getFiltered();
    const allSelected =
      filtered.length > 0 && filtered.every((d) => s.selected.has(d.applianceId));
    const someSelected = s.selected.size > 0;
    const pendingCount = s.changes.size;
    const types = this._getTypes();
    const groups = this._getGroups();

    const errorMessages = {
      alexa_media_unavailable:
        "The <strong>Alexa Media Player</strong> integration is not installed or not configured.",
      not_logged_in:
        "No active Alexa Media Player session found. Please log in via the Alexa Media Player integration first.",
      no_amazon_entry:
        "No <em>Amazon account management</em> entry is configured. Add one via Settings → Integrations.",
    };

    // ── Device rows
    const rowsHtml = filtered
      .map((d) => {
        const change = s.changes.get(d.applianceId);
        const isSelected = s.selected.has(d.applianceId);
        const rowClass = [
          isSelected ? "row-selected" : "",
          change?.action === "rename" ? "row-rename" : "",
          change?.action === "delete" ? "row-delete" : "",
        ]
          .filter(Boolean)
          .join(" ");

        const displayName =
          change?.action === "rename"
            ? `${esc(change.newName)} <small>(was: ${esc(d.friendlyName)})</small>`
            : esc(d.friendlyName);

        const typeBadges = (d.applianceTypes || [])
          .slice(0, 3)
          .map((t) => `<span class="badge">${esc(t)}</span>`)
          .join("");

        const undoBtn = change
          ? `<button class="undo" data-id="${esc(d.applianceId)}" title="Undo change">↩</button>`
          : "";

        return `
          <tr class="${rowClass}">
            <td><input type="checkbox" class="chk-row" data-id="${esc(d.applianceId)}" ${isSelected ? "checked" : ""}></td>
            <td class="name-cell">
              ${displayName}
              ${change ? `<span class="badge ${change.action}">${esc(change.action)}</span>` : ""}
            </td>
            <td>${typeBadges}</td>
            <td>${esc(d.groupName)}</td>
            <td>${esc(d.manufacturerName)}</td>
            <td><small>${esc(d.applianceId)}</small></td>
            <td class="act-cell">
              <button class="edit" data-id="${esc(d.applianceId)}" title="Rename">✏️</button>
              <button class="del" data-id="${esc(d.applianceId)}" title="${
                change?.action === "delete" ? "Undo delete" : "Mark for delete"
              }">${change?.action === "delete" ? "↩" : "🗑"}</button>
              ${undoBtn}
            </td>
          </tr>`;
      })
      .join("");

    // ── Preview change list
    const previewRows = [...s.changes.entries()]
      .map(([id, c]) => {
        const dev = s.devices.find((d) => d.applianceId === id);
        const name = dev?.friendlyName || id;
        if (c.action === "delete") {
          return `<div class="change-item">
            <span class="badge delete">delete</span>
            <span>${esc(name)}</span>
          </div>`;
        }
        return `<div class="change-item">
          <span class="badge rename">rename</span>
          <span>${esc(name)}</span>
          <span class="arrow">→</span>
          <strong>${esc(c.newName)}</strong>
        </div>`;
      })
      .join("");

    // ── Result list
    const resultRows = (s.results || [])
      .map((r) => {
        const dev = s.devices.find((d) => d.applianceId === r.applianceId);
        const name = dev?.friendlyName || r.applianceId;
        return `<div class="change-item">
          <span class="${r.success ? "icon-ok" : "icon-fail"}">${r.success ? "✓" : "✗"}</span>
          <span class="badge ${r.action}">${esc(r.action)}</span>
          <span>${esc(name)}</span>
          ${r.error ? `<small style="color:var(--error-color,#db4437)">(${esc(r.error)})</small>` : ""}
        </div>`;
      })
      .join("");

    // ── Modals
    const editModal =
      s.modal === "edit" && s.editDevice
        ? `<div class="overlay" id="modal-overlay">
            <div class="modal">
              <h2>✏️ Rename Device</h2>
              <div class="form-row">
                <label>Appliance ID</label>
                <small>${esc(s.editDevice.applianceId)}</small>
              </div>
              <div class="form-row">
                <label>New name</label>
                <input type="text" id="edit-name" value="${esc(s.editName)}" placeholder="Enter new name…">
              </div>
              <div class="modal-footer">
                <button class="btn btn-secondary" id="btn-edit-cancel">Cancel</button>
                <button class="btn btn-primary" id="btn-edit-save">Save</button>
              </div>
            </div>
          </div>`
        : "";

    const bulkRenameModal =
      s.modal === "bulk-rename"
        ? `<div class="overlay" id="modal-overlay">
            <div class="modal">
              <h2>✏️ Bulk Rename (${s.selected.size} device${s.selected.size > 1 ? "s" : ""})</h2>
              <div class="form-row">
                <label>Name pattern</label>
                <input type="text" id="bulk-pattern" value="${esc(s.bulkPattern)}" placeholder="e.g. Living Room {name}">
                <small>Use <code>{name}</code> to include the original device name.</small>
              </div>
              <div class="modal-footer">
                <button class="btn btn-secondary" id="btn-bulk-cancel">Cancel</button>
                <button class="btn btn-primary" id="btn-bulk-apply">Apply pattern</button>
              </div>
            </div>
          </div>`
        : "";

    const previewModal =
      s.modal === "preview"
        ? `<div class="overlay" id="modal-overlay">
            <div class="modal">
              <h2>Preview Changes (${pendingCount})</h2>
              <p style="font-size:13px;margin:0 0 8px">The following changes will be sent to your Amazon account:</p>
              <div class="change-list">${previewRows}</div>
              <div class="warn-box">⚠️ Changes are applied directly to Amazon. This action cannot be undone from this panel.</div>
              <div class="modal-footer">
                <button class="btn btn-secondary" id="btn-preview-cancel">Cancel</button>
                <button class="btn btn-danger" id="btn-preview-apply">Apply to Amazon</button>
              </div>
            </div>
          </div>`
        : "";

    const resultsModal =
      s.modal === "results"
        ? (() => {
            const ok = (s.results || []).filter((r) => r.success).length;
            const fail = (s.results || []).length - ok;
            return `<div class="overlay" id="modal-overlay">
              <div class="modal">
                <h2>Results</h2>
                ${
                  ok > 0
                    ? `<div class="info-box">✓ ${ok} change${ok > 1 ? "s" : ""} applied successfully.</div>`
                    : ""
                }
                ${
                  fail > 0
                    ? `<div class="error-box">✗ ${fail} change${fail > 1 ? "s" : ""} failed.</div>`
                    : ""
                }
                <div class="change-list">${resultRows}</div>
                <div class="modal-footer">
                  <button class="btn btn-primary" id="btn-results-close">Close &amp; Refresh</button>
                </div>
              </div>
            </div>`;
          })()
        : "";

    // ── Full HTML
    this.shadowRoot.innerHTML = `
      <style>${STYLES}</style>

      <div class="header">
        <h1>☁️ Alexa Device Manager</h1>
        ${pendingCount > 0 ? `<span class="pending-badge">${pendingCount} pending</span>` : ""}
        ${pendingCount > 0 ? `<button class="btn btn-primary" id="btn-preview">Preview &amp; Apply</button>` : ""}
        <button class="btn btn-secondary" id="btn-refresh">↻ Refresh</button>
      </div>

      ${s.error ? `<div class="error-box">⚠️ ${errorMessages[s.error] || esc(s.error)}</div>` : ""}

      ${
        s.loading
          ? `<div class="loading">Loading devices…</div>`
          : `
        <div class="card">
          <div class="filters">
            <input class="filter-input" id="search" placeholder="Search name or ID…" value="${esc(s.search)}">
            <select class="filter-select" id="filter-type">
              <option value="">All types</option>
              ${types.map((t) => `<option value="${esc(t)}" ${s.filterType === t ? "selected" : ""}>${esc(t)}</option>`).join("")}
            </select>
            <select class="filter-select" id="filter-group">
              <option value="">All groups</option>
              ${groups.map((g) => `<option value="${esc(g)}" ${s.filterGroup === g ? "selected" : ""}>${esc(g)}</option>`).join("")}
            </select>
            <button class="btn btn-secondary" id="btn-reset-filters">Reset</button>
          </div>
        </div>

        ${
          someSelected
            ? `<div class="bulk-bar">
                <span class="lbl">${s.selected.size} device${s.selected.size > 1 ? "s" : ""} selected</span>
                <button class="btn btn-secondary" id="btn-bulk-rename">✏️ Rename (pattern)</button>
                <button class="btn btn-danger"    id="btn-bulk-delete">🗑 Delete</button>
                <button class="btn btn-secondary" id="btn-deselect">✕ Clear selection</button>
              </div>`
            : ""
        }

        <div class="card">
          ${
            filtered.length === 0
              ? `<div class="empty">No devices found${s.search || s.filterType || s.filterGroup ? " – try resetting the filters" : ""}.</div>`
              : `<div class="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th><input type="checkbox" id="chk-all" ${allSelected ? "checked" : ""}></th>
                        <th>Name</th>
                        <th>Type</th>
                        <th>Group</th>
                        <th>Manufacturer</th>
                        <th>Appliance ID</th>
                        <th></th>
                      </tr>
                    </thead>
                    <tbody>${rowsHtml}</tbody>
                  </table>
                </div>`
          }
        </div>
      `
      }

      ${editModal}
      ${bulkRenameModal}
      ${previewModal}
      ${resultsModal}
    `;

    this._bindEvents();

    // Restore focus after re-render (keeps search/filter inputs usable)
    if (focusedId) {
      const el = this.shadowRoot.getElementById(focusedId);
      if (el) {
        el.focus();
        if (selStart != null && el.setSelectionRange) {
          try {
            el.setSelectionRange(selStart, selStart);
          } catch (_) {
            // non-text inputs — ignore
          }
        }
      }
    }
  }

  // ── Event binding ─────────────────────────────────────────

  _bindEvents() {
    const R = this.shadowRoot;
    const on = (id, ev, fn) => R.getElementById(id)?.addEventListener(ev, fn);

    on("btn-refresh", "click", () => this._loadDevices());
    on("btn-preview", "click", () => this._setState({ modal: "preview" }));
    on("btn-reset-filters", "click", () =>
      this._setState({ search: "", filterType: "", filterGroup: "" })
    );

    // Search / filter inputs – update state without full re-render to keep focus
    R.getElementById("search")?.addEventListener("input", (e) => {
      this._s.search = e.target.value;
      this._render();
    });
    R.getElementById("filter-type")?.addEventListener("change", (e) => {
      this._setState({ filterType: e.target.value });
    });
    R.getElementById("filter-group")?.addEventListener("change", (e) => {
      this._setState({ filterGroup: e.target.value });
    });

    // Select all / row checkboxes
    R.getElementById("chk-all")?.addEventListener("change", (e) =>
      this._toggleSelectAll(e.target.checked)
    );
    R.querySelectorAll(".chk-row").forEach((chk) =>
      chk.addEventListener("change", (e) =>
        this._toggleSelect(e.target.dataset.id)
      )
    );

    // Row action buttons
    R.querySelectorAll("button.edit").forEach((btn) =>
      btn.addEventListener("click", (e) => {
        const dev = this._s.devices.find(
          (d) => d.applianceId === e.currentTarget.dataset.id
        );
        if (dev) this._openEdit(dev);
      })
    );
    R.querySelectorAll("button.del").forEach((btn) =>
      btn.addEventListener("click", (e) =>
        this._markDelete(e.currentTarget.dataset.id)
      )
    );
    R.querySelectorAll("button.undo").forEach((btn) =>
      btn.addEventListener("click", (e) =>
        this._undoChange(e.currentTarget.dataset.id)
      )
    );

    // Bulk actions
    on("btn-bulk-rename", "click", () => this._setState({ modal: "bulk-rename" }));
    on("btn-bulk-delete", "click", () => this._bulkDelete());
    on("btn-deselect",    "click", () => this._setState({ selected: new Set() }));

    // Edit modal
    on("btn-edit-cancel", "click", () =>
      this._setState({ modal: null, editDevice: null })
    );
    on("btn-edit-save", "click", () => this._saveEdit());
    const editNameEl = R.getElementById("edit-name");
    if (editNameEl) {
      // Sync editName without full re-render so cursor stays in place
      editNameEl.addEventListener("input", (e) => {
        this._s.editName = e.target.value;
      });
      editNameEl.addEventListener("keydown", (e) => {
        if (e.key === "Enter") this._saveEdit();
        if (e.key === "Escape") this._setState({ modal: null, editDevice: null });
      });
    }

    // Bulk rename modal
    on("btn-bulk-cancel", "click", () =>
      this._setState({ modal: null, bulkPattern: "" })
    );
    on("btn-bulk-apply", "click", () => this._applyBulkRename());
    const bulkEl = R.getElementById("bulk-pattern");
    if (bulkEl) {
      bulkEl.addEventListener("input", (e) => {
        this._s.bulkPattern = e.target.value;
      });
      bulkEl.addEventListener("keydown", (e) => {
        if (e.key === "Enter") this._applyBulkRename();
        if (e.key === "Escape")
          this._setState({ modal: null, bulkPattern: "" });
      });
    }

    // Preview modal
    on("btn-preview-cancel", "click", () => this._setState({ modal: null }));
    on("btn-preview-apply",  "click", () => this._applyChanges());

    // Results modal
    on("btn-results-close", "click", () => {
      this._setState({ modal: null, changes: new Map(), results: null });
      this._loadDevices();
    });

    // Close modal on overlay click
    R.getElementById("modal-overlay")?.addEventListener("click", (e) => {
      if (e.target.id === "modal-overlay") this._setState({ modal: null });
    });
  }
}

customElements.define("alexa-device-panel", AlexaDevicePanel);
