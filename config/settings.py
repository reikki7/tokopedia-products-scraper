# Search result URLs - can be customized per run
SEARCH_URLS = [
    "https://www.tokopedia.com/search?condition=1&navsource=&rt=4%2C5&search_id=2025060121103634ED066DF378EF24BAT1&shop_tier=3%232&srp_component_id=04.06.00.00&srp_page_id=&srp_page_title=&st=&q=polo%20pria",
    "https://www.tokopedia.com/search?condition=1&navsource=home&rt=4%2C5&search_id=2025060111193894F6D7E04A4D4512DOPF&shop_tier=2&source=universe&srp_component_id=04.06.00.00&st=product&q=polo%20shirt%20wanita",
    # "https://www.tokopedia.com/search?navsource=home&q=case+custom+hp&source=universe&st=product"
    # Add more URLs as needed
]

# Product scraping limits - whichever reaches maximum first will stop the process
MAX_PRODUCTS = 5  # Maximum products to scrape per search
MAX_PAGES = 2     # Maximum search pages to scrape per search

# Review scraping limit
MAX_REVIEW_PAGES = 2  # Maximum review pages to scrape per product