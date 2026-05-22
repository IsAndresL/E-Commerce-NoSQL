import json
import sys

try:
    o = json.load(open('/tmp/cdk-outputs.json'))
    stack = o.get('EcommerceLambda', {})
    api_id = stack.get('ApiId')
    api_url = stack.get('ApiUrl')
    # Prefer a path-based URL for local MiniStack to avoid DNS resolution issues
    if api_id:
        url = f'http://localhost:4566/_aws/execute-api/{api_id}/$default'
    elif api_url:
        url = api_url
    else:
        url = None

    if url:
        with open('frontend/.env', 'w') as f:
            f.write(f'VITE_API_BASE_URL={url}\n')
        print('WROTE frontend/.env ->', url)
    else:
        print('No ApiId or ApiUrl found in outputs', file=sys.stderr)
except Exception as e:
    print('Failed to write frontend/.env:', e, file=sys.stderr)
    sys.exit(1)
