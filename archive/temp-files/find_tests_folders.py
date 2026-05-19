import os


for root, dirs, files in os.walk("."):
    for d in dirs:
        if "tests" in d.lower():
            full_path = os.path.join(root, d)
            print(full_path)
