import React, { useState } from "react";

function NFTPanel() {
  const [userId, setUserId] = useState("");
  const [metadata, setMetadata] = useState(null);

  const handleMint = async () => {
    const res = await fetch("/mint", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId }),
    });
    const data = await res.json();
    setMetadata(data.metadata);
  };

  return (
    <div className="mb-4">
      <input value={userId} onChange={e => setUserId(e.target.value)} placeholder="User ID for Minting" className="bg-gray-800 p-2 w-full" />
      <button onClick={handleMint} className="bg-green-500 px-4 py-2 mt-2">Mint NFT</button>
      {metadata && <pre className="mt-4 bg-gray-700 p-2">{JSON.stringify(metadata, null, 2)}</pre>}
    </div>
  );
}

export default NFTPanel;
