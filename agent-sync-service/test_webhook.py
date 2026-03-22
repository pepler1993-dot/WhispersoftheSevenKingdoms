import hashlib
import hmac
import json
import os
from pathlib import Path

os.environ['GITHUB_WEBHOOK_SECRET'] = 'testsecret'
os.environ['DATA_DIR'] = 'data/test'

from fastapi.testclient import TestClient
from app.main import app


def sign(secret: str, payload: bytes) -> str:
    return 'sha256=' + hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()


def post_event(client: TestClient, delivery_id: str, event_type: str, payload: dict):
    raw = json.dumps(payload).encode('utf-8')
    return client.post(
        '/github/webhook',
        content=raw,
        headers={
            'X-GitHub-Delivery': delivery_id,
            'X-GitHub-Event': event_type,
            'X-Hub-Signature-256': sign('testsecret', raw),
            'Content-Type': 'application/json',
        },
    )


def test_issue_event_is_logged_and_snapshotted() -> None:
    Path('data/test').mkdir(parents=True, exist_ok=True)
    client = TestClient(app)
    payload = {
        'action': 'opened',
        'repository': {'full_name': 'fued1011-2/agent-sync-service'},
        'issue': {'number': 123, 'state': 'open'},
        'sender': {'login': 'xDisslike'},
    }

    response = post_event(client, 'test-delivery-1', 'issues', payload)
    assert response.status_code == 200
    body = response.json()
    assert body['event_type'] == 'issues'
    assert body['task_id'] == 'fued1011-2/agent-sync-service#123'

    tasks = client.get('/github/tasks')
    assert tasks.status_code == 200
    assert tasks.json()['count'] >= 1


def test_pull_request_review_updates_snapshot() -> None:
    Path('data/test').mkdir(parents=True, exist_ok=True)
    client = TestClient(app)
    payload = {
        'action': 'submitted',
        'repository': {'full_name': 'fued1011-2/agent-sync-service'},
        'pull_request': {
            'number': 45,
            'state': 'open',
            'head': {'ref': 'feature/test', 'sha': 'abc1234'},
        },
        'review': {'state': 'approved'},
        'sender': {'login': 'review-bot'},
        'number': 45,
    }

    response = post_event(client, 'test-delivery-2', 'pull_request_review', payload)
    assert response.status_code == 200
    body = response.json()
    assert body['task_id'] == 'fued1011-2/agent-sync-service#45'

    snapshot = client.get('/github/task', params={'task_id': 'fued1011-2/agent-sync-service#45'})
    assert snapshot.status_code == 200
    data = snapshot.json()
    assert data['review_state'] == 'approved'
    assert data['branch'] == 'feature/test'
    assert data['last_commit_sha'] == 'abc1234'
