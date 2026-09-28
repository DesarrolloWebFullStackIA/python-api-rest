/**
 * ============================================================================
 * VaporStore Web Client Application Controller
 * Handles UI interactions, state management, search debounce, modal flows,
 * toast notifications, and interactive API documentation explorer.
 * ============================================================================
 */

import { categoriesApi, gamesApi, healthApi, steamApi } from './api.js';

// Application State
const state = {
  page: 1,
  pageSize: 6,
  total: 0,
  totalPages: 1,
  search: '',
  categoryId: '',
  minRating: '',
  maxPrice: '',
  categories: [],
  editingGameId: null,
  pendingDeleteAction: null
};

// DOM Elements Cache
const elements = {
  // Navigation & Tabs
  tabCatalogBtn: document.getElementById('tabCatalogBtn'),
  tabDocsBtn: document.getElementById('tabDocsBtn'),
  catalogSection: document.getElementById('catalogSection'),
  docsSection: document.getElementById('docsSection'),
  backendStatus: document.getElementById('backendStatus'),

  // Stats Counters
  totalGamesStat: document.getElementById('totalGamesStat'),
  totalCategoriesStat: document.getElementById('totalCategoriesStat'),

  // Search & Filters
  searchInput: document.getElementById('searchInput'),
  searchClearBtn: document.getElementById('searchClearBtn'),
  categoryFilter: document.getElementById('categoryFilter'),
  ratingFilter: document.getElementById('ratingFilter'),
  priceFilter: document.getElementById('priceFilter'),
  resetFiltersBtn: document.getElementById('resetFiltersBtn'),
  activeFiltersSummary: document.getElementById('activeFiltersSummary'),

  // Grid & Pagination
  gamesGrid: document.getElementById('gamesGrid'),
  paginationBar: document.getElementById('paginationBar'),
  paginationInfo: document.getElementById('paginationInfo'),
  prevPageBtn: document.getElementById('prevPageBtn'),
  nextPageBtn: document.getElementById('nextPageBtn'),
  pageSizeSelect: document.getElementById('pageSizeSelect'),

  // Actions
  newGameBtn: document.getElementById('newGameBtn'),
  manageCategoriesBtn: document.getElementById('manageCategoriesBtn'),

  // Game Modal
  gameModal: document.getElementById('gameModal'),
  gameModalTitle: document.getElementById('gameModalTitle'),
  gameForm: document.getElementById('gameForm'),
  gameCategorySelect: document.getElementById('gameCategorySelect'),
  gameTitleInput: document.getElementById('gameTitleInput'),
  gameDescInput: document.getElementById('gameDescInput'),
  gamePriceInput: document.getElementById('gamePriceInput'),
  gameYearInput: document.getElementById('gameYearInput'),
  gameRatingInput: document.getElementById('gameRatingInput'),
  gameSteamIdInput: document.getElementById('gameSteamIdInput'),
  gameActiveCheck: document.getElementById('gameActiveCheck'),
  gameModalCancelBtn: document.getElementById('gameModalCancelBtn'),
  gameSubmitBtn: document.getElementById('gameSubmitBtn'),

  // Category Manager Modal
  categoryModal: document.getElementById('categoryModal'),
  categoryListContainer: document.getElementById('categoryListContainer'),
  categoryForm: document.getElementById('categoryForm'),
  categoryNameInput: document.getElementById('categoryNameInput'),
  categoryDescInput: document.getElementById('categoryDescInput'),
  categoryModalCloseBtn: document.getElementById('categoryModalCloseBtn'),

  // Confirm Delete Modal
  confirmModal: document.getElementById('confirmModal'),
  confirmModalTitle: document.getElementById('confirmModalTitle'),
  confirmModalMessage: document.getElementById('confirmModalMessage'),
  confirmModalCancelBtn: document.getElementById('confirmModalCancelBtn'),
  confirmModalProceedBtn: document.getElementById('confirmModalProceedBtn'),

  // Steam Modal
  openSteamModalBtn: document.getElementById('openSteamModalBtn'),
  steamModal: document.getElementById('steamModal'),
  steamModalCloseBtn: document.getElementById('steamModalCloseBtn'),
  steamSearchInput: document.getElementById('steamSearchInput'),
  steamResultsContainer: document.getElementById('steamResultsContainer'),

  // Toast Container
  toastContainer: document.getElementById('toastContainer')
};

