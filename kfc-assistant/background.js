/**
 * Background service worker for Rostics Menu Assistant
 * Handles extension lifecycle and message routing
 */

// Extension installation handler
chrome.runtime.onInstalled.addListener((details) => {
  console.log('Rostics Menu Assistant installed:', details.reason);

  if (details.reason === 'install') {
    // Open welcome/instructions on first install
    chrome.tabs.create({
      url: 'https://rostics.ru/menu'
    });
  }
});

// Message handler for communication between popup and content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message.type);

  switch (message.type) {
    case 'MENU_PARSED':
      // Menu was parsed by content script, notify popup if open
      handleMenuParsed(message.data);
      sendResponse({ success: true });
      break;

    case 'GET_MENU':
      // Request to get cached menu
      getMenuFromStorage().then(menu => {
        sendResponse({ success: true, data: menu });
      }).catch(error => {
        sendResponse({ success: false, error: error.message });
      });
      return true; // Keep channel open for async response

    case 'PARSE_REQUEST':
      // Request to parse menu from current tab
      requestMenuParse(sender.tab?.id);
      sendResponse({ success: true });
      break;

    default:
      console.log('Unknown message type:', message.type);
  }
});

/**
 * Handle parsed menu data from content script
 */
async function handleMenuParsed(menuData) {
  try {
    // Store the menu data
    await chrome.storage.local.set({
      menuData: {
        ...menuData,
        cachedAt: new Date().toISOString()
      }
    });

    console.log('Menu data saved:', menuData.items?.length, 'items');

    // Notify any open popups
    chrome.runtime.sendMessage({ type: 'MENU_UPDATED' }).catch(() => {
      // Popup might not be open, that's ok
    });
  } catch (error) {
    console.error('Failed to save menu:', error);
  }
}

/**
 * Get menu from storage
 */
async function getMenuFromStorage() {
  const result = await chrome.storage.local.get('menuData');
  return result.menuData || null;
}

/**
 * Request menu parse from content script
 */
async function requestMenuParse(tabId) {
  if (!tabId) {
    // Find rostics.ru tab
    const tabs = await chrome.tabs.query({
      url: ['https://rostics.ru/menu*', 'https://www.rostics.ru/menu*']
    });

    if (tabs.length > 0) {
      tabId = tabs[0].id;
    } else {
      console.log('No rostics.ru menu tab found');
      return;
    }
  }

  try {
    await chrome.tabs.sendMessage(tabId, { type: 'PARSE_MENU' });
  } catch (error) {
    console.error('Failed to send parse request:', error);
  }
}

// Handle extension icon click (optional - popup handles most interactions)
chrome.action.onClicked.addListener((tab) => {
  // This won't fire when popup is defined, but kept for future flexibility
  console.log('Extension icon clicked on tab:', tab.url);
});

console.log('Rostics Menu Assistant background service worker started');
