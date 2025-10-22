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
print(res_sougouTranslate["data"])