// Utilities: Light-dismiss polyfill for <dialog>
function setupDialogLightDismiss(dialog) {
  if (!dialog) return;
  // If browser doesn't natively support closedby="any"
  if (!('closedBy' in HTMLDialogElement.prototype)) {
    dialog.addEventListener('click', (event) => {
      if (event.target !== dialog) return;
      const rect = dialog.getBoundingClientRect();
      const isInside = (
        rect.top <= event.clientY &&
        event.clientY <= rect.top + rect.height &&
        rect.left <= event.clientX &&
        event.clientX <= rect.left + rect.width
      );
      if (!isInside) {
        dialog.close();
      }
    });
  }
}

// Toast Notifications System
function showToast(message, type = 'info', duration = 3500) {
  if (!elements.toastContainer) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'alert');

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || 'ℹ'}</span>
    <span class="toast-message">${escapeHtml(message)}</span>
  `;

  elements.toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(50px)';
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// Debounce helper
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Load Categories
async function loadCategories() {
  try {
    const categories = await categoriesApi.getAll();
    state.categories = categories;

    // Update Category Filter dropdown
    const currentFilterVal = elements.categoryFilter.value;
    elements.categoryFilter.innerHTML = '<option value="">All Categories</option>';
    categories.forEach((cat) => {
      const option = document.createElement('option');
      option.value = cat.id;
      option.textContent = `${cat.name} (${cat.games_count})`;
      elements.categoryFilter.appendChild(option);
    });
    elements.categoryFilter.value = currentFilterVal;

    // Update Game Form Category select
    elements.gameCategorySelect.innerHTML = '<option value="" disabled selected>Select a category...</option>';
    categories.forEach((cat) => {
      const option = document.createElement('option');
      option.value = cat.id;
      option.textContent = cat.name;
      elements.gameCategorySelect.appendChild(option);
    });

    // Update Header Stat
    if (elements.totalCategoriesStat) {
      elements.totalCategoriesStat.textContent = categories.length;
    }

    renderCategoryManagerList();
  } catch (error) {
    showToast(error.userMessage || 'Failed to load categories', 'error');
  }
}

// Fetch and Render Games
async function fetchGames() {
  // Show loading indicator in grid
  elements.gamesGrid.innerHTML = `
    <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
      <span class="spinner" style="width: 32px; height: 32px; border-width: 3px;"></span>
      <p style="margin-top: 1rem; color: var(--text-muted);">Loading games catalog...</p>
    </div>
  `;

  try {
    const params = {
      page: state.page,
      page_size: state.pageSize,
      category_id: state.categoryId || undefined,
      search: state.search || undefined,
      min_rating: state.minRating || undefined,
      max_price: state.maxPrice || undefined
    };

    const data = await gamesApi.getAll(params);
    state.total = data.total;
    state.totalPages = data.total_pages;

    if (elements.totalGamesStat) {
      elements.totalGamesStat.textContent = data.total;
    }

    renderGames(data.items);
    renderPagination();
    renderActiveFilterSummary();
  } catch (error) {
    elements.gamesGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-icon">⚠️</div>
        <div class="empty-title">Error Loading Games</div>
        <div class="empty-desc">${escapeHtml(error.userMessage || 'Could not fetch games.')}</div>
        <button class="btn btn-secondary" onclick="window.retryFetchGames()">Retry</button>
      </div>
    `;
    showToast(error.userMessage || 'Failed to load games catalog', 'error');
  }
}

