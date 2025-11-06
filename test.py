import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

import dashscope
from dashscope import Generation

# === 阿里云 API 配置 ===
dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
if not dashscope_api_key:
    raise EnvironmentError("请设置环境变量 DASHSCOPE_API_KEY")
dashscope.api_key = dashscope_api_key

def summarize_with_qwen(titles):
    prompt = (
        "以下是关于“Selenium 爬虫”的一些搜索结果标题，请用中文总结这些标题反映的核心内容、常见问题或技术趋势，"
        "要求简洁、有条理，不超过150字：\n\n" + "\n".join(f"- {title}" for title in titles)
    )
    try:
        response = Generation.call(model="qwen-max", prompt=prompt)
        if response.status_code == 200:
            return response.output.text.strip()
        else:
            print("❌ AI 调用失败:", response)
            return "AI 总结失败"
    except Exception as e:
        print("❌ 调用异常:", e)
        return "AI 调用异常"

# === Selenium 配置 ===
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
# chrome_options.add_argument("--headless=new")  # 调试时建议关闭 headless

chromedriver_path = r"D:\PythonProject\practice-spider\chromedriver.exe"
service = Service(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

titles_list = []

try:
    driver.get("https://www.baidu.com")  # ←←← 请替换为你实际的目标 URL
    print("当前 URL:", driver.current_url)

    wait = WebDriverWait(driver, 15)

    # === 第一次搜索 ===
    search_box = wait.until(EC.visibility_of_element_located((By.ID, "chat-textarea")))
    driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
    search_box.send_keys("Selenium 爬虫")

    search_button = wait.until(EC.element_to_be_clickable((By.ID, "chat-submit-button")))
    search_button.click()

    # 等待首次结果加载（假设有一个结果容器）
    wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'sc-link')]")))

    # === 开始翻页（共5页）===
    for page in range(1, 6):
        print(f"\n🔍 正在处理第 {page} 页...")

        # 等待当前页结果稳定
        try:
            wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'sc-link')]")))
        except TimeoutException:
            print("⚠️ 当前页结果加载超时")
            break

        # 提取当前页所有标题
        results = driver.find_elements(By.XPATH, "//a[contains(@class, 'sc-link') and @href]")
        current_page_titles = []
        for result in results:
            try:
                title_span = result.find_element(By.XPATH, ".//span[@class='tts-b-hl']")
                title_text = title_span.text.strip()
                if title_text and title_text not in titles_list:
                    current_page_titles.append(title_text)
                    titles_list.append(title_text)
            except (NoSuchElementException, StaleElementReferenceException):
                continue  # 跳过无法解析的项

        print(f"✅ 第 {page} 页获取 {len(current_page_titles)} 个新标题")

        # === 尝试点击“下一页”（第5页不点）===
        if page < 5:
            try:
                # ←←← 请根据实际页面修改下一页按钮的定位方式！
                next_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'n') and .//span[contains(text(), '下一页')]]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                driver.execute_script("arguments[0].click();", next_button)  # 强制 JS 点击

                # 可选：等待新内容加载（比如至少出现一个新 sc-link）
                wait.until(EC.staleness_of(results[0]) if results else EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'sc-link')]")))

            except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
                print(f"⚠️ 第 {page} 页无法找到或点击‘下一页’，停止翻页。错误: {e}")
                break

    # 打印所有标题
    print("\n✅ 总计获取到", len(titles_list), "个标题")
    print("-" * 50)
    print("\n".join(titles_list))

    # === AI 总结 ===
    if titles_list:
        print("\n🧠 正在调用 AI 进行总结...")
        summary = summarize_with_qwen(titles_list)
        print("\n✅ AI 总结结果：")
        print(summary)
    else:
        print("⚠️ 未获取到任何标题，无法总结。")

finally:
    driver.quit()