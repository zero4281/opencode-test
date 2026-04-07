#!/usr/bin/env python3
"""Flexible command-line interface for searching Hugging Face Hub models."""

import sys
import argparse
from typing import Optional
import os

from huggingface_hub import HfApi, list_models



def print_models(models, limit: int = 10, header: bool = True) -> None:
    """Print a list of models with pagination control."""
    models_list = list(models)
    if header:
        print(f"\nShowing min(limit, {len(models_list)}) of {len(models_list)} results:\n")
    
    for model in models_list[:limit]:
        print_model(model)
    
    # Show pagination info
    if len(models_list) > limit and header:
        print(f"\n...and {len(models_list) - limit} more")



def print_model(model) -> None:
    """Print a single model in a compact format."""
    info = model.modelId
    if info == model.modelId:
        info = f"{model.modelId} ({model.tags[0]})" if model.tags else model.modelId
        
    display_info = model.modelId
    
    print(f"  {display_info} (S{model_size_str(model)}B {model.tags})" if model.tags else f"  {display_info} (S{model_size_str(model)}B)")



def model_size_str(model) -> str:
    """Get model size as a string."""
    size = model.size_in_bytes if hasattr(model, 'size_in_bytes') else getattr(model, 'size', 0)
    units = ["B", "KB", "MB", "GB", "TB"]
    for i in range(1, 5):
        if size < 1024 ** (i + 1):
            return f"{size / 1024 ** i:.1f}" + units[i-1]
    return f"{size / 1024 ** 5:.1f} PB"



def modelLiked(model) -> bool:
    """Check if model is liked."""
    return model.likedByMe if hasattr(model, 'likedByMe') else model.liked



def modelDownloads(model) -> int:
    """Get model downloads count."""
    return model.likesCount if hasattr(model, 'likesCount') else 0



def modelTotalDownloads(model) -> int:
    """Get total downloads count."""
    return model.downloadsCount if hasattr(model, 'downloadsCount') else 0



def search_models(
    term: str,
    token: Optional[str] = None,
    limit: int = 10,
    page: int = 0,
    page_size: int = 100,
    sort: Optional[str] = None,
    direction: str = "-1",
) -> None:
    """Search for models on HuggingFace Hub."""
    api = HfApi(token=token)
    
    # Use list_models() with search/limit parameters
    models = api.list_models(
        search=term,
        limit=min(limit, 1000 + page * 100),
        sort=sort or "lastModified",
    )

    print_models(models, limit=limit, header=True)



def modelType(model) -> str:
    """Get model type."""
    return model.model_type



def get_file_type_summary(files: list) -> tuple:
    """Group files by their extensions/types."""
    from collections import Counter
    type_counts = Counter()
    
    for f in files:
        ext = f.split('.')[-1].lower() if '.' in f else "no-ext"
        type_counts[ext] += 1
    
    return type_counts, dict(type_counts)



def _load_token(use_default: bool = False) -> Optional[str]:
    """Try to get token from environment or config."""
    return os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")



def download_token() -> Optional[str]:
    """Try to get token from environment or config."""
    return _load_token()




def browse_model(model_id: str, token: Optional[str] = None) -> None:
    """Browse a specific model and print its details."""
    api = HfApi(token=token)
    
    try:
        model_info = api.model_info(repo_id=model_id, token=token)
        print(f"\nModel: {model_info.model_id}")
        print(f"  Type: {model_info.model_type}")
        print(f"  Last modified: {model_info.last_modified}")
        print(f"  Size: {model.size_str}")
        if model_info.tags:
            print(f"  Tags: {', '.join(model_info.tags)}")
    except Exception as e:
        print(f"\nError browsing model '{model_id}': {e}")



def main():
    """Command-line interface for model browser and search."""
    parser = argparse.ArgumentParser(
        description="Search and browse Hugging Face Hub models.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Search for models:
    %(prog)s -q "gpt2"
    %(prog)s -q "image-classification" -l 20
    %(prog)s -q "whisper" -t 1
  
  Browse a specific model:
    %(prog)s -m bert-base-cased
    %(prog)s -m mistral-7b-instruct-v0.1 -t 1
"""
    )
    
    parser.add_argument("-q", "--query", help="Search query term")
    parser.add_argument("-m", "--model", help="Model ID to browse (e.g. bert-base-cased)")
    parser.add_argument("-t", "--token", help="HF API token (overrides env)")
    parser.add_argument("-l", "--limit", type=int, default=10,
                       help="Results limit (default: 10)")
    parser.add_argument("-n", "--num", type=int, default=10,
                       help="Number of models to print (default: 10)")
    parser.add_argument("-p", "--page", type=int, default=0,
                       help="Page number (default: 0)")
    parser.add_argument("-ps", "--page-size", type=int, default=100,
                       help="Results per page (default: 100)")
    parser.add_argument("-s", "--sort", choices=["lastModified", "trendingScore", "likesCount", "downloadsCount", "createdAt"],
                       help="Sort field")
    parser.add_argument("-d", "--direction", default="-1", choices=["-1", "1"],
                       help="Sort direction: -1=desc, 1=asc (default: -1)")
    parser.add_argument("-dft", "--default-token", action="store_true", dest="use_default",
                       help="Use default token from environment/config")
    parser.add_argument("-w", "--width", type=int, default=80,
                       help="Terminal width for output")
    parser.add_argument("-c", "--color", choices=["auto", "true", "false"], default="auto",
                       help="Color output: auto/true/false")
    parser.add_argument("-e", "--examples", action="store_true",
                       help="Show example searches")
    
    args = parser.parse_args()
    
    # Examples mode
    if args.examples:
        print("Example searches:")
        print("  Search models:")
        print("    hf -q \"gpt2\"")
        print("    hf -q \"image-classification\" -l 20")
        print("    hf -q \"whisper\" -t 1")
        print("  Browse a model:")
        print("    hf -m bert-base-cased")
        print("    hf -m mistral-7b-instruct-v0.1 -t 1")
        print("  Combine search and browse:")
        print("    hf --query \"roberta\"  # returns 25 results")
        print("    hf --model bert-base-cased  # shows detailed info")
        sys.exit(0)
    
    # Get token - user-provided takes priority, then env, then config
    token = args.token or _load_token(args.use_default)
    
    # Run main functionality
    if args.query:
        # Search mode
        search_models(
            term=args.query or "",
            token=token,
            limit=args.limit,
            page=args.page,
            page_size=args.page_size,
            sort=args.sort,
            direction=args.direction,
        )
    elif args.model:
        # Browse mode
        browse_model(args.model, token)
    else:
        # Default: interactive prompt
        query = input("Enter search term: ")
        if query:
            search_models(query, token, args.limit, args.page, args.page_size, args.sort, args.direction)
        else:
            print("No search term provided. Use --query or -m for specific mode, or enter a term.")


if __name__ == "__main__":
    main()