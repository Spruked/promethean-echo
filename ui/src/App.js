import React, { useState, useEffect } from 'react';

const App = () => {
  const [suggestion, setSuggestion] = useState('');
  const [memoryInput, setMemoryInput] = useState('');
  const [response, setResponse] = useState('');

  useEffect(() => {
    fetch('/api/suggestion')
      .then((res) => res.json())
      .then((data) => {
        if (data) setSuggestion(data.message || JSON.stringify(data));
      })
      .catch((err) => console.error('Error fetching suggestion:', err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = { entry: memoryInput };

    try {
      const res = await fetch('/api/memory', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setResponse(data.message || JSON.stringify(data));
    } catch (err) {
      console.error('Error posting memory:', err);
      setResponse('Error posting memory');
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto text-white">
      <h1 className="text-3xl font-bold mb-4">Prometheus Prime Dashboard</h1>
      <p className="mb-4">🧠 System Suggestion:</p>
      <div className="bg-gray-800 p-4 rounded mb-6">{suggestion || 'Loading...'}</div>

      <form onSubmit={handleSubmit} className="mb-6">
        <label className="block mb-2">Push Memory Entry:</label>
        <textarea
          value={memoryInput}
          onChange={(e) => setMemoryInput(e.target.value)}
          className="w-full p-2 text-black rounded"
          rows={4}
        ></textarea>
        <button
          type="submit"
          className="mt-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded"
        >
          Submit
        </button>
      </form>

      {response && (
        <div className="bg-green-800 p-4 rounded">
          <strong>Server Response:</strong> {response}
        </div>
      )}
    </div>
  );
};

export default App;
