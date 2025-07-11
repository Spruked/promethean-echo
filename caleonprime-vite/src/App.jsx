import './tailwind.css';
import PromptForm from './components/PromptForm';
import NFTPanel from './components/NFTPanel';
import LogViewer from './components/LogViewer';
import EchoStackLiveWidget from './components/EchoStackLiveWidget';

function App() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-2xl p-8 bg-white rounded-lg shadow-lg text-center">
        <h1 className="text-2xl font-bold mb-6">🧠 Prometheus Prime Dashboard</h1>

        <EchoStackLiveWidget />
        <PromptForm />
        <NFTPanel />
        <LogViewer />

      </div>
    </div>
  );
}

export default App;
