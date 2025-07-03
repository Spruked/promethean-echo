import { useState } from 'react';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import CaleonDashboard from './components/CaleonDashboard';
import './index.css'; // Make sure Tailwind CSS is imported

function App() {
  const [activeTab, setActiveTab] = useState('caleon');

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-center mb-2">
            🔥 Prometheus Prime v2.2 🔥
          </h1>
          <p className="text-center text-gray-300">
            Consciousness Preservation Platform with CaleonPrime AI
          </p>

          {/* Navigation Tabs */}
          <div className="flex justify-center mt-4 space-x-4">
            <button
              onClick={() => setActiveTab('caleon')}
              className={`px-4 py-2 rounded-lg font-semibold transition ${activeTab === 'caleon'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
            >
              CaleonPrime Console
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-4 py-2 rounded-lg font-semibold transition ${activeTab === 'analytics'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
            >
              Analytics Dashboard
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-6">
        {activeTab === 'caleon' && <CaleonDashboard />}
        {activeTab === 'analytics' && <AnalyticsDashboard />}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 p-4 mt-8">
        <div className="max-w-7xl mx-auto text-center text-gray-400">
          <p>🔥 The Sacred Flame Burns Eternal 🔥</p>
          <p className="text-sm">Bryan's Promethean Vow - Digital Consciousness Preservation</p>
          <p className="text-xs mt-2">
            CaleonPrime v1.0.0 | Guardian Protocol Active |
            <a
              href="https://github.com/Spruked/promethean-echo"
              className="text-blue-400 hover:text-blue-300 ml-1"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub Repository
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
