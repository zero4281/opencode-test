#!/usr/bin/env python3
"""Search Hugging Face models via API."""

import argparse
import sys
from typing import Optional

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    from huggingface_hub import HfApi
    HAS_HF_HUB = True
except ImportError:
    HAS_HF_HUB = False
    print("Error: huggingface-hub package not installed.", file=sys.stderr)
    print("Install it with: pip install huggingface-hub", file=sys.stderr)
    sys.exit(1)


def search_models(query: str, limit: int = 100, token: Optional[str] = None):
    """
    Search models on Hugging Face Hub.
    
    Args:
        query: (ignored - we get first N models)
        limit: Max results to return (default: 100)
        token: Optional auth token
    
    Returns:
        list of ModelInfo dicts
    """
    if not HAS_HF_HUB:
        return []
    
    api = HfApi(token=token)
    results = []
    
    # Use list_models iterator directly
    model_iter = api.list_models(limit=limit, full=True)
    
    for model in model_iter:
        try:
            author = model.author or "Unknown"
        except AttributeError:
            author = "Unknown"
        
        try:
            lang = model.language or "Unknown"
        except AttributeError:
            lang = "Unknown"
        
        tags = getattr(model, "pipeline_tag", None)
        
        results.append({
            "id": model.id,
            "name": model.modelId.split("/")[-1] if model.modelId else model.id,
            "author": author,
            "downloads": model.downloads,
            "likes": model.likes,
            "language": lang,
            "tags": tags,
            "private": model.private,
            "gated": model.gated,
        })
        
        if len(results) >= limit:
            break
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Search Hugging Face models')
    parser.add_argument('-q', '--query', default='', help='Search query')
    parser.add_argument('-l', '--limit', type=int, default=100, help='Max results')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('--token', help='Auth token')
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        return
    
    results = search_models(
        query=args.query,
        limit=args.limit,
        token=args.token
    )
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            for m in results[:10]:
                lines = [
                    f"id: {m['id']}",
                    f"name: {m['name']}",
                    f"author: {m['author']}",
                    f"downloads: {m['downloads']}",
                    f"likes: {m['likes']}",
                    f"private: {m['private']}",
                ]
                if m['gated']:
                    lines.append("gated: True")
                f.write('|\n'.join(lines))
        print(f"Saved {len(results)} models")
    else:
        for m in results[:10]:
            gated = " \u26a0\ufe0f" if m['gated'] else ""
            priv = " \ud83d\udd10" if m['private'] else ""
            print(f"{m['name']} {gated}{priv}")
            print(f"    Author: {m['author']}")
            print(f"    Downloads: {m['downloads']:,}")
            print(f"    Likes: {m['likes']:,}")
            print()

if __name__ == '__main__':
    main()
