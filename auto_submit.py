from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import os
from dotenv import load_dotenv
load_dotenv()
import time
import requests

username = os.environ.get("USC_USERNAME", "")
print(username)
password = os.environ.get("USC_PASSWORD", "")
term = os.environ.get("USC_TERM", "Fall 2026")
browser = os.environ.get("USC_BROWSER", "Chrome")
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "csci599")
NTFY_URL = os.environ.get("NTFY_URL", f"https://ntfy.sh/{NTFY_TOPIC}")

def make_driver(browser_name: str):
    if browser_name == "Chrome":
        opts = webdriver.ChromeOptions()
        return webdriver.Chrome(options=opts)
    if browser_name == "Edge":
        opts = webdriver.EdgeOptions()
        return webdriver.Edge(options=opts)
    if browser_name == "IE":
        opts = webdriver.IEOptions()
        return webdriver.Ie(options=opts)
    if browser_name == "Firefox":
        opts = webdriver.FirefoxOptions()
        return webdriver.Firefox(options=opts)
    return webdriver.Safari()

def main():
    driver = make_driver(browser)
    wait = WebDriverWait(driver, 180)
    driver.get("https://my.usc.edu")
    wait.until(EC.presence_of_element_located((By.NAME, "j_username"))).send_keys(username)
    wait.until(EC.presence_of_element_located((By.NAME, "j_password"))).send_keys(password)
    driver.find_element(By.CLASS_NAME, "button--primary").click()
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "button"))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[data-slug="registration"]'))).click()
    wait.until(EC.number_of_windows_to_be(2))
    for window_handle in driver.window_handles:
        if window_handle != driver.current_window_handle:
            driver.switch_to.window(window_handle)
            break
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, term))).click()

    while True:
        wait.until(EC.element_to_be_clickable((By.ID, "mItReg"))).click()
        wait.until(EC.element_to_be_clickable((By.ID, "SubmitButton"))).click()
        try:
            wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h3"), "Registration"))
            response = driver.find_element(By.CSS_SELECTOR, ".content-wrapper-regconfirm").text
            if ("Failed" in response):
                print("[Failed] Waiting 40s until next try")
                time.sleep(40)
                continue
            elif ("successful" in response):
                print("Success")
                # 发送 ntfy 推送
                try:
                    r = requests.post(NTFY_URL, data=f"CSCI599选课成功 (user: {username})", timeout=10)
                    if r.status_code // 100 == 2:
                        print("ntfy push sent")
                    else:
                        print("ntfy push failed", r.status_code, r.text)
                except Exception as e:
                    print("ntfy push error:", e)
                break
            else:
                driver.refresh()
                print("[Retry] Waiting 40s until next try")
                time.sleep(40)
        except TimeoutException:
            driver.refresh()
            print("[Timeout] Waiting 40s until next try")
            time.sleep(40)
    driver.quit()

if __name__ == '__main__':
    main()
