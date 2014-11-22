# Wechat Pay For Python
实现微信支付V2版。

### 发起支付
python端, 修改version2中的config文件

```
config = {
    'appId': 'xxx',
    'appSecret': 'xxx',
    'paySignKey': 'xxx',
    'partnerId': 'xxx',
    'partnerKey': 'xxx',
    'notify_url': 'xxx'
}
```

```
import version2
import json

params = version2.build_form(
    'body': 'product name',
    'out_trade_no': 'order number',
    'total_fee': '1',
    'spbill_create_ip': 'd.d.d.d'
)

json.dumps(params)
```

前端

```
var json_str = $.get(url)
var params = JSON.parse(json_str)

document.addEventListener('WeixinJSBridgeReady', function onBridgeReady() {
    WeixinJSBridge.call('hideOptionMenu');
    WeixinJSBridge.call('hideToolbar');

    $('a#getBrandWCPayRequest').click(function(e){
        WeixinJSBridge.invoke('getBrandWCPayRequest', params, function(res){
            alert(res.err_msg)

            if(res.err_msg == "get_brand_wcpay_request:ok" ) {
                // check notify, or query
            }
            if(res.err_msg == "get_brand_wcpay_request:cancel") {
            }
            if(res.err_msg == "get_brand_wcpay_request:fail") {
                alert("支付失败.")
            }
        });
    });

}, false)
```


### 验证notify
python端

```
import version2

version2.verify_notify_string(request_string)
返回True或者False
```
