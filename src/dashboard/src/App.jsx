import React from 'react';
import { createRoot } from 'react-dom/client';
import MetricsDisplay from './components/MetricsDisplay';

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <h1 className="text-3xl font-bold text-center mb-4">x-agentic-ai Dashboard</h1>
      <MetricsDisplay />
    </div>
  );
}

const root = createRoot(document.getElementById('root'));
root.render(<App />);