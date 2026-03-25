#!/usr/bin/env python3
"""Automatische Slug-Generierung aus dem Titel.

Usage:
    python auto_slug.py "Mein cooler Titel" -> "mein-cooler-titel"
"""

import re
import sys

def slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def main():
    if len(sys.argv) < 2:
        print("Usage: python auto_slug.py \"<title>\"")
        sys.exit(1)
    
    title = sys.argv[1]
    slug = slugify(title)
    print(slug)

if __name__ == "__main__":
    main()