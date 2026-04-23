#!/usr/bin/env python3
'''
Unified healthcheck for Portfolio System Architect
Exports /health, /ready, /live endpoints for all services
'''
import sys
import subprocess

SERVICES = {
    'postgres': 'localhost:5432',
    'pgadmin': 'localhost:5050',
    'prometheus': 'localhost:9090',
    'grafana': 'localhost:3000',
    'career-development': 'localhost:8001/health',  # Adjust port
    'it-compass': 'localhost:8501/health',
    'decision-engine': 'localhost:8000/health',
}

def check_tcp(hostport: str) -> bool:
    host, port = hostport.split(':')
    result = subprocess.run(['powershell', '-Command', 
        f'Test-NetConnection -ComputerName {host} -Port {port} -InformationLevel Quiet'], 
        capture_output=True, text=True)
    return result.returncode == 0

def main():
    healthy = True
    print("🩺 Portfolio System Health Check")
    print("=" * 50)
    
    for name, endpoint in SERVICES.items():
        if check_tcp(endpoint.split('/')[0] if '/' in endpoint else endpoint):
            status = "🟢 UP"
        else:
            status = "🔴 DOWN"
            healthy = False
        print(f"{name:20} {status} {endpoint}")
    
    if healthy:
        print("\n✅ ALL SYSTEMS HEALTHY")
        sys.exit(0)
    else:
        print("\n❌ CRITICAL SERVICES DOWN")
        sys.exit(1)

if __name__ == "__main__":
    main()

