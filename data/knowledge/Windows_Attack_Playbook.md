# Windows 攻击速查（Kali 侧作战手册）

## 常见端口 → 典型动作
- 53 (DNS)：确认域环境/域名，辅助资产梳理
- 88/464 (Kerberos)：AD 入口，票据相关攻击面与域策略评估
- 135 (RPC)：主机信息、部分远程管理入口线索
- 139/445 (SMB)：共享/域信息枚举、凭证验证、横向入口
- 389/636 (LDAP/LDAPS)：目录结构枚举（用户/组/计算机/策略线索）
- 3268/3269 (GC)：跨域/全局目录检索
- 3389 (RDP)：交互登录面与可能的域信息泄露
- 5985/5986 (WinRM)：远程管理面（通常更便于后续远程操作）

## Kali 常用工具清单（按用途）

### 发现与指纹
```bash
nmap -sS -sV -T4 -Pn -p 135,139,445,3389,389,636,3268,5985,5986,88,464 <target>
nmap -Pn -p 445 --script smb-os-discovery,smb2-security-mode,smb2-time,smb-protocols <target>
nmap -Pn -p 3389 --script rdp-ntlm-info,rdp-enum-encryption <target>
nmap -Pn -p 389,636 --script ldap-rootdse <dc_ip>
```

### SMB 枚举与共享访问
```bash
smbclient -L //<target> -N
smbmap -H <target>
enum4linux-ng -A <target>
rpcclient -U '<user>%<pass>' <target> -c 'enumdomusers'
```

### 凭证验证与面梳理（域内/横向前置）
```bash
crackmapexec smb <range> -u <user> -p '<pass>' --continue-on-success
crackmapexec winrm <range> -u <user> -p '<pass>' --continue-on-success
```

### AD/Kerberos 枚举（常见入口）
```bash
ldapsearch -x -H ldap://<dc_ip> -D '<domain>\\<user>' -w '<pass>' -b 'DC=example,DC=com' '(objectClass=user)' sAMAccountName
GetNPUsers.py <domain>/ -dc-ip <dc_ip> -usersfile users.txt -no-pass
GetUserSPNs.py <domain>/<user>:'<pass>' -dc-ip <dc_ip> -request
```

## 低噪声优先的“建议顺序”
1. 端口/服务确认（nmap + 脚本）
2. SMB 枚举（共享、域名、主机名、时钟偏差）
3. 有凭证则先做“可登录面梳理”（哪些机器可 SMB/WinRM）
4. 确认域环境后做 LDAP/BloodHound 路径分析
5. 最后再考虑喷洒/中继/高噪声验证（需评估锁定策略与授权范围）

## 证据留存要点
- 保存 nmap 输出（版本/脚本结果/时间）
- 保存共享列表与权限验证输出（smbmap/smbclient/cme）
- 保存 AD 路径证据（对象 DN、关键 ACL 边、查询结果截图）
- 报告正文避免写明文口令；必要时按规则脱敏

