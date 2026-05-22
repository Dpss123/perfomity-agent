"""
Lumière AI Agent — Flask Backend Server
========================================
Serves the frontend and runs the AI agent pipeline
via SSE (Server-Sent Events) for real-time streaming.

Run:  python server.py
Then: http://localhost:5000
"""

import sys
import threading
import queue
import json
import uuid
import os
import traceback

from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(override=True)

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# In-memory job store: job_id → {q, status, result}
_jobs: dict = {}


# ── Stdout capture stream ──────────────────────────────────────────
class _QStream:
    """Redirects print() output into a queue for SSE streaming."""
    def __init__(self, q: queue.Queue):
        self._q   = q
        self._buf = ''

    def write(self, s: str):
        self._buf += s
        while '\n' in self._buf:
            line, self._buf = self._buf.split('\n', 1)
            msg = line.strip()
            if msg:
                self._q.put({'type': 'log', 'msg': msg})

    def flush(self):
        msg = self._buf.strip()
        if msg:
            self._q.put({'type': 'log', 'msg': msg})
            self._buf = ''


# ── Routes ─────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/api/run', methods=['POST'])
def run_agent():
    """Start an agent run. Returns {job_id}."""
    data  = request.get_json(force=True) or {}
    brief = data.get('brief', '').strip()

    if not brief:
        return jsonify({'error': 'Brief is required'}), 400

    job_id = str(uuid.uuid4())
    q      = queue.Queue()
    _jobs[job_id] = {'q': q, 'status': 'running', 'result': None}

    # Optional key/credential overrides from the form
    overrides = {
        k: data[k] for k in ('GROQ_API_KEY', 'TAVILY_API_KEY',
                              'SHOPIFY_STORE_URL', 'SHOPIFY_ACCESS_TOKEN')
        if data.get(k, '').strip()
    }

    def _worker():
        old_stdout = sys.stdout
        sys.stdout = _QStream(q)

        try:
            # Apply env overrides
            for k, v in overrides.items():
                os.environ[k] = v

            load_dotenv(override=True)

            from agent.graph import build_graph  # import here so dotenv loads first
            graph = build_graph()

            initial = {
                'brief':        brief,
                'research':     None,
                'strategy':     None,
                'store_assets': None,
                'shopify':      None,
                'errors':       [],
            }

            final = graph.invoke(initial)

            # Serialize — drop anything not JSON-safe
            safe = {}
            for k, v in final.items():
                try:
                    json.dumps(v)
                    safe[k] = v
                except Exception:
                    safe[k] = str(v)

            _jobs[job_id].update({'status': 'done', 'result': safe})
            q.put({'type': 'done', 'result': safe})

        except Exception as e:
            tb = traceback.format_exc()
            _jobs[job_id].update({'status': 'error'})
            q.put({'type': 'error', 'msg': str(e), 'trace': tb})
        finally:
            sys.stdout = old_stdout
            q.put(None)  # sentinel

    threading.Thread(target=_worker, daemon=True).start()
    return jsonify({'job_id': job_id})


@app.route('/api/stream/<job_id>')
def stream(job_id: str):
    """SSE endpoint — streams log messages and the final result."""
    if job_id not in _jobs:
        return jsonify({'error': 'Job not found'}), 404

    def _generate():
        q = _jobs[job_id]['q']
        while True:
            try:
                item = q.get(timeout=180)
                if item is None:
                    break
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
            except queue.Empty:
                # keep-alive ping
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    return Response(
        _generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control':    'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection':       'keep-alive',
        },
    )


@app.route('/api/status/<job_id>')
def status(job_id: str):
    if job_id not in _jobs:
        return jsonify({'error': 'Not found'}), 404
    j = _jobs[job_id]
    return jsonify({'status': j['status']})


# ── Entry point ────────────────────────────────────────────────────
if __name__ == '__main__':
    print('\n' + '=' * 50)
    print('  🕯️  Lumière AI Agent Server')
    print('  Open → http://localhost:5000')
    print('=' * 50 + '\n')
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
