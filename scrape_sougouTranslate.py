import requests

from safe_requests import safe_post

url_sougouTranslate = "https://fanyi.sogou.com/reventondc/suggV3"
s = input("请输入要翻译的文字：")
data ={
    "text": s,
    "from": "auto",
    "to": "zh-CHS",
    "client": "web",
    "uuid": "d965db3d-3c40-436e-95b7-b8d2283b28c3",
    "pid":"sogou-dict-vr",
    "addSugg":"on"
}
res_sougouTranslate = safe_post(url_sougouTranslate, data=data, return_json=True)
if res_sougouTranslate['success']:
    result = res_sougouTranslate['data']
    if 'sugg' in result:
        sugg_list = result['sugg']
        print("翻译建议：")
        for item in sugg_list:
            print(f"{item['k']}: {item['v']}")
    else:
        print("响应中没有 'sugg' 字段")
else:
    print("请求失败:", res_sougouTranslate['error'])
