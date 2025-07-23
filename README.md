# Prometheus Prime – Backend API (v0.7.1)

This is the core AI backend for **Prometheus Prime**, built to handle symbolic reasoning, ethical reflection, memory storage, and prompt processing. It exposes a modular, secure API for front-end UIs or developer tools.

---

## 🚀 Features

- ⚖️ **Ethics Core** (YAML-driven)
- 🧠 **Helix Echo Engine** (reflective output)
- 🪞 **Caleon Mirror AI** (codex-style symbolic reflection)
- 🗂️ **Memory Storage** (SQLite + JSON Vaults)
- 🌐 **RESTful API + WebSocket Support**
- 🔒 Security headers, CORS, and modular design

---

## 📦 Folder Structure

```plaintext
PrometheusPrime/
├── app.py                # Main Flask app
├── cali/
│   ├── config/ethics.yaml
│   ├── vault/storage/
│   │   └── cali_vault_storage.py
│   ├── memory/
│   │   └── memory_store.py
├── core/
│   ├── helix_echo_core.py
│   ├── mirror/
│   │   ├── mirror.py (Caleon)
│   │   └── codex.py (LocalCodex)
│   └── trust_glyph_verifier.py
├── routes/
│   └── glyphfeed.py
├── test_ethics.py
├── requirements.txt
└── README.md
```

---

## 🛠️ Quickstart

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the backend:**
   ```bash
   python app.py
   ```
3. **API available at:**
   - http://localhost:5000/

---

## 📚 Key Endpoints

- `/` — Health check
- `/prompt` — Store prompt in DB and file vault
- `/vault-files` — List vaults
- `/vault-files/<vault_id>` — Get vault by ID
- `/vault-files/<vault_id>/download` — Download vault JSON
- `/helix/process` — Symbolic echo (Helix)
- `/helix/status` — Helix engine status
- `/api/reflect` — Symbolic reflection (Caleon)
- `/reflect` — Symbolic reflection (GET/POST)
- `/memory/add` — Add memory entry
- `/memory/get/<id>` — Get memory entry
- `/memory/search` — Search memory
- `/memory/tag/<tag>` — Search by tag
- `/memory/recent` — Recent memory entries
- `/reconcile` — Reconcile vaults

---

## 📝 System Diagram

See `docs/diagrams/system_diagram.txt` for a conceptual overview.

---

## 🧪 Testing

- Use tools like Postman or curl to test endpoints.
- Example:
  ```bash
  curl -X POST http://localhost:5000/prompt -H "Content-Type: application/json" -d '{"title": "Test", "description": "Demo"}'
  ```

---

## 📄 License

MIT License. See LICENSE file for details.
