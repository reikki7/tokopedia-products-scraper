import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from core.base_collector import BaseCollector


class ReviewsCollector(BaseCollector):
    """
    Handles scraping of paginated reviews for a single product page.  
    Must be passed an already‐started Selenium `driver` pointing to the product page.
    """

    def __init__(self, headless=True):
        super().__init__(headless=headless)

    def scrape_reviews_with_pagination(self, max_pages=2):
        """
        Scroll down incrementally to load reviews, then:
         - collect all reviews on this page
         - click “next” until either no more or max_pages reached
        Returns a list of dicts:
         { user_name, variant, rating, time_ago, text, image_url }
        """
        all_reviews = []
        current_page = 1

        while current_page <= max_pages:
            print(f"📖 Gathering reviews page {current_page}/{max_pages}...")

            for _ in range(5):
                self.driver.execute_script("window.scrollBy(0, window.innerHeight)")
                time.sleep(0.4)

            try:
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//article[contains(@class,'css-15m2bcr')]")
                ))
            except:
                print(f"   ⚠️ No reviews found on page {current_page}")
                break

            page_reviews = self.scrape_reviews_on_current_page()
            if not page_reviews:
                print(f"   ⚠️ No reviews collected from page {current_page}")
                break

            all_reviews.extend(page_reviews)
            print(f"   ✅ Collected {len(page_reviews)} reviews from page {current_page}")

            if current_page >= max_pages:
                print(f"   ℹ️  Reached max review pages ({max_pages})")
                break

            if not self.navigate_to_next_review_page():
                print(f"   ℹ️  No more review pages available")
                break

            current_page += 1
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//article[contains(@class,'css-15m2bcr')]"))
                )
            except:
                print(f"   ⚠️ Failed to load page {current_page}")
                break

        print(f"📋 Total reviews collected: {len(all_reviews)} from {current_page} pages")
        return all_reviews

    def scrape_reviews_on_current_page(self):
        """
        Finds all <article class="css-15m2bcr"> nodes and extracts:
         - user_name
         - variant (if shown)
         - rating
         - time_ago
         - text (expand “Selengkapnya” first if truncated)
         - image_url (if present)
        Returns a list of dicts.
        """
        reviews = []
        review_wrappers = self.driver.find_elements(
            By.XPATH, "//article[contains(@class,'css-15m2bcr')]"
        )

        for rev in review_wrappers:
            single = {
                "user_name": None,
                "variant": None,
                "rating": None,
                "time_ago": None,
                "text": "",
                "image_url": None
            }

            try:
                single["user_name"] = rev.find_element(
                    By.XPATH, ".//span[@class='name']"
                ).text.strip()
            except:
                pass

            try:
                var_txt = rev.find_element(
                    By.XPATH, ".//p[@data-testid='lblVarian']"
                ).text
                single["variant"] = var_txt.replace("Varian:", "").strip()
            except:
                pass

            try:
                single["time_ago"] = rev.find_element(
                    By.XPATH, ".//p[contains(@class,'css-vqrjg4')]"
                ).text.strip()
            except:
                pass

            try:
                rating_el = rev.find_element(
                    By.XPATH, ".//div[@data-testid='icnStarRating']"
                )
                aria = rating_el.get_attribute("aria-label")
                m2 = re.search(r"bintang\s*(\d+)", aria.lower())
                if m2:
                    single["rating"] = float(m2.group(1))
            except:
                pass

            try:
                more_btn = rev.find_element(
                    By.XPATH,
                    ".//button[contains(text(),'Selengkapnya') or contains(text(),'Lihat Ulasan')]"
                )
                more_btn.click()
                time.sleep(0.3)
            except:
                pass

            try:
                comment_span = rev.find_element(
                    By.XPATH, ".//span[@data-testid='lblItemUlasan']"
                )
                raw = comment_span.get_attribute("innerHTML")
                tmp2 = raw.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
                soup2 = BeautifulSoup(tmp2, "html.parser")
                single["text"] = soup2.get_text(separator="\n").strip()
            except:
                single["text"] = ""

            try:
                img_el = rev.find_element(
                    By.XPATH, ".//img[@data-testid='imgItemPhotoulasan']"
                )
                single["image_url"] = img_el.get_attribute("src")
            except:
                pass

            reviews.append(single)

        return reviews

    def navigate_to_next_review_page(self):
        """
        Looks for the “Next page” button under the pagination nav,
        clicks it (JS fallback if regular click fails), and waits for new reviews.
        Returns True if navigation succeeded, False otherwise.
        """
        try:
            pagination = self.driver.find_element(
                By.CSS_SELECTOR,
                "nav[aria-label='Navigasi laman'][data-unify='Pagination']"
            )
            next_button = pagination.find_element(
                By.CSS_SELECTOR, "button[aria-label='Laman berikutnya']"
            )
            if next_button.get_attribute("disabled"):
                print("   ℹ️ Next page button disabled")
                return False

            # Scroll into view
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", pagination
            )
            time.sleep(0.5)

            try:
                next_button.click()
            except:
                self.driver.execute_script("arguments[0].click();", next_button)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//article[contains(@class,'css-15m2bcr')]"))
            )
            return True
        except:
            return False
