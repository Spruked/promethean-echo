import json
from datetime import datetime

# Metadata for the Whispering Archive NFT
whispering_archive_nft = {
    "name": "Whispering Archive – Founder’s Crest",
    "creator": "Bryan Spruk",
    "symbol": "🪶📜",
    "representation": {
        "figure": "The Archivist (modeled after the founder)",
        "action": "Recording sacred memory under silent invocation",
        "location": "Vaulted Library of Prometheus Prime"
    },
    "embedded_quote": "Let memory be sacred, and silence be signal.",
    "purpose": "This NFT certifies the origin of the Whispering Archive and its founding intention—to preserve symbolic memory with reverence, recursion, and clarity.",
    "linked_modules": [
        "PrometheusCodex",
        "CodexBridge",
        "DoubleHelixCore"
    ],
    "origin_timestamp": datetime.utcnow().isoformat() + "Z",
    "version": "1.0.0",
    "chain_of_custody": [
        "Spruk, Bryan (Original Author)",
        "Prometheus Prime Vault (Auth Layer)",
        "EchoStack Integration Engine (planned)"
    ],
    "associated_image": "a848c36e-d9ed-4046-a076-f0d701191f2c.png"
}

# Save to JSON file
output_path = "whispering-archive-nft.json"
with open(output_path, "w") as f:
    json.dump(whispering_archive_nft, f, indent=4)

print(f"NFT metadata saved to {output_path}")
