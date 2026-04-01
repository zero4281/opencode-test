#
#Search models in the Hugging Face Hub
#
#Usage example:
#    python3 hf_search.py 'text-to-image'
#
#Command line arguments:
#    python3 hf_search.py 'image-to-text' --limit 50
#
#Or in Python as a module:
#    import hf_search
#    results = hf_search.search('stable-diffusion', limit=10)
#    for m in results:
#        print(m.id)

import argparse
import json
from huggingface_hub.search_models_basic import search_models


# Default CLI behavior
def _cli_main():
    parser = argparse.ArgumentParser(description='Search models on Hugging Face Hub')
    parser.add_argument('query', help='Search term (e.g., image-to-text, stable-diffusion)')
    parser.add_argument('--limit', '-l', type=int, default=25, help='Max results (default: 25)')
    parser.add_argument('--filter', '-f', help='Filter tag (e.g., space:my_space)')
    parser.add_argument('--full', '-f', action='store_true', help='Output full JSON instead of CSV')
    parser.add_argument('--json', action='store_true', help='Output as JSON (overrides text/csv)')
    parser.add_argument('--limit-all', action='store_true', help='Return all results instead of just the top N')
    parser.add_argument('--sort', default='recentlyAdded', help='Sort field: recentlyAdded, likes, downloads, etc.')
    parser.add_argument('--fields', help='Comma-separated fields to output (default: id,type,size,likes,downloads)')

    args = parser.parse_args()

    # Build search parameters
    params = {
        'query': args.query,
        'filter': args.filter,
        'sort': args.sort if args.sort != 'recentlyAdded' else 'recentlyAdded',
        'full': args.full,
        'limit': args.limit,
    }

    if args.limit_all:
        params['limit'] = 0  # 0 = all results

    # Execute search
    results = search_models(**params)

    if args.json:
        # Full JSON output
        print(json.dumps(results, indent=2))
    elif args.full or len(results) <= 1:
        # Show detailed info for small/first result
        for m in results:
            print(json.dumps(m, indent=2))
            if args.full and len(results) > 1:
                break
    else:
        # Default: CSV output (faster to read in terminals/text editors)
        fields = args.fields or 'id,type,size,blobs.size,likes,downloads'
        print(','.join(fields))
        for m in results[:500]:  # cap output to avoid massive lines
            values = []
            for f in fields.split(','):
                v = getattr(m, f, f'--')
                values.append(str(v))
            print(','.join(values))


# Entry point
if __name__ == '__main__':
    _cli_main()
    print(f'Total results (truncated to 500 for CLI output): {len(results)}')

