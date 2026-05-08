# NOVAstore — Bug Report Walkthrough

I have analyzed the `index.html` codebase and identified **23 distinct bugs** across functionality, UI, and interaction.

## 📋 Comprehensive Bug List

| # | ID / Category | Bug Description | Root Cause / Code Snippet |
|:---:|:---|:---|:---|
| 1 | **B01** | "Price: Low to High" sorts in descending order (highest first). | `list.sort((a, b) => b.price - a.price)` |
| 2 | **B02** | OOS "Add to Cart" button is enabled in the product modal. | `btn.disabled = false;` (overrides logic) |
| 3 | **B03-B05** | All products display 5 stars regardless of actual rating. | `return '★★★★★';` |
| 4 | **B06** | Modal quantity can be decreased to 0 or negative numbers. | Missing `Math.max(1, ...)` on decrement. |
| 5 | **B07/B14** | Price filter is ignored and hard-caps results at $250. | `if (maxP < 500) list.filter(p => p.price <= 250);` |
| 6 | **B08 (UI)** | Wishlist icon uses a star (`⭐`) instead of a heart. | `el.textContent = p._wished ? '⭐' : '♡';` |
| 7 | **B08 (Logic)** | Wishlist header count never decrements when items are removed. | Decrement logic intentionally omitted. |
| 8 | **B09** | Search is case-sensitive (e.g., "head" won't find "Headphones"). | Missing `.toLowerCase()` on search query/data. |
| 9 | **B10** | Phantom extra page exists in the pagination. | `totalPages = Math.ceil(...) + 1;` |
| 10 | **B11** | "Clear All" resets the UI but does not refresh the product list. | `renderProducts()` is not called at end of clear. |
| 11 | **B12** | Sale items increment the cart count by 2 instead of 1. | `cartCount += (p.badge === 'sale') ? 2 : 1;` |
| 12 | **B13** | "Sports" category incorrectly includes "Home" products. | `(checkedCats.includes('Sports') && p.category === 'Home')` |
| 13 | **B15 (UI)** | Modal does not close when clicking the background overlay. | Overlay click handler logic is commented out. |
| 14 | **B15 (State)** | Modal quantity is not reset to 1 when opening a new product. | Reset logic intentionally omitted. |
| 15 | **Pricing** | "Save $" display is artificially inflated by $5. | `Save $${p.origPrice - p.price + 5}` |
| 16 | **Sorting** | "Name A-Z" sorts by the second word of the product name. | `const w = s => s.split(' ')[1] || s;` |
| 17 | **Search** | Artificial 800ms lag delay added to search input. | `setTimeout(() => applyFilters(), 800);` |
| 18 | **Modal Add** | "Add to Cart" from modal ignores the selected quantity. | `addToCart(currentProd.id, null);` (qty ignored) |
| 19 | **Quick Stats** | Sidebar stats (Total, Sale, Avg) are hardcoded and static. | Recalculation logic was never implemented. |
| 20 | **Navigation** | Pagination is hard-capped at 3 buttons regardless of data. | `Math.min(Math.max(totalPages, 3), 3)` |
| 21 | **Filtering** | Rating filter excludes exact matches (uses `>` instead of `>=`). | `list.filter(p => p.rating > minRating);` |
| 22 | **Broken Link** | Terms of Service link points to a non-existent file. | `/terms-and-conditions-v2-final.html` is 404. |
| 23 | **Responsive** | Layout breaks on mobile (labels, price overflow, text clipping). | Specific CSS bugs noted at lines 1429, 1443, 1465. |

