from flask import Blueprint, request, jsonify
from .helix_echo_core import HelixEchoCore, PrometheusCodex

codex_bp = Blueprint('codex', __name__)
helix = HelixEchoCore()
codex = PrometheusCodex(helix_core=helix)
helix.prometheus_codex = codex

@codex_bp.route("/codex/pulse", methods=["GET"])
def codex_pulse():
    return jsonify({"resonance": codex.resonance_pulse()})

@codex_bp.route("/helix/state", methods=["GET"])
def helix_state():
    return jsonify({
        "emotional_state": helix.emotional_state,
        "epigenetic_memory": helix.epigenetic_memory
    })

@codex_bp.route("/helix/execute", methods=["POST"])
def execute_helix():
    data = request.json or {}
    helix.execute(data)
    return jsonify({"status": "executed", "input": data})

@codex_bp.route("/codex/echo", methods=["POST"])
def codex_echo():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message required"}), 400
    response = codex.echo(message)
    return jsonify({"echo": response})

@codex_bp.route("/logs/consolidation", methods=["GET"])
def get_consolidation_logs():
    import os
    log_path = "logs/consolidation_log.json"
    if not os.path.exists(log_path):
        return jsonify({"logs": []})
    try:
        with open(log_path, "r") as f:
            raw = f.read()
            lines = raw.split("\n")
            lines = [line.strip() for line in lines if line.strip()]
            if not lines:
                return jsonify({"logs": []})
            return jsonify({"logs": lines[-50:]})  # return last 50 lines
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@codex_bp.route("/daemon/sanctify", methods=["POST"])
def daemon_sanctify():
    from .vault_sync_daemon import VaultSyncDaemon
    data = request.get_json()
    changelist_id = data.get("changelist_id", "0000")
    description = data.get("description", "")
    files = data.get("files", [])

    try:
        daemon = VaultSyncDaemon()
        result = daemon.process_changelist(changelist_id, description, files)
        return jsonify({
            "changelist_id": changelist_id,
            "result": "sanctified" if result else "rejected"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@codex_bp.route("/codex/query", methods=["POST"])
def codex_query():
    import requests
    data = request.get_json()
    prompt = data.get("prompt", "")

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        })
        result = response.json().get("response", "[No response from Minstrel]")
        return jsonify({"response": result})
    except Exception as e:
        return jsonify({"error": f"Failed to connect to Minstrel: {str(e)}"}), 500

@codex_bp.route("/codex/vault", methods=["GET"])
def codex_vault_contents():
    try:
        summary = codex.seed_vault.summarize()
        entries = codex.seed_vault.entries[-50:]  # Return last 50 entries
        return jsonify({"summary": summary, "entries": entries}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500