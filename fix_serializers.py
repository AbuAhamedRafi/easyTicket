#!/usr/bin/env python
"""Fix serializers to use uid instead of id"""

files = [
    "Tickets/serializers.py",
    "Orders/serializers.py",
]

for filepath in files:
    with open(filepath, "r") as f:
        content = f.read()

    # Replace "id", with "uid",
    content = content.replace('"id",', '"uid",')

    with open(filepath, "w") as f:
        f.write(content)

    print(f"Updated {filepath}")

print("All serializers updated!")
