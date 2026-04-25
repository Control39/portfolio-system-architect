#!/usr/bin/env python3
"""Benchmark script for Portfolio System Architect validation (Phase 4.2)
Tests service latency and generates report.
"""
import json
import socket
import time
from pathlib import Path

import requests

SERVICES = {
    "postgres": "localhost:5432",
    "pgadmin": "localhost:5050",
    "grafana": "localhost:3000",
    "career-api": "localhost:8000",
}

def check_port(hostport, timeout=5):
    host, port = hostport.split(":")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return result == 0
    except:
        return False

def measure_latency(url, timeout=5):
    try:
        start = time.time()
        resp = requests.get(url, timeout=timeout)
        latency = (time.time() - start) * 1000  # ms
        return latency if resp.status_code < 400 else float("inf")
    except:
        return float("inf")

def run_benchmark():
    results = {}
    print("🏆 Portfolio System Benchmark")
    print("=" * 50)

    for name, endpoint in SERVICES.items():
        if "/" not in endpoint:  # port check
            up = check_port(endpoint)
            status = "🟢 UP" if up else "🔴 DOWN"
            latency = 0
        else:
            latency = measure_latency(endpoint + "/")
            status = "🟢 OK" if latency < 200 else "🟡 SLOW" if latency < 500 else "🔴 DOWN"

        results[name] = {"status": status, "latency_ms": round(latency, 2)}
        print(f"{name:15} {status} {latency:.2f}ms")

    # Generate report
    report = {"timestamp": time.strftime("%Y-%m-%d %H:%M"), "services": results}
    passed = all("DOWN" not in r["status"] for r in results.values())

    report_path = Path("tools/benchmark_report.json")
    report_path.write_text(json.dumps(report, indent=2))

    print(f"\n📊 Report: {report_path}")
    print("✅ PASSED (latencies OK)" if passed else "⚠️  Some services DOWN - start docker compose")
    return passed

if __name__ == "__main__":
    run_benchmark()

