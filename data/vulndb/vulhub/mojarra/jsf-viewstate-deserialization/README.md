# mojarra / jsf-viewstate-deserialization

- 来源: c:\Users\29530\Desktop\DM\vulhub\mojarra\jsf-viewstate-deserialization\README.md
- Vulhub 相对路径: mojarra/jsf-viewstate-deserialization/README.md
- 脱敏代码块: 1

---
# Mojarra JSF ViewState Deserialization Vulnerability

[中文版本(Chinese version)](README.zh-cn.md)

JavaServer Faces (JSF) is a standard for building Web applications, and Mojarra is a framework that implements JSF. The Mojarra that before 2.1.29-08 and 2.0.11-04, is not configured to encrypt the ViewState, so the web application may have a serious remote code execution (RCE) vulnerability.

Reference links:

- https://www.alphabot.com/security/blog/2017/java/Misconfigured-JSF-ViewStates-can-lead-to-severe-RCE-vulnerabilities.html
- https://www.exploit-db.com/docs/48126
- https://www.synacktiv.com/ressources/JSF_ViewState_InYourFace.pdf

## Setup

Execute the following command to start a JSF application which using JDK7u21 and Mojarra 2.1.28:

```
docker compose up -d
```

After the application is started, visit `http://your-ip:8080` to see the demo page.

## Exploit

Here is the structure of ViewState that encoding without a security layer:

![](1.png)

According to this structure, we can use [ysoserial's Jdk7u21 Gadget](https://github.com/frohoff/ysoserial) to generate a payload:

[REDACTED: potential weaponization content removed]

Then, intercept and modify the http request from demo page, put the url-encoded payload into value of `javax.faces.ViewState` field:

![](2.png)

`touch /tmp/success` has been successfully executed:

![](3.png)
