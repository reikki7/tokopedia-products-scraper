import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.base_collector import BaseCollector

class SearchResultsCollector(BaseCollector):
    """
    Handles scraping of Tokopedia search‐results pages (with pagination),
    extracting each product card’s summary details.
    """

    def __init__(self, headless=True):
        super().__init__(headless=headless)

    def get_active_filters(self):
        """
        Scrape currently active filters on the search page, if any.
        Returns a list of strings (filter names).
        """
        # Wait for the 'dSRPSearchInfo' (present regardless of filters)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='dSRPSearchInfo']"))
        )

        # Now wait (max 3s) for at least one filter chip to appear, but ignore if timeout
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-unify='Chip']"))
            )
        except:
            # No filter chips appeared in time
            return []

        chips = self.driver.find_elements(By.CSS_SELECTOR, "button[data-unify='Chip']")
        filters = []
        for chip in chips:
            text = chip.text.strip()
            if text and text not in ("×", "x"):
                filters.append(text)
        return filters

    def scrape_search_results(self, url, max_products=50, max_pages=1):
        """
        - Navigate through `max_pages` of search results (or until `max_products` found).
        - For each product‐card, call `extract_product_info(...)` to gather summary info.
        - Returns a list of dicts, each containing: title, label (search query), prices, discount, image_url, seller_name, location, rating, sold_count, product_url.
        """
        if not self.driver:
            self.start_driver()

        all_data = []
        current_page = 1

        while current_page <= max_pages and len(all_data) < max_products:
            if current_page == 1:
                page_url = url
            else:
                sep = "&" if "?" in url else "?"
                page_url = f"{url}{sep}page={current_page}"

            print(f"📄 Loading page {current_page} of {max_pages}...")
            self.driver.get(page_url)

            wait = WebDriverWait(self.driver, 10)
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.oQ94Awb6LlTiGByQZo8Lyw\\=\\="))
            )

            if current_page == 1:
                filters = self.get_active_filters()
                print()
                if filters:
                    print("📋 Active filters:")
                    for f in filters:
                        print(f"  * {f}")
                else:
                    print("📋 No active filters detected")
                print()

            # Scroll to load more products
            self.scroll_page(duration=3)

            # Try multiple selectors to locate product card containers
            product_selectors = [
                "[data-testid='spnSRP - Product Card']",
                ".css-bk6tzz",
                "[data-testid='divSRPContentProducts'] > div > div",
                ".css-1sn1xa2",
                ".pcv3_product_content",
                ".css-5wh65g"
            ]

            products = []
            for sel in product_selectors:
                products = self.driver.find_elements(By.CSS_SELECTOR, sel)
                if products:
                    print(f"\nFound {len(products)} products using selector: {sel}")
                    break

            if not products:
                print(f"No products found on page {current_page}, stopping.")
                break

            remaining = max_products - len(all_data)
            to_scrape = min(len(products), remaining)
            page_data = []

            for idx, prod in enumerate(products[:to_scrape]):
                try:
                    info = self.extract_product_info(prod)
                    # Filter out “N/A” titles
                    if info and info["title"] != "N/A":
                        page_data.append(info)
                        total = len(all_data) + len(page_data)
                        print(f"✏️  Product {total}: {info['title'][:65]}...")
                        time.sleep(0.5)  # small delay
                        if total >= max_products:
                            break
                except Exception as e:
                    print(f"Error collecting product {idx+1} on page {current_page}: {e}")
                    continue

            all_data.extend(page_data)
            print(f"→ Retrieved {len(page_data)} items (Total so far: {len(all_data)})")

            if len(all_data) >= max_products:
                print(f"✅ Reached max products limit ({max_products})")
                break

            if len(products) < 20:
                print(f"ℹ️  Only {len(products)} products found; maybe last page.")
                if current_page < max_pages:
                    print("🔍 Checking next page anyway...")

            current_page += 1
            if current_page <= max_pages:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a.oQ94Awb6LlTiGByQZo8Lyw\\=\\="))
                )

        if current_page > max_pages:
            print(f"✅ Reached page limit ({max_pages})")

        print(f"📊 Finished: {len(all_data)} products from {min(current_page, max_pages)} pages")
        return all_data

    def extract_product_info(self, product_element):
        """
        Given a Selenium‐WebElement for a single product card, extract:
         - title
         - label (search query)
         - displayed_price_final, displayed_price_original, discount
         - image_url
         - seller_name, location
         - product_rating
         - sold_count
         - product_url
        Returns a dict with those keys.
        """
        data = {}

        # Title
        title = "N/A"
        title_selectors = [
            "._0T8-iGxMpV6NEsYEhwkqEg==",
            "span._0T8-iGxMpV6NEsYEhwkqEg==",
            "[data-testid='spnSRPProdName']",
            ".css-3um8ox",
            "span[class*='_0T8-iGxMpV6NEsYEhwkqEg']"
        ]
        for sel in title_selectors:
            try:
                elem = product_element.find_element(By.CSS_SELECTOR, sel)
                txt = elem.text.strip()
                if txt and len(txt) > 5:
                    title = txt
                    break
            except:
                continue
        data["title"] = title

        # Search‐query label (from the “You searched for X” element)
        try:
            search_info = self.driver.find_element(
                By.CSS_SELECTOR, "[data-testid='dSRPSearchInfo'] strong"
            )
            search_text = search_info.text.strip('"')
            search_text = re.sub(r"[^a-zA-Z0-9\s]", "", search_text)
            data["label"] = search_text.strip().title()
        except:
            # fallback: parse “q=” from current_url
            try:
                cur = self.driver.current_url
                m = re.search(r"[?&]q=([^&]+)", cur)
                if m:
                    txt = m.group(1).replace("+", " ").replace("%20", " ")
                    txt = re.sub(r"[^a-zA-Z0-9\s]", "", txt)
                    data["label"] = txt.strip().title()
                else:
                    data["label"] = ""
            except:
                data["label"] = ""

        # Final price, Original price, Discount %
        def _parse_price(selectors_list):
            for sel in selectors_list:
                try:
                    el = product_element.find_element(By.CSS_SELECTOR, sel)
                    p_txt = el.text.strip()
                    if "Rp" in p_txt:
                        return int(p_txt.replace("Rp", "").replace(".", "").strip())
                except:
                    continue
            return 0

        data["displayed_price_final"] = _parse_price([
            "._67d6E1xDKIzw+i2D2L0tjw==",
            "div._67d6E1xDKIzw+i2D2L0tjw==",
            "[data-testid='spnSRPProdPrice']",
            ".css-h66vau",
            "div[class*='_67d6E1xDKIzw']"
        ])

        data["displayed_price_original"] = _parse_price([
            ".q6wH9+Ht7LxnxrEgD22BCQ==",
            "div.q6wH9+Ht7LxnxrEgD22BCQ==",
            "span[class*='q6wH9+Ht7LxnxrEgD22BCQ']",
            "div[class*='strike']"
        ])

        # Discount %
        discount = 0
        for sel in [
            ".vRrrC5GSv6FRRkbCqM7QcQ\\=\\=",
            "span[class*='vRrrC5GSv6FRRkbCqM7QcQ']",
            "div.rpRIligrl1WcKourBjzy9g\\=\\= span",
            "span[style*='background: rgb(249, 77, 99)']"
        ]:
            try:
                de = product_element.find_element(By.CSS_SELECTOR, sel).text.strip()
                if "%" in de:
                    discount = int(de.replace("%", ""))
                    break
            except:
                continue
        data["discount"] = discount

        # Image URL
        img_url = "N/A"
        for sel in [
            "img[alt='product-image']",
            "img.Q6EyY3lHkLBxLWawflt9Sg==",
            "img[src*='tokopedia.net']",
            "img"
        ]:
            try:
                img_el = product_element.find_element(By.CSS_SELECTOR, sel)
                candidate = img_el.get_attribute("src") or img_el.get_attribute("data-src")
                if candidate and "http" in candidate:
                    img_url = candidate
                    break
            except:
                continue
        data["image_url"] = img_url

        # Seller name & location
        try:
            container = product_element.find_element(
                By.CSS_SELECTOR, "div[class='Jh7geoVa-F3B5Hk8ORh2qw==']"
            )
            raw_html = container.get_attribute("outerHTML")
            soup = BeautifulSoup(raw_html, "html.parser")
            text_only = soup.get_text(separator="|")
            chunks = [c.strip() for c in text_only.split("|") if c.strip()]
            data["seller_name"] = chunks[0] if len(chunks) > 0 else "N/A"
            data["location"] = chunks[1] if len(chunks) > 1 else "N/A"
        except:
            data["seller_name"] = "N/A"
            data["location"] = "N/A"

        # Product rating
        rating = None
        for sel in [
            "span._9jWGz3C-GX7Myq-32zWG9w\\=\\=",
            "[data-testid='icnSRPRating'] + span",
            "span[class*='_9jWGz3C-GX7Myq']"
        ]:
            try:
                r_el = product_element.find_element(By.CSS_SELECTOR, sel)
                rt = r_el.text.strip()
                if rt:
                    rating = float(rt.replace(",", "."))
                    break
            except:
                continue
        data["product_rating"] = rating

        # Sold count
        sold = None
        for sel in [
            ".se8WAnkjbVXZNA8mT+Veuw==",
            "span.se8WAnkjbVXZNA8mT+Veuw==",
            "span[class*='se8WAnkjbVXZNA8mT']"
        ]:
            try:
                sold_el = product_element.find_element(By.CSS_SELECTOR, sel)
                txt = sold_el.text.strip()
                txt = txt.replace("terjual", "").replace("Terjual", "").strip()
                if txt:
                    sold = txt
                    break
            except:
                continue
        data["sold_count"] = sold

        # Product URL
        try:
            link_el = product_element.find_element(By.TAG_NAME, "a")
            pu = link_el.get_attribute("href")
            if not pu.startswith("http"):
                pu = "https://www.tokopedia.com" + pu
            data["product_url"] = pu
        except:
            data["product_url"] = "N/A"

        return data
