# Linux 提权速查（Privilege Escalation Cheatsheet）

## 0. 先做最小代价的信息收集
- 基本信息：`id; whoami; hostname; uname -a; cat /etc/os-release`
- 网络与出网：`ip a; ip r; ss -lntup; cat /etc/resolv.conf`
- 权限面：`sudo -l`、`groups`、`getcap -r / 2>/dev/null`
- 关键路径：`pwd; ls -la; find /home -maxdepth 2 -type f -name ".*history" 2>/dev/null`

## 1. Sudo 配置错误（最常见）
- 查看 sudo 权限：`sudo -l`
- 重点关注：
  - `NOPASSWD`
  - 可执行编辑器/解释器（vim、less、python、perl、ruby、awk、find、tar、zip、nmap 等）
  - 可执行自定义脚本/二进制（尤其是可写路径）
- 参考：优先按 GTFOBins 思路构造提权链（在授权环境验证）

## 2. SUID/SGID 与文件能力（Capabilities）
- 查找 SUID：`find / -perm -4000 -type f 2>/dev/null`
- 查找 SGID：`find / -perm -2000 -type f 2>/dev/null`
- 查找 capabilities：`getcap -r / 2>/dev/null`
- 典型危险点：
  - `bash` / `dash` / `busybox`
  - `find` / `tar` / `cp` / `python*` / `perl` / `ruby`
  - `cap_setuid` / `cap_dac_read_search` 等能力赋予解释器或可写二进制

## 3. Cron / Systemd 定时任务（可写即提权）
- 全局 crontab：`cat /etc/crontab; ls -la /etc/cron.*`
- 用户 crontab：`crontab -l 2>/dev/null`
- systemd timers：`systemctl list-timers --all 2>/dev/null`
- 排查要点：
  - 任务执行的脚本/二进制是否可写：`ls -la <path>`
  - 任务是否使用相对路径/通配符（可控目录、PATH 劫持）

## 4. 内核与本地提权漏洞（最后手段）
- 内核版本：`uname -r`
- 快速检索：`searchsploit linux kernel $(uname -r | cut -d- -f1)`
- 注意：
  - 先确认是否容器环境/是否有防护（seccomp、AppArmor）
  - 尽量选择只读验证/低破坏 PoC；避免在生产环境运行高风险提权

## 5. 常见敏感信息与配置泄露
- 凭证与密钥：
  - `grep -Rin \"password\\|passwd\\|token\\|secret\\|apikey\\|api_key\" /etc /opt /var/www 2>/dev/null | head`
  - `find / -type f \\( -name \"*.pem\" -o -name \"id_rsa\" -o -name \"*.key\" \\) 2>/dev/null`
- 服务配置：
  - Web：`/var/www/`、`/etc/nginx/`、`/etc/apache2/`
  - DB：`/etc/mysql/`、`/var/lib/postgresql/`
  - 容器：`/var/run/docker.sock`（高危）

## 6. 建议的自动化枚举（授权环境）
- `linpeas`：本地枚举与提权路径建议
- `pspy`：观察定时任务/后台进程执行（无需 root）
