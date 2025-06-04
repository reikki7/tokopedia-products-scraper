from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config.config import CHROME_OPTIONS

class BaseCollector:
    """
    Base class that sets up and tears down the Selenium Chrome driver,
    and provides common utilities (scrolling, click helpers, etc.).
    """

    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")

        if CHROME_OPTIONS.get("no_sandbox"):
            self.options.add_argument("--no-sandbox")
        if CHROME_OPTIONS.get("disable_dev_shm_usage"):
            self.options.add_argument("--disable-dev-shm-usage")
        if CHROME_OPTIONS.get("disable_blink_features"):
            self.options.add_argument(f"--disable-blink-features={CHROME_OPTIONS['disable_blink_features']}")
        if CHROME_OPTIONS.get("user_agent"):
            self.options.add_argument(f"--user-agent={CHROME_OPTIONS['user_agent']}")

        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--enable-unsafe-webgl")
        self.options.add_argument("--enable-unsafe-swiftshader")
        self.options.add_argument("--disable-background-timer-throttling")
        self.options.add_argument("--disable-backgrounding-occluded-windows")
        self.options.add_argument("--disable-renderer-backgrounding")
        self.options.add_argument("--disable-features=Translate")
        
        self.options.add_argument("--disable-speech-api")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-plugins")
        self.options.add_argument("--disable-sync")
        self.options.add_argument("--disable-default-apps")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-notifications")
        self.options.add_argument("--disable-application-cache")
        self.options.add_argument("--disable-component-update")
        self.options.add_argument("--disable-pinch")
        self.options.add_argument("--disable-translate")
        self.options.add_argument("--disable-webgl")
        self.options.add_argument("--disable-webgl2-compute-context")

        self.options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        self.options.add_experimental_option("useAutomationExtension", False)

        self.driver = None

    def start_driver(self):
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        return self.driver

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def scroll_page(self, duration=3):
        if not self.driver:
            return

        print("Scrolling to load more products...")

        start = 0
        end = self.driver.execute_script("return document.body.scrollHeight")
        steps = int(duration * 60)
        if steps == 0:
            steps = 1

        step_y = (end - start) / steps
        import time
        for i in range(steps):
            next_pos = start + (step_y * (i + 1))
            self.driver.execute_script(f"window.scrollTo(0, {next_pos});")
            time.sleep(duration / steps)

        print("Scroll completed")

