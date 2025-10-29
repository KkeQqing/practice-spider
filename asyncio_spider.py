import asyncio
import aiohttp

async def fetch(session, url):
    try:
        async with session.get(url) as response:
            html = await response.text()
            print(f"✅ Fetched {url[:30]}... | Status: {response.status}")
            return html
    except Exception as e:
        print(f"❌ Error fetching {url}: {e}")
        return None

async def main():
    urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1',
        'https://httpbin.org/delay/1',
        'https://example.com',
        'https://python.org'
    ]

    # 创建一个异步 HTTP 会话（连接池复用）
    async with aiohttp.ClientSession() as session:
        # 并发执行所有请求
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# 运行异步主函数
if __name__ == "__main__":
    asyncio.run(main())