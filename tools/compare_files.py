import hashlib


def hash_file(file_path):
    """Вычислить SHA256 хеш файла."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


if __name__ == "__main__":
    file1 = "c:\\Users\\Z\\DeveloperEnvironment\\projects\\portfolio-system-architect-fresh\\apps\\career_development\\api\\app.py"
    file2 = "c:\\Users\\Z\\DeveloperEnvironment\\projects\\portfolio-system-architect-fresh\\apps\\career_development\\src\\api\\app.py"

    hash1 = hash_file(file1)
    hash2 = hash_file(file2)

    print(f"Хеш {file1}: {hash1}")
    print(f"Хеш {file2}: {hash2}")

    if hash1 == hash2:
        print("Файлы идентичны.")
    else:
        print("Файлы различаются.")
