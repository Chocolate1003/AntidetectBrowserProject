import os
import json
import time
import random
import logging
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

API_KEY = 'YOUR_2CAPTCHA_API_KEY'
BATCH_SIZE = 2  # Number of configs to process per batch
CTR_LOWER = 0.01  # Minimum CTR for clicking ads
CTR_UPPER = 0.019  # Maximum CTR for clicking ads

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

# Simulate human behavior with random scrolls and movements
def simulate_human_behavior(driver):
    for _ in range(random.randint(3, 5)):
        scroll_amount = random.randint(300, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(3, 7))

    width = driver.execute_script("return window.innerWidth")
    height = driver.execute_script("return window.innerHeight")
    ActionChains(driver).move_by_offset(random.randint(0, width), random.randint(0, height)).perform()
    time.sleep(random.uniform(2, 4))

# Visit website and spend time on it
def visit_website(driver, website):
    print(f"Visiting website: {website}")
    driver.get(website)
    simulate_human_behavior(driver)
    
    # Random time on website
    time_spent = random.choice([5 * 60, 7 * 60, 10 * 60, 12 * 60])
    print(f"Spending {time_spent // 60} minutes on the website.")
    time.sleep(time_spent)

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

    for website in websites:
        visit_website(driver, website)
        click_ads(driver, ad_selectors)

        # Log interaction in the config
        interaction = {
            "profile_name": profile_name,
            "website": website,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }
        if "interactions" not in config:
            config["interactions"] = []
        config["interactions"].append(interaction)

        # Save interactions and cookies back to the config file
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
                interact_with_websites(
                    driver,
                    config.get("websites", []),
                    config.get("ad_xpaths", []),
                    config.get("profile_name", ""),
                    config,
                    config_path
                )
                driver.quit()
                
        # Wait between batches
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
