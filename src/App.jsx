import React, { useState } from "react";
import PromptForm from "./components/PromptForm";
import NFTPanel from "./components/NFTPanel";
import LogViewer from "./components/LogViewer";

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-4">Prometheus Prime Interface</h1>
      <PromptForm />
      <NFTPanel />
      <LogViewer />
    </div>
  );
}

export default App;
