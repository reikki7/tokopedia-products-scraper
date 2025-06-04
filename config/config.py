# Configurations for scraping
DEFAULT_HEADLESS = True  # Run browser in headless mode (browser will not be visible if set to True)
SCROLL_DURATION = 3      # Duration to scroll down the page
PRODUCT_DELAY = 0.5      # Delay between scraping products

# Logging settings
VERBOSE_LOGGING = True

# Test Search URL
TEST_SEARCH_URL = (
    "https://www.tokopedia.com/search?condition=1&fcity=174%2C175%2C176%2C177%2C178%2C179&navsource=&preorder=false&rt=4%2C5&search_id=2025060203323434ED066DF378EF3BDVGD&shop_tier=2&srp_component_id=04.06.00.00&srp_page_id=&srp_page_title=&st=&q=asus"
)

# Chrome driver options
CHROME_OPTIONS = {
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
    'disable_blink_features': 'AutomationControlled',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
