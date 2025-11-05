import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === 配置 Chrome 选项 ===
chrome_options = Options()
# 禁用自动化标志（重要！）
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# === 启动浏览器 ===
chromedriver_path =  r"D:\PythonProject\practice-spider\chromedriver.exe"
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 绕过 webdriver 检测（关键 JS）
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    driver.get("https://www.baidu.com")
    print("当前 URL:", driver.current_url)

    wait = WebDriverWait(driver, 15)

    # 等待搜索框可见且可交互
    search_box = wait.until(EC.visibility_of_element_located((By.ID, "chat-textarea")))

    # 可选：滚动到元素
    driver.execute_script("arguments[0].scrollIntoView(true);", search_box)


    search_box.send_keys("Selenium 爬虫")

    search_button = wait.until(EC.element_to_be_clickable((By.ID, "chat-submit-button")))
    search_button.click()

    WebDriverWait(driver, 10).until(EC.title_contains("Selenium 爬虫"))
    print("✅ 页面标题:", driver.title)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "content_left"))
    )

    # === 提取所有搜索结果（标题 + 链接）===
    results = driver.find_elements(By.XPATH, "//div[@id='content_left']//a[contains(@class, 'sc-link') and @href]")

    for result in results:
        # 获取标题：找到其下的 span.tts-b-hl 或直接用 innerHTML
        title_span = result.find_element(By.XPATH, ".//span[@class='tts-b-hl']")

        # 使用 .get_attribute("innerHTML") 来保留 <em> 高亮标签
        title_html = title_span.get_attribute("innerHTML")

        # 也可以输出纯文本（忽略 HTML 标签），可以用 .text
        title_text = title_span.text

        # 获取链接
        link_url = result.get_attribute("href")

        print(f"标题: {title_text}")
        print(f"链接: {link_url}")
        print("-" * 50)


finally:
    driver.quit()