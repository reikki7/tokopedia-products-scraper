import time
from core.search_results_collector import SearchResultsCollector
from core.products_collector import ProductsCollector
from core.data_manager import DataManager
from config.settings import SEARCH_URLS, MAX_PRODUCTS, MAX_PAGES
from config.config import (
    DEFAULT_HEADLESS,
    PRODUCT_DELAY,
    VERBOSE_LOGGING,
    TEST_SEARCH_URL
)
from utils.utils import log_progress, is_valid_url

def main():
    urls = SEARCH_URLS
    max_products = MAX_PRODUCTS

    searcher = SearchResultsCollector(headless=DEFAULT_HEADLESS)
    prod_scraper = ProductsCollector(headless=DEFAULT_HEADLESS)
    data_manager = DataManager()
    all_products = []

    print("🚀 Starting Tokopedia Scraper...")
    print(f"📊 Will gather up to {max_products} products per URL")

    valid_urls = [u for u in urls if is_valid_url(u)]
    if not valid_urls:
        print("❌ No valid URLs provided. Exiting.")
        return

    print(f"🔗 Processing {len(valid_urls)} URL(s)")

    try:
        # Search Results
        for idx, search_url in enumerate(valid_urls, start=1):
            print(f"\n--- Processing search URL {idx} of {len(valid_urls)} ---")
            print(f"URL: {search_url}")

            try:
                products_on_page = searcher.scrape_search_results(
                    search_url,
                    max_products=max_products,
                    max_pages=MAX_PAGES
                )
                print(f"→ Retrieved {len(products_on_page)} products on this search page.")
                all_products.extend(products_on_page)
            except Exception as e:
                print(f"❌ Failed to collect search results for URL {search_url}: {e}")
                continue

            time.sleep(PRODUCT_DELAY)

        total_products = len(all_products)
        if total_products == 0:
            print("❌ No products found. Exiting.")
            return

        print(f"\n✅ Successfully collected basic info for {total_products} products")
        print(f"\n=== Collecting details for {total_products} products ===")

        prod_scraper.driver = searcher.driver
        driver = prod_scraper.driver

        for i, prod in enumerate(all_products, start=1):
            product_url = prod.get("product_url", "")

            if i % 10 == 0 or i == 1:
                log_progress(i, total_products, "products", "Collecting details")

            print(f"\n({i}/{total_products}) {product_url}")

            if product_url and product_url != "N/A":
                try:
                    driver.get(product_url)

                    details = prod_scraper.scrape_product_details(product_url)
                    prod["details"] = details

                    variants = details.get("variants", {})
                    available_variant_details = details.get("available_variant_details", [])
                    reviews = details.get("reviews", [])

                    variant_types = len(variants)
                    total_variant_options = sum(len(v) for v in variants.values())
                    variant_combinations = len(available_variant_details)
                    reviews_count = len(reviews)

                    print(
                        f"   ✅ Details: {variant_types} variant types, "
                        f"{total_variant_options} options, "
                        f"{variant_combinations} available variant combinations, "
                        f"{reviews_count} reviews"
                    )

                except Exception as e:
                    print(f"   ❌ Error fetching details: {e}")
                    prod["details"] = {}
            else:
                prod["details"] = {}
                if VERBOSE_LOGGING:
                    print("   ⚠️ No valid product_url, skipping details.")

            time.sleep(PRODUCT_DELAY)

        # Save data
        print(f"\n💾 Saving data...")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        saved_files = data_manager.save_detailed_products(all_products, timestamp)

        if saved_files.get("json"):
            print(f"✅ JSON saved: {saved_files['json']}")
        if saved_files.get("csv"):
            print(f"✅ CSV saved: {saved_files['csv']}")

        # Summary
        print(f"\n🎉 Scraping completed successfully!")
        print(f"📊 Total products collected: {total_products}")
        print(f"📁 Files saved with timestamp: {timestamp}")

        products_with_details = sum(1 for p in all_products if p.get("details"))
        products_with_reviews = sum(
            1
            for p in all_products
            if p.get("details", {}).get("reviews")
        )

        print(f"📈 Products with detailed info: {products_with_details}")
        print(f"💬 Products with reviews: {products_with_reviews}")

    except KeyboardInterrupt:
        print("\n❗ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        start = time.time()
        searcher.close_driver()
        print(f"\n🕒 Closed driver in {time.time() - start:.2f} seconds")
        print("🔒 Browsers closed. Done.")

def quick_test():
    """Quick test function with minimal setup (uses TEST_SEARCH_URL)."""
    print("🧪 Running quick test...")

    test_url = TEST_SEARCH_URL
    searcher = SearchResultsCollector(headless=True)

    try:
        products = searcher.scrape_search_results(
            test_url,
            max_products=2,
            max_pages=1
        )
        print(f"✅ Quick test result: {len(products)} products found")

        if products:
            print("\nSample products:")
            for idx, product in enumerate(products, 1):
                print(f"\nProduct {idx}:")
                print(f"  Title: {product.get('title', 'N/A')}")
                # Field name changed from `new_price` to `displayed_price_final`
                print(f"  Price: {product.get('displayed_price_final', 'N/A')}")
                print(f"  Rating: {product.get('product_rating', 'N/A')}")
                print(f"  Shop: {product.get('seller_name', 'N/A')}")
                print(f"  Location: {product.get('location', 'N/A')}")
                print(f"  Product URL: {product.get('product_url', 'N/A')}")
                print("  " + "-" * 50)
        else:
            print("❌ No products found in quick test")

        return products
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return []
    finally:
        searcher.close_driver()


def run_basic_scraping_only():
    """Run only basic scraping (no detailed product info)."""
    print("🚀 Running basic scraping...")

    urls = SEARCH_URLS
    searcher = SearchResultsCollector(headless=DEFAULT_HEADLESS)
    data_manager = DataManager()
    all_products = []

    try:
        for idx, search_url in enumerate(urls, start=1):
            if VERBOSE_LOGGING:
                print(f"\n--- Processing search URL {idx} of {len(urls)} ---")
            products_on_page = searcher.scrape_search_results(
                search_url,
                max_products=MAX_PRODUCTS,
                max_pages=MAX_PAGES
            )
            all_products.extend(products_on_page)
            time.sleep(PRODUCT_DELAY)

        if all_products:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            json_filename = f"tokopedia_basic_{timestamp}.json"
            csv_filename = f"tokopedia_basic_{timestamp}.csv"

            json_path = data_manager.save_to_json(all_products, json_filename)
            csv_path = data_manager.save_to_csv(all_products, csv_filename)

            print(f"\n💾 Saving data...")
            if json_path:
                print(f"✅ JSON saved: {json_path}")
            if csv_path:
                print(f"✅ CSV saved: {csv_path}")

            print(f"\n🎉 Scraping completed successfully!")
            print(f"📊 Total products collected: {len(all_products)}")
            print(f"📁 Files saved with timestamp: {timestamp}")
        else:
            print("❌ No products found")

    finally:
        searcher.close_driver()


if __name__ == "__main__":
    # By default, run full scraping with details:
    main()

    # To run quick_test instead, uncomment the following line:
    # quick_test()

    # To run only basic scraping (no product details), uncomment:
    # run_basic_scraping_only()
