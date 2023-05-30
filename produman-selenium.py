import time, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

options = webdriver.ChromeOptions()

user_agent = UserAgent()
random_user_agent = user_agent.random
proxy = 'socks5://f0YSJS:20NoiEo3TH@46.8.110.159:1051'

options.add_argument(f'user-agent={user_agent}')
options.add_argument("--no-sandbox")
options.add_argument('--disable-javascript')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,700")
# options.add_argument(f'--proxy-server={proxy}')
options.add_argument("--headless=new")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

driver.get("https://kassa.produman.org/login")

wait = WebDriverWait(driver, 10)
email = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputIdentity"]')))
email.send_keys("vladakulikova@gmail.com")

password = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="inputPassword"]')))
password.send_keys("r4frvzf5aw")

wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="loginForm"]/button'))).click()

time.sleep(10)

cookies = driver.get_cookies()

d = {"cookie_list": []}

for cookie in cookies:
    d['cookie_list'].append({'domain': cookie['domain'],'name': cookie['name'], 'path': cookie['path'], 'value': cookie['value']})
with open ('cookies_produman.json', 'w+') as f:
    json.dump(d,f, indent=2)

# print(d)