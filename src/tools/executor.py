import subprocess
import shlex
import time
import threading
import queue
import os
import signal
import re
from collections import deque
from typing import Dict, Any, Tuple
import logging
from src.tools.msf_parser import MsfParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolExecutor:
    def __init__(self, tool_manager, base_dir: str | None = None):
        self.tool_manager = tool_manager
        self.base_dir = base_dir
        self._lock = threading.Lock()
        self._running: Dict[str, subprocess.Popen] = {}
        self._cancel_flags: Dict[str, threading.Event] = {}
        self._docker_cidfiles: Dict[str, str] = {}
        self._msf_lock = threading.Lock()
        self._msf_cli: Dict[str, Dict[str, Any]] = {}

    def msf_cli_status(self, task_id: str) -> Dict[str, Any]:
        tid = str(task_id or "").strip()
        if not tid:
            return {"running": False}
        with self._msf_lock:
            st = self._msf_cli.get(tid)
            if not st:
                return {"running": False}
            proc = st.get("process")
            running = bool(proc) and (proc.poll() is None)
            return {
                "running": running,
                "pid": int(getattr(proc, "pid", 0) or 0) if running else 0,
            }

    def msf_cli_output(self, task_id: str, since_seq: int = 0, limit: int = 400) -> Dict[str, Any]:
        tid = str(task_id or "").strip()
        if not tid:
            return {"running": False, "seq": 0, "lines": []}
        try:
            since = int(since_seq)
        except Exception:
            since = 0
        try:
            limit = max(1, min(int(limit), 2000))
        except Exception:
            limit = 400

        with self._msf_lock:
            st = self._msf_cli.get(tid)
            if not st:
                return {"running": False, "seq": 0, "lines": []}
            proc = st.get("process")
            running = bool(proc) and (proc.poll() is None)
            buf: deque = st.get("buffer")  # type: ignore
            seq = int(st.get("seq") or 0)
            lines = []
            for item in list(buf):
                if int(item.get("seq") or 0) <= since:
                    continue
                lines.append(item)
                if len(lines) >= limit:
                    break
            return {"running": running, "seq": seq, "lines": lines}

    def msf_cli_send(self, task_id: str, cmd: str) -> Dict[str, Any]:
        tid = str(task_id or "").strip()
        c = str(cmd or "").rstrip("\r\n")
        if not tid or not c:
            return {"ok": False, "error": "missing_task_or_cmd"}
        with self._msf_lock:
            st = self._msf_cli.get(tid)
            if not st:
                return {"ok": False, "error": "msf_not_running"}
            proc = st.get("process")
            if not proc or proc.poll() is not None:
                return {"ok": False, "error": "msf_not_running"}
            try:
                stdin = proc.stdin
                if not stdin:
                    return {"ok": False, "error": "no_stdin"}
                stdin.write(c + "\n")
                stdin.flush()
            except Exception:
                return {"ok": False, "error": "send_failed"}
            return {"ok": True}

    def msf_cli_stop(self, task_id: str) -> Dict[str, Any]:
        tid = str(task_id or "").strip()
        if not tid:
            return {"ok": False, "error": "missing_task_id"}
        with self._msf_lock:
            st = self._msf_cli.get(tid)
            if not st:
                return {"ok": True, "stopped": False}
            proc = st.get("process")
        if proc and proc.poll() is None:
            try:
                self._kill_process_tree(proc)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        with self._msf_lock:
            self._msf_cli.pop(tid, None)
        return {"ok": True, "stopped": True}

    def _msf_cli_append(self, task_id: str, stream: str, line: str):
        tid = str(task_id or "").strip()
        if not tid:
            return
        with self._msf_lock:
            st = self._msf_cli.get(tid)
            if not st:
                return
            st["seq"] = int(st.get("seq") or 0) + 1
            seq = int(st["seq"])
            buf: deque = st.get("buffer")  # type: ignore
            buf.append({"seq": seq, "ts": time.time(), "stream": stream, "line": line})

    def _msf_cli_reader(self, task_id: str, pipe, stream: str):
        try:
            with pipe:
                for line in iter(pipe.readline, ""):
                    if not line:
                        break
                    self._msf_cli_append(task_id, stream, line)
        except Exception:
            pass

    def msf_cli_start(self, *, task_id: str, command: list[str], cwd: str | None, env: Dict[str, str] | None) -> Dict[str, Any]:
        tid = str(task_id or "").strip()
        if not tid:
            return {"ok": False, "error": "missing_task_id"}
        with self._msf_lock:
            st = self._msf_cli.get(tid)
            if st:
                proc = st.get("process")
                if proc and proc.poll() is None:
                    return {"ok": True, "already_running": True, "pid": int(getattr(proc, "pid", 0) or 0)}
                self._msf_cli.pop(tid, None)

        popen_kwargs: Dict[str, Any] = {
            "stdin": subprocess.PIPE,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "bufsize": 1,
            "encoding": "utf-8",
            "errors": "replace",
            "env": env,
            "cwd": cwd,
        }
        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs["start_new_session"] = True

        process = subprocess.Popen(command, **popen_kwargs)
        with self._msf_lock:
            self._msf_cli[tid] = {
                "process": process,
                "buffer": deque(maxlen=4000),
                "seq": 0,
            }

        t_out = threading.Thread(target=self._msf_cli_reader, args=(tid, process.stdout, "stdout"))
        t_err = threading.Thread(target=self._msf_cli_reader, args=(tid, process.stderr, "stderr"))
        t_out.daemon = True
        t_err.daemon = True
        t_out.start()
        t_err.start()
        return {"ok": True, "already_running": False, "pid": int(process.pid or 0)}

    def _ensure_msf_exit(self, args: Dict[str, Any]):
        """
        Ensures that the MSF resource script contains an exit command to prevent hanging.
        """
        rc_file = None
        # Check explicit arguments or parsed ones
        for key, value in args.items():
            if isinstance(value, str) and value.endswith('.rc'):
                rc_file = value
                break
        
        # Also check if it's in the command list constructed later, 
        # but here we only have args dict. 
        # Usually the AI writes a file and passes it.
        
        keep_session = bool(args.get("keep_session"))

        if rc_file and os.path.exists(rc_file):
            try:
                with open(rc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                raw_lines = content.splitlines()
                meaningful = []
                for ln in raw_lines:
                    s = ln.strip()
                    if not s:
                        continue
                    if s.startswith("#"):
                        continue
                    meaningful.append(s)

                has_exit = bool(meaningful) and ("exit" in meaningful[-1].lower())
                has_sessions_check = any(s.lower().startswith("sessions ") for s in meaningful)
                has_run = any(re.match(r"^(run|exploit)\b", s, re.IGNORECASE) for s in meaningful)

                verification_block = [
                    "sessions -l",
                    'sessions -i -1 -C "whoami"',
                    'sessions -i -1 -C "getuid"',
                    'sessions -i -1 -C "pwd"',
                    'sessions -i -1 -C "ls"',
                    'sessions -i -1 -C "dir"',
                ]

                new_lines = list(raw_lines)
                if has_run and not has_sessions_check:
                    insert_at = None
                    for i in range(len(new_lines) - 1, -1, -1):
                        s = new_lines[i].strip().lower()
                        if not s or s.startswith("#"):
                            continue
                        if s.startswith("exit"):
                            insert_at = i
                            break
                    if insert_at is None:
                        insert_at = len(new_lines)
                    for i, cmd in enumerate(verification_block):
                        new_lines.insert(insert_at + i, cmd)
                    logger.info(f"[AutoFix] Injected session verification commands into {rc_file}.")
                    has_exit = False

                if (not has_exit) and (not keep_session):
                    logger.info(f"[AutoFix] Appending 'exit -y' to {rc_file} to prevent MSF hang.")
                    if new_lines and new_lines[-1].strip():
                        new_lines.append("")
                    new_lines.append("exit -y")

                if new_lines != raw_lines:
                    with open(rc_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(new_lines) + "\n")
            except Exception as e:
                logger.warning(f"Failed to append exit to RC file: {e}")

    def _stream_reader(self, pipe, q, tag):
        try:
            with pipe:
                for line in iter(pipe.readline, ''):
                    q.put((tag, line))
        finally:
            pass

    def _execute_msf_monitored(self, command: list, env: Dict[str, str] | None = None) -> Tuple[str, str, int]:
        """
        Executes MSFConsole with real-time monitoring to prevent hangs.
        """
        logger.info(f"Starting Monitored MSF Execution: {' '.join(command)}")
        
        popen_kwargs: Dict[str, Any] = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "bufsize": 1,
            "encoding": "utf-8",
            "errors": "replace",
            "env": env,
        }
        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs["start_new_session"] = True

        process = subprocess.Popen(
            command,
            **popen_kwargs,
        )
        
        q = queue.Queue()
        t_out = threading.Thread(target=self._stream_reader, args=(process.stdout, q, 'out'))
        t_err = threading.Thread(target=self._stream_reader, args=(process.stderr, q, 'err'))
        t_out.daemon = True
        t_err.daemon = True
        t_out.start()
        t_err.start()
        
        stdout_acc = []
        stderr_acc = []
        
        start_time = time.time()
        last_output_time = time.time()
        max_idle_time = 120 # 2 minutes idle timeout
        
        # Keywords that indicate we can stop early (optional)
        # For now, we rely on 'exit -y' working, and idle timeout as backup.
        
        while True:
            # Check if process is still alive
            retcode = process.poll()
            
            # Read all available lines from queue
            while True:
                try:
                    tag, line = q.get_nowait()
                    last_output_time = time.time()
                    if tag == 'out':
                        stdout_acc.append(line)
                        # Real-time log or analysis could happen here
                    else:
                        stderr_acc.append(line)
                except queue.Empty:
                    break
            
            if retcode is not None:
                # Process finished
                break
                
            # Check Global Timeout (15 mins)
            if time.time() - start_time > 900:
                process.kill()
                error_msg = "\n[System] MSFConsole execution timed out (15m). Process killed."
                stdout_acc.append(error_msg)
                return "".join(stdout_acc), "".join(stderr_acc) + error_msg, -1
                
            # Check Idle Timeout
            if time.time() - last_output_time > max_idle_time:
                process.kill()
                error_msg = f"\n[System] MSFConsole idle for {max_idle_time}s. Assuming hang/interactive wait. Process killed."
                stdout_acc.append(error_msg)
                # It might actually be a success that just didn't exit.
                # MsfParser will parse the output we have so far.
                return "".join(stdout_acc), "".join(stderr_acc) + error_msg, 0 # Return 0 to allow parsing
            
            time.sleep(0.5)
            
        t_out.join(timeout=1)
        t_err.join(timeout=1)
        
        return "".join(stdout_acc), "".join(stderr_acc), process.returncode

    def _append_limited(self, acc: list[str], text: str, max_chars: int, truncated_flag: list[bool]):
        if truncated_flag[0]:
            return
        current_len = sum(len(x) for x in acc)
        remaining = max_chars - current_len
        if remaining <= 0:
            truncated_flag[0] = True
            return
        if len(text) <= remaining:
            acc.append(text)
            return
        acc.append(text[:remaining])
        truncated_flag[0] = True

    def _kill_process_tree(self, process: subprocess.Popen):
        if process.poll() is not None:
            return
        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    capture_output=True,
                    text=True,
                )
                try:
                    process.wait(timeout=2)
                except Exception:
                    pass
                return
            except Exception:
                pass
            try:
                process.kill()
                try:
                    process.wait(timeout=2)
                except Exception:
                    pass
            except Exception:
                pass
            return

        try:
            pgid = os.getpgid(process.pid)
        except Exception:
            pgid = None

        if pgid:
            try:
                os.killpg(pgid, signal.SIGTERM)
            except Exception:
                pass
            try:
                process.wait(timeout=2)
                return
            except Exception:
                pass
            try:
                os.killpg(pgid, signal.SIGKILL)
            except Exception:
                pass
            try:
                process.wait(timeout=2)
            except Exception:
                pass
        else:
            try:
                process.terminate()
                process.wait(timeout=2)
                return
            except Exception:
                pass
            try:
                process.kill()
                try:
                    process.wait(timeout=2)
                except Exception:
                    pass
            except Exception:
                pass

    def _docker_force_remove(self, task_id: str):
        cidfile = None
        with self._lock:
            cidfile = self._docker_cidfiles.get(task_id)
        if not cidfile:
            return
        try:
            if os.path.exists(cidfile):
                with open(cidfile, "r", encoding="utf-8", errors="replace") as f:
                    cid = (f.read() or "").strip()
                if cid:
                    subprocess.run(["docker", "rm", "-f", cid], capture_output=True, text=True)
        finally:
            try:
                if os.path.exists(cidfile):
                    os.remove(cidfile)
            except Exception:
                pass
            with self._lock:
                self._docker_cidfiles.pop(task_id, None)

    def cancel(self, task_id: str) -> bool:
        with self._lock:
            cancel_flag = self._cancel_flags.get(task_id)
            proc = self._running.get(task_id)

        if cancel_flag:
            cancel_flag.set()
        self._docker_force_remove(task_id)
        if proc:
            self._kill_process_tree(proc)
            return True
        return bool(cancel_flag)

    def _wrap_with_docker(
        self,
        command: list,
        *,
        tool_def: Dict[str, Any],
        cwd: str | None,
        task_id: str | None,
    ) -> Tuple[list, str | None]:
        if os.name == "nt":
            return command, None
        if not self.base_dir:
            return command, None

        sandbox_mode = (tool_def.get("sandbox") or os.getenv("TOOL_SANDBOX", "process") or "process").strip().lower()
        if sandbox_mode != "docker":
            return command, None

        image = (tool_def.get("docker_image") or os.getenv("TOOL_DOCKER_IMAGE") or "").strip()
        if not image:
            raise RuntimeError("已启用 Docker 沙箱，但未配置 TOOL_DOCKER_IMAGE 或工具 docker_image")

        network = (tool_def.get("docker_network") or os.getenv("TOOL_DOCKER_NETWORK", "bridge") or "bridge").strip().lower()
        if network not in {"bridge", "host", "none"}:
            network = "bridge"

        memory = str(tool_def.get("docker_memory") or os.getenv("TOOL_DOCKER_MEMORY", "") or "").strip()
        pids_limit = str(tool_def.get("docker_pids_limit") or os.getenv("TOOL_DOCKER_PIDS_LIMIT", "") or "").strip()
        read_only = (tool_def.get("docker_read_only") if tool_def.get("docker_read_only") is not None else True)

        data_dir = os.path.join(self.base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)

        container_workdir = "/data"
        if cwd:
            try:
                data_abs = os.path.abspath(data_dir)
                cwd_abs = os.path.abspath(cwd)
                if cwd_abs == data_abs or cwd_abs.startswith(data_abs + os.sep):
                    rel = os.path.relpath(cwd_abs, data_abs).replace("\\", "/")
                    container_workdir = "/data" if rel == "." else f"/data/{rel}"
            except Exception:
                container_workdir = "/data"

        cidfile = None
        if task_id:
            cidfile = os.path.join(self.base_dir, "data", "temp", "tool_runs", f"{task_id}.cid")
            os.makedirs(os.path.dirname(cidfile), exist_ok=True)
            with self._lock:
                self._docker_cidfiles[task_id] = cidfile

        docker_cmd = ["docker", "run", "--rm", "--init"]
        if cidfile:
            docker_cmd.extend(["--cidfile", cidfile])
        docker_cmd.extend(["--network", network])
        docker_cmd.extend(["--security-opt", "no-new-privileges:true", "--cap-drop", "ALL"])
        if read_only:
            docker_cmd.append("--read-only")
            docker_cmd.extend(["--tmpfs", "/tmp:rw,noexec,nosuid,size=256m"])
        if pids_limit:
            docker_cmd.extend(["--pids-limit", pids_limit])
        if memory:
            docker_cmd.extend(["--memory", memory])
        docker_cmd.extend(["-v", f"{data_dir}:/data:rw", "-w", container_workdir, image])
        docker_cmd.extend(command)
        return docker_cmd, cidfile

    def _execute_generic_monitored(
        self,
        command: list,
        env: Dict[str, str] | None,
        timeout_s: float,
        cancel_flag: threading.Event | None,
        cwd: str | None,
        task_id: str | None,
    ) -> Tuple[str, str, int]:
        popen_kwargs: Dict[str, Any] = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "text": True,
            "bufsize": 1,
            "encoding": "utf-8",
            "errors": "replace",
            "env": env,
            "cwd": cwd,
        }
        if os.name == "nt":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            popen_kwargs["start_new_session"] = True

        process = subprocess.Popen(command, **popen_kwargs)
        if task_id:
            with self._lock:
                self._running[task_id] = process

        q = queue.Queue()
        t_out = threading.Thread(target=self._stream_reader, args=(process.stdout, q, "out"))
        t_err = threading.Thread(target=self._stream_reader, args=(process.stderr, q, "err"))
        t_out.daemon = True
        t_err.daemon = True
        t_out.start()
        t_err.start()

        stdout_acc: list[str] = []
        stderr_acc: list[str] = []
        truncated_out = [False]
        truncated_err = [False]
        max_chars = int(os.getenv("TOOL_MAX_OUTPUT_CHARS", "200000"))

        start_time = time.time()

        try:
            while True:
                if cancel_flag and cancel_flag.is_set():
                    self._kill_process_tree(process)
                    msg = "\n[系统提示] 工具执行已被用户取消。"
                    self._append_limited(stdout_acc, msg, max_chars, truncated_out)
                    return "".join(stdout_acc), "".join(stderr_acc), -2

                retcode = process.poll()

                while True:
                    try:
                        tag, line = q.get_nowait()
                        if tag == "out":
                            self._append_limited(stdout_acc, line, max_chars, truncated_out)
                        else:
                            self._append_limited(stderr_acc, line, max_chars, truncated_err)
                    except queue.Empty:
                        break

                if retcode is not None:
                    break

                if time.time() - start_time > timeout_s:
                    self._kill_process_tree(process)
                    msg = f"\n[系统提示] 工具执行超时（{int(timeout_s)}s），已终止进程。"
                    self._append_limited(stdout_acc, msg, max_chars, truncated_out)
                    self._append_limited(stderr_acc, msg, max_chars, truncated_err)
                    return "".join(stdout_acc), "".join(stderr_acc), -1

                time.sleep(0.2)

            t_out.join(timeout=1)
            t_err.join(timeout=1)
            return "".join(stdout_acc), "".join(stderr_acc), process.returncode
        finally:
            if task_id:
                with self._lock:
                    self._running.pop(task_id, None)

    def execute(self, tool_name: str, args: Dict[str, Any], task_id: str | None = None) -> Tuple[str, str, int]:
        """
        Executes a tool with the provided arguments.
        Returns: (stdout, stderr, return_code)
        """
        tool_def = self.tool_manager.get_tool(tool_name)
        if not tool_def:
            return "", f"Tool '{tool_name}' not found.", -1

        command = [tool_def.get('binary', tool_def.get('command', tool_name))]
        
        # Append fixed args if they are a list (e.g. nmap's ["-sT", ...])
        fixed_args = tool_def.get('args')
        if isinstance(fixed_args, list):
            command.extend(fixed_args)
        
        # Parse parameters
        parameters = tool_def.get('parameters', [])
        # Legacy support: if parameters not found, try 'args' as dict
        if not parameters and isinstance(tool_def.get('args'), dict):
            # Convert legacy args dict to parameters list format for unified processing
            for name, config in tool_def['args'].items():
                param = config.copy()
                param['name'] = name
                parameters.append(param)

        # Check required args
        for param in parameters:
            if param.get('required') and param['name'] not in args:
                 return "", f"Missing required argument: {param['name']}", -1

        # Build arguments list
        # We need to separate flags/options from positional args to ensure order
        # However, some positionals need to be at the start (like gobuster mode) and some at end (target)
        # We will use a simple strategy:
        # 1. Collect all parts with their 'position' index if available.
        # 2. If no position, assume flags go before positionals.
        
        ordered_parts = [] # List of (position, value_list)
        flags_parts = []   # List of value_list
        end_parts = []     # List of value_list (for positionals without explicit low index)

        for param in parameters:
            name = param['name']
            if name not in args:
                continue
                
            value = args[name]
            param_format = param.get('format', 'flag') # flag, positional, template
            
            part = []
            
            if param_format == 'flag':
                flag = param.get('flag')
                if not flag: continue
                
                if isinstance(value, bool):
                    if value: part.append(flag)
                else:
                    part.append(flag)
                    part.append(str(value))
                    
                flags_parts.append(part)
                
            elif param_format == 'positional':
                # Special handling for 'additional_args'
                if name == 'additional_args':
                    part.extend(shlex.split(str(value)))
                    # usually goes to the end
                    end_parts.append(part)
                else:
                    part.append(str(value))
                    if 'position' in param:
                        ordered_parts.append((param['position'], part))
                    else:
                        end_parts.append(part)

            elif param_format == 'template':
                template = param.get('template', '{value}')
                rendered = template.format(value=value)
                part.extend(shlex.split(str(rendered)))
                flags_parts.append(part)
                
            elif param_format == 'combined': # e.g. --level=3
                flag = param.get('flag')
                part.append(f"{flag}={value}")
                flags_parts.append(part)

        # Sort ordered parts
        ordered_parts.sort(key=lambda x: x[0])
        
        # Assemble command: 
        # Strategy: 
        # 1. Positional args with position < 0 (if any? unlikely) or position 0 (like gobuster mode)
        # 2. Flags
        # 3. Positional args with position > 0 or no position (target)
        
        # Actually, let's just stick to: Ordered Positionals -> Flags -> Unordered Positionals (End)
        # But 'nmap target' has position 0 but is usually last?
        # Wait, nmap.yaml says target position: 0. 
        # If I put target first: `nmap 192.168.1.1 -p 80` -> Works
        # `nmap -p 80 192.168.1.1` -> Also works
        # Gobuster: `gobuster dir -u ...` -> 'dir' must be first.
        
        # So, if position is specified, we respect it relative to other positioned args.
        # But where do flags go?
        # Usually flags can go anywhere, but best practice is before the final target argument.
        # If 'target' has position 0, and 'mode' has position 0, conflict?
        # Let's check gobuster.yaml: mode position 0.
        # Let's check nmap.yaml: target position 0.
        
        # Conflict!
        # CyberStrikeAI logic likely relies on specific tool implementations or assumes specific order.
        # Let's assume:
        # If it's a "subcommand" style tool (gobuster), position 0 is subcommand.
        # If it's a standard tool (nmap), position 0 is target.
        
        # Heuristic:
        # Put Ordered Parts (Positionals) FIRST if they are likely subcommands (no dots/slashes? just alpha?).
        # Then Flags.
        # Then Remaining Positionals.
        
        # Actually, let's look at `nmap.yaml` again.
        # target position: 0.
        # If we put target first, `nmap target -p port` works.
        # So we can just put Ordered parts, then Flags, then End parts.
        # But wait, `additional_args` usually needs to be at the end? 
        # In my logic above, `additional_args` went to `end_parts`.
        
        final_args = []
        
        # 1. Ordered Positionals
        for _, part in ordered_parts:
            final_args.extend(part)
            
        # 2. Flags
        for part in flags_parts:
            final_args.extend(part)
            
        # 3. End parts (Unordered positionals)
        for part in end_parts:
            final_args.extend(part)

        command.extend(final_args)

        # Pre-execution hooks
        if tool_name == 'msfconsole':
            self._ensure_msf_exit(args)
            
            # Force append 'exit -y' to command if it's an inline search or command execution
            # This handles cases like `msfconsole -x "search ..."` where there is no .rc file
            # We check if '-x' is in the arguments or command list
            
            # Helper to find and patch -x argument
            keep_session = bool(args.get("keep_session"))
            for i, arg in enumerate(command):
                if arg == '-x':
                    if i + 1 < len(command):
                        existing_cmd = command[i+1]
                        if (not keep_session) and ('exit' not in existing_cmd):
                            command[i+1] = f"{existing_cmd}; exit -y"
                            logger.info(f"[AutoFix] Appended 'exit -y' to msfconsole -x command.")
                            
        logger.info(f"Executing: {' '.join(command)}")
        
        try:
            env = os.environ.copy()
            env["PULSE_SERVER"] = "tcp:127.0.0.1:4713"
            env["PULSE_CLIENTCONFIG"] = os.devnull
            env["PULSE_COOKIE"] = os.devnull
            timeout_s = float(tool_def.get("timeout_seconds", 900))

            cwd = None
            workdir_mode = (os.getenv("TOOL_WORKDIR_MODE", "project") or "project").strip().lower()
            if self.base_dir:
                if workdir_mode == "isolated" and task_id:
                    cwd = os.path.join(self.base_dir, "data", "temp", "tool_runs", task_id)
                    os.makedirs(cwd, exist_ok=True)
                elif workdir_mode == "project":
                    cwd = self.base_dir
                elif workdir_mode == "inherit":
                    cwd = None

            cancel_flag = None
            if task_id:
                cancel_flag = threading.Event()
                with self._lock:
                    self._cancel_flags[task_id] = cancel_flag

            try:
                command, _ = self._wrap_with_docker(command, tool_def=tool_def, cwd=cwd, task_id=task_id)
            except Exception as e:
                return "", str(e), -1
            
            if tool_name == 'msfconsole':
                keep_session = bool(args.get("keep_session")) and bool(task_id)
                if keep_session and task_id:
                    started = self.msf_cli_start(task_id=task_id, command=command, cwd=cwd, env=env)
                    wait_s = args.get("wait_session_seconds", 90)
                    try:
                        wait_s = float(wait_s)
                    except Exception:
                        wait_s = 90.0
                    wait_s = max(5.0, min(wait_s, 600.0))

                    begin = time.time()
                    cursor = 0
                    acc: list[str] = []
                    sess_id = None
                    while time.time() - begin < wait_s:
                        out = self.msf_cli_output(task_id, since_seq=cursor, limit=800)
                        cursor = int(out.get("seq") or cursor)
                        for item in out.get("lines") or []:
                            ln = str(item.get("line") or "")
                            acc.append(ln)
                            m = re.search(r"(?:command shell|meterpreter)?\s*session\s+(\d+)\s+opened", ln, re.IGNORECASE)
                            if m:
                                sess_id = str(m.group(1) or "").strip() or sess_id
                        if sess_id:
                            break
                        time.sleep(0.2)

                    captured = "".join(acc)
                    enhanced = MsfParser.enhance_output(captured)
                    pid = int(started.get("pid") or 0)
                    if not sess_id:
                        self.msf_cli_stop(task_id)
                        tip = "\n\n[系统提示] 未识别到已打开会话（超时等待）。已自动停止 MSF 进程，避免占用资源。\n"
                        return enhanced + tip, "", 0

                    tip = "\n\n[系统提示] 已保留 MSF 连接（交互式进程保持运行）。请在漏洞详情页的 CLI 面板中手动接管。\n"
                    if pid:
                        tip += f"[系统提示] MSF CLI PID: {pid}\n"
                    tip += f"[系统提示] 识别到会话 Session {sess_id} opened。\n"
                    return enhanced + tip, "", 0

                process = None
                try:
                    popen_kwargs: Dict[str, Any] = {
                        "stdout": subprocess.PIPE,
                        "stderr": subprocess.PIPE,
                        "text": True,
                        "bufsize": 1,
                        "encoding": "utf-8",
                        "errors": "replace",
                        "env": env,
                        "cwd": cwd,
                    }
                    if os.name == "nt":
                        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
                    else:
                        popen_kwargs["start_new_session"] = True

                    process = subprocess.Popen(command, **popen_kwargs)
                    if task_id:
                        with self._lock:
                            self._running[task_id] = process

                    q = queue.Queue()
                    t_out = threading.Thread(target=self._stream_reader, args=(process.stdout, q, "out"))
                    t_err = threading.Thread(target=self._stream_reader, args=(process.stderr, q, "err"))
                    t_out.daemon = True
                    t_err.daemon = True
                    t_out.start()
                    t_err.start()

                    stdout_acc: list[str] = []
                    stderr_acc: list[str] = []
                    truncated_out = [False]
                    truncated_err = [False]
                    max_chars = int(os.getenv("TOOL_MAX_OUTPUT_CHARS", "200000"))

                    start_time = time.time()
                    last_output_time = time.time()
                    max_idle_time = float(tool_def.get("idle_timeout_seconds", 120))

                    while True:
                        if cancel_flag and cancel_flag.is_set():
                            self._kill_process_tree(process)
                            msg = "\n[系统提示] MSF 执行已被用户取消。"
                            self._append_limited(stdout_acc, msg, max_chars, truncated_out)
                            retcode = -2
                            break

                        retcode = process.poll()
                        while True:
                            try:
                                tag, line = q.get_nowait()
                                last_output_time = time.time()
                                if tag == "out":
                                    self._append_limited(stdout_acc, line, max_chars, truncated_out)
                                else:
                                    self._append_limited(stderr_acc, line, max_chars, truncated_err)
                            except queue.Empty:
                                break

                        if retcode is not None:
                            break

                        if time.time() - start_time > timeout_s:
                            self._kill_process_tree(process)
                            msg = f"\n[System] MSFConsole execution timed out ({int(timeout_s)}s). Process killed."
                            self._append_limited(stdout_acc, msg, max_chars, truncated_out)
                            self._append_limited(stderr_acc, msg, max_chars, truncated_err)
                            retcode = -1
                            break

                        if time.time() - last_output_time > max_idle_time:
                            self._kill_process_tree(process)
                            msg = f"\n[System] MSFConsole idle for {int(max_idle_time)}s. Assuming hang/interactive wait. Process killed."
                            self._append_limited(stdout_acc, msg, max_chars, truncated_out)
                            self._append_limited(stderr_acc, msg, max_chars, truncated_err)
                            retcode = -1
                            break

                        time.sleep(0.5)

                    t_out.join(timeout=1)
                    t_err.join(timeout=1)
                    stdout = "".join(stdout_acc)
                    stderr = "".join(stderr_acc)
                finally:
                    if task_id:
                        with self._lock:
                            self._running.pop(task_id, None)
                            self._cancel_flags.pop(task_id, None)
                            self._docker_cidfiles.pop(task_id, None)
                
                # Enhanced output for msfconsole
                stdout = MsfParser.enhance_output(stdout)
                
                status_msg = ""
                if retcode == 0:
                     status_msg = "\n[系统提示] MSF 执行完成。"
                else:
                     status_msg = f"\n[系统提示] MSF 执行结束 (Code: {retcode})。"
                
                return stdout + status_msg, stderr, retcode

            try:
                stdout, stderr, retcode = self._execute_generic_monitored(
                    command=command,
                    env=env,
                    timeout_s=timeout_s,
                    cancel_flag=cancel_flag,
                    cwd=cwd,
                    task_id=task_id,
                )
            finally:
                if task_id:
                    with self._lock:
                        self._cancel_flags.pop(task_id, None)
                        self._docker_cidfiles.pop(task_id, None)

            status_msg = ""
            if retcode == 0:
                if not stdout.strip() and not stderr.strip():
                    status_msg = "\n[系统提示] 工具执行完成，但没有输出内容。请检查参数是否正确，或目标是否存活。"
                else:
                    status_msg = "\n[系统提示] 工具执行成功完成 (Return Code: 0)。"
            elif retcode == -2:
                status_msg = "\n[系统提示] 工具执行已取消。"
            else:
                status_msg = f"\n[系统提示] 工具执行结束 (Return Code: {retcode})。请检查输出与错误信息。"

            return stdout + status_msg, stderr, retcode
        except Exception as e:
            return "", str(e), -1
