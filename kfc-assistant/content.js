/**
 * Content Script for Rostics Menu Assistant
 * Runs on rostics.ru/menu pages to parse and cache menu data
 */

(function() {
  'use strict';

  console.log('[Rostics Assistant] Content script loaded on:', window.location.href);

  // Configuration
  const CONFIG = {
    // Delay before parsing to ensure page is fully loaded
    parseDelay: 2000,
    // Auto-refresh if user scrolls (might load more items)
    watchScroll: true,
    // Debounce scroll events
    scrollDebounce: 1000
  };

  // State
  let isParsing = false;
  let lastParseTime = 0;
  let scrollTimeout = null;

  /**
   * Initialize content script
   */
  function init() {
    // Wait for page to fully load
    if (document.readyState === 'complete') {
      scheduleInitialParse();
    } else {
      window.addEventListener('load', scheduleInitialParse);
    }

    // Listen for messages from popup/background
    chrome.runtime.onMessage.addListener(handleMessage);

    // Watch for dynamic content changes
    observeMutations();

    // Watch for scroll (lazy-loaded content)
    if (CONFIG.watchScroll) {
      window.addEventListener('scroll', handleScroll, { passive: true });
    }
  }

  /**
   * Schedule initial parse with delay
   */
  function scheduleInitialParse() {
    console.log('[Rostics Assistant] Scheduling initial parse...');
    setTimeout(() => {
      parseAndSave();
    }, CONFIG.parseDelay);
  }

  /**
   * Handle messages from other parts of the extension
   */
  function handleMessage(message, sender, sendResponse) {
    console.log('[Rostics Assistant] Received message:', message.type);

    switch (message.type) {
      case 'PARSE_MENU':
        parseAndSave().then(result => {
          sendResponse({ success: true, data: result });
        }).catch(error => {
          sendResponse({ success: false, error: error.message });
        });
        return true; // Keep channel open for async response

      case 'GET_STATUS':
        sendResponse({
          success: true,
          data: {
            url: window.location.href,
            isParsing: isParsing,
            lastParseTime: lastParseTime
          }
        });
        break;

      default:
        console.log('[Rostics Assistant] Unknown message type:', message.type);
    }
  }

  /**
   * Parse menu and save to storage
   */
  async function parseAndSave() {
    if (isParsing) {
      console.log('[Rostics Assistant] Parse already in progress, skipping...');
      return null;
    }

    isParsing = true;
    console.log('[Rostics Assistant] Starting parse...');

    try {
      // Use the MenuParser from parser.js
      const menuData = MenuParser.parseMenu();

      if (!menuData.items || menuData.items.length === 0) {
        console.warn('[Rostics Assistant] No menu items found!');
        showNotification('No menu items found on this page', 'warning');
        return null;
      }

      console.log('[Rostics Assistant] Parsed', menuData.items.length, 'items');

      // Save to storage via background script
      await saveMenuData(menuData);

      // Update last parse time
      lastParseTime = Date.now();

      // Show success notification
      showNotification(`Menu updated: ${menuData.items.length} items`, 'success');

      return menuData;

    } catch (error) {
      console.error('[Rostics Assistant] Parse error:', error);
      showNotification('Failed to parse menu', 'error');
      throw error;

    } finally {
      isParsing = false;
    }
  }

  /**
   * Save menu data via chrome.storage
   */
  async function saveMenuData(menuData) {
    return new Promise((resolve, reject) => {
      const dataToStore = {
        ...menuData,
        cachedAt: new Date().toISOString()
      };

      chrome.storage.local.set({ menuData: dataToStore }, () => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          console.log('[Rostics Assistant] Menu saved to storage');

          // Notify background/popup about update
          chrome.runtime.sendMessage({ type: 'MENU_UPDATED', data: dataToStore })
            .catch(() => {
              // Popup might not be open, that's ok
            });

          resolve();
        }
      });
    });
  }

  /**
   * Observe DOM mutations for dynamically loaded content
   */
  function observeMutations() {
    const observer = new MutationObserver((mutations) => {
      // Check if significant content was added
      const hasNewContent = mutations.some(mutation => {
        return mutation.addedNodes.length > 0 &&
               Array.from(mutation.addedNodes).some(node => {
                 return node.nodeType === Node.ELEMENT_NODE &&
                        (node.matches?.('[class*="product"], [class*="menu-item"], article') ||
                         node.querySelector?.('[class*="product"], [class*="menu-item"]'));
               });
      });

      if (hasNewContent) {
        console.log('[Rostics Assistant] New content detected, scheduling reparse...');
        debounceReparse();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  /**
   * Handle scroll events for lazy-loaded content
   */
  function handleScroll() {
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
    }

    scrollTimeout = setTimeout(() => {
      // Check if we're near the bottom (might trigger lazy load)
      const scrolledToBottom = (window.innerHeight + window.scrollY) >= (document.body.scrollHeight - 500);

      if (scrolledToBottom) {
        console.log('[Rostics Assistant] Scrolled to bottom, checking for new content...');
        debounceReparse();
      }
    }, CONFIG.scrollDebounce);
  }

  /**
   * Debounced reparse
   */
  let reparseTimeout = null;
  function debounceReparse() {
    if (reparseTimeout) {
      clearTimeout(reparseTimeout);
    }

    reparseTimeout = setTimeout(() => {
      // Only reparse if enough time has passed since last parse
      if (Date.now() - lastParseTime > 5000) {
        parseAndSave();
      }
    }, 2000);
  }

  /**
   * Show a notification on the page
   */
  function showNotification(message, type = 'info') {
    // Remove existing notification
    const existing = document.getElementById('rostics-assistant-notification');
    if (existing) {
      existing.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'rostics-assistant-notification';
    notification.textContent = message;

    // Style based on type
    const colors = {
      success: { bg: '#4caf50', text: '#fff' },
      warning: { bg: '#ff9800', text: '#fff' },
      error: { bg: '#f44336', text: '#fff' },
      info: { bg: '#2196f3', text: '#fff' }
    };
    const color = colors[type] || colors.info;

    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 20px;
      background: ${color.bg};
      color: ${color.text};
      border-radius: 8px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      font-weight: 500;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
      z-index: 999999;
      transition: opacity 0.3s, transform 0.3s;
      transform: translateY(0);
    `;

    document.body.appendChild(notification);

    // Auto-remove after 3 seconds
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateY(-10px)';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  // Initialize
  init();

})();
