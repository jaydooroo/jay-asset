import React, { useState } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <main>
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'settings' && <Settings />}
      </main>
    </div>
  );
}

export default App;
