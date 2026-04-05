#!/usr/bin/env python3
"""
Search for models in the Hugging Face Hub.

Usage:
    python hf_search.py -q "your search query" [options]

Examples:
    python hf_search.py -q "transformer"
    python hf_search.py -q "vision"
    python hf_search.py -t space -q "interactive"
    python hf_search.py -t space -t dataset -q "interactive"
"""

import argparse
import json
from typing import Optional
from huggingface_hub import HfApi


def search_models(
    query: str,
    filter: Optional[str] = None,
    limit: Optional[int] = 10,
    sort: Optional[str] = None,
    token: Optional[str] = None,
) -> list:
    """
    Search for models in the Hugging Face Hub.

    Args:
        query: Search query string.
        filter: Filter option (e.g. "tag:transformer", "type:image-model", "author:dylanvrck”).
               Can be an AND filter (e.g., "tag:transformer AND license:mit”).
        limit: Maximum number of results to return (default: 10).
        sort: Sort criterion (e.g. "downloads_last_7_days", "likes", "trending_date”).
        directions: Sort order ("asc" or "desc"). Default: "desc”.
        token: Hugging Face token for private repositories (optional).
        cursor: Cursor for pagination (default: None).

    Returns:
        List of model dictionaries with key information.
    """
    api = HfApi(token=token)
    
    try:
        models = api.list_models(
            search=query,
            filter=filter,
            limit=limit,
            sort=sort,
            token=token,
        )
        result = list(models)
        return result[:limit] if len(result) > limit else result
    except Exception as e:
        print(f"Hugging Face API error: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Search for models in the Hugging Face Hub."
    )
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        required=True,
        help="Search query (e.g., 'transformer', 'vision')"
    )
    parser.add_argument(
        "-t",
        "--tag",
        type=str,
        action="append",
        help="Add a tag filter. Can be specified multiple times for AND filtering (e.g., '-t transformer -t vision')"
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results. Default: 10"
    )


    parser.add_argument(
        "-f",
        "--filter",
        type=str,
        default=None,
        help="Additional filter string (e.g., 'tag:transformer', 'license:mit')"
    )
    parser.add_argument(
        "-j",
        "--json",
        type=str,
        default="",
        help="Output format: 'json'. Default: plain"
    )
    parser.add_argument(
        "-k",
        "--token",
        type=str,
        default=None,
        help="Hugging Face token for private repositories"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show additional model information (tags, license, size)"
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="",
        help="Output format: 'json' or 'plain'. Default: plain"
    )
    parser.add_argument(
        "-w",
        "--write",
        type=str,
        default="models.json",
        help="File to write results (for json output). Default: models.json"
    )
    parser.add_argument(
        "-s",
        "--sort",
        type=str,
        default=None,
        help="Sort criterion: downloads_last_7_days, likes, trending_date. Default: trending_date"
    )
    parser.add_argument(
        "-d",
        "--direction",
        type=str,
        default="desc",
        help="Sort order: asc or desc. Default: desc"
    )

    args = parser.parse_args()

    # Convert multiple -t (tag) arguments into an AND filter string
    tags = []
    if args.tag:
        for tag in args.tag:
            if tag.endswith(':AND'): 
                tag = tag[:-3] 
            tags.append(tag)
    
    # Build the filter string
    filter_str = None
    if args.filter:
        filter_str = args.filter
    elif tags:
        filter_str = "AND".join(tags)

    # Search models
    models = search_models(
        query=args.query,
        filter=filter_str,
        limit=args.limit,
        sort=args.sort,
        token=args.token,
    )

    # Output results
    if args.output == "json":
        output = json.dumps(models, indent=2)
        if args.write:
            with open(args.write, "w") as f:
                f.write(output)
            print(f"Results written to {args.write}")
        else:
            print(output)
        return

    # Plain text output
    if not models:
        print(f"No results found for: '{args.query}'")
        return

    print(f"Found {len(models)} results for: '{args.query}'")
    print(f"Sorted by: {args.sort}, direction: {args.direction}")
    print("-" * 100)

    for idx, model in enumerate(models, 1):
        print(f"{idx}. {model.id}")
        print(f"   Author: {model.author}")
        if model.tags:
            print(f"   Tags: {', '.join([f'- {tag}' for tag in model.tags[:3]])}")
        print()


def format_bytes(size_bytes: int) -> str:
    """Format bytes into human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024**2:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


if __name__ == "__main__":
    main()
