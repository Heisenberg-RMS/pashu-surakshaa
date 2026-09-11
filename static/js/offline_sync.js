/**
 * Pashu Suraksha - IndexedDB Offline Queue & Auto-Sync Engine
 * Allows para-vets and farmers to submit symptom reports in remote areas with zero cell connectivity.
 * Automatically synchronizes reports when internet connectivity is re-established.
 */

class OfflineSyncManager {
  constructor() {
    this.dbName = 'PashuSurakshaDB';
    this.storeName = 'offline_reports';
    this.db = null;
    this.isOnline = navigator.onLine;
    this.initDB();
    this.setupListeners();
  }

  initDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, 1);

      request.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(this.storeName)) {
          db.createObjectStore(this.storeName, { keyPath: 'client_id', autoIncrement: true });
        }
      };

      request.onsuccess = (e) => {
        this.db = e.target.result;
        this.updatePendingCountUI();
        resolve(this.db);
      };

      request.onerror = (e) => {
        console.error('IndexedDB error:', e);
        reject(e);
      };
    });
  }

  setupListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.updateNetworkBadge();
      this.syncPendingReports();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.updateNetworkBadge();
    });

    this.updateNetworkBadge();
  }

  updateNetworkBadge() {
    const badge = document.getElementById('syncBadge');
    if (!badge) return;

    if (this.isOnline) {
      badge.className = 'sync-badge';
      badge.innerHTML = `<span class="dot"></span> Online (Auto-Sync Ready)`;
    } else {
      badge.className = 'sync-badge offline';
      badge.innerHTML = `<span class="dot"></span> Offline Mode (Queuing)`;
    }
  }

  async saveReportLocally(reportData) {
    if (!this.db) await this.initDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      reportData.queued_at = new Date().toISOString();
      const req = store.add(reportData);

      req.onsuccess = () => {
        this.updatePendingCountUI();
        resolve(true);
      };

      req.onerror = (e) => reject(e);
    });
  }

  async getPendingReports() {
    if (!this.db) await this.initDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName], 'readonly');
      const store = transaction.objectStore(this.storeName);
      const req = store.getAll();

      req.onsuccess = () => resolve(req.result || []);
      req.onerror = (e) => reject(e);
    });
  }

  async clearPendingReport(clientId) {
    if (!this.db) await this.initDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.storeName], 'readwrite');
      const store = transaction.objectStore(this.storeName);
      const req = store.delete(clientId);
      req.onsuccess = () => {
        this.updatePendingCountUI();
        resolve(true);
      };
      req.onerror = (e) => reject(e);
    });
  }

  async updatePendingCountUI() {
    try {
      const pending = await this.getPendingReports();
      const count = pending.length;
      const counterEl = document.getElementById('pendingQueueCount');
      if (counterEl) {
        counterEl.innerText = count > 0 ? `(${count} Pending Sync)` : '';
      }
    } catch (e) {
      console.warn('Could not update pending count:', e);
    }
  }

  async syncPendingReports() {
    if (!this.isOnline) return;

    const pending = await this.getPendingReports();
    if (pending.length === 0) return;

    console.log(`Syncing ${pending.length} offline animal disease reports...`);
    let synced = 0;

    for (const report of pending) {
      try {
        const response = await fetch('/api/reports', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(report)
        });

        if (response.ok) {
          await this.clearPendingReport(report.client_id);
          synced++;
        }
      } catch (err) {
        console.error('Failed to sync report:', err);
        break;
      }
    }

    if (synced > 0) {
      const badge = document.getElementById('syncBadge');
      if (badge) {
        badge.innerHTML = `<span class="dot"></span> Synced ${synced} Reports!`;
        setTimeout(() => this.updateNetworkBadge(), 4000);
      }
      if (window.App && window.App.refreshData) {
        window.App.refreshData();
      }
    }
  }
}

window.OfflineManager = new OfflineSyncManager();
