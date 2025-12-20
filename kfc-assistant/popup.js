/**
 * Popup script for Rostics Menu Assistant
 * Handles UI interactions and menu display
 */

// DOM Elements
const searchInput = document.getElementById('search-input');
const categoriesNav = document.getElementById('categories');
const menuGrid = document.getElementById('menu-grid');
const loadingEl = document.getElementById('loading');
const emptyStateEl = document.getElementById('empty-state');
const cacheInfoEl = document.getElementById('cache-info');
const refreshBtn = document.getElementById('refresh-btn');

// State
let menuData = null;
let currentCategory = 'all';
let searchQuery = '';

/**
 * Initialize popup
 */
async function init() {
  try {
    // Load cached menu data
    const cached = await MenuStorage.getMenu();

    if (cached && cached.items && cached.items.length > 0) {
      menuData = cached;
      renderMenu();
      updateCacheInfo(cached.cachedAt);
    } else {
      showEmptyState();
    }
  } catch (error) {
    console.error('Failed to load menu:', error);
    showError('Failed to load menu data');
  }
}

/**
 * Render the menu UI
 */
function renderMenu() {
  hideLoading();
  hideEmptyState();

  if (!menuData || !menuData.items) {
    showEmptyState();
    return;
  }

  // Render categories
  renderCategories();

  // Render menu items
  renderMenuItems();
}

/**
 * Render category buttons
 */
function renderCategories() {
  const categories = menuData.categories || [];

  let html = '<button class="category-btn active" data-category="all">All</button>';

  categories.forEach(category => {
    html += `<button class="category-btn" data-category="${escapeHtml(category.id)}">${escapeHtml(category.name)}</button>`;
  });

  categoriesNav.innerHTML = html;

  // Add click handlers
  categoriesNav.querySelectorAll('.category-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      currentCategory = btn.dataset.category;

      // Update active state
      categoriesNav.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      renderMenuItems();
    });
  });
}

/**
 * Render filtered menu items
 */
function renderMenuItems() {
  const items = filterItems(menuData.items);

  if (items.length === 0) {
    menuGrid.innerHTML = '<div class="no-results">No dishes found</div>';
    return;
  }

  let html = '';

  items.forEach(item => {
    html += `
      <div class="menu-item">
        <img
          class="menu-item-image"
          src="${escapeHtml(item.image || '')}"
          alt="${escapeHtml(item.name)}"
          onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%23f0f0f0%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2250%22 text-anchor=%22middle%22 dy=%22.3em%22 fill=%22%23999%22 font-size=%2214%22>No image</text></svg>'"
        >
        <div class="menu-item-content">
          <div class="menu-item-name">${escapeHtml(item.name)}</div>
          ${item.description ? `<div class="menu-item-description">${escapeHtml(item.description)}</div>` : ''}
          <div class="menu-item-price">${formatPrice(item.price)}</div>
        </div>
      </div>
    `;
  });

  menuGrid.innerHTML = html;
}

/**
 * Filter items by category and search query
 */
function filterItems(items) {
  return items.filter(item => {
    // Category filter
    const categoryMatch = currentCategory === 'all' || item.categoryId === currentCategory;

    // Search filter
    const query = searchQuery.toLowerCase().trim();
    const searchMatch = !query ||
      item.name.toLowerCase().includes(query) ||
      (item.description && item.description.toLowerCase().includes(query));

    return categoryMatch && searchMatch;
  });
}

/**
 * Format price for display
 */
function formatPrice(price) {
  if (!price && price !== 0) return '';
  return `${price} rub`;
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Show loading state
 */
function showLoading() {
  loadingEl.style.display = 'flex';
  menuGrid.style.display = 'none';
  emptyStateEl.style.display = 'none';
}

/**
 * Hide loading state
 */
function hideLoading() {
  loadingEl.style.display = 'none';
  menuGrid.style.display = 'grid';
}

/**
 * Show empty state
 */
function showEmptyState() {
  hideLoading();
  emptyStateEl.style.display = 'block';
  menuGrid.style.display = 'none';
}

/**
 * Hide empty state
 */
function hideEmptyState() {
  emptyStateEl.style.display = 'none';
}

/**
 * Show error message
 */
function showError(message) {
  hideLoading();
  const errorHtml = `<div class="error-message">${escapeHtml(message)}</div>`;
  menuGrid.innerHTML = errorHtml;
  menuGrid.style.display = 'block';
}

/**
 * Update cache info display
 */
function updateCacheInfo(cachedAt) {
  if (!cachedAt) {
    cacheInfoEl.textContent = '';
    return;
  }

  const date = new Date(cachedAt);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  let timeAgo;
  if (diffMins < 1) {
    timeAgo = 'just now';
  } else if (diffMins < 60) {
    timeAgo = `${diffMins} min ago`;
  } else if (diffHours < 24) {
    timeAgo = `${diffHours}h ago`;
  } else {
    timeAgo = `${diffDays}d ago`;
  }

  cacheInfoEl.textContent = `Updated ${timeAgo}`;
}

/**
 * Handle refresh button click
 */
async function handleRefresh() {
  refreshBtn.disabled = true;
  refreshBtn.textContent = 'Refreshing...';

  try {
    // Send message to open rostics.ru/menu in a new tab
    chrome.tabs.create({
      url: 'https://rostics.ru/menu',
      active: true
    });

    // Close popup - user will see the menu page
    window.close();
  } catch (error) {
    console.error('Failed to open menu page:', error);
    refreshBtn.disabled = false;
    refreshBtn.textContent = 'Refresh';
  }
}

// Event listeners
searchInput.addEventListener('input', (e) => {
  searchQuery = e.target.value;
  if (menuData) {
    renderMenuItems();
  }
});

refreshBtn.addEventListener('click', handleRefresh);

// Listen for menu updates from content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'MENU_UPDATED') {
    // Reload menu data
    init();
  }
});

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
