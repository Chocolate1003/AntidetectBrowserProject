import json
import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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

def setup_driver(config):
    options = webdriver.ChromeOptions()
    if config.get("proxy"):
        options.add_argument(f'--proxy-server={config["proxy"]}')
    if config.get("user_agent"):
        options.add_argument(f'user-agent={config["user_agent"]}')
    
    try:
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    except WebDriverException as e:
        print(f"Error setting up WebDriver: {e}")
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
        
        driver = setup_driver(config)
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
