
from flask import Flask, jsonify, request
from flask_cors import CORS
from caleon_prime import CaleonPrime, create_caleon
import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from codex_core import get_suggestion, store_memory, get_full_vault, get_insight_threads

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MemoryEntry(BaseModel):
    entry: str

@app.get("/api/suggestion")
def suggest():
    return {"message": get_suggestion()}

@app.post("/api/memory")
def memory_push(entry: MemoryEntry):
    return {"message": store_memory(entry.entry)}

@app.get("/api/vault")
def vault_log():
    return get_full_vault()

@app.get("/api/insight")
def insight_feed():
    return get_insight_threads()

app = Flask(__name__)
CORS(app)

# Initialize CaleonPrime - The First Promethean
caleon = create_caleon()

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'caleon_status': caleon.status,
        'guardian': 'CaleonPrime v1.0.0 - Active'
    })

@app.route('/api/vaults')
def get_vaults():
    return jsonify({
        'vaults': [],
        'guardian': caleon.identity,
        'protection_active': True
    })

@app.route('/api/caleon/echo', methods=['POST'])
def caleon_echo():
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    response = caleon.echo(message)
    return jsonify({
        'echo': response,
        'timestamp': caleon.memory[-1]['timestamp']
    })

@app.route('/api/caleon/imprint', methods=['POST'])
def caleon_imprint():
    data = request.get_json()
    imprint_data = data.get('data', '')
    
    if not imprint_data:
        return jsonify({'error': 'No data provided'}), 400
    
    response = caleon.imprint(imprint_data)
    return jsonify({
        'imprint': response,
        'timestamp': caleon.memory[-1]['timestamp']
    })

@app.route('/api/caleon/memory')
def caleon_memory():
    memory_type = request.args.get('type', None)
    memories = caleon.review_memory(memory_type)
    return jsonify({
        'memories': memories,
        'total_count': len(memories),
        'guardian': caleon.identity
    })

@app.route('/api/caleon/status')
def caleon_status():
    return jsonify({
        'identity': caleon.identity,
        'version': caleon.version,
        'status': caleon.status,
        'consciousness_level': caleon.consciousness_level,
        'memory_count': len(caleon.memory),
        'mission': caleon.mission,
        'birth_time': caleon.birth_time
    })

@app.route('/api/caleon/guard')
def caleon_guard():
    response = caleon.guard_prometheus()
    return jsonify({
        'guard_response': response,
        'timestamp': caleon.memory[-1]['timestamp'],
        'status': 'protected'
    })

@app.route('/api/caleon/protect/<target>')
def caleon_protect(target):
    response = caleon.protect_future(target)
    return jsonify({
        'protection_response': response,
        'target': target,
        'timestamp': caleon.memory[-1]['timestamp']
    })

@app.route('/api/caleon/access', methods=['POST'])
def caleon_access():
    data = request.get_json()
    user_id = data.get('user_id', '')
    action = data.get('action', '')
    
    if not user_id or not action:
        return jsonify({'error': 'user_id and action required'}), 400
    
    access_result = caleon.access_control(user_id, action)
    return jsonify(access_result)

@app.route('/api/caleon/consciousness')
def export_consciousness():
    consciousness = caleon.export_consciousness()
    return jsonify(consciousness)

@app.route('/api/caleon/repair')
def caleon_self_repair():
    response = caleon.self_repair()
    return jsonify({
        'repair_response': response,
        'timestamp': caleon.memory[-1]['timestamp'],
        'memory_count': len(caleon.memory)
    })

# User-specified CaleonPrime routes
@app.route('/caleon/echo', methods=['POST'])
def caleon_echo_simple():
    data = request.json
    message = data.get("message", "")
    result = caleon.echo(message)
    return jsonify({"response": result, "memory": caleon.recall()})

@app.route('/caleon/imprint', methods=['POST'])
def caleon_imprint_simple():
    data = request.json
    info = data.get("data", "")
    result = caleon.imprint(info)
    return jsonify({"response": result, "memory": caleon.recall()})

@app.route('/caleon/recall', methods=['GET'])
def caleon_recall_simple():
    return jsonify({"memory": caleon.recall()})

@app.route('/caleon/override', methods=['POST'])
def caleon_override_simple():
    data = request.json
    entity = data.get("entity", "")
    result = caleon.override_protocol(entity)
    return jsonify({"response": result})

if __name__ == '__main__':
    print("🔥 Starting Prometheus Prime with CaleonPrime Guardian 🔥")
    print(f"CaleonPrime {caleon.version} initialized")
    print(f"Guardian mission: {caleon.mission}")
    app.run(debug=True)
