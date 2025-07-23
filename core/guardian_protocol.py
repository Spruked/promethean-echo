from datetime import datetime

class KaitosDriftSentinel:
    def __init__(self):
        self.voice_log = []
        self.signature_index = {}
        self.alerts = []

    def archive_response(self, response_text, timestamp, emotional_vector, source):
        entry = {
            "text": response_text,
            "timestamp": timestamp,
            "emotion": emotional_vector,
            "source": source
        }
        self.voice_log.append(entry)
        self.signature_index.setdefault(source, []).append(entry)

    def monitor_for_drift(self, latest_text):
        drift_detected = self._detect_symbolic_drift(latest_text)
        if drift_detected:
            self.alerts.append({
                "timestamp": datetime.utcnow(),
                "message": "Symbolic Drift Detected",
                "details": drift_detected
            })

    def _detect_symbolic_drift(self, text):
        lost_glyphs = [glyph for glyph in ["legacy", "trust", "constellation"] if glyph not in text]
        if lost_glyphs:
            return {"missing_symbols": lost_glyphs}
        return None

    def invoke_guardian_recall(self):
        return self.alerts[-1] if self.alerts else "Kaitos reports: no deviation beyond tolerance."
