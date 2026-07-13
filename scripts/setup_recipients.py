#!/usr/bin/env python3
"""Setup script to configure email recipients"""

import sys
from pathlib import Path
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def setup_recipients():
    """Copy recipients.yaml.example to recipients.yaml"""
    config_dir = Path(__file__).parent.parent / "config"
    
    example_file = config_dir / "recipients.yaml.example"
    target_file = config_dir / "recipients.yaml"
    
    if target_file.exists():
        print(f"✓ {target_file} already exists")
        response = input("Overwrite with template? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            return
    
    if not example_file.exists():
        print(f"✗ Template not found: {example_file}")
        return
    
    # Copy template
    shutil.copy(example_file, target_file)
    print(f"✓ Created {target_file}")
    print("\nNext steps:")
    print(f"1. Edit {target_file}")
    print("2. Replace example@example.com with your email addresses")
    print("3. This file is gitignored - your emails stay private")


if __name__ == "__main__":
    setup_recipients()
