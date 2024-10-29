import os
import time
import random
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

INTERACTIONS_FILE = 'interactions.json'

def load_config(profile_path):
    config_file = os.path.join(profile_path, 'config.json')
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config

def visit_website(driver, website):
    print(f"Visiting website: {website}")
    driver.get(website)
    simulate_human_behavior(driver)
    
    # Randomly select a time to spend on the website (5, 7, 10, or 12 minutes)
    time_options = [5 * 60, 7 * 60, 10 * 60, 12 * 60]  # Convert minutes to seconds
    time_spent = random.choice(time_options)
    print(f"Spending {time_spent // 60} minutes on the website.")
    time.sleep(time_spent)

def click_ads(driver, ad_selectors):
    for selector in ad_selectors:
        ads = driver.find_elements(By.XPATH, selector)
        if ads:
            for ad in ads:
                try:
                    ad.click()  # Click on the ad
                    print("Clicked on an ad.")
                    time.sleep(random.uniform(3, 7))  # Simulate time spent on the ad
                except Exception as e:
                    print(f"Error clicking ad: {e}")

def stream_content(driver, platform):
    try:
        play_button = driver.find_element(By.XPATH, platform['selectors']['play_button'])
        play_button.click()
        print(f"Started streaming on {platform['name']}.")
        
        # Simulate watching for a random duration
        time.sleep(random.uniform(15, 45))  # Simulate watching for 15 to 45 seconds
    except Exception as e:
        print(f"Error streaming content on {platform['name']}: {e}")

def interact_with_platforms(driver, platforms):
    for platform in platforms:
        stream_content(driver, platform)  # Stream content on the platform
        print(f"Interacted with platform: {platform['name']}")

def simulate_human_behavior(driver):
    # Scroll down and up slowly
    scroll_times = random.randint(3, 5)
    for _ in range(scroll_times):
        scroll_amount = random.randint(300, 800)  # Random scroll amount
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(3, 7))  # Adjusted to 3 to 7 seconds

    # Move the mouse randomly within the viewport
    width = driver.execute_script("return window.innerWidth")
    height = driver.execute_script("return window.innerHeight")
    random_x = random.randint(0, width)
    random_y = random.randint(0, height)
    ActionChains(driver).move_by_offset(random_x, random_y).perform()
    time.sleep(random.uniform(2, 4))  # Adjusted to 2 to 4 seconds

def detect_and_solve_captcha(driver, api_key):
    # Placeholder for CAPTCHA detection and solving logic
    pass

def record_impression(profile_name, website):
    # Create the impression record
    impression = {
        "profile_name": profile_name,
        "website": website,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    }

    # Load existing interactions or create a new list
    interactions = []
    if os.path.exists(INTERACTIONS_FILE):
        with open(INTERACTIONS_FILE, 'r') as f:
            try:
                interactions = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: {INTERACTIONS_FILE} is corrupted. Starting a new log.")

    # Append the new impression
    interactions.append(impression)

    # Save the updated interactions
    with open(INTERACTIONS_FILE, 'w') as f:
        json.dump(interactions, f, indent=4)
    print(f"Impression recorded for Profile: {profile_name}, Website: {website}")

def load_cookies(driver, profile_name):
    # Implement logic to load cookies from cookies.json for the profile
    cookies_file = os.path.join("Profiles", profile_name, "cookies.json")
    if os.path.exists(cookies_file):
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print(f"Loaded cookies for profile: {profile_name}")

def save_cookies(driver, profile_name):
    # Implement logic to save cookies to cookies.json for the profile
    cookies_file = os.path.join("Profiles", profile_name, "cookies.json")
    cookies = driver.get_cookies()
    with open(cookies_file, 'w') as f:
        json.dump(cookies, f, indent=4)
    print(f"Saved cookies for profile: {profile_name}")

def interact_with_websites(driver, websites, profile_name, config):
    load_cookies(driver, profile_name)  # Load cookies before interacting

    for website in websites:
        visit_website(driver, website)
        detect_and_solve_captcha(driver, config['api_key'])  # Detect and solve CAPTCHA if needed
        click_ads(driver, config.get('ad_xpaths', []))  # Click specified ads from config
        record_impression(profile_name, website)  # Record the impression

        interact_with_platforms(driver, config['platforms'])  # Stream content on platforms
        
        save_cookies(driver, profile_name)  # Save cookies after interaction

def click_batched(profiles):
    for profile in profiles:
        print(f"Processing profile: {profile}") 
        profile_path = os.path.join("Profiles", profile)  # Adjust path to match your structure
        config = load_config(profile_path)  # Load configuration for the current profile
        websites = config.get("websites", [])  # Get websites from the profile config

        driver = setup_driver(config)  # Set up the driver for the current profile
        
        if driver is None:
            print(f"Skipping profile {profile} due to driver setup failure.")
            continue

        # Interact with the websites
        interact_with_websites(driver, websites, profile, config)

        driver.quit()  # Ensure the driver is closed after processing

        # Sleep for a random duration between batches
        time.sleep(random.uniform(5, 15))  # Adjust this duration to fit your needs
