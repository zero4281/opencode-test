import sys
import os
from huggingface_hub import HfApi
from typing import Optional, List
import argparse

HUGGINGFACE_HUB_LINK = "https://huggingface.co"


def create_api_instance(token: str = None) -> HfApi:
    """Create and configure HfApi instance."""
    api = HfApi()
    if token:
        api.token = token
    return api


class ModelSearcher:
    """Interface for searching models in the Hugging Face Hub."""

    def __init__(self, token: Optional[str] = None):
        self.api = create_api_instance(token)
        self.token = token
        self.query: Optional[str] = None
        self.limit: int = 5

    def search_text(self, query: str, limit: int = 5) -> List[dict]:
        """Search for models with given query using HfApi's root method."""
        self.query = query
        self.limit = limit
        models = list(self.api.list_models(search=query, limit=limit))
        return models


    def get_results_text(self, models: List, limit: int = 5, show_desc: bool = False) -> List[str]:
        """Format model results as text."""
        if not models:
            return []

        def truncate(text: str, max_len: int = 100, suffix: str = ". ..") -> str:
            if not text:
                return text
            if len(text) <= max_len:
                return text
            return text[:max_len].rstrip() + suffix

        results = []
        for r in models[:limit]:
            truncate_id = truncate(r.modelId, 80)
            id_line = f"{r.id} ({truncate_id})" if truncate_id else ".?"
            metadata = f"  Author: {r.author or '.'} | Downloads: {r.downloads:10,} | Likes: {r.likes}"
            tag_line = f"  Tags: {', '.join(r.tags[:5])}..." if r.tags else ""
            results.append(id_line + metadata + tag_line)
        return results



def main():
    """Run some example searches."""
    parser = argparse.ArgumentParser(description="Search HuggingFace models")
    parser.add_argument("-a", "--arg", help="Search argument", default="llama")
    parser.add_argument("-t", "--token", help="HuggingFace API token (optional)", default=None)
    parser.add_argument("-l", "--limit", help="Results limit", type=int, default=10)
    args = parser.parse_args()

    searcher = ModelSearcher(token=args.token)

    query = args.arg

    h = 80
    print(f"\n{'=' * h}")
    print(f"{'ID':<51} | {'Author':<21} | {'Downloads':>13} | {'Likes':>7}")
    print(f"{'=' * h}")
    print(f"{'Search Results for: ' + query.title()}")
    print(f"{'=' * h}")
    print("-" * 60)
    models = searcher.search_text(query, limit=args.limit)

    formatted = searcher.get_results_text(models, limit=args.limit)
    for line in formatted:
        print(line)

    print(f"\nTotal found: {len(models)}")
    print("-" * 60)
    print("=" * h)



if __name__ == "__main__":
    main()
