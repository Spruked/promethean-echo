// src/components/DashboardTabs.jsx
import React, { useState } from 'react';
import EchoStackWidget from './components/EchoStackWidget';

function DashboardTabs() {
  const [activeTab, setActiveTab] = useState('master');

  return (
    <div className="min-h-screen bg-gray-100 p-6 text-center">
      <h1 className="text-4xl font-bold text-red-600 mb-8">🔥 PROMETHEUS PRIME</h1>

      <div className="flex justify-center space-x-4 mb-6">
        <button
          className={`px-6 py-2 font-bold text-white rounded ${
            activeTab === 'master' ? 'bg-cyan-400 text-gray-900' : 'bg-gray-800'
          }`}
          onClick={() => setActiveTab('master')}
        >
          Master Dashboard
        </button>
        <button
          className={`px-6 py-2 font-bold text-white rounded ${
            activeTab === 'user' ? 'bg-cyan-400 text-gray-900' : 'bg-gray-800'
          }`}
          onClick={() => setActiveTab('user')}
        >
          User Dashboard
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-6 max-w-3xl mx-auto">
        {activeTab === 'master' && (
          <div className="text-left">
            <h2 className="text-2xl font-semibold mb-4">Master Dashboard</h2>
            <div className="space-y-2">
              <div className="p-4 bg-gray-100 rounded shadow">🔥 AI Core Status: Active</div>
              <div className="p-4 bg-gray-100 rounded shadow">📈 System Performance: Optimized</div>
            </div>
            <footer className="mt-6 text-sm text-gray-500">
              Prometheus Prime - Fortified Intelligence
            </footer>
          </div>
        )}

        {activeTab === 'user' && (
          <div className="text-left">
            <h2 className="text-2xl font-semibold mb-4">User Dashboard</h2>
            <div className="space-y-2">
              <div className="p-4 bg-gray-100 rounded shadow">📊 User Insights: Adaptive Tracking Enabled</div>
              <div className="p-4 bg-gray-100 rounded shadow">⏳ Habit Evolution Metrics: Synced</div>
            </div>
            <footer className="mt-6 text-sm text-gray-500">
              Connected to EchoStack - Continuous Learning Active
            </footer>
          </div>
        )}
      </div>
    </div>
  );
}

export default DashboardTabs;
