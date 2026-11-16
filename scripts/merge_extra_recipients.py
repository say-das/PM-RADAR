"""Merge extra recipients (from EXTRA_RECIPIENTS env, comma/space separated)
into config/recipients.yaml under topics.<topic>, without duplicates.

Usage: python scripts/merge_extra_recipients.py <topic> [--only-extra]
  --only-extra  replace the topic's list (and global) with just the extras
"""
import os
import re
import sys
from pathlib import Path

import yaml

PATH = Path("config/recipients.yaml")


def main():
    topic = sys.argv[1]
    only_extra = "--only-extra" in sys.argv
    extras = [e.strip() for e in re.split(r"[,\s]+", os.environ.get("EXTRA_RECIPIENTS", "")) if e.strip()]
    if only_extra and not extras:
        sys.exit("--only-extra set but EXTRA_RECIPIENTS is empty")

    cfg = yaml.safe_load(PATH.read_text()) or {}
    topics = cfg.setdefault("topics", {})
    current = [] if only_extra else list(topics.get(topic) or [])
    seen = {e.lower() for e in current}
    current += [e for e in extras if e.lower() not in seen]
    topics[topic] = current
    if only_extra:
        cfg["global"] = []

    PATH.write_text(yaml.safe_dump(cfg, sort_keys=False))
    print(f"recipients for '{topic}': {len(current)} (extras added: {len(extras)})")


if __name__ == "__main__":
    main()
