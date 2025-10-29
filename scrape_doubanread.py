import requests
from bs4 import BeautifulSoup
from safe_requests import safe_get, BROWSER_HEADERS

for star_num in range(0, 250, 25):
    response = safe_get(f"https://book.douban.com/top250?start={star_num}")
    if response["success"]:
        soup = BeautifulSoup(response["data"], "html.parser")
        # 使用 CSS 选择器：class 为 pl2 的 div 下的 a 标签
        a_tags = soup.select('div.pl2 a')
        book_names = []
        for a_tag in a_tags:
            book_name = a_tag.get_text(strip=True)
            book_names.append(book_name)
        for book_name in book_names:
            print(book_name)
    else:
        print("请求失败:", response["error"])


