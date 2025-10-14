import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

# 定义常量 BROWSER_HEADERS  浏览器请求头
BROWSER_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def safe_get(url,
             headers=None,
             timeout=10,
             max_retries=2,
             backoff_factor=1,
             return_json=False):
    """
    安全地发送 GET 请求，自动处理异常、重试和超时。

    参数:
        url (str): 目标 URL
        headers (dict, optional): 请求头，默认包含 User-Agent
        timeout (int or tuple): 超时时间（秒），默认 10
        max_retries (int): 失败后最大重试次数，默认 2 次（共尝试 3 次）
        backoff_factor (float): 重试间隔指数退避因子，默认 1 秒
        return_json (bool): 是否尝试返回 JSON 数据（若响应是 JSON）

    返回:
        dict: 包含以下字段
            - success (bool): 是否成功
            - response (requests.Response or None): 响应对象（成功时）
            - data (str or dict or None): 响应文本或 JSON 数据
            - error (str or None): 错误信息（失败时）
    """

    # 默认 User-Agent（模拟 Chrome）
    default_headers = BROWSER_HEADERS
    if headers:
        default_headers.update(headers)
    headers = default_headers

    # 配置重试策略：对 5xx 和连接错误重试
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],  # 服务器错误时重试
        allowed_methods=["HEAD", "GET", "OPTIONS"]  # 只对幂等方法重试
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        response = session.get(url, headers=headers, timeout=timeout)

        # 如果状态码不是 2xx，仍视为“成功请求”（因为拿到了响应）
        # 如需严格检查，可调用 response.raise_for_status()

        data = None
        if return_json:
            try:
                data = response.json()
            except ValueError:
                return {
                    'success': False,
                    'response': None,
                    'data': None,
                    'error': '响应不是有效的 JSON'
                }
        else:
            data = response.text

        return {
            'success': True,
            'response': response,
            'data': data,
            'error': None
        }

    except requests.exceptions.Timeout:
        error_msg = f"请求超时（超过 {timeout} 秒）"
    except requests.exceptions.ConnectionError:
        error_msg = "网络连接错误（DNS失败、拒绝连接等）"
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP错误: {e}"
    except requests.exceptions.TooManyRedirects:
        error_msg = "重定向次数过多"
    except requests.exceptions.RequestException as e:
        error_msg = f"未知请求错误: {e}"
    except Exception as e:
        error_msg = f"未预期的错误: {e}"

    return {
        'success': False,
        'response': None,
        'data': None,
        'error': error_msg
    }