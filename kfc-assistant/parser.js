/**
 * Menu Parser for Rostics website
 * Extracts menu items from the DOM of rostics.ru/menu
 */

const MenuParser = {
  // Selectors for rostics.ru menu page
  // These may need updating if the site structure changes
  SELECTORS: {
    // Category container
    categoryNav: '[data-testid="category-nav"], .menu-categories, nav.categories',
    categoryItem: '[data-testid="category-item"], .category-item, .menu-category',
    categoryName: '[data-testid="category-name"], .category-name, h2, h3',

    // Menu items
    menuContainer: '[data-testid="menu-items"], .menu-items, .products-grid, .menu-grid',
    menuItem: '[data-testid="menu-item"], .menu-item, .product-card, article.product',
    itemName: '[data-testid="item-name"], .product-name, .item-title, h3, h4',
    itemPrice: '[data-testid="item-price"], .product-price, .price, .item-price',
    itemDescription: '[data-testid="item-description"], .product-description, .description, p',
    itemImage: '[data-testid="item-image"], .product-image img, .item-image img, img',

    // Alternative selectors for different page layouts
    altMenuCard: '.menu-card, .dish-card, [class*="product"], [class*="menu-item"]',
    altPrice: '[class*="price"], [class*="cost"]',
    altImage: 'img[src*="product"], img[src*="menu"], img[src*="dish"]'
  },

  /**
   * Parse the entire menu from the current page
   * @returns {Object} Parsed menu data with categories and items
   */
  parseMenu() {
    console.log('[Rostics Parser] Starting menu parse...');

    const result = {
      categories: [],
      items: [],
      parsedAt: new Date().toISOString(),
      source: window.location.href
    };

    try {
      // Try to parse categories first
      result.categories = this.parseCategories();
      console.log('[Rostics Parser] Found categories:', result.categories.length);

      // Parse menu items
      result.items = this.parseMenuItems();
      console.log('[Rostics Parser] Found items:', result.items.length);

      // If no items found with primary selectors, try alternative approach
      if (result.items.length === 0) {
        console.log('[Rostics Parser] Trying alternative parsing...');
        result.items = this.parseMenuItemsAlternative();
        console.log('[Rostics Parser] Alternative found items:', result.items.length);
      }

      // Assign categories to items if not already assigned
      if (result.categories.length > 0 && result.items.length > 0) {
        this.assignCategoriesToItems(result);
      }

    } catch (error) {
      console.error('[Rostics Parser] Error parsing menu:', error);
    }

    return result;
  },

  /**
   * Parse category navigation
   * @returns {Array} Array of category objects
   */
  parseCategories() {
    const categories = [];
    const categoryElements = this.findElements(this.SELECTORS.categoryItem);

    categoryElements.forEach((el, index) => {
      const nameEl = el.querySelector(this.SELECTORS.categoryName) || el;
      const name = this.cleanText(nameEl.textContent);

      if (name) {
        categories.push({
          id: `cat-${index + 1}`,
          name: name,
          slug: this.slugify(name)
        });
      }
    });

    // If no categories found from nav, try to extract from section headers
    if (categories.length === 0) {
      const headers = document.querySelectorAll('h2, h3.category-title, [class*="category-header"]');
      headers.forEach((el, index) => {
        const name = this.cleanText(el.textContent);
        if (name && name.length < 50) { // Reasonable category name length
          categories.push({
            id: `cat-${index + 1}`,
            name: name,
            slug: this.slugify(name)
          });
        }
      });
    }

    return categories;
  },

  /**
   * Parse menu items from the page
   * @returns {Array} Array of menu item objects
   */
  parseMenuItems() {
    const items = [];
    const itemElements = this.findElements(this.SELECTORS.menuItem);

    itemElements.forEach((el, index) => {
      const item = this.parseMenuItem(el, index);
      if (item && item.name) {
        items.push(item);
      }
    });

    return items;
  },

  /**
   * Alternative menu parsing for different page structures
   * @returns {Array} Array of menu item objects
   */
  parseMenuItemsAlternative() {
    const items = [];
    const cards = document.querySelectorAll(this.SELECTORS.altMenuCard);

    cards.forEach((el, index) => {
      const item = this.parseMenuItem(el, index);
      if (item && item.name) {
        items.push(item);
      }
    });

    return items;
  },

  /**
   * Parse a single menu item element
   * @param {Element} el - The DOM element
   * @param {number} index - Item index
   * @returns {Object|null} Parsed item or null
   */
  parseMenuItem(el, index) {
    try {
      // Get name
      const nameEl = el.querySelector(this.SELECTORS.itemName) ||
                     el.querySelector('h3, h4, [class*="name"], [class*="title"]');
      const name = nameEl ? this.cleanText(nameEl.textContent) : null;

      if (!name) return null;

      // Get price
      const priceEl = el.querySelector(this.SELECTORS.itemPrice) ||
                      el.querySelector(this.SELECTORS.altPrice);
      const price = priceEl ? this.parsePrice(priceEl.textContent) : null;

      // Get description
      const descEl = el.querySelector(this.SELECTORS.itemDescription) ||
                     el.querySelector('p, [class*="desc"]');
      const description = descEl ? this.cleanText(descEl.textContent) : null;

      // Get image
      const imgEl = el.querySelector(this.SELECTORS.itemImage) ||
                    el.querySelector('img');
      let image = imgEl ? (imgEl.src || imgEl.dataset.src || imgEl.dataset.lazySrc) : null;

      // Make relative URLs absolute
      if (image && !image.startsWith('http')) {
        image = new URL(image, window.location.origin).href;
      }

      // Get category from data attribute or parent section
      const categoryId = el.dataset.category ||
                        el.closest('[data-category]')?.dataset.category ||
                        null;

      return {
        id: `item-${index + 1}`,
        name: name,
        description: description,
        price: price,
        image: image,
        categoryId: categoryId
      };
    } catch (error) {
      console.error('[Rostics Parser] Error parsing item:', error);
      return null;
    }
  },

  /**
   * Assign categories to items based on DOM structure
   * @param {Object} menuData - The parsed menu data
   */
  assignCategoriesToItems(menuData) {
    // This is a simplified assignment
    // In reality, we'd need to analyze the DOM structure more carefully
    const sections = document.querySelectorAll('section, [class*="category-section"]');

    sections.forEach((section, sectionIndex) => {
      const header = section.querySelector('h2, h3, [class*="category-header"]');
      if (!header) return;

      const categoryName = this.cleanText(header.textContent);
      const category = menuData.categories.find(c => c.name === categoryName);
      if (!category) return;

      const itemsInSection = section.querySelectorAll(this.SELECTORS.menuItem + ', ' + this.SELECTORS.altMenuCard);
      itemsInSection.forEach(itemEl => {
        const itemName = itemEl.querySelector('h3, h4, [class*="name"]')?.textContent;
        if (itemName) {
          const cleanName = this.cleanText(itemName);
          const menuItem = menuData.items.find(i => i.name === cleanName);
          if (menuItem && !menuItem.categoryId) {
            menuItem.categoryId = category.id;
          }
        }
      });
    });
  },

  /**
   * Find elements using multiple selectors
   * @param {string} selectorString - Comma-separated selectors
   * @returns {Array} Array of found elements
   */
  findElements(selectorString) {
    const selectors = selectorString.split(',').map(s => s.trim());
    const elements = new Set();

    selectors.forEach(selector => {
      try {
        document.querySelectorAll(selector).forEach(el => elements.add(el));
      } catch (e) {
        // Invalid selector, skip
      }
    });

    return Array.from(elements);
  },

  /**
   * Clean text content
   * @param {string} text - Raw text
   * @returns {string} Cleaned text
   */
  cleanText(text) {
    if (!text) return '';
    return text
      .replace(/\s+/g, ' ')
      .replace(/\n/g, ' ')
      .trim();
  },

  /**
   * Parse price from text
   * @param {string} text - Price text (e.g., "199 rub", "199P")
   * @returns {number|null} Price as number or null
   */
  parsePrice(text) {
    if (!text) return null;

    // Remove non-numeric characters except digits and decimal point
    const cleaned = text.replace(/[^\d.,]/g, '').replace(',', '.');
    const price = parseFloat(cleaned);

    return isNaN(price) ? null : Math.round(price);
  },

  /**
   * Convert text to URL-friendly slug
   * @param {string} text - Text to slugify
   * @returns {string} Slugified text
   */
  slugify(text) {
    return text
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim();
  }
};

// Make available globally
if (typeof window !== 'undefined') {
  window.MenuParser = MenuParser;
}
