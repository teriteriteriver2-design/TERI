import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_login():
    print("Starting Selenium...")
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://www.speedauction.co.kr/mem/login.php")
        print("Page title:", driver.title)
        
        # Wait for user input field
        wait = WebDriverWait(driver, 10)
        try:
            id_input = wait.until(EC.presence_of_element_located((By.NAME, "mem_id")))
            pw_input = driver.find_element(By.NAME, "mem_pass")
        except:
            print("Could not find standard mem_id/mem_pass fields. Attempting alternative selectors.")
            id_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
            pw_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            
        print("Found input fields.")
        id_input.send_keys("teri-1023")
        pw_input.send_keys("fuck85213")
        
        pw_input.submit()
        print("Form submitted. Waiting for redirect...")
        time.sleep(3)
        
        print("New URL:", driver.current_url)
        print("New title:", driver.title)
        
        # Check if logged in successfully by looking for logout button or username
        page_source = driver.page_source
        if "로그아웃" in page_source or "logout" in page_source.lower() or "마이페이지" in page_source:
            print("LOGIN SUCCESSFUL!")
        else:
            print("LOGIN FAILED. Check credentials or CAPTCHA.")
            
        driver.quit()
    except Exception as e:
        print("Error during Selenium test:", str(e))

if __name__ == "__main__":
    test_login()
