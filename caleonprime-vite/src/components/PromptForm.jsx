import React, { useState } from "react";

function PromptForm() {
  const [userId, setUserId] = useState("");
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState(null);
  const [tone, setTone] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, prompt }),
    });
    const data = await res.json();
    setResponse(data.response);
    setTone(data.tone);
  };

  return (
    <div className="mb-4">
      <form onSubmit={handleSubmit} className="space-y-2">
        <input value={userId} onChange={e => setUserId(e.target.value)} placeholder="User ID" className="bg-gray-800 p-2 w-full" />
        <input value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Enter prompt" className="bg-gray-800 p-2 w-full" />
        <button type="submit" className="bg-blue-500 px-4 py-2">Ask</button>
      </form>
      {response && <div className="mt-4"><strong>Response:</strong> {response}</div>}
      {tone && <div><strong>Tone:</strong> {tone}</div>}
    </div>
  );
}

export default PromptForm;
