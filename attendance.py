from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time


def get_attendance(username, password):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Speed & Stability Optimizations
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-features=NetworkServiceInProcess")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")

    # Path handling for both Linux and Windows
    env_chrome_path = os.getenv("CHROME_PATH")
    env_driver_path = os.getenv("CHROMEDRIVER_PATH")

    if env_chrome_path and os.path.exists(env_chrome_path):
        chrome_options.binary_location = env_chrome_path
    elif os.path.exists("/usr/bin/chromium"):
        chrome_options.binary_location = "/usr/bin/chromium"

    if env_driver_path and os.path.exists(env_driver_path):
        service = Service(executable_path=env_driver_path)
    elif os.path.exists("/usr/bin/chromedriver"):
        service = Service(executable_path="/usr/bin/chromedriver")
    else:
        # Let Selenium Manager handle finding/downloading the driver
        service = Service()

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"🌐 Navigating to login page for {username}...")
        driver.get("https://webprosindia.com/vignanvskp/default.aspx")

        print("🔑 Entering credentials...")
        driver.find_element(By.ID, "txtId2").send_keys(username)
        driver.find_element(By.ID, "txtPwd2").send_keys(password)
        
        print("🖱️ Clicking login...")
        driver.find_element(By.ID, "imgBtn2").click()

        # Small sleep for site stabilization
        time.sleep(2)

        wait = WebDriverWait(driver, 20)

        print("⏳ Waiting for 'ATTENDANCE' link...")
        attendance_link = wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "ATTENDANCE"))
        )
        print("✅ Found 'ATTENDANCE' link, clicking...")
        attendance_link.click()

        print("🖼️ Switching to iframe...")
        wait.until(
            EC.frame_to_be_available_and_switch_to_it((By.NAME, "capIframe"))
        )

        print("🔘 Selecting 'Till Now'...")
        wait.until(
            EC.element_to_be_clickable((By.ID, "radTillNow"))
        ).click()

        print("🔍 Clicking 'Show'...")
        wait.until(
            EC.element_to_be_clickable((By.ID, "btnShow"))
        ).click()

        print("📊 Waiting for tables to load...")
        wait.until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "table"))
        )

        tables = driver.find_elements(By.TAG_NAME, "table")
        table = tables[-1]

        rows = table.find_elements(By.TAG_NAME, "tr")

        result = "📊 Attendance Summary\n\n"

        # Subject rows
        for row in rows[1:-1]:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) >= 5:
                subject = cols[1].text.strip()
                percentage = cols[4].text.strip()
                result += f"{subject} → {percentage}%\n"

        # Last row (Overall)
        last_row = rows[-1]
        last_cols = last_row.find_elements(By.TAG_NAME, "td")

        if len(last_cols) >= 1:
            overall_percentage = last_cols[-1].text.strip()
            result += "\n"
            result += f"🎯 Overall Attendance → {overall_percentage}%"

        print("✅ Attendance fetch complete!")
        return result

    except Exception as e:
        print(f"❌ Error during fetch: {e}")
        return f"❌ Error: {str(e)}"

    finally:
        driver.quit()