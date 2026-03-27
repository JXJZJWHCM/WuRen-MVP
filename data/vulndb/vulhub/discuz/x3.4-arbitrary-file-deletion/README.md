# discuz / x3.4-arbitrary-file-deletion

- 来源: c:\Users\29530\Desktop\DM\vulhub\discuz\x3.4-arbitrary-file-deletion\README.md
- Vulhub 相对路径: discuz/x3.4-arbitrary-file-deletion/README.md
- 脱敏代码块: 2

---
# Discuz!X ≤3.4 Arbitrary File Deletion

[中文版本(Chinese version)](README.zh-cn.md)

Discuz!X is a popular forum software widely used in China. A vulnerability in Discuz!X versions 3.4 and below allows attackers to delete arbitrary files on the server through the user profile modification functionality.

References:

- <https://lorexxar.cn/2017/09/30/dz-delete/>

## Environment Setup

Execute the following command to deploy Discuz!X 3.4:

```
docker compose up -d
```

During installation, only modify the database host to `db` and keep other settings as default:

![](1.png)

## Vulnerability Reproduction

First, verify that the target file (e.g., robots.txt) exists by visiting `http://your-ip/robots.txt`:

![](2.png)

After registering a user account, find your formhash value in the personal settings page:

![](4.png)

Send the following HTTP request with your cookie and formhash:

[REDACTED: potential weaponization content removed]

After successful submission, the birthplace field in the user profile page will show the following state:

![](5.png)

This indicates that our malicious data has been inserted into the database.

Next, create an `upload.html` file with the following code (replace `[your-ip]` with your Discuz domain and `[form-hash]` with your formhash):

[REDACTED: potential weaponization content removed]

Open this page in a browser and upload a normal image file. At this point, the malicious data should have been processed and the vulnerability exploitation is complete.

Visit `http://your-ip/robots.txt` again to verify that the file has been successfully deleted:

![](6.png)
