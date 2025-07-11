import React, { useEffect, useState } from "react";

function LogViewer() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch("/logs")
      .then(res => res.json())
      .then(data => setLogs(data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-semibold mt-6 mb-2">Execution Logs</h2>
      <ul className="text-sm max-h-60 overflow-auto bg-gray-800 p-2">
        {logs.map((log, i) => (
          <li key={i}>[{log.timestamp}] {log.user}: {log.prompt}</li>
        ))}
      </ul>
    </div>
  );
}

export default LogViewer;
