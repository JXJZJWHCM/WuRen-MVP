import re

class MsfParser:
    """
    Parses output from msfconsole to determine execution status and extract key information.
    """
    
    @staticmethod
    def parse(output: str) -> dict:
        result = {
            "status": "unknown",
            "session_opened": False,
            "session_id": None,
            "vulnerable": False,
            "verified": False,
            "verification": [],
            "failure_category": None,
            "failure_evidence": [],
            "details": []
        }
        
        out = output or ""

        # Check for sessions
        # Example: "Command shell session 1 opened (192.168.1.5:4444 -> 192.168.1.10:49158)"
        session_match = re.search(r"(?:command shell|meterpreter)?\s*session\s+(\d+)\s+opened", out, re.IGNORECASE)
        if session_match:
            result["session_opened"] = True
            result["session_id"] = session_match.group(1)
            result["status"] = "success"
            result["details"].append(f"Session {result['session_id']} opened successfully.")

        # Check for interactive shell indicators (sometimes session isn't explicitly mentioned but shell is found)
        if "Found shell" in out or "Command shell session" in out:
            result["session_opened"] = True
            result["status"] = "success"
            result["details"].append("Interactive Shell FOUND! The exploit likely succeeded.")

        # Check for vulnerability confirmation (Auxiliary modules)
        # Example: "[+] 192.168.1.10:445 - Host is likely VULNERABLE to MS17-010!"
        if "[+]" in out and "VULNERABLE" in out:
            result["vulnerable"] = True
            result["status"] = "success"
            result["details"].append("Vulnerability confirmed.")

        # Check for specific failure messages
        if "Exploit completed, but no session was created" in out:
            result["status"] = "failed"
            result["failure_category"] = "no_session"
            result["failure_evidence"].append("exploit_completed_but_no_session")
            result["details"].append("Exploit completed but no session was created.")

        if "Exploit failed" in out or "Exploit exception" in out:
            result["status"] = "failed"
            result["details"].append("Exploit execution failed.")
            
        if "No active sessions" in out or "No sessions created" in out:
            if result["status"] != "success":
                result["status"] = "failed"
            if not result["failure_category"]:
                result["failure_category"] = "no_session"
            result["failure_evidence"].append("no_active_sessions")
            result["details"].append("No sessions created.")

        lower = out.lower()
        if result["status"] != "success":
            patterns = [
                ("network_timeout", [r"timed out", r"connection timeout", r"rex::connectiontimeout", r"operation timed out"]),
                ("network_refused", [r"connection refused", r"rex::connectionrefused", r"econnrefused"]),
                ("network_unreachable", [r"no route to host", r"host unreachable", r"network is unreachable", r"ehostunreach"]),
                ("dns", [r"temporary failure in name resolution", r"name or service not known", r"getaddrinfo", r"nodename nor servname provided"]),
                ("tls", [r"ssl", r"tls", r"certificate verify failed", r"wrong version number"]),
                ("auth", [r"authentication failed", r"login failed", r"invalid credentials", r"status_logon_failure", r"access denied"]),
                ("options", [r"failed to validate", r"missing required option", r"unknown datastore option", r"you must select a target", r"rhosts.*must be specified", r"rport.*must be specified"]),
                ("payload", [r"handler failed", r"failed to bind", r"payload.*could not", r"could not generate payload", r"lhost", r"lport"]),
            ]
            for cat, pats in patterns:
                for p in pats:
                    if re.search(p, lower, re.IGNORECASE):
                        result["failure_category"] = result["failure_category"] or cat
                        result["failure_evidence"].append(p)
                        break
                if result["failure_category"]:
                    break

        verifications = []
        m = re.search(r"Server username:\s*(.+)", out, re.IGNORECASE)
        if m:
            user = (m.group(1) or "").strip()
            if user:
                verifications.append(f"getuid: {user}")
        m = re.search(r"Current User\s*:\s*(.+)", out, re.IGNORECASE)
        if m:
            user = (m.group(1) or "").strip()
            if user:
                verifications.append(f"user: {user}")
        m = re.search(r"^\s*(root|www-data|administrator|nt authority\\\\system|system)\s*$", out, re.IGNORECASE | re.MULTILINE)
        if m:
            verifications.append(f"whoami: {m.group(1)}")
        if verifications:
            result["verified"] = True
            result["verification"] = verifications

        return result

    @staticmethod
    def enhance_output(stdout: str) -> str:
        """
        Appends an analysis summary to the original stdout for the AI to read.
        """
        analysis = MsfParser.parse(stdout)
        
        summary = "\n\n[雾刃渗透测试系统1.0 Analysis]\n"
        summary += f"Status: {analysis['status'].upper()}\n"
        if analysis['session_opened']:
            summary += f"SUCCESS: Session {analysis['session_id']} established! You can now use post-exploitation modules.\n"
            if analysis.get("verified"):
                v = analysis.get("verification") or []
                summary += "VERIFIED: " + ("; ".join(v[:3]) if v else "yes") + "\n"
        elif analysis['vulnerable']:
            summary += "SUCCESS: Target is confirmed VULNERABLE.\n"
        elif analysis['status'] == 'failed':
            cat = analysis.get("failure_category") or "unknown"
            summary += f"FAILURE: Exploit failed or no session was created. Category: {cat}\n"
            if cat.startswith("network"):
                summary += "HINT: Check reachability (RHOSTS/RPORT), firewall, and service availability; retry with adjusted timeouts.\n"
            elif cat == "dns":
                summary += "HINT: Check DNS/hosts resolution and proxy settings.\n"
            elif cat == "auth":
                summary += "HINT: Check credentials, account lockout policy, and service authentication requirements.\n"
            elif cat == "options":
                summary += "HINT: Check required options (RHOSTS/RPORT/TARGETURI/SSL) and validate module configuration.\n"
            elif cat == "payload":
                summary += "HINT: Check payload selection and handler/LHOST/LPORT binding and egress restrictions.\n"
            else:
                summary += "HINT: Review module output; distinguish between 'not vulnerable', 'no session', and network/config issues.\n"
        else:
            summary += "UNCERTAIN: Could not determine definitive success. Check output manually.\n"
            
        return stdout + summary
