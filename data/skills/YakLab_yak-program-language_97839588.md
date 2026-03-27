# 通用框架登录 | Yak Program Language

- 来源: https://yaklang.com/en/Yaklab/wiki/AnyUserLogin/General-framework/
- 抓取时间: 2026-02-06T07:03:38Z

---
漏洞描述：

一些oa或者别的web框架可能会爆出任意用户登录漏洞，因为为白盒审计出来的漏洞所以可能会跟常规的任意用户登录的绕过手法有所不同

漏洞案例：

这里以通达oa的任意用户登录作例子
使用yakit抓取登录的数据包

修改接口logincheck.php为logincheck_code.php
删除cookie的值
添加UID=1参数

返回包中会返回管理员的cookie
访问url，在浏览器中替换cookie即可登录

成功以管理员身份登录
