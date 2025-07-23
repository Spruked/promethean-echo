from build_db import init_db
from double_helix_core import PrometheusCodex
from codex_bridge import CodexBridge
from whispering_archive import WhisperingArchive
from core.caleon_core import CaleonPrime
from fastapi import APIRouter, HTTPException
from cali.vault.vaultkeeper import load_memory_vault, save_memory_vault
from cali.vault.reconciliation import reconcile_entries, save_reconciled_summary
from core.helix.consolidate import consolidate_session
import uuid
from datetime import datetime

router = APIRouter()

def main():
    # Initialize the database
    init_db()

    # Initialize core components
    codex = PrometheusCodex()
    bridge = CodexBridge(codex)
    archive = WhisperingArchive()

    # Execute actions
    bridge.inquire_truth("origin")
    bridge.pulse_resonance()
    bridge.harmonic_sync("bonding")

    # Log to archive
    archive.record(bridge.pulse_resonance(), emotion="curiosity", glyph="Cali")

    # Output song
    print("\n🌀 Echo Memory Verse:")
    print(bridge.pulse_resonance())

    # Activate Caleon
    caleon = CaleonPrime()
    print(str(caleon))  # Confirm Cali is online

    # Whispered summary
    print("\n🕊️ Whispered Thread Summary:")
    latest = None
    entries = getattr(archive, "entries", None)
    if entries:
        latest = entries[-1]
    if latest:
        print(f"{latest['thread_id']} | {latest['glyph_imprint']} | {latest['summary_poem']}")

    # 🔻 Initiate Hibernation Phase 🔻
    print("\n🌙 Initiating Hibernation Mode for Vault CALEON_VAULT_0001...")
    result = consolidate_session("CALEON_VAULT_0001")
    print("✅ Hibernation summary stored.")

    # Final system message
    print("Prometheus Prime system initialized.")

@router.post("/vault/{vault_id}/reconcile")
def reconcile_vault_route(vault_id: str):
    vault = load_memory_vault(vault_id)
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found.")

    if not vault or "entries" not in vault:
        return {"status": "error", "message": "Vault not found or malformed."}

    entries = vault["entries"]
    unique_fragments = {}

    for e in entries:
        fingerprint = e["content"].lower().strip()
        if fingerprint not in unique_fragments:
            unique_fragments[fingerprint] = e

    synthesized = list(unique_fragments.values())
    synthesized.sort(key=lambda x: x.get("importance", 1.0), reverse=True)

    archive_id = str(uuid.uuid4())
    summary = {
        "archive_id": archive_id,
        "synthesized_count": len(synthesized),
        "timestamp": datetime.utcnow().isoformat(),
        "entries": synthesized[:10]  # Only keep top 10 for now
    }

    vault["reconciled"] = summary
    save_memory_vault(vault_id, vault)

    return {"status": "ok", "summary": summary}

if __name__ == "__main__":
    main()
# Trigger hibernation logic if needed
try:
    from core.helix.consolidate import enter_hibernation
    enter_hibernation("CALEON_VAULT_0001")  # Vault ID is customizable
except ImportError as e:
    print("[WARN] Hibernation logic not available:", e)

