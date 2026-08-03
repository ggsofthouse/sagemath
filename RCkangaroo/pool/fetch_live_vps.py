import paramiko
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    env_vars = {}
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env_vars[k] = v

    host = env_vars.get("VPS_HOST", "179.197.231.166")
    user = env_vars.get("VPS_USER", "root")
    password = env_vars.get("VPS_PASS", "Gg@005500441133")

    print(f"Connecting to VPS ({user}@{host})...\n")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password, timeout=15)

    py_db_cmd = """python3 -c "import sqlite3; conn = sqlite3.connect('/opt/rckangaroo/pool/server/pool.db'); c = conn.cursor(); total = c.execute('SELECT COUNT(*) FROM chunks').fetchone()[0]; completed = c.execute('SELECT COUNT(*) FROM chunks WHERE status=\\"COMPLETED\\"').fetchone()[0]; keys_tested = completed * (2**66); keys_septillion = keys_tested / (10**24); print('TOTAL DE CHUNKS:', total); print('CHUNKS STATUS COMPLETED (SALVOS):', completed); print('CHAVES APROXIMADAS TESTADAS:', f'{keys_tested:,}'); print('CHAVES EM SEPTILHÕES DE CHAVES: %.4f Septilhoes' % keys_septillion); jobs = c.execute('SELECT job_id, start_percent, end_percent, current_offset_hex FROM jobs').fetchall(); [print('Job %s (%.1f%% -> %.1f%%): %d chunks COMPLETED' % (j[0], j[1], j[2], c.execute('SELECT COUNT(*) FROM chunks WHERE job_id=? AND status=\\"COMPLETED\\"', (j[0],)).fetchone()[0])) for j in jobs]" """

    commands = [
        ("DETALHAMENTO DE CHUNKS & CHAVES TESTADAS DIRETO DO SQLITE (pool.db)", py_db_cmd)
    ]

    for title, cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        out = stdout.read().decode('utf-8', errors='replace')
        err = stderr.read().decode('utf-8', errors='replace')
        if out:
            print(out)
        if err:
            print("[ERR]", err)
        print("\n")

    ssh.close()

if __name__ == "__main__":
    main()
