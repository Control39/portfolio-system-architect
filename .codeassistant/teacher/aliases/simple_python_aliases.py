# Простые Python алиасы для когнитивного архитектора

import os
import subprocess


def run(cmd):
    """Выполнить команду"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error: {e}"


# Git
def gs():
    return run("git status")


def ga():
    return run("git add .")


def gcm(msg):
    return run(f'git commit -m "{msg}"')


def gp():
    return run("git push")


def gpl():
    return run("git pull")


def gl(n=10):
    return run(f"git log --oneline -{n}")


def gb():
    return run("git branch")


# Docker
def dps():
    return run("docker ps")


def dcup():
    return run("docker-compose up -d")


def dcdown():
    return run("docker-compose down")


# Python
def pyv():
    return run("python --version")


def pipi(pkg):
    return run(f"pip install {pkg}")


def pipr():
    return run("pip install -r requirements.txt")


def test():
    return run("pytest")


def lint():
    return run("black --check .")


def fmt():
    return run("black .")


# VS Code
def codec():
    return run("code .")


def codelist():
    return run("code --list-extensions")


# System
def disk():
    total = 0
    for root, dirs, files in os.walk("."):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    gb = total / (1024**3)
    return f"{gb:.2f} GB"


def help():
    print(
        """
=== Python Aliases ===
Git: gs(), ga(), gcm(msg), gp(), gpl(), gl(), gb()
Docker: dps(), dcup(), dcdown()
Python: pyv(), pipi(pkg), pipr(), test(), lint(), fmt()
VS Code: codec(), codelist()
System: disk()
"""
    )


if __name__ == "__main__":
    help()
