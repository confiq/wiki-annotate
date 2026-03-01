#!/usr/bin/env python3
"""
Cleanup old cache files — keeps only the latest file per page directory.
Run as a cron job, e.g.:
    0 3 * * * /path/to/.venv/bin/python /path/to/scripts/cleanup_cache.py
"""
import os
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'data-page', 'v1'))


def cleanup(dry_run: bool = False):
    if not os.path.exists(DATA_DIR):
        log.info(f"Data directory {DATA_DIR} does not exist, nothing to do.")
        return

    total_deleted = 0
    total_freed = 0

    for wikiid in os.listdir(DATA_DIR):
        wiki_dir = os.path.join(DATA_DIR, wikiid)
        if not os.path.isdir(wiki_dir):
            continue
        for page in os.listdir(wiki_dir):
            page_dir = os.path.join(wiki_dir, page)
            if not os.path.isdir(page_dir):
                continue

            files = [f for f in os.listdir(page_dir) if f.endswith('.json')]
            if len(files) <= 1:
                continue

            files_with_mtime = [(f, os.path.getmtime(os.path.join(page_dir, f))) for f in files]
            files_with_mtime.sort(key=lambda x: x[1], reverse=True)
            to_keep = files_with_mtime[0][0]
            to_delete = [f for f, _ in files_with_mtime[1:]]

            for f in to_delete:
                fpath = os.path.join(page_dir, f)
                size = os.path.getsize(fpath)
                if not dry_run:
                    os.remove(fpath)
                total_deleted += 1
                total_freed += size

            action = "would remove" if dry_run else "removed"
            log.info(f"{wikiid}/{page}: kept {to_keep}, {action} {len(to_delete)} old file(s)")

    log.info(f"Done. {'Would free' if dry_run else 'Freed'} {total_freed / 1024 / 1024:.1f} MB across {total_deleted} file(s)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up old wiki-annotate cache files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without deleting")
    args = parser.parse_args()
    cleanup(dry_run=args.dry_run)
