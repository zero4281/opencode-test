#!/usr/bin/env python3
"""
Hugging Face Hub Model Search Tool

A CLI tool for searching models on the Hugging Face Hub based on the HF API.
"""

import argparse
import sys
from typing import Optional
try:
    from huggingface_hub import HfApi
except ImportError:
    print("Error: Please install huggingface_hub library.")
    print("  pip install huggingface_hub")
    sys.exit(1)


DEFAULT_API_URL = "https://huggingface.co"
BASE_URL = DEFAULT_API_URL.rstrip("/")


def parse_url(url: Optional[str]) -> Optional[str]:
    """Parse Hugging Face Hub URL and return base URL."""
    if not url:
        return DEFAULT_API_URL
    # Strip common URL suffixes
    url = url.rstrip("/")
    if "/en" in url:
        url = url.replace("/en", "")
    if "/" in url:
        url = url.rsplit("/", 1)[0]
    return url or DEFAULT_API_URL


def search_models(
    api: HfApi,
    search: Optional[str] = None,
    filter: Optional[list] = None,
    author: Optional[str] = None,
    sort: Optional[str] = "lastModified",
    limit: int = 100,
    token: Optional[str] = None,
    _num_parameters: Optional[float] = None,
) -> list:
    """Search for models on the Hub matching given criteria."""
    try:
        models_iterator = api.list_models(search=search, filter=filter, author=author, sort=sort, limit=limit, token=token)
        return list(models_iterator)
    except Exception as e:
        print(f"Error searching models: {e}")
        return []


def format_model_info(model) -> str:
    """Format and return user-friendly info about a model."""
    try:
        size = model.num_parameters
        size_str = "N/A"
        if size < 1_000_000_000:
            size_str = f"{size / 1_000_000:.1f}M"
        elif size < 1_000_000_000_000:
            size_str = f"{size / 1_000_000_000:.1f}B"
        else:
            size_str = f"{size / 1_000_000_000_000:.1f}T"
    except AttributeError:
        size_str = "N/A"

    try:
        date = model.last_modified
        date_str = date.strftime("%Y-%m-%d") if date else "N/A"
    except AttributeError:
        date_str = "N/A"

    try:
        downloads = model.downloads
        downloads_str = f"{downloads:,.0f}"
    except AttributeError:
        downloads_str = "N/A"

    tags = ", ".join(model.tags) if model.tags else "N/A"

    return f"{model.id[:20]:20} | {size_str:>10} | {date_str:>10} | {downloads_str:>12} | {tags[:50]:<50}"


def main():
    parser = argparse.ArgumentParser(description="Search models on Hugging Face Hub")
    parser.add_argument("-a", "--author", help="Search by author")
    parser.add_argument("-s", "--search", help="Search query")
    parser.add_argument("-t", "--token", help="Hugging Face token")
    parser.add_argument("-o", "--output", help="Output format (json or plain)")
    parser.add_argument("-l", "--limit", type=int, default=100, help="Number of results")
    parser.add_argument("-f", "--filter", type=str, help="Filter by tag")
    parser.add_argument("-n", "--num-parameters", help="Filter by number of parameters")
    args = parser.parse_args()
    
    # Normalize output option
    output_format = args.output
    # Normalize output option
    output_format = args.output

    # Build token if specified
    token = args.token or None

    # Create API client
    api = HfApi(token=token)
    models = search_models(
        api,
        search=args.search,
        filter=args.filter,
        author=args.author,
        _num_parameters=args.num_parameters,
        sort="lastModified",
        limit=args.limit,
    )

    # Output results
    if args.output == "json":
        import json
        print(json.dumps(models, indent=2, default=str))
    else:
        if not models:
            print("No models found.")
            return

        # Print header
        header = "  ID              | SIZE   | DATE      | DOWNLOADS | TAGS"
        print(header)
        print("-" * 110)

        # Print each model
        for model in models:
            info_line = format_model_info(model)
            print(info_line)


if __name__ == "__main__":
    main()
