import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

SERVER_URL = "https://valyrafi.com.br"
TARGET_PUZZLE = 140

SLICES = [
    (30.0, 35.5),
    (35.5, 41.0),
    (41.0, 46.5),
    (46.5, 52.0),
    (52.0, 57.5),
    (57.5, 63.0),
    (63.0, 68.5),
    (68.5, 74.0),
    (74.0, 79.5),
    (79.5, 85.0)
]

def main():
    print("Reativando as 10 Fatias da Janela Quente no Servidor...\n")
    for idx, (start_pct, end_pct) in enumerate(SLICES, 1):
        payload = {
            "puzzle_number": TARGET_PUZZLE,
            "start_percent": start_pct,
            "end_percent": end_pct
        }
        url = f"{SERVER_URL}/api/worker/ensure_job"
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                print(f"  Fatia {idx:2d} ({start_pct:4.1f}% -> {end_pct:4.1f}%): Status = {res.get('status')} | Job ID = {res.get('job_id')}")
        except Exception as e:
            print(f"  Erro ao criar Fatia {idx}: {e}")

    print("\nTodas as 10 Fatias foram reativadas com sucesso na VPS!")

if __name__ == "__main__":
    main()
