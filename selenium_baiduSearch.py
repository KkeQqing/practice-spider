import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import dashscope  # 阿里云SDK
from dashscope import Generation

# 阿里云 API 密钥
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")  # 获取阿里云 API 密钥（环境变量形式）

# 阿里云 QWEN 模型
def summarize_with_qwen(titles):
    prompt = (
        "以下是关于“Selenium 爬虫”的一些搜索结果标题，请用中文总结这些标题反映的核心内容、常见问题或技术趋势，"
        "要求简洁、有条理，不超过150字：\n\n" + "\n".join(f"- {title}" for title in titles)
    )

    try:
        response = Generation.call(
            model="qwen-max",  # 也可以用 qwen-plus、qwen-turbo
            prompt=prompt
        )
        if response.status_code == 200:
            return response.output.text.strip()
        else:
            print("❌ AI 调用失败:", response)
            return "AI 总结失败"
    except Exception as e:
        print("❌ 调用异常:", e)
        return "AI 调用异常"

# === 配置 Chrome 选项 ===
chrome_options = Options()
# 禁用自动化标志（重要！）
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# === 启动浏览器 ===
chromedriver_path = r"D:\PythonProject\practice-spider\chromedriver.exe"
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# 绕过 webdriver 检测（关键 JS）
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

titles_list = []  # 用于存储标题

try:
    driver.get("https://www.baidu.com")
    print("当前 URL:", driver.current_url)

    wait = WebDriverWait(driver, 15)

    try:
        # 等待搜索框可见且可交互
        search_box = wait.until(EC.visibility_of_element_located((By.ID, "chat-textarea")))
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
            try:
                title_span = result.find_element(By.XPATH, ".//span[@class='tts-b-hl']")
                title_text = title_span.text
                link_url = result.get_attribute("href")

                print(f"标题: {title_text}")
                print(f"链接: {link_url}")
                print("-" * 50)

                title_text_clean = result.text.strip()
                if title_text_clean:
                    titles_list.append(title_text_clean)
            except NoSuchElementException:
                # 跳过无法解析的单个结果
                continue

    except (TimeoutException, NoSuchElementException) as e:
        print("⚠️ 页面交互或元素定位失败:", e)

    if titles_list:
        print("\n🧠 正在调用 AI 进行总结...")
        summary = summarize_with_qwen(titles_list)
        print("\n✅ AI 总结结果：")
        print(summary)
    else:
        print("⚠️ 未获取到任何标题，无法总结。")

finally:
    driver.quit()