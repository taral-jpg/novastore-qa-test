import sys
from playwright.sync_api import sync_playwright
import time

# Config
BASE_URL = "http://localhost:8000"

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        results = []

        def report(test_id, description, passed, observation):
            results.append({
                "id": test_id,
                "desc": description,
                "status": "PASS" if passed else "FAIL (Bug Present)",
                "note": observation
            })

        print(f"\nStarting QA Grading Script against {BASE_URL}...\n")

        try:
            page.goto(BASE_URL)
            page.wait_for_selector(".product-card")
        except Exception as e:
            print(f"Error: Could not connect to {BASE_URL}. Ensure 'python3 serve.py' is running.")
            return

        # --- B01: Sorting ---
        page.select_option("#sortSelect", "price-asc")
        page.wait_for_timeout(500)
        prices = [int(p.inner_text().replace('$', '')) for p in page.query_selector_all(".price") if '$' in p.inner_text()]
        b01_pass = all(prices[i] <= prices[i+1] for i in range(len(prices)-1)) if prices else False
        report("B01", "Sort Price: Low to High", b01_pass, f"Order: {prices[:5]}...")

        # --- B02: OOS Modal ---
        # Aura Mist Diffuser (ID 4) is OOS
        page.click("text=Aura Mist Diffuser")
        page.wait_for_selector("#modalContent")
        add_btn = page.query_selector("#modalAddBtn")
        b02_pass = add_btn.is_disabled()
        report("B02", "OOS Item Modal Add Button Disabled", b02_pass, "Button was enabled" if not b02_pass else "Correct")
        page.click(".modal-close")

        # --- B03-B05: Rating Mismatch ---
        # B03: UltraWatch Pro (ID 2), Rating 4.5, Stars should be 5 (incorrectly 4)
        watch_stars = len(page.query_selector_all(".product-card:has-text('UltraWatch Pro') .rating-stars:has-text('★')")) # This is simplified
        # Actually checking the stars text
        watch_stars_txt = page.inner_text(".product-card:has-text('UltraWatch Pro') .rating-stars")
        b03_pass = watch_stars_txt.count('★') == 5
        report("B03", "UltraWatch Pro Stars Match Rating (4.5 -> 5)", b03_pass, f"Stars: {watch_stars_txt}")

        # --- B06: Negative Qty ---
        page.click("text=ProSound X7")
        for _ in range(5): page.click("text=−") # The HTML entity for minus is &#8722;
        qty = int(page.inner_text("#qtyVal"))
        b06_pass = qty >= 1
        report("B06", "Modal Qty Cannot Go Below 1", b06_pass, f"Qty reached: {qty}")
        page.click(".modal-close")

        # --- B07: Price Filter ---
        page.fill("#priceRange", "100")
        page.dispatch_event("#priceRange", "input")
        page.click(".apply-btn")
        page.wait_for_timeout(500)
        visible_prices = [int(p.inner_text().replace('$', '')) for p in page.query_selector_all(".product-card:not([style*='display: none']) .price") if '$' in p.inner_text()]
        b07_pass = all(p <= 100 for p in visible_prices) if visible_prices else True
        report("B07", "Price Filter Shows Items BELOW Max", b07_pass, f"Prices shown up to: {max(visible_prices) if visible_prices else 0}")

        # --- B08: Wishlist Count ---
        initial_wish = int(page.inner_text("#wishlistCount"))
        page.click(".wish-icon", position={"x": 5, "y": 5}) # Click first available wish icon
        page.wait_for_timeout(200)
        final_wish = int(page.inner_text("#wishlistCount"))
        b08_pass = final_wish == initial_wish + 1
        report("B08", "Wishlist Header Counter Updates", b08_pass, f"Initial: {initial_wish}, Final: {final_wish}")

        # --- B09: Search Sensitivity ---
        page.click(".clear-btn")
        page.fill("#searchInput", "headphones")
        page.click(".search-btn")
        results_count = len(page.query_selector_all(".product-card"))
        b09_pass = results_count > 0
        report("B09", "Search is Case-Insensitive", b09_pass, f"Found {results_count} items for 'headphones'")

        # --- B10: Pagination Phantom ---
        page.click(".clear-btn")
        page_btns = page.query_selector_all(".page-btn")
        has_page_3 = any("3" in b.inner_text() for b in page_btns)
        b10_pass = not has_page_3
        report("B10", "No Phantom Page 3", b01_pass, "Page 3 button exists" if has_page_3 else "Correct")

        # --- B11: Clear Sync ---
        page.fill("#searchInput", "ProSound")
        page.click(".search-btn")
        page.click(".clear-btn")
        all_visible = len(page.query_selector_all(".product-card"))
        b11_pass = all_visible > 5 # Should be 9 on first page
        report("B11", "Clear All Refreshes Product List", b11_pass, f"Visible items after clear: {all_visible}")

        # --- B12: Sale items Double Cart ---
        initial_cart = int(page.inner_text("#cartCount"))
        page.click(".product-card:has-text('ProSound X7') .add-to-cart") # ProSound is on sale
        page.wait_for_timeout(200)
        final_cart = int(page.inner_text("#cartCount"))
        b12_pass = final_cart == initial_cart + 1
        report("B12", "Sale Items Only Incr. Cart by 1", b12_pass, f"Added 1, count increased by {final_cart - initial_cart}")

        # --- B13: Category Leak ---
        page.click(".clear-btn")
        page.check("input[value='Sports']")
        page.click(".apply-btn")
        categories = [p.inner_text() for p in page.query_selector_all(".product-brand")] # Checking brands then lookup?
        # Better: check if 'Aura Mist Diffuser' (Home) is visible
        is_home_visible = page.is_visible("text=Aura Mist Diffuser")
        b13_pass = not is_home_visible
        report("B13", "Sports Category Does Not Leak Home Items", b13_pass, "Home items visible" if is_home_visible else "Correct")

        # --- B14: Hardcoded Price Cap ---
        page.click(".clear-btn")
        page.fill("#priceRange", "400")
        page.dispatch_event("#priceRange", "input")
        page.click(".apply-btn")
        watch_visible = page.is_visible("text=UltraWatch Pro") # Price $299
        b14_pass = watch_visible
        report("B14", "Filtering Operates Above $250", b14_pass, "UltraWatch ($299) hidden" if not b14_pass else "Correct")

        # --- B15: Overlay Close ---
        page.click("text=ProSound X7")
        page.wait_for_selector(".modal.open")
        page.click("#modalOverlay", position={"x": 5, "y": 5}) # Click corner of overlay
        page.wait_for_timeout(500)
        is_still_open = page.is_visible(".modal.open")
        b15_pass = not is_still_open
        report("B15", "Modal Closes via Overlay Click", b15_pass, "Modal stayed open" if is_still_open else "Correct")

        # Summary Output
        print("-" * 60)
        print(f"{'ID':<5} {'Description':<35} {'Status':<15}")
        print("-" * 60)
        for r in results:
            print(f"{r['id']:<5} {r['desc']:<35} {r['status']:<15}")
        
        pass_count = sum(1 for r in results if "PASS" in r["status"])
        print("-" * 60)
        print(f"TOTAL SCORE: {pass_count}/15 Issues Fixed")
        print("-" * 60)

        browser.close()

if __name__ == "__main__":
    run_tests()
