import os, re, json
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'groupmatch.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from django.conf import settings

def collect_asset_paths(html):
    refs = re.findall(r'(?:href|src)=["\'](/static/[^"\']+)["\']', html)
    return sorted(set(refs))

def asset_size(url_path):
    rel = url_path.removeprefix('/static/')
    path = Path(settings.BASE_DIR) / 'static' / rel
    return path.stat().st_size if path.exists() else 0

def audit_page(path, login_as=None):
    client = Client()
    if login_as:
        client.login(username=login_as, password='pass12345')
    resp = client.get(path)
    html = resp.content.decode('utf-8')
    assets = collect_asset_paths(html)
    total_bytes = len(resp.content) + sum(asset_size(a) for a in assets)
    return {'path': path,'status_code': resp.status_code,'html_bytes': len(resp.content),'asset_count': len(assets),'request_count': 1 + len(assets),'asset_bytes': sum(asset_size(a) for a in assets),'total_bytes': total_bytes,'assets': assets}

results = {'home_before': audit_page('/?perf=baseline'),'home_after': audit_page('/'),'task_board_before': audit_page('/projects/1/tasks/?perf=baseline', login_as='leader'),'task_board_after': audit_page('/projects/1/tasks/', login_as='leader')}
print(json.dumps(results, indent=2))
