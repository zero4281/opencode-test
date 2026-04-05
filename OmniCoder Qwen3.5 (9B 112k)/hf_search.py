#!/usr/bin/env python3
"""Interactive HuggingFace Hub model search tool."""

import argparse
import sys
from textwrap import dedent

from huggingface_hub import HfApi, list_models


def create_parser():
    parser = argparse.ArgumentParser(
        description="Search models in the Hugging Face Hub",
        epilog="""
Examples:
  Search models
  python hf_search.py

  Search with filters
  python hf_search.py --search "llama" --limit 30

  Filter by library
  python hf_search.py --library torch

  Export to JSON
  python hf_search.py --search "bge" --limit 20 --out models.json

  Sort by downloads
  python hf_search.py --sort downloads
        """,
    )

    # Required/optional args
    parser.add_argument("-q", "--query", help="Query string to search")
    parser.add_argument("-l", "--limit", type=int, default=100, help="Max results (default 100)")
    parser.add_argument("-t", "--tag", help="Filter by tag (e.g. 'text-generation')")
    parser.add_argument("-f", "--filter", help="Filter by library/framework (e.g. 'torch')")
    parser.add_argument("-s", "--sort", choices=["downloads", "lastModified", "likes", "createdAt"],
                        default="downloads", help="Sort by (default: downloads)")
    parser.add_argument("--library", help="Filter by library/type (e.g. 'text-classification')")
    parser.add_argument("--author", help="Filter by author/organization")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--out", help="Output JSON file path")
    parser.add_argument("-w", "--width", type=int, default=80, help="Terminal width for table")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show more details (tags etc.)")
    
    return parser


def format_size(n):
    """Format bytes into human readable."""
    units = ["B", "KB", "MB", "GB"]
    if n < 1024:
        return f"{n:.1f} {units[0]}"
    i = 1
    while n >= 1024 and i < 3:
        n /= 1024
        i += 1
    return f"{n:.1f} {units[i] if i < 4 else 'TB'}"


def format_tag(tag):
    """Format tag for display."""
    for library, name in [
        ("text-generation", "Text Generation"),
        ("text-classification", "Text Classification"),
        ("token-classification", "Token Classification"),
        ("question-answering", "Question Answering"),
        ("summarization", "Summarization"),
        ("translation", "Translation"),
        ("translation", "Translation"),
        ("translation", "Translation"),
        ("tabular-classification", "Tabular Classification"),
        ("tabular-regression", "Tabular Regression"),
        ("tabular-forecasting", "Tabular Forecasting"),
        ("image-classification", "Image Classification"),
        ("image-segmentation", "Image Segmentation"),
        ("image-to-text", "Image to Text"),
    ]:
        if name and f"{library}:" in tag:
            return f"{name}:{tag}"
    return tag


def pretty_print(results, verbose=False, json_mode=False, out_file=None):
    """Print results nicely."""
    if json_mode:
        data = [{
            "id": r.id,
            "author": r.author,
            "library": r.library,
            "tags": r.tags,
            "likes": r.likes,
            "downloads": r.downloads,
            "safetensors": r.safetensors,  # True if safetensors format
            "pipeline_tag": r.pipeline_tag,
        } for r in results]
        
        if out_file:
            import json
            with open(out_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        else:
            print(json.dumps(data, indent=2, default=str))
        return

    # Create a table
   # Header
    print(f"\n{'='*78}")
    print(f"\nFound {len(results):,} results. Showing first {min(len(results), 50)}...\n")
    print(f"{'ID':<55} {'Author':<18} {'Likes':>8} {'Downloads':>10}")
    print(f"{'-'*55}{'-'*18}{''*8}{''*10}")
    
    for r in results[:50]:
        line = f"{r.id:<55} {r.author or '-':<18} {r.likes or 0:>8,}     {r.downloads or 0:>10,}"
        print(line)
    
    if len(results) > 50:
        print(f"\n... and {len(results) - 50:,} more. Use --limit <N> to increase.")
    
    print(f"\n{'='*78}")


def main():
    parser = create_parser()
    args = parser.parse_args()
    hf = HfApi()

    # Build filter params
    params = {}
    if args.query:
        params["search"] = args.query
    if args.filter:
        params["library"] = args.filter
    if args.tag:
        params["tags"] = args.tag
    if args.library:
        params["library"] = args.library
    if args.author:
        params["author"] = args.author
    if args.sort == "downloads":
        params["sort"] = "downloads"
    elif args.sort == "lastModified":
        params["sort"] = "lastModified"
    elif args.sort == "likes":
        params["sort"] = "likes"
    elif args.sort == "createdAt":
        params["sort"] = "createdAt"
    
    # Default to -1000 (no limit) if not specified, but cap for display
    cap = 1000000 if args.limit is None else args.limit
    
    # Fetch results
    results: list[SearchResult] = list(list_models(**params, full=True, limit=5000))  # Convert generator to list

    print(f"\nQuery: {args.query or 'none'}")
    print(f"Filter: {args.filter or args.tag or args.library or 'none'}")
    print(f"Sort:  {args.sort}")
    print(f"Limit: {cap:,}")

    # Display results (default or JSON mode)
    pretty_print(results, verbose=args.verbose, json_mode=args.json, out_file=args.out)


if __name__ == "__main__":
    main()
