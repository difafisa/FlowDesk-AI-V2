import subprocess, sys, time
import psutil

def main():
    if len(sys.argv) < 2:
        print("pakai: python scripts/measure_ram.py <script/module + args>")
        sys.exit(1)
    cmd = [sys.executable] + sys.argv[1:]
    print("menjalankan:", " ".join(cmd), "\n")
    start = time.monotonic()

    proc = subprocess.Popen(cmd)
    parent = psutil.Process(proc.pid)
    peak_rss = 0
    n_samples = 0
    while proc.poll() is None:
        try:
            total = parent.memory_info().rss          # proses utama
            for child in parent.children(recursive=True):
                total += child.memory_info().rss      # + seluruh process tree
            peak_rss = max(peak_rss, total)
            n_samples += 1
        except psutil.Error:
            pass                                      # proses sudah exit saat poll
        time.sleep(0.2)                               # sampling 5x per detik

    dur = time.monotonic() - start
    print("\n=== RAM measurement ===")
    print(f"exit code     : {proc.returncode}")
    print(f"duration      : {dur:.0f} s")
    print(f"samples       : {n_samples} (interval 0.2 s)")
    print(f"RAM peak (RSS): {peak_rss / 1024**3:.2f} GB")
    print(f"                {peak_rss / 1024**2:.0f} MB")

if __name__ == "__main__":
    main()
