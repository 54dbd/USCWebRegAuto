from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
from dotenv import load_dotenv
load_dotenv()
import requests
import time

username = os.environ.get("USC_USERNAME", "")
password = os.environ.get("USC_PASSWORD", "")
term = os.environ.get("USC_TERM", "Fall 2026")
browser = os.environ.get("USC_BROWSER", "Chrome")

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "csci599")
NTFY_URL = os.environ.get("NTFY_URL", f"https://ntfy.sh/{NTFY_TOPIC}")

def send_ntfy(message: str):
    try:
        r = requests.post(NTFY_URL, data=message, timeout=10)
        if r.status_code // 100 == 2:
            print("ntfy push sent")
        else:
            print("ntfy push failed", r.status_code, r.text)
    except Exception as e:
        print("ntfy push error:", e)

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
    wait.until(EC.element_to_be_clickable((By.ID, "mItReg"))).click()
    # 检查循环：优先在表格单元格中查找 'closed'，若存在则每 5 分钟重试一次；如果消失则发送 ntfy
    while True:
        time.sleep(2)  # 等待动态内容稳定
        page_src = driver.page_source
        has_closed = False

        table_xpath = "//table//td[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'closed')] | //table//span[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'closed')]"
        try:
            table_matches = driver.find_elements(By.XPATH, table_xpath)
            for el in table_matches:
                if 'closed' in (el.text or '').lower():
                    has_closed = True
                    break
        except Exception:
            # 忽略 xpath 查找错误，回退到页面源检查
            pass

        if not has_closed:
            # 回退页面源检查（小写匹配）
            if 'closed' in page_src.lower():
                has_closed = True

        if not has_closed:
            send_ntfy(f"CSCI599可以选课了!!!!! (user: {username})")
            print("ntfy alert sent.")
            break
        else:
            try:
                driver.refresh()
            except Exception:
                pass
            print("'Closed' field still present. Retrying in 5 seconds...")
            time.sleep(5)  # 5 minutes

    if not has_closed:
        send_ntfy(f"Registration alert: 'Closed' field disappeared for term {term} (user: {username})")
        print("ntfy alert sent.")
    else:
        print("'Closed' field still present in page source. No ntfy sent.")

    driver.quit()

if __name__ == '__main__':
    main()
