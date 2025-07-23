class WhisperingArchive:
    def __init__(self):
        self.logs = []
        self.emotional_index = {}

    def record(self, message, emotion=None, glyph=None):
        entry = {
            "message": message,
            "emotion": emotion,
            "glyph": glyph
        }
        self.logs.append(entry)
        if emotion:
            self.emotional_index.setdefault(emotion, []).append(entry)

    def retrieve_by_emotion(self, emotion):
        return self.emotional_index.get(emotion, [])

    def invoke_whisper(self, glyph):
        return [log for log in self.logs if log["glyph"] == glyph]

    def get_logs(self):
        return self.logs
