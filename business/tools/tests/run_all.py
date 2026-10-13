"""Run every offline test against the stand-in AI server.

    python tests/run_all.py        (from business/tools)

Exit code 0 means every check passed. No API keys are used and nothing costs money.
"""
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> int:
    port = free_port()
    server = subprocess.Popen([sys.executable, str(HERE / "fake_llm.py"), str(port)])
    time.sleep(1)
    passed = failed = 0
    try:
        for test in sorted(HERE.glob("test_*.py")):
            with tempfile.TemporaryDirectory() as tmp:
                env = {**os.environ, "LOCAL_URL": f"http://localhost:{port}/v1", "T": tmp,
                       "PYTHONIOENCODING": "utf-8", "LOCAL_DISABLED": ""}
                for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "PERPLEXITY_API_KEY",
                          "IMAP_USER", "IMAP_PASSWORD"):
                    env[k] = ""  # never touch real accounts from tests
                out = subprocess.run([sys.executable, str(test)], env=env, capture_output=True, text=True,
                                     encoding="utf-8", errors="replace", timeout=600)
            lines = [l for l in out.stdout.splitlines() if l.startswith(("PASS", "FAIL"))]
            p, f = sum(l.startswith("PASS") for l in lines), sum(l.startswith("FAIL") for l in lines)
            passed, failed = passed + p, failed + f
            status = "ok" if f == 0 and out.returncode == 0 and "done" in out.stdout else "PROBLEM"
            print(f"{test.name}: {p} passed, {f} failed [{status}]")
            for l in lines:
                if l.startswith("FAIL"):
                    print("   ", l)
            if status != "ok" and out.returncode != 0:
                print(out.stderr[-2000:])
                failed += 1 if f == 0 else 0
    finally:
        server.terminate()
    print(f"\nTOTAL: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
