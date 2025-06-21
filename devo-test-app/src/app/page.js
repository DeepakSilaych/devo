'use client';

import { useState } from 'react';

export default function Home() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResponse('');

    try {
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: input }),
      });

      const data = await res.json();
      
      if (res.ok) {
        setResponse(`✅ Success: ${data.message}`);
      } else {
        setResponse(`❌ Error: ${data.error}`);
      }
    } catch (error) {
      setResponse(`❌ Network Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 dark:text-white mb-4">
            🧪 TestDevoApp
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Test CI/CD pipeline with intentional failures for Devo integration
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="command" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Enter Command
              </label>
              <input
                id="command"
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Try: hello, warn, or fail"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium py-2 px-4 rounded-md transition-colors"
            >
              {loading ? 'Processing...' : 'Submit Command'}
            </button>
          </form>

          {response && (
            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-md">
              <h3 className="font-medium text-gray-800 dark:text-gray-200 mb-2">Response:</h3>
              <p className="text-sm text-gray-600 dark:text-gray-300">{response}</p>
            </div>
          )}

          <div className="mt-8 p-4 bg-blue-50 dark:bg-blue-900 rounded-md">
            <h3 className="font-medium text-blue-800 dark:text-blue-200 mb-2">Command Examples:</h3>
            <ul className="text-sm text-blue-600 dark:text-blue-300 space-y-1">
              <li><code className="bg-blue-100 dark:bg-blue-800 px-2 py-1 rounded">hello</code> - Normal operation (CI passes)</li>
              <li><code className="bg-yellow-100 dark:bg-yellow-800 px-2 py-1 rounded">warn</code> - Warning message (CI shows warning)</li>
              <li><code className="bg-red-100 dark:bg-red-800 px-2 py-1 rounded">fail</code> - Error condition (CI fails)</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
