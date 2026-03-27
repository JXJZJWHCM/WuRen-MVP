# 注销功能有效性 | Yak Program Language

- 来源: https://www.yaklang.com/Yaklab/wiki/SessionManagement/LogoffFunction/
- 抓取时间: 2026-02-06T07:03:11Z

---
漏洞描述：

Session 是应用系统对浏览器客户端身份认证的属性标识，在用户注销或退出应用系统时，系统应将客户端Session 认证属性标识清空。如果未能清空 Session 认证会话，该认证会话将持续有效，此时攻击者获得该Session 认证会话会导致用户权限被盗取。

漏洞案例：

通过登录界面和账号密码登录进系统后台

登录后点击我的账号，开启抓包，把返回当前账号信息的数据包放到Web Fuzzer中

退出系统后，重放Web Fuzzer中保留的数据包，发现还能访问到本应需要登录系统后才能访问到的系统信息，证明存在会话注销问题

漏洞修复方案

在用户注销或退出应用系统时，服务器应及时销毁Session认证会话信息并清空客户端浏览器Session属性标识