// Window helper for inline retry
window.retryFetchGames = () => fetchGames();

// Render Games Grid
function renderGames(games) {
  if (!games || games.length === 0) {
    elements.gamesGrid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <div class="empty-icon">🎮</div>
        <div class="empty-title">No games found</div>
        <div class="empty-desc">No video games match your active search or filter criteria. Try adjusting your query or create a new game!</div>
        <button class="btn btn-primary" id="emptyStateNewGameBtn">+ Add New Game</button>
      </div>
    `;
    const emptyBtn = document.getElementById('emptyStateNewGameBtn');
    if (emptyBtn) emptyBtn.addEventListener('click', openCreateGameModal);
    return;
  }

  elements.gamesGrid.innerHTML = games.map((game) => {
    const isFree = game.price === 0;
    const priceDisplay = isFree
      ? '<span class="price-free">Free to Play</span>'
      : `<span class="price-tag">$${Number(game.price).toFixed(2)}</span>`;

    const ratingDisplay = game.rating !== null && game.rating !== undefined
      ? `<span class="rating-badge"><span class="rating-star">★</span> ${Number(game.rating).toFixed(1)}</span>`
      : '<span class="rating-badge" style="color: var(--text-dim); border-color: var(--border-color); background: none;">Unrated</span>';

    const steamBadge = game.steam_app_id
      ? `<button type="button" class="steam-badge steam-badge-interactive steam-stats-btn" data-game-id="${game.id}" data-app-id="${game.steam_app_id}" title="Click to fetch live concurrent Steam players">⚡ Steam: ${game.steam_app_id}</button>`
      : '';

    return `
      <article class="game-card" data-game-id="${game.id}">
        <header class="game-card-header">
          <div class="card-badges-top">
            <span class="badge-category">${escapeHtml(game.category ? game.category.name : 'Unknown')}</span>
            <span class="badge-year">${game.release_year || '—'}</span>
          </div>
          <h2 class="game-title">${escapeHtml(game.title)}</h2>
        </header>

        <div class="game-card-body">
          <p class="game-description">${escapeHtml(game.description || 'No description provided for this game.')}</p>
          <div class="game-meta-row">
            ${priceDisplay}
            ${ratingDisplay}
          </div>
        </div>

        <footer class="game-card-footer">
          <div>${steamBadge}</div>
          <div class="card-actions">
            <button class="btn btn-secondary btn-sm edit-game-btn" data-id="${game.id}" title="Edit Game">
              ✏️ Edit
            </button>
            <button class="btn btn-danger btn-sm delete-game-btn" data-id="${game.id}" data-title="${escapeHtml(game.title)}" title="Delete Game">
              🗑️
            </button>
          </div>
        </footer>
      </article>
    `;
  }).join('');

  // Attach event listeners to card action buttons
  document.querySelectorAll('.edit-game-btn').forEach((btn) => {
    btn.addEventListener('click', () => openEditGameModal(Number(btn.dataset.id)));
  });

  document.querySelectorAll('.delete-game-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      confirmDeleteGame(Number(btn.dataset.id), btn.dataset.title);
    });
  });

  // Attach event listeners to live Steam player stats buttons
  document.querySelectorAll('.steam-stats-btn').forEach((btn) => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const gameId = btn.dataset.gameId;
      const origText = btn.innerHTML;
      btn.innerHTML = '⚡ Checking...';
      try {
        const stats = await steamApi.getStats(gameId);
        if (stats && stats.player_count !== null) {
          btn.innerHTML = `<span class="steam-player-dot"></span> 👥 ${stats.player_count.toLocaleString()} online`;
          btn.title = `Steam AppID ${stats.steam_app_id}: ${stats.player_count.toLocaleString()} current players!`;
        } else {
          btn.innerHTML = `⚡ Steam: ${btn.dataset.appId}`;
          showToast('Steam player stats currently unavailable.', 'info');
        }
      } catch (err) {
        btn.innerHTML = origText;
        showToast(err.userMessage || 'Could not fetch Steam stats', 'warning');
      }
    });
  });
}

// Render Pagination Controls
function renderPagination() {
  if (state.total === 0) {
    elements.paginationBar.style.display = 'none';
    return;
  }
  elements.paginationBar.style.display = 'flex';

  const start = (state.page - 1) * state.pageSize + 1;
  const end = Math.min(state.page * state.pageSize, state.total);

  elements.paginationInfo.textContent = `Showing ${start}–${end} of ${state.total} games (Page ${state.page} of ${state.totalPages})`;
  elements.prevPageBtn.disabled = state.page <= 1;
  elements.nextPageBtn.disabled = state.page >= state.totalPages;
}

// Render Active Filter Chips
function renderActiveFilterSummary() {
  const chips = [];

  if (state.search) {
    chips.push(`Search: "${state.search}"`);
  }
  if (state.categoryId) {
    const cat = state.categories.find((c) => String(c.id) === String(state.categoryId));
    chips.push(`Category: ${cat ? cat.name : state.categoryId}`);
  }
  if (state.minRating) {
    chips.push(`Rating: ≥ ${state.minRating}`);
  }
  if (state.maxPrice) {
    chips.push(`Price: ≤ $${state.maxPrice}`);
  }

  if (chips.length > 0) {
    elements.activeFiltersSummary.innerHTML = `
      <div class="filter-chips">
        <span style="align-self: center; font-weight: 600;">Active Filters:</span>
        ${chips.map((c) => `<span class="chip">${escapeHtml(c)}</span>`).join('')}
      </div>
    `;
    elements.activeFiltersSummary.style.display = 'block';
  } else {
    elements.activeFiltersSummary.style.display = 'none';
  }
}

// Game Modal Logic
function openCreateGameModal() {
  state.editingGameId = null;
  elements.gameModalTitle.textContent = 'Add New Game';
  elements.gameSubmitBtn.innerHTML = 'Create Game';
  elements.gameForm.reset();
  elements.gameActiveCheck.checked = true;
  elements.gameModal.showModal();
}

async function openEditGameModal(gameId) {
  try {
    const game = await gamesApi.getById(gameId);
    state.editingGameId = gameId;
    elements.gameModalTitle.textContent = `Edit Game: ${game.title}`;
    elements.gameSubmitBtn.innerHTML = 'Save Changes';

    elements.gameTitleInput.value = game.title || '';
    elements.gameCategorySelect.value = game.category_id || '';
    elements.gameDescInput.value = game.description || '';
    elements.gamePriceInput.value = game.price !== undefined ? game.price : 0;
    elements.gameYearInput.value = game.release_year || '';
    elements.gameRatingInput.value = game.rating !== undefined && game.rating !== null ? game.rating : '';
    elements.gameSteamIdInput.value = game.steam_app_id || '';
    elements.gameActiveCheck.checked = Boolean(game.is_active);

    elements.gameModal.showModal();
  } catch (error) {
    showToast(error.userMessage || 'Failed to fetch game details', 'error');
  }
}

async function handleGameFormSubmit(event) {
  event.preventDefault();

  const title = elements.gameTitleInput.value.trim();
  const categoryId = parseInt(elements.gameCategorySelect.value, 10);
  const description = elements.gameDescInput.value.trim() || null;
  const price = parseFloat(elements.gamePriceInput.value) || 0.0;
  const releaseYear = elements.gameYearInput.value ? parseInt(elements.gameYearInput.value, 10) : null;
  const rating = elements.gameRatingInput.value !== '' ? parseFloat(elements.gameRatingInput.value) : null;
  const steamAppId = elements.gameSteamIdInput.value ? parseInt(elements.gameSteamIdInput.value, 10) : null;
  const isActive = elements.gameActiveCheck.checked;

  if (!title) {
    showToast('Game title is required.', 'warning');
    return;
  }
  if (!categoryId || isNaN(categoryId)) {
    showToast('Please select a valid category.', 'warning');
    return;
  }

  const payload = {
    title,
    category_id: categoryId,
    description,
    price,
    release_year: releaseYear,
    rating,
    steam_app_id: steamAppId,
    is_active: isActive
  };

  const originalSubmitText = elements.gameSubmitBtn.innerHTML;
  elements.gameSubmitBtn.disabled = true;
  elements.gameSubmitBtn.innerHTML = '<span class="spinner"></span> Saving...';

  try {
    if (state.editingGameId) {
      await gamesApi.update(state.editingGameId, payload);
      showToast(`Game "${title}" successfully updated!`, 'success');
    } else {
      await gamesApi.create(payload);
      showToast(`Game "${title}" successfully created!`, 'success');
    }

    elements.gameModal.close();
    await loadCategories(); // refresh category games counts
    await fetchGames();
  } catch (error) {
    showToast(error.userMessage || 'Operation failed', 'error');
  } finally {
    elements.gameSubmitBtn.disabled = false;
    elements.gameSubmitBtn.innerHTML = originalSubmitText;
  }
}

// Category Manager Logic
function openCategoryModal() {
  elements.categoryForm.reset();
  renderCategoryManagerList();
  elements.categoryModal.showModal();
}

function renderCategoryManagerList() {
  if (!elements.categoryListContainer) return;

  if (state.categories.length === 0) {
    elements.categoryListContainer.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem;">No categories defined yet.</p>';
    return;
  }

  elements.categoryListContainer.innerHTML = state.categories.map((cat) => `
    <div class="cat-item-card">
      <div class="cat-item-info">
        <div class="cat-item-name">${escapeHtml(cat.name)}</div>
        <div class="cat-item-desc">${escapeHtml(cat.description || 'No description.')}</div>
      </div>
      <div class="cat-item-games-badge">${cat.games_count} games</div>
      <div style="display: flex; gap: 0.35rem;">
        <button class="btn btn-secondary btn-sm edit-cat-inline-btn" data-id="${cat.id}" title="Edit Category">✏️</button>
        <button class="btn btn-danger btn-sm delete-cat-inline-btn" data-id="${cat.id}" data-name="${escapeHtml(cat.name)}" data-count="${cat.games_count}" title="Delete Category">🗑️</button>
      </div>
    </div>
  `).join('');

  // Attach Category Action Buttons
  elements.categoryListContainer.querySelectorAll('.edit-cat-inline-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const cat = state.categories.find((c) => String(c.id) === String(btn.dataset.id));
      if (cat) {
        state.editingCategoryId = cat.id;
        elements.categoryNameInput.value = cat.name;
        elements.categoryDescInput.value = cat.description || '';
        document.getElementById('saveCategoryBtn').textContent = 'Update Category';
      }
    });
  });

  elements.categoryListContainer.querySelectorAll('.delete-cat-inline-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      confirmDeleteCategory(Number(btn.dataset.id), btn.dataset.name, Number(btn.dataset.count));
    });
  });
}

async function handleCategoryFormSubmit(event) {
  event.preventDefault();
  const name = elements.categoryNameInput.value.trim();
  const description = elements.categoryDescInput.value.trim() || null;

  if (!name) {
    showToast('Category name is required.', 'warning');
    return;
  }

  const payload = { name, description };
  const saveBtn = document.getElementById('saveCategoryBtn');
  const origText = saveBtn.textContent;
  saveBtn.disabled = true;
  saveBtn.innerHTML = '<span class="spinner"></span> Saving...';

  try {
    if (state.editingCategoryId) {
      await categoriesApi.update(state.editingCategoryId, payload);
      showToast(`Category "${name}" updated successfully!`, 'success');
      state.editingCategoryId = null;
    } else {
      await categoriesApi.create(payload);
      showToast(`Category "${name}" created successfully!`, 'success');
    }

    elements.categoryForm.reset();
    saveBtn.textContent = 'Add Category';
    await loadCategories();
    await fetchGames();
  } catch (error) {
    showToast(error.userMessage || 'Category operation failed', 'error');
  } finally {
    saveBtn.disabled = false;
    saveBtn.textContent = origText;
  }
}

// Delete Confirmation Handlers
function confirmDeleteGame(gameId, title) {
  elements.confirmModalTitle.textContent = 'Delete Game Confirmation';
  elements.confirmModalMessage.innerHTML = `Are you sure you want to delete <strong>"${escapeHtml(title)}"</strong>? This action cannot be undone.`;
  state.pendingDeleteAction = async () => {
    try {
      await gamesApi.delete(gameId);
      showToast(`Game "${title}" deleted.`, 'success');
      await loadCategories();
      await fetchGames();
    } catch (error) {
      showToast(error.userMessage || 'Failed to delete game', 'error');
    }
  };
  elements.confirmModal.showModal();
}

function confirmDeleteCategory(catId, name, gamesCount) {
  elements.confirmModalTitle.textContent = 'Cascade Delete Category Warning';
  elements.confirmModalMessage.innerHTML = `
    Are you sure you want to delete category <strong>"${escapeHtml(name)}"</strong>?<br><br>
    <span style="color: var(--accent-rose); font-weight: 600;">⚠️ CASCADE WARNING:</span>
    Deleting this category will permanently delete all <strong>${gamesCount}</strong> associated games due to relational cascade rules!
  `;
  state.pendingDeleteAction = async () => {
    try {
      await categoriesApi.delete(catId);
      showToast(`Category "${name}" and all associated games were deleted.`, 'success');
      await loadCategories();
      if (state.categoryId === String(catId)) {
        state.categoryId = '';
        elements.categoryFilter.value = '';
      }
      await fetchGames();
    } catch (error) {
      showToast(error.userMessage || 'Failed to delete category', 'error');
    }
  };
  elements.confirmModal.showModal();
}

// Health Check Runner
async function checkBackendHealth() {
  try {
    const health = await healthApi.check();
    if (health.status === 'healthy' || health.status === 'ok') {
      elements.backendStatus.innerHTML = '<span class="status-dot"></span> API Online (v' + (health.version || '1.0.0') + ')';
      elements.backendStatus.className = 'status-pill';
    } else {
      elements.backendStatus.innerHTML = '<span class="status-dot" style="background-color: var(--accent-amber);"></span> Degraded';
    }
  } catch (error) {
    elements.backendStatus.innerHTML = '<span class="status-dot" style="background-color: var(--accent-rose); animation: none;"></span> API Offline';
    elements.backendStatus.style.borderColor = 'rgba(244, 63, 94, 0.4)';
    elements.backendStatus.style.color = '#fca5a5';
  }
}

// Steam Search & Import Controller
function openSteamModal() {
  elements.steamSearchInput.value = '';
  elements.steamResultsContainer.innerHTML = `
    <div style="text-align: center; padding: 2rem; color: var(--text-dim); font-size: 0.9rem;">
      Type at least 2 characters to search Steam...
    </div>
  `;
  elements.steamModal.showModal();
  elements.steamSearchInput.focus();
}

async function searchSteam(query) {
  if (!query || query.length < 2) {
    elements.steamResultsContainer.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--text-dim); font-size: 0.9rem;">
        Type at least 2 characters to search Steam...
      </div>
    `;
    return;
  }

  elements.steamResultsContainer.innerHTML = `
    <div style="text-align: center; padding: 2rem; color: var(--text-muted);">
      <span class="spinner"></span> Searching Steam Store...
    </div>
  `;

  try {
    const data = await steamApi.search(query, 8);
    if (!data.items || data.items.length === 0) {
      elements.steamResultsContainer.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.9rem;">
          No matching games found on Steam for "${escapeHtml(query)}".
        </div>
      `;
      return;
    }

    elements.steamResultsContainer.innerHTML = data.items.map((item) => {
      const priceText = item.price === 0 ? 'Free to Play' : `$${Number(item.price).toFixed(2)}`;
      const thumb = item.image_url || 'https://via.placeholder.com/92x43/1b2838/ffffff?text=Steam';
      return `
        <div class="steam-result-card" data-app-id="${item.id}">
          <img src="${thumb}" alt="${escapeHtml(item.name)}" class="steam-result-thumb" loading="lazy">
          <div class="steam-result-info">
            <div class="steam-result-title">${escapeHtml(item.name)}</div>
            <div class="steam-result-sub">
              <span>AppID: ${item.id}</span> &bull; 
              <span style="color: var(--accent-emerald); font-weight: 600;">${priceText}</span>
            </div>
          </div>
          <button class="btn btn-steam btn-sm import-steam-btn" data-app-id="${item.id}" data-name="${escapeHtml(item.name)}" type="button">
            ⚡ Import
          </button>
        </div>
      `;
    }).join('');

    // Attach Import Listeners
    elements.steamResultsContainer.querySelectorAll('.import-steam-btn').forEach((btn) => {
      btn.addEventListener('click', async () => {
        const appId = parseInt(btn.dataset.appId, 10);
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Importing...';

        try {
          const importedGame = await steamApi.importGame(appId);
          btn.innerHTML = '✓ Imported';
          btn.style.borderColor = 'var(--accent-emerald)';
          btn.style.color = 'var(--accent-emerald)';
          showToast(`Game "${importedGame.title}" successfully imported from Steam!`, 'success');
          await loadCategories();
          await fetchGames();
        } catch (err) {
          btn.disabled = false;
          btn.innerHTML = '⚡ Import';
          showToast(err.userMessage || 'Failed to import Steam game', 'error');
        }
      });
    });
  } catch (err) {
    elements.steamResultsContainer.innerHTML = `
      <div style="text-align: center; padding: 2rem; color: var(--accent-rose); font-size: 0.9rem;">
        ${escapeHtml(err.userMessage || 'Failed to search Steam Store.')}
      </div>
    `;
  }
}

// Interactive API Explorer Runner
function setupApiExplorer() {
  document.querySelectorAll('.try-endpoint-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const endpoint = btn.dataset.endpoint;
      const method = btn.dataset.method;
      const targetViewer = document.getElementById(`res-${btn.dataset.target}`);
      if (!targetViewer) return;

      const startTime = performance.now();
      targetViewer.textContent = 'Executing request via Axios...';
      btn.disabled = true;

      try {
        let result;
        if (endpoint === '/health') {
          result = await healthApi.check();
        } else if (endpoint === '/categories/') {
          result = await categoriesApi.getAll();
        } else if (endpoint === '/games/') {
          result = await gamesApi.getAll({ page: 1, page_size: 2 });
        } else if (endpoint === '/steam/search') {
          result = await steamApi.search('Hades', 3);
        } else {
          result = { message: `Executed ${method} ${endpoint}` };
        }

        const duration = Math.round(performance.now() - startTime);
        targetViewer.textContent = `// HTTP 200 OK (${duration}ms)\n` + JSON.stringify(result, null, 2);
      } catch (err) {
        const duration = Math.round(performance.now() - startTime);
        targetViewer.textContent = `// Error (${duration}ms)\n` + (err.userMessage || err.message);
      } finally {
        btn.disabled = false;
      }
    });
  });
}

