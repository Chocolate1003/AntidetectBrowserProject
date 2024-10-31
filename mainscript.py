import json
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.opera import OperaDriverManager
from selenium.common.exceptions import WebDriverException
from action import visit_website, click_ads, detect_and_solve_captcha, record_impression, load_cookies, save_cookies

# Add your 2Captcha API key
API_KEY = 'YOUR_2CAPTCHA_API_KEY'

# Set up logging
logging.basicConfig(
    filename='interactions.json',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config(profile_path):
    config_path = os.path.join(profile_path, "config.json")
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except IOError as e:
        print(f"Error loading config file {config_path}: {e}")
        return {}

def get_browser_driver(config):
    options = None
    browser_info = config["device_info"]["browser_version"].split(" ")
    browser_name = browser_info[0].lower()
    browser_version = browser_info[1] if len(browser_info) > 1 else None

    try:
        if browser_name == "chrome":
            options = webdriver.ChromeOptions()
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager(version=browser_version).install()), options=options)

        elif browser_name == "firefox":
            options = webdriver.FirefoxOptions()
            if config.get("proxy"):
                options.set_preference("network.proxy.http", config["proxy"])
            if config.get("user_agent"):
                options.set_preference("general.useragent.override", config["user_agent"])
            return webdriver.Firefox(service=FirefoxService(GeckoDriverManager(version=browser_version).install()), options=options)

        elif browser_name == "edge":
            options = webdriver.EdgeOptions()
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            return webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager(version=browser_version).install()), options=options)

        elif browser_name == "opera":
            options = webdriver.ChromeOptions()  # Opera uses ChromeOptions
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            return webdriver.Opera(service=ChromeService(OperaDriverManager(version=browser_version).install()), options=options)

        # Placeholder for Yandex, UC Browser, and Brave
        elif browser_name == "brave":
            options = webdriver.ChromeOptions()  # Brave also uses ChromeOptions
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager(version=browser_version).install()), options=options)

        elif browser_name == "yandex":
            options = webdriver.ChromeOptions()  # Yandex uses ChromeOptions
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager(version=browser_version).install()), options=options)

        elif browser_name == "uc":
            options = webdriver.ChromeOptions()  # UC Browser uses ChromeOptions
            if config.get("proxy"):
                options.add_argument(f'--proxy-server={config["proxy"]}')
            if config.get("user_agent"):
                options.add_argument(f'user-agent={config["user_agent"]}')
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager(version=browser_version).install()), options=options)

        print(f"Unsupported browser: {browser_name}. Please check config.json.")
    except WebDriverException as e:
        print(f"Error setting up {browser_name} WebDriver: {e}")

    return None

def interact_with_websites(driver, websites, profile_name):
    for website in websites:
        visit_website(driver, website)
        detect_and_solve_captcha(driver, API_KEY)
        click_ads(driver)
        record_impression(profile_name, website)

def click_batched(profiles):
    for profile in profiles:
        profile_path = os.path.join("Profiles", profile)
        config = load_config(profile_path)
        websites = ["https://deviceinfo.me"] + config.get("websites", [])
        
        driver = get_browser_driver(config)
        if driver is None:
            continue
        
        load_cookies(driver, profile)
        
        try:
            interact_with_websites(driver, websites, profile)
        finally:
            save_cookies(driver, profile)
            driver.quit()

def main():
    profiles = os.listdir("Profiles")
    click_batched(profiles)

if __name__ == "__main__":
    main()
