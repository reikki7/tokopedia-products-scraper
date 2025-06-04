# Tokopedia Products Scraper

This project is a modular Python-based web scraping tool built with Selenium and BeautifulSoup, designed to collect detailed product data from [Tokopedia](https://www.tokopedia.com/) for research, analytics, or e-commerce monitoring. It scrapes both search result pages and individual product detail pages, capturing key information such as titles, prices, discounts, variants, stock levels, seller info, descriptions, images, paginated customer reviews, and more. The scraper supports robust pagination handling, and product variant combination traversal.

## Features

- 🔍 **Search Results Scraping**: Extract product listings from Tokopedia search pages
- 📄 **Detailed Product Info**: Scrape comprehensive product details including descriptions, variants, and reviews
- 📊 **Variant Combination Scanning**: Scrape all variant options with latest stock, price, and discount
- 🔍 **Filter Detection**: Identify and display active search filters (e.g., condition, shop tier)
- 💬 **Pagination Support**: Scrape multiple pages of search results and product reviews
- 💾 **Multiple Export Formats**: Save data in JSON and CSV formats
- ⚙️ **Configurable**: Customizable chrome driver options, scraping configuration, and other settings
- 🚀 **Multiple Run Modes**: Full scraping, basic scraping, or quick test modes

## Project Structure

```
tokopedia-products-scraper/
├── main.py                   # Entry point script
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore
├── LICENSE

├── config/
│   ├── config.py             # Technical constants
│   └── settings.py           # Runtime settings

├── core/
│   ├── base_collector.py     # Selenium driver setup and shared utilities
│   ├── search_results_collector.py   # Search results pagination & scraping
│   ├── products_collector.py         # Product detail scraping & pagination
│   ├── reviews_collector.py          # Review pagination & scraping
│   └── data_manager.py       # Data saving and management logic

├── utils/
│   └── utils.py              # Helper/utility functions

└── output/                   # Output (automatically generated)
    ├── json/                 # JSON export files
    └── csv/                  # CSV export files
```

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - Download from [python.org](https://python.org)
- **Google Chrome** - Latest stable version
- **Git** (optional) - For cloning the repository
- **ChromeDriver** is handled automatically using `chromedriver-autoinstaller` and `undetected-chromedriver`.

## Setup and Installation

1. **Get the Project Files**

   **Option A: Clone with Git**

   ```bash
   git clone https://github.com/reikki7/tokopedia-products-scraper.git
   cd tokopedia-products-scraper
   ```

   **Option B: Download ZIP**

   1\. Visit the repository page (You are here)

   2\. Click the "Code" button → "Download ZIP"

   3\. Extract to your preferred location

   4\. Open Command Prompt and navigate to the folder:

   ```cmd
   cd /d "path\to\tokopedia-products-scraper"
   ```

   Alternatively, you can also right click inside the folder and choose "Open in Terminal".

2. **Create a Python Virtual Environment (Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate      # On macOS/Linux
   venv\Scripts\activate         # On Windows
   ```

3. **Install Python dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the main scraper:

```bash
python main.py
```

This will:

1. Read `SEARCH_URLS` and `MAX_PRODUCTS` from `config/settings.py`.
2. Scrape products from those URLs, supporting pagination across multiple search result pages.
3. Extract detailed information for each product, including paginated reviews.
4. Save results in both JSON and CSV formats under `output/`.

### Configuration

#### `config/settings.py`

- **SEARCH_URLS**: List of search‐page URLs to scrape.
- **MAX_PRODUCTS**: Maximum number of products to scrape per URL.
- **MAX_PAGES**: Maximum number of search result pages to scrape per URL.
- **MAX_REVIEW_PAGES**: Maximum number of review pages to scrape per product.

Edit these runtime values according to your need.

```python
# Search result URLs - can be customized per run
SEARCH_URLS = [
    "https://www.tokopedia.com/search?q=polo+pria",
    "https://www.tokopedia.com/search?q=sepatu+pria"
]

# Product scraping limits - whichever reaches maximum first will stop the process
MAX_PRODUCTS = 10
MAX_PAGES = 2

# Review scraping limit
MAX_REVIEW_PAGES = 2
```

🔗 **How to Get a Search URL**:
You can obtain a valid `SEARCH_URL` by:

1. Going to [https://www.tokopedia.com](https://www.tokopedia.com)
2. Searching with your desired keyword
3. Applying any filters you want (e.g., rating, shop type, product condition)
4. Copying the full URL from the browser’s address bar into `config/settings.py`

📌 Tip: Search filters in the URL (like "Baru", "Power Merchant", etc.) **will be respected by the scraper**.

#### `config/config.py`

This file contains technical and runtime constants for the scraper, such as:

- **DEFAULT_HEADLESS**: Whether to run Chrome in headless mode.
- **SCROLL_DURATION**: How long to scroll the page to load products.
- **PRODUCT_DELAY**: Delay between scraping products.
- **VERBOSE_LOGGING**: Enable verbose logging output.
- **TEST_SEARCH_URL**: A sample search URL for quick testing.
- **CHROME_OPTIONS**: Chrome driver options for Selenium.

```python
DEFAULT_HEADLESS = True  # Run browser in headless mode (browser will not be visible if set to True)
SCROLL_DURATION = 3      # Duration to scroll down the page
PRODUCT_DELAY = 0.5      # Delay between scraping products

VERBOSE_LOGGING = True

TEST_SEARCH_URL = (
    "https://www.tokopedia.com/search?condition=1&fcity=174%2C175%2C176%2C177%2C178%2C179&navsource=&preorder=false&rt=4%2C5&search_id=2025060203323434ED066DF378EF3BDVGD&shop_tier=2&srp_component_id=04.06.00.00&srp_page_id=&srp_page_title=&st=&q=asus"
)

CHROME_OPTIONS = {
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
    'disable_blink_features': 'AutomationControlled',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
```

### Run Modes

The main script supports different modes (all defined in `main.py`):

- **Full Scraping (default)**

  ```python
  main()  # Scrapes basic info + detailed product information
  ```

  Scrapes both basic info and detailed product information.

- **Basic Scraping Only**

  ```python
  run_basic_scraping_only()  # Only search results, no product details
  ```

  Scrapes only the search results (no product details).

- **Quick Test**

  ```python
  quick_test()  # Test with 2 products (Basic Scraping)
  ```

  Runs a minimal test to verify setup.

## Output Data Structure

### Basic Product Information (exported from search results)

- `title`: Product name
- `label`: Product scrape label (Retrieved from search query or URL)
- `displayed_price_final`: Final price after discount (int)
- `displayed_price_original`: Original price before discount (int)
- `discount`: Percentage off (int)
- `image_url`: Product image
- `seller_name`: Seller name
- `location`: Shop location
- `product_rating`: Rating (float)
- `sold_count`: Sold count (text)
- `product_url`: Product detail URL

### Detailed Information (nested under `details` field)

- `variants`: Dict of available variant types and their options
- `available_variant_details`: List of available variant combinations with:

  - `variant_options`: Combination of variant types
  - `final_price`: Final price
  - `original_price`: Original price
  - `stock`: Available stock
  - `discount_percent`: Discount percentage

- `description`: Full product description
- `seller_rating`: Numerical rating of the seller (float, typically 0-5)
- `condition`: Product condition status (e.g., "Baru" for new)
- `min_order`: Minimum order quantity required
- `collection`: Shop's category/collection the product belongs to
- `delivery_origin`: Shipping origin location
- `detail_images`: List with:

  - `thumbnail`: small image URLs
  - `preview`: full-size image URLs

- `reviews`: List of review objects (now supports multiple review pages):

  - `user_name`: Name of the buyer
  - `variant`: Purchased variant/option
  - `rating`: Review score (float, 1–5 stars)
  - `time_ago`: Relative time of review (e.g., "2 minggu lalu")
  - `text`: The actual review content
  - `image_url`: Optional review image

## Sample Output

Here’s an example of a product object from the final JSON:

```json
[
  {
    "title": "Portable USB Rechargeable Blender – Smoothie Maker untuk Traveling & Olahraga",
    "label": "Portable Blender",
    "displayed_price_final": 249000,
    "displayed_price_original": 349000,
    "discount": 29,
    "image_url": "https://images.tokopedia.net/img/cache/200-square/product-1/2025/1/15/abcd1234efgh5678~.jpeg.webp?ect=4g",
    "seller_name": "SampleStore",
    "location": "Bandung",
    "product_rating": 4.6,
    "sold_count": "50+",
    "product_url": "https://www.tokopedia.com/samplestore/portable-usb-rechargeable-blender-smoothie-maker-1234567890",
    "details": {
      "seller_rating": 4.7,
      "condition": "Baru",
      "collection": [
        {
          "text": "Semua Etalase",
          "url": "https://www.tokopedia.com/samplestore/etalase/all"
        }
      ],
      "min_order": 1,
      "description": "Portable USB Rechargeable Blender – sempurna untuk membuat smoothie, jus buah, atau milkshake saat bepergian. \n\n- Kapasitas 300ml / 500ml: Pilih sesuai kebutuhan Anda.  \n- Baterai Built-in: Isi ulang lewat USB, tahan hingga 10 kali pemakaian.  \n- Pisau Stainless Steel 6-Bilah: Efisien menghancurkan buah beku.  \n- Mudah Dibersihkan: Cukup isi air dan putar beberapa detik.  \n- Portable & Ringan: Cocok untuk gym, kantor, atau piknik.  \n\nDapatkan kemudahan membuat minuman sehat di mana saja!",
      "delivery_origin": "Bandung",
      "variants": {
        "Capacity": ["300ml", "500ml"],
        "Color": ["Black", "Pink"]
      },
      "available_variant_details": [
        {
          "variant_options": {
            "Capacity": "300ml",
            "Color": "Black"
          },
          "final_price": 199000,
          "original_price": 299000,
          "stock": 20,
          "discount_percent": 33.4
        },
        {
          "variant_options": {
            "Capacity": "500ml",
            "Color": "Pink"
          },
          "final_price": 249000,
          "original_price": 349000,
          "stock": 12,
          "discount_percent": 28.7
        }
      ],
      "detail_images": [
        {
          "thumbnail": [
            "https://images.tokopedia.net/img/cache/200-square/product-1/2025/1/15/abcd1234efgh5678~.jpeg.webp?ect=4g",
            "https://images.tokopedia.net/img/cache/200-square/product-1/2025/1/15/wxyz9876lmno5432~.jpeg.webp?ect=4g"
          ],
          "preview": [
            "https://images.tokopedia.net/img/cache/500-square/product-1/2025/1/15/abcd1234efgh5678~.jpeg.webp?ect=4g",
            "https://images.tokopedia.net/img/cache/500-square/product-1/2025/1/15/wxyz9876lmno5432~.jpeg.webp?ect=4g"
          ]
        }
      ],
      "reviews": [
        {
          "user_name": "Bob",
          "variant": "300ml - Black",
          "rating": 5.0,
          "time_ago": "2 minggu lalu",
          "text": "mantap, praktis buat dipake",
          "image_url": "https://images.tokopedia.net/img/cache/200-square/review/2025/3/10/revimg12345~.webp?ect=4g"
        },
        {
          "user_name": "K***n",
          "variant": "500ml - Pink",
          "rating": 4.0,
          "time_ago": "1 bulan lalu",
          "text": "Bagus tapi kadang susah dibersihkan",
          "image_url": null
        }
      ]
    }
  }
]
```

## Data Management

The **DataManager** class (in `core/data_manager.py`) provides utilities for:

- Saving: `save_to_json`, `save_to_csv`, `save_detailed_products`
- File naming with timestamp
- Output folder: `output/json`, `output/csv`

## Utilities

The **utils** module (`utils/utils.py`) provides helper functions:

- URL validation
- Progress logging
- Timestamp formatting
- Additional HTML/text helpers

## Error Handling

The scraper includes robust error handling:

- Tries multiple selectors for robustness
- Continues scraping even if some products fail
- Graceful fallback for missing or broken product details
- Browser is always closed cleanly, even on error or keyboard interruption (Ctrl+C)

## Best Practices

1. **Respect Website Terms**: Always check and comply with Tokopedia's [Terms of Service](https://www.tokopedia.com/terms?lang=en) and [robots.txt](https://www.tokopedia.com/robots.txt).
2. **Rate Limiting**: Built-in delays help avoid overwhelming the server.
3. **Error Monitoring**: Check console output for warnings and errors.
4. **Data Validation**: Verify scraped data quality before using it downstream.

## Limitations and Notes

- **Website Structure May Change**: If scraping fails, inspect and update selectors in the collector files under `core/`.
- **Rate Limiting**: Excessive scraping may result in blocks or CAPTCHAs. Adjust delays and limits as needed.

## Troubleshooting

### Common Issues

- **No products found**

  This message means the scraper could not find any products on the search results page. Possible solutions:

  - **Try again:** Sometimes network issues or temporary website changes can cause this. Simply rerun the script.
  - **Check your search URL:** Make sure the URLs in `config/settings.py` are valid and point to a real Tokopedia search results page.
  - **Update selectors:** If Tokopedia has changed its website layout, you may need to update the CSS selectors in the collector files under `core/`.
  - **Disable headless mode:** Set `DEFAULT_HEADLESS = False` in `config/config.py` to debug visually and see what the browser is displaying.
  - **Check your internet connection:** Ensure you have a stable connection.

- **ChromeDriver Not Found**

  Ensure these libraries are installed:

  ```bash
  pip install chromedriver-autoinstaller undetected-chromedriver webdriver-manager
  ```

- **Selectors Not Working**

  Website layout may have changed. Update CSS selectors in the collector files under `core/` by inspecting the current HTML.

- **Products Not Loading**

  - Run in non-headless mode (`Config.DEFAULT_HEADLESS = False`) to debug visually.
  - Check your internet connection and try again.

- **Memory Issues with Large Datasets**

  - Reduce `MAX_PRODUCTS` or `MAX_PAGES` in `config/settings.py`.
  - Reduce `SEARCH_URLS` in `config/settings.py`.
  - Use `cleanup_old_files()` in data manager to remove old outputs periodically.

## References & Documentation

### Core Libraries

- [Selenium with Python](https://selenium-python.readthedocs.io/) - Official Selenium Python bindings documentation
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - HTML parsing library documentation
- [Pandas](https://pandas.pydata.org/docs/) - Data manipulation and CSV handling

### WebDriver Tools

- [ChromeDriver](https://chromedriver.chromium.org/) - Official ChromeDriver documentation
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - Anti-detection ChromeDriver
- [selenium-stealth](https://github.com/diprajpatra/selenium-stealth) - Stealth automation helper

### Web Scraping Best Practices

- [Robots.txt Protocol](https://www.robotstxt.org/robotstxt.html) - Web crawling guidelines
- [Selenium WebDriver Documentation](https://www.selenium.dev/documentation/webdriver/) - Complete WebDriver guide

### Python Virtual Environments

- [venv documentation](https://docs.python.org/3/library/venv.html) - Python's built-in virtual environment
- [pip documentation](https://pip.pypa.io/en/stable/) - Python package installer

### Additional Resources

- [Chrome DevTools Documentation](https://developer.chrome.com/docs/devtools/) - For inspecting web elements
- [XPath Syntax](https://www.w3schools.com/xml/xpath_syntax.asp) - XPath selectors reference
- [CSS Selectors Reference](https://www.w3schools.com/cssref/css_selectors.asp) - CSS selectors guide

## Disclaimer

This tool is for educational and research purposes only. Always respect website terms of service and implement appropriate rate limiting. The author is not responsible for any misuse of this software.

## License

This project is open source under the terms specified in the [LICENSE](LICENSE) file.
