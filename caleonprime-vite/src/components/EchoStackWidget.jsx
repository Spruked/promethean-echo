import React from 'react';

function EchoStackWidget() {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6 text-center">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">
        🔊 EchoStack Live Widget
      </h2>
      <div className="text-gray-600">
        <p>Status: <span className="font-bold text-green-600">Online</span></p>
        <p>Mode: <span className="font-medium">Listening</span></p>
        <p>Last Signal: <span className="italic">Awaiting Transmission...</span></p>
      </div>
    </div>
  );
}

export default EchoStackWidget;