// Event Bindings Initialization
function initEventBindings() {
  // Navigation Tabs
  elements.tabCatalogBtn.addEventListener('click', () => {
    elements.tabCatalogBtn.classList.add('active');
    elements.tabDocsBtn.classList.remove('active');
    elements.catalogSection.classList.add('active');
    elements.docsSection.classList.remove('active');
  });

  elements.tabDocsBtn.addEventListener('click', () => {
    elements.tabDocsBtn.classList.add('active');
    elements.tabCatalogBtn.classList.remove('active');
    elements.docsSection.classList.add('active');
    elements.catalogSection.classList.remove('active');
  });

  // Search input debounced
  const debouncedSearch = debounce((query) => {
    state.search = query;
    state.page = 1;
    fetchGames();
  }, 350);

  elements.searchInput.addEventListener('input', (e) => {
    const val = e.target.value.trim();
    elements.searchClearBtn.style.display = val ? 'block' : 'none';
    debouncedSearch(val);
  });

  elements.searchClearBtn.addEventListener('click', () => {
    elements.searchInput.value = '';
    elements.searchClearBtn.style.display = 'none';
    state.search = '';
    state.page = 1;
    fetchGames();
  });

  // Filters
  elements.categoryFilter.addEventListener('change', (e) => {
    state.categoryId = e.target.value;
    state.page = 1;
    fetchGames();
  });

  elements.ratingFilter.addEventListener('change', (e) => {
    state.minRating = e.target.value;
    state.page = 1;
    fetchGames();
  });

  elements.priceFilter.addEventListener('change', (e) => {
    state.maxPrice = e.target.value;
    state.page = 1;
    fetchGames();
  });

  elements.resetFiltersBtn.addEventListener('click', () => {
    elements.searchInput.value = '';
    elements.searchClearBtn.style.display = 'none';
    elements.categoryFilter.value = '';
    elements.ratingFilter.value = '';
    elements.priceFilter.value = '';
    state.search = '';
    state.categoryId = '';
    state.minRating = '';
    state.maxPrice = '';
    state.page = 1;
    fetchGames();
  });

  // Pagination buttons
  elements.prevPageBtn.addEventListener('click', () => {
    if (state.page > 1) {
      state.page -= 1;
      fetchGames();
    }
  });

  elements.nextPageBtn.addEventListener('click', () => {
    if (state.page < state.totalPages) {
      state.page += 1;
      fetchGames();
    }
  });

  elements.pageSizeSelect.addEventListener('change', (e) => {
    state.pageSize = parseInt(e.target.value, 10);
    state.page = 1;
    fetchGames();
  });

  // Modals Open Buttons
  elements.newGameBtn.addEventListener('click', openCreateGameModal);
  elements.manageCategoriesBtn.addEventListener('click', openCategoryModal);

  // Steam Modal
  elements.openSteamModalBtn.addEventListener('click', openSteamModal);
  elements.steamModalCloseBtn.addEventListener('click', () => elements.steamModal.close());

  const debouncedSteamSearch = debounce((query) => {
    searchSteam(query);
  }, 400);

  elements.steamSearchInput.addEventListener('input', (e) => {
    debouncedSteamSearch(e.target.value.trim());
  });

  // Forms
  elements.gameForm.addEventListener('submit', handleGameFormSubmit);
  elements.gameModalCancelBtn.addEventListener('click', () => elements.gameModal.close());

  elements.categoryForm.addEventListener('submit', handleCategoryFormSubmit);
  elements.categoryModalCloseBtn.addEventListener('click', () => elements.categoryModal.close());

  // Confirm Modal
  elements.confirmModalCancelBtn.addEventListener('click', () => {
    state.pendingDeleteAction = null;
    elements.confirmModal.close();
  });

  elements.confirmModalProceedBtn.addEventListener('click', async () => {
    if (typeof state.pendingDeleteAction === 'function') {
      await state.pendingDeleteAction();
    }
    state.pendingDeleteAction = null;
    elements.confirmModal.close();
  });

  // Accessible light dismiss setup
  [elements.gameModal, elements.categoryModal, elements.confirmModal, elements.steamModal].forEach(setupDialogLightDismiss);
}

// App Initialization
async function initApp() {
  initEventBindings();
  setupApiExplorer();
  await checkBackendHealth();
  await loadCategories();
  await fetchGames();
}

// Run when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
