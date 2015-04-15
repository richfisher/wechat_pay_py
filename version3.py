#-*- coding: utf-8 -*-
# 微信支付V3接口

import hashlib
from random import Random
import time
import xmltodict
import requests

config = {
    'appId': '',
    'Mchid': '',
    'Key': '',
    'notify_url': ''
}

def build_sign(params):
    # 对所有传入参数按照字段名的 ASCII 码从小到大排序（字典序）
    keys = params.keys()
    keys.sort()

    array = []
    for key in keys:
        # 值为空的参数不参与签名
        if params[key] == None or params[key] == '':
            continue
        # sign不参与签名
        if key == 'sign':
            continue
        array.append("%s=%s" % (key, params[key]))
    # 使用 URL 键值对的格式拼接成字符串string1
    string1 = "&".join(array)

    # 在 string1 最后拼接上 key=Key(商户支付密钥)得到 stringSignTemp 字符串
    stringSignTemp = string1 + '&key=' + config['Key']

    # 对 stringSignTemp 进行 md5 运算，再将得到的字符串所有字符转换为大写
    m = hashlib.md5(stringSignTemp.encode('utf-8'))
    return m.hexdigest().upper()

def build_unifiedorder(params):
    base_params = {
        'appid': config['appId'],
        'mch_id': config['Mchid'],
        'nonce_str': generate_random_string(),
        'trade_type': 'JSAPI',
        'body': params['body'],
        'out_trade_no': params['out_trade_no'],
        'total_fee': params['total_fee'],
        'spbill_create_ip': params['spbill_create_ip'],
        'notify_url': config['notify_url'],
        'openid': params['openid']
    }

    base_params['sign'] = build_sign(base_params)
    return dict_to_xml(base_params)

def generate_random_string(randomlength=32):
    str = ''
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def dict_to_xml(params):
    xml_elements = ["<xml>",]
    for (k, v) in params.items():
        if str(v).isdigit():
            xml_elements.append('<%s>%s</%s>' % (k, v, k))
        else:
            xml_elements.append('<%s><![CDATA[%s]]></%s>' % (k, v, k))
    xml_elements.append('</xml>')
    return ''.join(xml_elements)

def build_form_by_prepay_id(prepay_id):
    base_params = {
        'appId': config['appId'],
        'timeStamp': str(int(time.time())),
        'nonceStr': generate_random_string(),
        'package': "prepay_id=%s" % prepay_id,
        'signType': "MD5"
    }
    base_params['paySign'] = build_sign(base_params)
    return base_params

def build_form_by_params(params):
    headers = {'Content-Type': 'application/xml'}
    xml = build_unifiedorder(params)
    response = requests.post('https://api.mch.weixin.qq.com/pay/unifiedorder', data=xml, headers=headers)
    response.encoding = 'utf-8'
    response_dict = xmltodict.parse(response.text)['xml']
    if response_dict['return_code'] == 'SUCCESS':
        return build_form_by_prepay_id(response_dict['prepay_id'])

def notify_string_to_params(string):
    params = {}
    key_value_array = string.split('&')
    for item in key_value_array:
        key, value = item.split('=')
        params[key] = value
    return params

def verify_notify_string(string):
    params = notify_string_to_params(string)

    notify_sign = params['sign']
    del params['sign']

    if build_sign(params) == notify_sign:
        return True
    return False
