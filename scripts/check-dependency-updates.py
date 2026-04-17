#!/usr/bin/env python3
"""
Script to check for dependency updates and generate report.
Run this script manually to see what dependencies need updating.
"""

import subprocess  # nosec: B404 - We need subprocess for system commands
import json
import shutil
from pathlib import Path

def run_command(cmd):
    """Run a shell command and return output.
    
    Args:
        cmd: Command to run as list of arguments
    """
    try:
        # Always use list format for safety
        if isinstance(cmd, str):
            # Split string into list for simple commands
            import shlex
            cmd = shlex.split(cmd)
        # nosec: B603 - We control the commands, no user input
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return ""

def check_pip_updates():
    """Check for outdated Python packages."""
    print("🔍 Checking for outdated Python packages...")
    
    # Get current dependencies from pyproject.toml
    with open("pyproject.toml", "r") as f:
        # Read file but don't assign to variable since we're not using it yet
        _ = f.read()
    
    print("Current dependencies from pyproject.toml:")
    
    # Check outdated packages - use list instead of shell command
    outdated = run_command(["pip", "list", "--outdated", "--format=json"])
    if outdated:
        packages = json.loads(outdated)
        if packages:
            print(f"\n📦 Found {len(packages)} outdated packages:")
            for pkg in packages:
                print(f"  - {pkg['name']}: {pkg['version']} → {pkg['latest_version']}")
            
            # Generate update command
            update_cmd = "pip install --upgrade " + " ".join([pkg['name'] for pkg in packages])
            print(f"\n💡 To update all: {update_cmd}")
        else:
            print("✅ All Python packages are up to date!")
    else:
        print("⚠️  Could not check for outdated packages")

def check_security_vulnerabilities():
    """Check for security vulnerabilities using safety."""
    print("\n🔒 Checking for security vulnerabilities...")
    
    # Check if safety is installed using which/safety --version
    safety_path = shutil.which("safety")
    if not safety_path:
        print("⚠️  Safety not installed. Install with: pip install safety")
        return
    
    try:
        # Run safety check with full path
        result = run_command([safety_path, "check", "--json"])
        if not result:
            print("⚠️  No output from safety check")
            return
        
        try:
            vulnerabilities = json.loads(result)
        except json.JSONDecodeError:
            print("Could not parse safety output")
            return
        
        vuln_list = vulnerabilities.get("vulnerabilities", [])
        if vuln_list:
            print(f"⚠️  Found {len(vuln_list)} security vulnerabilities:")
            for vuln in vuln_list[:5]:  # Show first 5
                pkg_name = vuln.get('package_name', 'Unknown')
                advisory = vuln.get('advisory', 'No details')
                print(f"  - {pkg_name}: {advisory}")
            if len(vuln_list) > 5:
                print(f"  ... and {len(vuln_list) - 5} more")
        else:
            print("✅ No security vulnerabilities found!")
            
    except Exception as e:
        print(f"⚠️  Error running safety: {e}")

def check_docker_updates():
    """Check for Docker base image updates."""
    print("\n🐳 Checking Docker base images...")
    
    dockerfiles = list(Path(".").glob("**/Dockerfile"))
    if dockerfiles:
        print(f"Found {len(dockerfiles)} Dockerfiles:")
        for dockerfile in dockerfiles:
            print(f"  - {dockerfile}")
            # Simple check for FROM lines
            try:
                with open(dockerfile, "r") as f:
                    for line in f:
                        if line.strip().startswith("FROM"):
                            print(f"    Base image: {line.strip()}")
            except Exception as e:
                print(f"    Error reading: {e}")
    else:
        print("No Dockerfiles found")

def generate_report():
    """Generate a summary report."""
    print("\n" + "="*60)
    print("📊 DEPENDENCY UPDATE REPORT")
    print("="*60)
    
    check_pip_updates()
    check_security_vulnerabilities()
    check_docker_updates()
    
    print("\n" + "="*60)
    print("💡 RECOMMENDATIONS:")
    print("1. Review outdated packages above")
    print("2. Run security checks regularly")
    print("3. Update Docker base images monthly")
    print("4. Enable Dependabot for automatic updates")
    print("="*60)

if __name__ == "__main__":
    print("Starting dependency update check...")
    generate_report()
    
    # Save report to file
    with open("dependency-update-report.txt", "w") as f:
        # Redirect stdout to file
        import io
        from contextlib import redirect_stdout
        
        f_capture = io.StringIO()
        with redirect_stdout(f_capture):
            generate_report()
        f.write(f_capture.getvalue())
    
    print("\n📄 Report saved to: dependency-update-report.txt")
