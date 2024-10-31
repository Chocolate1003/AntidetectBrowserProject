import os
import json
import time
import random
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.opera import OperaDriverManager
from webdriver_manager.utils import ChromeType

API_KEY = 'YOUR_2CAPTCHA_API_KEY'
BATCH_SIZE = 2
CTR_LOWER = 0.01
CTR_UPPER = 0.019

logging.basicConfig(
    filename='interactions_log.json',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load profile data from config file
def load_config(config_path):
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except IOError as e:
        print(f"Error loading config file {config_path}: {e}")
        return {}

# Save updated config data back to the file
def save_config(config, config_path):
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    except IOError as e:
        print(f"Error saving config file {config_path}: {e}")

# Set up the WebDriver with proxy and user agent from config
def setup_driver(config):
    browser = config.get("browser", "chrome").lower()  # Default to Chrome
    options = None
    driver = None

    try:
        # Set up options and drivers for each browser
        if browser == "chrome":
            options = webdriver.ChromeOptions()
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        elif browser == "firefox":
            options = webdriver.FirefoxOptions()
            if config.get("proxy"):
                options.set_preference("network.proxy.type", 1)
                options.set_preference("network.proxy.http", config["proxy"])
            if config.get("user_agent"):
                options.set_preference("general.useragent.override", config["user_agent"])
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

        elif browser == "edge":
            options = webdriver.EdgeOptions()
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

        elif browser == "opera":
            options = webdriver.ChromeOptions()
            options.binary_location = OperaDriverManager().install()
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            driver = webdriver.Chrome(options=options, chrome_options=options)

        elif browser == "brave":
            options = webdriver.ChromeOptions()
            options.binary_location = ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()), options=options)

        elif browser == "yandex":
            options = webdriver.ChromeOptions()
            options.binary_location = "/path/to/yandex/browser"  # Update with Yandex's actual path
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    except Exception as e:
        print(f"Error setting up WebDriver for {browser}: {e}")
        driver = None

    return driver

# Simulate full page scroll, from top to bottom and back up
def full_page_scroll(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(1, 3))
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(random.uniform(1, 3))

# Simulate human behavior with random scrolls and movements
def simulate_human_behavior(driver):
    full_page_scroll(driver)

# Visit the main page and some random subpages of each website
def visit_website(driver, website):
    print(f"Visiting website: {website}")
    driver.get(website)
    simulate_human_behavior(driver)
    time.sleep(random.randint(5, 15))

    links = driver.find_elements(By.TAG_NAME, 'a')
    random.shuffle(links)
    links_to_visit = links[:3]

    for link in links_to_visit:
        try:
            link.click()
            simulate_human_behavior(driver)
            time.sleep(random.randint(5, 15))
            driver.back()
            time.sleep(2)
        except WebDriverException as e:
            print(f"Error visiting link: {e}")
            continue

# Function to visit deviceinfo.me
def visit_deviceinfo(driver):
    print("Visiting deviceinfo.me for initial device check")
    driver.get("https://deviceinfo.me")
    simulate_human_behavior(driver)
    time.sleep(random.uniform(15, 30))

# Click ads based on a CTR range
def click_ads(driver, ad_selectors):
    if random.uniform(0, 1) <= random.uniform(CTR_LOWER, CTR_UPPER):
        for selector in ad_selectors:
            ads = driver.find_elements(By.XPATH, selector)
            if ads:
                for ad in ads:
                    try:
                        ad.click()
                        print("Clicked on an ad.")
                        time.sleep(random.uniform(3, 7))
                    except Exception as e:
                        print(f"Error clicking ad: {e}")

# Click random elements on the page in addition to ads
def click_random_elements(driver):
    elements = driver.find_elements(By.XPATH, "//*")
    if elements:
        random_elements = random.sample(elements, min(len(elements), 3))
        for element in random_elements:
            try:
                element.click()
                print("Clicked on a random element.")
                time.sleep(random.uniform(2, 5))
            except Exception as e:
                print(f"Error clicking random element: {e}")

# Load cookies from the config data
def load_cookies(driver, config):
    cookies = config.get("cookies", [])
    for cookie in cookies:
        driver.add_cookie(cookie)
    print("Loaded cookies from config.")

# Save cookies to the config data
def save_cookies(driver, config, config_path):
    config["cookies"] = driver.get_cookies()
    save_config(config, config_path)
    print("Saved cookies to config.")

# Main function to interact with websites and click ads
def interact_with_websites(driver, websites, ad_selectors, profile_name, config, config_path):
    load_cookies(driver, config)
    
    visit_deviceinfo(driver)

    for website in websites:
        visit_website(driver, website)
        click_ads(driver, ad_selectors)
        click_random_elements(driver)

        interaction = {
            "profile_name": profile_name,
            "website": website,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }
        if "interactions" not in config:
            config["interactions"] = []
        config["interactions"].append(interaction)

        save_cookies(driver, config, config_path)

# Process profiles in batches
def process_profiles_in_batches(config_files):
    for i in range(0, len(config_files), BATCH_SIZE):
        batch_files = config_files[i:i + BATCH_SIZE]
        
        for config_path in batch_files:
            profile_path = os.path.dirname(config_path)
            config = load_config(config_path)
            
            driver = setup_driver(config)
            if driver:
                try:
                    interact_with_websites(
                        driver,
                        config.get("websites", []),
                        config.get("ad_xpaths", []),
                        config.get("profile_name", ""),
                        config,
                        config_path
                    )
                finally:
                    driver.quit()
                
        time.sleep(5)

# Main entry point
def main():
    config_dir = Path("configs")
    config_files = list(config_dir.glob("*.json"))

    if config_files:
        process_profiles_in_batches(config_files)
    else:
        print("No config files found.")

if __name__ == "__main__":
    main()
