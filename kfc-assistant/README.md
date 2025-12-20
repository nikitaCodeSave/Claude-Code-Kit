# Rostics Menu Assistant

Chrome extension for viewing Rostics (former KFC) menu with offline access.

## Features

- View menu items with images, descriptions, and prices
- Search dishes by name or description
- Filter by categories
- Offline access after first load (24h cache)
- Automatic menu parsing from rostics.ru

## Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `kfc-assistant` folder

## Usage

1. Click the extension icon to open the popup
2. If no menu data is cached, click "Refresh" to open rostics.ru/menu
3. The menu will be automatically parsed and cached
4. Use the search box to find specific dishes
5. Click category buttons to filter by type

## How It Works

1. **Content Script**: When you visit rostics.ru/menu, the extension automatically parses the menu items from the page
2. **Storage**: Menu data is cached in chrome.storage.local for 24 hours
3. **Popup**: Displays cached menu with search and category filters

## Files

- `manifest.json` - Extension configuration (Manifest V3)
- `popup.html/css/js` - Popup UI
- `background.js` - Service worker for extension lifecycle
- `content.js` - Script that runs on rostics.ru pages
- `parser.js` - Menu parsing logic
- `storage.js` - Cache management utilities

## Development

No build step required. Just load the unpacked extension in Chrome.

To update selectors if rostics.ru changes their site structure, edit `parser.js`.

## Permissions

- `storage` - For caching menu data
- `activeTab` - For accessing the current tab
- `host_permissions` for rostics.ru - For content script injection

## License

MIT
