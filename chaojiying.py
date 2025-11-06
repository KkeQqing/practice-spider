import hashlib

import requests
import json

class Chaojiying_Client:
    def __init__(self, username, password, soft_id):
        self.username = username
        self.password = password
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型，参考 https://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('captcha.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php',
                          data=params, files=files, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """报错返分"""
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php',
                          data=params, headers=self.headers)
        return r.json()


# ===== 使用示例 =====
if __name__ == '__main__':
    # 账号信息
    password = 'ee2px46z'
    pass2 = hashlib.md5(password.encode('utf-8')).hexdigest()
    USERNAME = '258469'
    PASSWORD = pass2
    SOFT_ID = '974315'

    # 初始化客户端
    chaojiying = Chaojiying_Client(USERNAME, PASSWORD, SOFT_ID)

    # 读取验证码图片
    with open('captcha.jpg', 'rb') as f:
        img_bytes = f.read()

    # 识别验证码（1902 表示 4位英文数字混合验证码，具体类型见官网价格表）
    result = chaojiying.PostPic(img_bytes, 1902)

    print("识别结果:", result)

    if result['err_no'] == 0:
        print("验证码内容:", result['pic_str'])
        # 如果识别错误，可调用报错接口（需传入 pic_id）
        # chaojiying.ReportError(result['pic_id'])
    else:
        print("识别失败，错误信息:", result['err_str'])