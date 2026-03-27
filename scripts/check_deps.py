import os
import shutil
import sys


REQUIRED_TOOLS = [
    "nmap",
    "sqlmap",
    "gobuster",
    "hydra",
    "dirsearch",
    "nuclei",
    "subfinder",
    "ssh",
    "ncat",
    "searchsploit",
]


def main() -> int:
    strict = os.getenv("STRICT_DEPS", "0").strip().lower() in ("1", "true", "yes", "y")
    missing = [t for t in REQUIRED_TOOLS if not shutil.which(t)]

    if missing:
        sys.stderr.write("[check_deps] Missing tools: " + ", ".join(missing) + "\n")
        if strict:
            return 1
        sys.stderr.write("[check_deps] STRICT_DEPS not enabled; continuing.\n")
        return 0

    sys.stdout.write("[check_deps] OK\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
