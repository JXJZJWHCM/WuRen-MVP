# flask / ssti

- 来源: c:\Users\29530\Desktop\DM\vulhub\flask\ssti\README.md
- Vulhub 相对路径: flask/ssti/README.md
- 脱敏代码块: 3

---
# Flask (Jinja2) Server-Side Template Injection

[中文版本(Chinese version)](README.zh-cn.md)

Flask is a popular Python web framework that uses Jinja2 as its template engine. A Server-Side Template Injection (SSTI) vulnerability can occur when user input is directly rendered in Jinja2 templates without proper sanitization, potentially leading to remote code execution.

References:

- <https://www.blackhat.com/docs/us-15/materials/us-15-Kettle-Server-Side-Template-Injection-RCE-For-The-Modern-Web-App-wp.pdf>
- <http://rickgray.me/use-python-features-to-execute-arbitrary-codes-in-jinja2-templates>

## Environment Setup

Execute the following commands to build and start a Web application based on Flask 1.1.1:

```
docker compose up -d
```

After the server starts, visit `http://your-ip:8000/` to view the default page.

## Vulnerability Reproduction

First, verify the SSTI vulnerability exists by visiting:

[REDACTED: potential weaponization content removed]

If you see the result `54289`, it confirms the presence of the SSTI vulnerability.

To achieve remote code execution, you can use the following POC that obtains the `eval` function and executes arbitrary Python code:

[REDACTED: potential weaponization content removed]

Visit the following URL (with the POC URL-encoded) to execute the command:

[REDACTED: potential weaponization content removed]

The command execution result will be displayed:

![](1.png)
