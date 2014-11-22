#-*- coding: utf-8 -*-

import hashlib
import urllib
from random import Random
import time
import xmltodict

config = {
    'appId': 'xxx',
    'appSecret': 'xxx',
    'paySignKey': 'xxx',
    'partnerId': 'xxx',
    'partnerKey': 'xxx',
    'notify_url': 'xxx'
}

def build_form(params):
    # 所有传入参数都是字符串类型
    base_params = {
        'appId': config['appId'],
        'timeStamp': str(int(time.time())),
        'nonceStr': generate_random_string(),
        'package': build_package(params),
        'signType': 'SHA1',
        'paySign': ''
    }

    string1 = build_pay_sign_string(base_params)
    # 对string1作签名算法，字段名和字段值都采用原始值，不进行URL转义。SHA1(string)
    pay_sign = hashlib.sha1(string1).hexdigest()

    base_params['paySign'] = pay_sign
    return base_params


def generate_random_string(randomlength=32):
    str = ''
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str

def build_pay_sign_string(params):
    # 所有参数名均为小写字符，如appId在排序后字符串则为appid
    # appkey即paySignkey
    sign_keys = ['appid', 'timestamp', 'noncestr', 'package', 'appkey']
    # 对所有待签名参数按照字段名的ASCII码从小到大排序（字典序）
    sign_keys.sort()

    array = []
    for key in sign_keys:
        if key == 'appkey':
            array.append("%s=%s" % (key, config['paySignKey']))
        for key2 in params:
            if key2.lower() == key:
                array.append("%s=%s" % (key, params[key2]))
    return "&".join(array)

def build_package(params):
    target_keys = ['body', 'out_trade_no', 'total_fee', 'spbill_create_ip']
    filtered_params = filter_package_params(params, target_keys)

    base_params = {
        'bank_type': 'WX',
        'partner': config['partnerId'],
        'fee_type': '1',
        'notify_url': config['notify_url'],
        'input_charset': 'UTF-8'
    }
    filtered_params.update(base_params)

    sign = generate_package_sign(filtered_params)
    string2 = params_to_encode_key_value_url_string(filtered_params)
    package = string2 + "&sign=%s" % sign
    return package

def filter_package_params(params, target_keys):
    filtered_params = {}
    for key in target_keys:
        if key not in params:
            raise Exception("Key %s not in params" % key)
        filtered_params[key] = params[key]
    return filtered_params

def generate_package_sign(params):
    string1 = params_to_asc_key_value_url_string(params)
    stringSignTemp = string1 + "&key=%s" % config['partnerKey']
    return string_upper_md5(stringSignTemp)

# 对所有传入参数按照字段名的ASCII码从小到大排序（字典序）后，使用URL键值对的格式
def params_to_asc_key_value_url_string(params):
    array = []
    # 按照字段名的ASCII码从小到大排序（字典序）
    keys = params.keys()
    keys.sort()
    for key in keys:
        # 值为空的参数不参与签名；
        if params[key] and params[key] != '':
            array.append("%s=%s" % (key, params[key]))
    return "&".join(array)

# 对stringSignTemp进行md5运算，再将得到的字符串所有字符转换为大写
def string_upper_md5(string):
    m = hashlib.md5(string.encode('utf-8'))
    m.digest()
    return m.hexdigest().upper()

# 对传入参数中所有键值对的value进行urlencode转码后重新拼接成字符串
def params_to_encode_key_value_url_string(params):
    array = []
    for key in params:
        value = urllib.quote(unicode(params[key]).encode('utf-8'))
        array.append("%s=%s" % (key, value))
    return "&".join(array)



def verify_notify_string(string):
    params = notify_string_to_params(string)

    # 接收参数后需要验证这些参数的签名，签名方式与2.6节package sign步骤和方式相同
    notify_sign = params['sign']
    del params['sign']

    sign = generate_package_sign(params)
    return notify_sign == sign

def notify_string_to_params(string):
    params = {}
    key_value_array = string.split('&')
    for item in key_value_array:
        key, value = item.split('=')
        params[key] = value
    return params

def notify_xml_data_to_dict(string):
    return xmltodict.parse(string)['xml']
