# xxl-job / unacc

- 来源: c:\Users\29530\Desktop\DM\vulhub\xxl-job\unacc\README.md
- Vulhub 相对路径: xxl-job/unacc/README.md
- 脱敏代码块: 1

---
# XXL-JOB Executor Unauthorized Access

[中文版本(Chinese version)](README.zh-cn.md)

XXL-JOB is a distributed task scheduling platform with core design goals of rapid development, simple learning, lightweight, and easy extensibility. It is now open source and has been integrated into many companies' production lines, ready to use out of the box.

XXL-JOB is divided into two parts: admin and executor, where the former is the backend management page and the latter is the task execution client. The executor has no authentication configured by default, allowing unauthorized attackers to execute arbitrary commands through the RESTful API.

References:

- <https://mp.weixin.qq.com/s/jzXIVrEl0vbjZxI4xlUm-g>
- <https://landgrey.me/blog/18/>
- <https://github.com/OneSourceCat/XxlJob-Hessian-RCE>

## Environment Setup

Execute the following command to start XXL-JOB version 2.2.0:

```
docker compose up -d
```

After the environment is started, you can access the management end (admin) at `http://your-ip:8080` and the client end (executor) at `http://your-ip:9999`.

## Vulnerability Reproduction

Send the following data packet to the client (executor) to execute commands:

[REDACTED: potential weaponization content removed]

![](1.png)

The command `touch /tmp/success` has been successfully executed:

![](2.png)

Additionally, for XXL-JOB versions below 2.2.0 that don't have a RESTful API, we can execute commands through [Hessian deserialization](https://github.com/OneSourceCat/XxlJob-Hessian-RCE).
