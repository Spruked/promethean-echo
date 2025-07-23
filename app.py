# ============================================================================
# CALI: Prometheus Prime Backend — app.py
# ============================================================================


# --- Force module visibility ---

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# --- Imports: Standard & Flask ---
import uuid
import logging
import yaml
import sqlite3
from datetime import datetime
from typing import Dict, Any
from flask import Flask, jsonify, request, send_file, Response
from flask_socketio import SocketIO
from flask_cors import CORS

# --- Imports: Custom Modules ---
from routes.glyphfeed import glyphfeed_bp
from cali.sandbox import sanitize_input, SandboxError
from cali.vault.storage.cali_vault_storage import load_memory_vault, save_memory_vault, VAULT_DIR
from core.trust_glyph_verifier import TrustGlyphVerifier
from core.helix_echo_core import HelixEchoCore

# ============================================================================
# Initialization
# ============================================================================

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CALI")

# Register Blueprint
app.register_blueprint(glyphfeed_bp)

# ============================================================================
# Ethics Framework Loader
# ============================================================================

try:
    with open('cali/config/ethics.yaml', 'r', encoding='utf-8') as f:
        ethics = yaml.safe_load(f)
        logger.info("✅ Ethical framework loaded.")
except Exception as e:
    logger.error(f"❌ Failed to load ethics.yaml: {e}")
    ethics = {}

# ============================================================================
# SQLite Vault DB Utilities
# ============================================================================

def get_db():
    conn = sqlite3.connect('legacy_vault.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS legacy_vault (
        vault_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        trigger_keywords TEXT,
        delivery_mode TEXT,
        unlock_condition TEXT,
        is_active INTEGER,
        created_at TEXT,
        category TEXT
    )''')
    conn.commit()
    conn.close()

# ============================================================================
# Root Endpoint
# ============================================================================

@app.route("/")
def index() -> str:
    return "Prometheus Prime backend online."

# ============================================================================
# Vault Routes (DB + File-Based)
# ============================================================================

@app.route('/prompt', methods=['POST'])
def handle_prompt():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    title = data.get('title', 'User Prompt')
    description = data.get('description', '')
    keywords = data.get('keywords', [])
    category = data.get('category', 'tasks')
    vault_id = str(uuid.uuid4())

    try:
        conn = get_db()
        conn.execute('''
            INSERT INTO legacy_vault (
                vault_id, title, description, trigger_keywords, delivery_mode,
                unlock_condition, is_active, created_at, category
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            vault_id,
            title,
            description,
            ",".join(keywords) if isinstance(keywords, list) else keywords,
            "manual",
            "none",
            1,
            datetime.now().isoformat(),
            category
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB error: {e}")
        return jsonify({"error": "Database error"}), 500

    save_memory_vault(vault_id, {
        "vault_id": vault_id, "title": title,
        "description": description, "keywords": keywords,
        "category": category, "created_at": datetime.now().isoformat()
    })

    return jsonify({'status': 'created', 'vault_id': vault_id}), 201

@app.route('/vault-files', methods=['GET'])
def list_vault_files():
    files = [f.replace(".json", "") for f in os.listdir(VAULT_DIR) if f.endswith(".json")]
    return jsonify({'vault_files': files})

@app.route('/vault-files/<vault_id>', methods=['GET'])
def view_vault_file(vault_id: str):
    vault = load_memory_vault(vault_id)
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    return jsonify(vault)

@app.route('/vault-files/<vault_id>/download', methods=['GET'])
def download_vault_file(vault_id: str):
    path = VAULT_DIR / f"{vault_id}.json"
    if not path.exists():
        return jsonify({'error': 'File not found'}), 404
    return send_file(path, as_attachment=True)

@app.route('/reconcile', methods=['GET'])
def reconcile_vault():
    return jsonify({'status': 'success', 'message': 'Reconciliation completed'}), 200

# ============================================================================
# Helix Echo Integration
# ============================================================================

HELIX_AVAILABLE = False
helix_engine = None

try:
    helix_engine = HelixEchoCore(ethics)
    HELIX_AVAILABLE = True
    logger.info("🧠 HelixEchoCore integrated successfully.")
except Exception as e:
    logger.warning(f"⚠️ HelixEchoCore unavailable: {e}")

@app.route("/helix/process", methods=["POST"])
def helix_process():
    if not HELIX_AVAILABLE:
        return jsonify({"error": "Helix unavailable"}), 503
    try:
        data = request.get_json()
        if not data or "input" not in data:
            return jsonify({"error": "Input required"}), 400
        result = helix_engine.echo(data["input"])
        return jsonify({"status": "success", "helix_response": result})
    except Exception as e:
        logger.error(f"Helix error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/helix/status")
def helix_status():
    return jsonify({
        "available": HELIX_AVAILABLE,
        "status": "ok" if HELIX_AVAILABLE else "not initialized"
    })

# ============================================================================
# Mirror + Codex Integration (Caleon)
# ============================================================================


from core.mirror.mirror import Caleon
# If you need LocalCodex, import it here as well (uncomment if exists):
# from core.mirror.codex import LocalCodex

# Example instantiation (adjust as needed):
caleon = Caleon()

@app.route("/api/reflect", methods=["POST"])
def reflect_input():
    data = request.get_json()
    user_input = data.get("input", "")
    if caleon:
        result = caleon.handle_input(user_input)
        return jsonify({"response": result})
    return jsonify({"error": "Caleon not ready"}), 503

@app.route("/reflect", methods=["GET", "POST"])
def reflect():
    input_text = request.values.get("input")
    if not input_text:
        return jsonify({'error': 'No input provided'}), 400
    if not caleon or not hasattr(caleon, "handle_input"):
        return jsonify({'error': 'Caleon not ready or method not found'}), 503
    output = caleon.handle_input(input_text)
    return jsonify({'input': input_text, 'output': output})

# ============================================================================
# Memory Store API (SQLite)
# ============================================================================

try:
    from cali.memory.memory_store import MemoryStore
except ModuleNotFoundError:
    # Add the parent directory to sys.path and try again
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'cali', 'memory')))
    try:
        from memory_store import MemoryStore
    except ImportError:
        raise ImportError("MemoryStore module not found. Please ensure 'cali/memory/memory_store.py' exists and is accessible.")

