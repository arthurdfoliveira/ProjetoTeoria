import os
import platform
import subprocess


def sh(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout.strip()
    except Exception:
        return ""


def cpu():
    if os.path.exists("/proc/cpuinfo"):
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    return sh("sysctl -n machdep.cpu.brand_string") or platform.processor() or "preencher manualmente"


def ram():
    if os.path.exists("/proc/meminfo"):
        kb = int(open("/proc/meminfo").readline().split()[1])
        return f"{kb / 1024 / 1024:.1f} GiB"
    b = sh("sysctl -n hw.memsize")
    return f"{int(b) / 1024 ** 3:.1f} GiB" if b.isdigit() else "preencher manualmente"


info = [
    f"CPU: {cpu()} ({os.cpu_count()} threads)",
    f"RAM: {ram()}",
    f"SO: {platform.platform()}",
    f"Python: {platform.python_version()} ({platform.python_implementation()}), sem flags (interpretado)",
    f"Node: {sh('node --version')} (V8, JIT; execucao com flags padrao)",
]
os.makedirs("results", exist_ok=True)
with open("results/ambiente.txt", "w") as f:
    f.write("\n".join(info) + "\n")
print("\n".join(info))