/**
 * Storage utilities for Rostics Menu Assistant
 * Handles caching menu data with TTL
 */

const MenuStorage = {
  STORAGE_KEY: 'menuData',
  CACHE_TTL: 24 * 60 * 60 * 1000, // 24 hours in milliseconds

  /**
   * Get cached menu data
   * @returns {Promise<Object|null>} Menu data or null if not cached/expired
   */
  async getMenu() {
    try {
      const result = await chrome.storage.local.get(this.STORAGE_KEY);
      const menuData = result[this.STORAGE_KEY];

      if (!menuData) {
        return null;
      }

      // Check if cache is still valid
      if (this.isCacheValid(menuData.cachedAt)) {
        return menuData;
      }

      // Cache expired but still return data (better stale than empty)
      console.log('Menu cache expired, returning stale data');
      return menuData;
    } catch (error) {
      console.error('Failed to get menu from storage:', error);
      return null;
    }
  },

  /**
   * Save menu data to storage
   * @param {Object} menuData - Menu data to cache
   * @returns {Promise<void>}
   */
  async saveMenu(menuData) {
    try {
      const dataToStore = {
        ...menuData,
        cachedAt: new Date().toISOString()
      };

      await chrome.storage.local.set({
        [this.STORAGE_KEY]: dataToStore
      });

      console.log('Menu saved to storage:', menuData.items?.length, 'items');
    } catch (error) {
      console.error('Failed to save menu to storage:', error);
      throw error;
    }
  },

  /**
   * Clear cached menu data
   * @returns {Promise<void>}
   */
  async clearMenu() {
    try {
      await chrome.storage.local.remove(this.STORAGE_KEY);
      console.log('Menu cache cleared');
    } catch (error) {
      console.error('Failed to clear menu cache:', error);
      throw error;
    }
  },

  /**
   * Check if cache timestamp is still valid
   * @param {string} cachedAt - ISO timestamp
   * @returns {boolean}
   */
  isCacheValid(cachedAt) {
    if (!cachedAt) return false;

    const cacheTime = new Date(cachedAt).getTime();
    const now = Date.now();

    return (now - cacheTime) < this.CACHE_TTL;
  },

  /**
   * Get cache age in human-readable format
   * @param {string} cachedAt - ISO timestamp
   * @returns {string}
   */
  getCacheAge(cachedAt) {
    if (!cachedAt) return 'never';

    const cacheTime = new Date(cachedAt).getTime();
    const now = Date.now();
    const diffMs = now - cacheTime;

    const minutes = Math.floor(diffMs / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 1) return 'just now';
    if (minutes < 60) return `${minutes} min ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  }
};

// Make available globally for popup.js
if (typeof window !== 'undefined') {
  window.MenuStorage = MenuStorage;
}