memory_store = MemoryStore()

@app.route('/memory/add', methods=['POST'])
def memory_add():
    data = request.get_json() or {}
    if not data.get('text'):
        return jsonify({'error': 'No text provided'}), 400
    entry_id = memory_store.add_entry(
        data['text'], data.get('emotion'), data.get('context'),
        data.get('tags'), data.get('usage_score', 1.0)
    )
    return jsonify({'status': 'created', 'entry_id': entry_id})

@app.route('/memory/get/<int:entry_id>', methods=['GET'])
def memory_get(entry_id):
    row = memory_store.get_entry(entry_id)
    if not row:
        return jsonify({'error': 'Not found'}), 404
    keys = ['id', 'text', 'emotion', 'context', 'tags', 'created_at', 'usage_score']
    return jsonify(dict(zip(keys, row)))

@app.route('/memory/search', methods=['GET'])
def memory_search():
    q = request.args.get('q')
    if not q:
        return jsonify({'error': 'No query provided'}), 400
    rows = memory_store.search_text(q)
    keys = ['id', 'text', 'emotion', 'context', 'tags', 'created_at', 'usage_score']
    return jsonify([dict(zip(keys, row)) for row in rows])

@app.route('/memory/tag/<tag>', methods=['GET'])
def memory_tag_search(tag):
    rows = memory_store.search_by_tag(tag)
    keys = ['id', 'text', 'emotion', 'context', 'tags', 'created_at', 'usage_score']
    return jsonify([dict(zip(keys, row)) for row in rows])

@app.route('/memory/recent', methods=['GET'])
def memory_recent():
    n = int(request.args.get('n', 10))
    rows = memory_store.search_recent(n)
    keys = ['id', 'text', 'emotion', 'context', 'tags', 'created_at', 'usage_score']
    return jsonify([dict(zip(keys, row)) for row in rows])

# ============================================================================
# Security Headers
# ============================================================================

@app.after_request
def add_security_headers(response: Response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# ============================================================================
# Run App
# ============================================================================

if __name__ == "__main__":
    init_db()
    logger.info("✅ Database initialized.")
    socketio.run(app, port=5000, debug=True)
# ============================================================================