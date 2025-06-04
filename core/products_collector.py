import re
import time
from itertools import product
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.base_collector import BaseCollector
from config.settings import MAX_REVIEW_PAGES
from core.reviews_collector import ReviewsCollector


class ProductsCollector(BaseCollector):
    """
    Handles scraping of an individual product page:
     - extracting variant types + options
     - iterating through all variant‐combinations for stock/pricing
     - grabbing “detail images,” description, seller rating, condition, min_order, collection links, etc.
     - then delegating to ReviewsCollector to fetch paginated reviews
    """

    def __init__(self, headless=True):
        super().__init__(headless=headless)
        self.review_scraper = ReviewsCollector(headless=headless)

    def scrape_product_details(self, product_url):
        """
        - Opens product_url
        - Extracts variants (data["variants"] = {variant_name: [option1, option2, …]})
        - Calls scrape_variant_details(...) if there are any variants
        - Scrapes seller_rating, description, detail images, delivery_origin
        - Scrapes reviews using ReviewsCollector
        - Scrapes condition / min_order / collection (“etalase”)
        """
        if not self.driver:
            self.start_driver()
        data = {
            "seller_rating": 0.0,
            "condition": "",
            "collection": [],
            "min_order": 0,
            "description": "",
            "delivery_origin": "",
            "variants": {},
            "available_variant_details": [],
            "detail_images": [],
            "reviews": []
        }

        self.driver.get(product_url)
        wait = WebDriverWait(self.driver, 15)
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[data-testid='lblPDPDescriptionProduk']")
                )
            )
        except:
            pass

        # Extract variants & options
        print("🔍 Extracting variant information...")
        try:
            variant_titles = self.driver.find_elements(
                By.XPATH, "//p[starts-with(@data-testid,'pdpVariantTitle#')]"
            )
            for title in variant_titles:
                label_text = title.text.strip()
                m = re.search(r"pilih\s+(.+?):", label_text, re.IGNORECASE)
                if not m:
                    continue
                variant_name = m.group(1).strip().lower()
                data["variants"][variant_name] = []

                # The buttons for that variant appear in a sibling div with class "css-hayuji"
                try:
                    button_container = title.find_element(
                        By.XPATH, "following-sibling::div[@class='css-hayuji']"
                    )
                    buttons = button_container.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        txt = btn.text.strip()
                        if txt:
                            data["variants"][variant_name].append(txt)
                except Exception as e:
                    print(f"   ⚠️ Error parsing variant '{variant_name}': {e}")
                    continue

            if data["variants"]:
                print(f"✅ Found variants: {list(data['variants'].keys())}")
            else:
                print("ℹ️  Product has no variants")
        except Exception as e:
            print(f"❌ Error extracting variants: {e}")

        # If available variants exist, iterate through all combinations
        if data["variants"]:
            print("\n💰 Collecting variant details…")
            data["available_variant_details"] = self.scrape_variant_details(data)

        # Seller rating
        try:
            rating_el = self.driver.find_element(
                By.XPATH,
                "//div[contains(@class,'css-b6ktge')]//p[contains(@class,'css-1gvq2cb-unf-heading')]"
            )
            rt_txt = rating_el.text.split()[0]
            data["seller_rating"] = float(rt_txt)
        except:
            data["seller_rating"] = 0.0

        # Full description
        try:
            self.driver.execute_script("window.scrollBy(0, 400)")
            time.sleep(0.3)
            see_more = self.driver.find_element(
                By.XPATH,
                "//button[contains(text(),'Lihat Selengkapnya') or contains(text(),'Lihat lebih') or contains(text(),'Lihat Semua')]"
            )
            see_more.click()
            time.sleep(0.5)
        except:
            pass

        try:
            desc_container = self.driver.find_element(
                By.CSS_SELECTOR, "div[data-testid='lblPDPDescriptionProduk']"
            )
            raw_html = desc_container.get_attribute("innerHTML")
            tmp = raw_html.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
            soup = BeautifulSoup(tmp, "html.parser")
            data["description"] = soup.get_text(separator="\n").strip()
        except:
            data["description"] = ""

        # Detail images
        detail_small = []
        detail_big = []
        try:
            thumbs = self.driver.find_elements(By.CSS_SELECTOR, "button[data-testid='PDPImageThumbnail'] img")
            for img in thumbs:
                src = img.get_attribute("src")
                if src and "http" in src and not src.startswith("data:image/svg"):
                    detail_small.append(src)
                    detail_big.append(src.replace("/cache/200/", "/cache/500-square/"))
        except:
            pass
        data["detail_images"] = [{"thumbnail": detail_small, "preview": detail_big}]

        # Delivery origin
        try:
            delivery_el = self.driver.find_element(By.XPATH, "//h2[contains(text(),'Dikirim dari')]")
            bold = delivery_el.find_element(By.TAG_NAME, "b")
            data["delivery_origin"] = bold.text.strip()
        except:
            data["delivery_origin"] = ""

        # Reviews
        print(f"\n📖 Collecting reviews (up to {MAX_REVIEW_PAGES} pages)…")
        self.review_scraper.driver = self.driver
        data["reviews"] = self.review_scraper.scrape_reviews_with_pagination(max_pages=MAX_REVIEW_PAGES)

        # Condition / Min order / Collection (“Etalase”)
        try:
            info_ul = self.driver.find_element(By.CSS_SELECTOR, "ul[data-testid='lblPDPInfoProduk']")
            lis = info_ul.find_elements(By.TAG_NAME, "li")
            for li in lis:
                spans = li.find_elements(By.TAG_NAME, "span")
                if len(spans) >= 2:
                    label = spans[0].text.strip().lower()
                    val = spans[1].text.strip()
                    if "kondisi" in label:
                        data["condition"] = val
                    elif "min. pemesanan" in label:
                        nums = re.findall(r"\d+", val)
                        data["min_order"] = int(nums[0]) if nums else 0
                # Collection (“Etalase”)
                if "etalase" in li.text.lower():
                    try:
                        a = li.find_element(By.TAG_NAME, "a")
                        b = a.find_element(By.TAG_NAME, "b")
                        data["collection"].append({
                            "text": b.text.strip(),
                            "url": a.get_attribute("href")
                        })
                    except:
                        pass
        except:
            data["condition"] = ""
            data["min_order"] = 0
            data["collection"] = []

        return data

    def scrape_variant_details(self, data):
        """
        Given data["variants"] == {variant_name: [option1, option2,…], …},
        this method will:
         - Generate all combinations of those options
         - For each combination, click through appropriate buttons on the page
         - Wait for price/stock to update
         - Record final_price, original_price, stock_count, discount%
        Returns a list of dicts, each with:
           { "variant_options": {...}, "final_price": int, "original_price": int, "stock": int, "discount_percent": float }
        """
        available_variant_details = []
        try:
            keys = list(data["variants"].keys())
            if not keys:
                return available_variant_details

            print(f"🔄 Processing {len(keys)} variant types: {keys}")
            all_option_lists = [data["variants"][k] for k in keys]

            if len(keys) == 1:
                available = self.get_available_variant_options(keys[0])
                combos = [{keys[0]: opt} for opt in available]
            else:
                first_combos = [dict(zip(keys[:-1], combo)) for combo in product(*all_option_lists[:-1])]
                combos = []
                for base in first_combos:
                    for vt, vv in base.items():
                        self.click_variant_button(vt, vv)
                        time.sleep(0.1)
                    last_variant = keys[-1]
                    last_opts = self.get_available_variant_options(last_variant)
                    for lo in last_opts:
                        cd = base.copy()
                        cd[last_variant] = lo
                        combos.append(cd)

            print(f"\n📊 Checking {len(combos)} variant combinations…")
            wait = WebDriverWait(self.driver, 5)

            for idx, combo in enumerate(combos):
                print(f"🔍 Checking variant {idx+1}/{len(combos)}: {combo}")
                for vt, vv in combo.items():
                    ok = self.click_variant_button(vt, vv)
                    if not ok:
                        print(f"   ⚠️ Failed to click {vt}:{vv}")
                    time.sleep(0.1)

                try:
                    wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "p[data-testid='pdpProductPrice']")
                    ))
                except:
                    continue

                # Item Stock
                stock_count = 0
                try:
                    s_el = self.driver.find_element(By.CSS_SELECTOR, "p[data-testid='stock-label']")
                    stxt = s_el.text.strip()
                    if "habis" in stxt.lower():
                        print(f"   ❌ Out of stock: {combo}")
                        continue
                    m2 = re.search(r"(\d+)", stxt)
                    if m2:
                        stock_count = int(m2.group(1))
                        print(f"   📦 Stock: {stock_count}")
                    else:
                        print(f"   ⚠️ Could not parse stock from: {stxt}")
                except Exception as e:
                    print(f"   ⚠️ Could not get stock info: {e}")
                    stock_count = 0

                # Final price
                final_price = None
                for sel in ["p[data-testid='pdpProductPrice']", ".css-brw1im-unf-heading"]:
                    try:
                        pe = self.driver.find_element(By.CSS_SELECTOR, sel)
                        ptxt = pe.text.strip()
                        if "Rp" in ptxt and "-" not in ptxt:
                            final_price = int(
                                ptxt.replace("Rp", "").replace(".", "").replace(",", "").strip()
                            )
                            print(f"   💰 Final price: Rp{final_price:,}")
                            break
                        elif "-" in ptxt:
                            print(f"   ⚠️ Price range detected, skipping: {ptxt}")
                            final_price = None
                            break
                    except:
                        continue

                # Original price (if discounted)
                original_price = None
                for sel in [
                    "p[data-testid='pdpSlashPrice'] del",
                    "del[data-testid='pdpSlashPrice']",
                    "p[color='var(--NN400, #98A3B4)'] del",
                    ".css-14nwhqu-unf-heading del"
                ]:
                    try:
                        pe = self.driver.find_element(By.CSS_SELECTOR, sel)
                        ptxt = pe.text.strip()
                        ptxt = re.sub(r"harga sebelum diskon\s*", "", ptxt, flags=re.IGNORECASE)
                        if "Rp" in ptxt:
                            original_price = int(
                                ptxt.replace("Rp", "").replace(".", "").replace(",", "").strip()
                            )
                            print(f"   🏷️  Original price: Rp{original_price:,}")
                            break
                    except:
                        continue

                if original_price is None and final_price is not None:
                    original_price = final_price
                    print("   ℹ️  No discount found")

                # Compute discount %
                if final_price is not None:
                    entry = {
                        "variant_options": combo,
                        "final_price": final_price,
                        "original_price": original_price,
                        "stock": stock_count,
                    }
                    if original_price and original_price > final_price:
                        dp = round(((original_price - final_price) / original_price) * 100, 1)
                        entry["discount_percent"] = dp
                        print(f"   🎯 Discount: {dp}%")
                    else:
                        entry["discount_percent"] = 0
                    available_variant_details.append(entry)
                else:
                    print(f"   ❌ No price for combination: {combo}")

            print(f"✅ Collected {len(available_variant_details)} variant detail entries")
            return available_variant_details
        except Exception as e:
            print(f"❌ Error in scrape_variant_details: {e}")
            return []

    def get_available_variant_options(self, variant_type):
        """
        Returns a list of non-disabled option texts under the given variant_type.
        """
        try:
            available = []
            # All variant headers:
            headers = self.driver.find_elements(
                By.XPATH,
                "//p[starts-with(@data-testid, 'pdpVariantTitle#')]"
            )
            target = None
            for h in headers:
                if f"pilih {variant_type.lower()}" in h.text.strip().lower():
                    target = h
                    break
            if not target:
                print(f"   ⚠️ Header not found for variant '{variant_type}'")
                return available

            # Buttons are in sibling div[class='css-hayuji']
            try:
                btn_container = target.find_element(By.XPATH, "following-sibling::div[@class='css-hayuji']")
            except:
                print(f"   ⚠️ Button container not found for '{variant_type}'")
                return available

            active_buttons = btn_container.find_elements(
                By.CSS_SELECTOR,
                "div[data-testid='btnVariantChipActive'] button, div[data-testid='btnVariantChipActiveSelected'] button"
            )
            for b in active_buttons:
                txt = b.text.strip()
                if txt and not txt.startswith("http"):
                    clean = txt.split("\n")[0].strip()
                    if clean:
                        available.append(clean)
            print(f"   📋 Available options for '{variant_type}': {available}")
            return available
        except Exception as e:
            print(f"   ❌ Error getting options for '{variant_type}': {e}")
            return []

    def click_variant_button(self, variant_type, variant_value):
        """
        Clicks the button matching variant_type + variant_value. Returns True/False.
        """
        try:
            headers = self.driver.find_elements(
                By.XPATH,
                "//p[starts-with(@data-testid, 'pdpVariantTitle#')]"
            )
            target = None
            for h in headers:
                if f"pilih {variant_type.lower()}" in h.text.strip().lower():
                    target = h
                    break
            if not target:
                print(f"   ⚠️ Header not found for variant '{variant_type}'")
                return False

            try:
                btn_container = target.find_element(By.XPATH, "following-sibling::div[@class='css-hayuji']")
            except:
                print(f"   ⚠️ Button container missing for '{variant_type}'")
                return False

            buttons = btn_container.find_elements(By.TAG_NAME, "button")
            for b in buttons:
                txt = b.text.strip()
                if variant_value in txt or txt == variant_value:
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", b)
                        time.sleep(0.2)
                        b.click()
                        return True
                    except:
                        try:
                            self.driver.execute_script("arguments[0].click();", b)
                            return True
                        except:
                            print(f"❌ JS click also failed for '{variant_value}'")
                            return False

            print(f"   ⚠️ Button not found for '{variant_value}'")
            return False
        except Exception as e:
            print(f"   ❌ Error clicking variant button {variant_type}:{variant_value} → {e}")
            return False
