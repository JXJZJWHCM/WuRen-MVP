# Nginx插件使用 | Yak Program Language

- 来源: https://yaklang.com/Yaklab/wiki/DetectionPlug-in/Nginx
- 抓取时间: 2026-02-06T07:02:03Z

---
## 1 Nginx 文件解析漏洞 #

插件id：

Yakit正在努力编写~

测试过程：

vulhub测试网站访问上传的图片 http://xx.xx.xx.xx/uploadfiles/nginx.png

利用文件解析漏洞进行解析 http://xx.xx.xx.xx/uploadfiles/nginx.png/.php

## 2 Nginx CVE-2017-7529 漏洞检测 #

插件id：

f863b7be-9536-4de3-bc94-5800ac2a7010

测试过程：

输入ip:端口 点击开始执行
成功检测出漏洞

## 3 Nginx 目录遍历漏洞检测 #

插件id：

58587b92-e88c-4557-8f56-23bac605bbe1

测试过程：

输入ip:端口 点击开始执行
成功检测出漏洞

## 4 Nginx CRLF注入漏洞检测 #

插件id：

Yakit正在努力编写~

测试过程：

执行pyload：curl -I http://xx.xx.xx.xx:8080/%0d%0aSet-Cookie:%20a=1

## 5 Nginx 空字节任意代码执行漏洞检测 #

插件id：

Yakit正在努力编写~

测试过程：

暂无案例

- 1 Nginx 文件解析漏洞
- 2 Nginx CVE-2017-7529 漏洞检测
- 3 Nginx 目录遍历漏洞检测
- 4 Nginx CRLF注入漏洞检测
- 5 Nginx 空字节任意代码执行漏洞检测
