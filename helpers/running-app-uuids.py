"""Generate 100 UUIDs"""

import uuid


def generate_uuids(count=100):
    """Generate specified number of UUIDs"""
    print(f"Generating {count} UUIDs:")
    print("-" * 40)

    for i in range(count):
        new_uuid = str(uuid.uuid4())
        print(f"{i+1:3d}: {new_uuid}")


if __name__ == "__main__":
    generate_uuids()
    print("UUID generation complete.")
