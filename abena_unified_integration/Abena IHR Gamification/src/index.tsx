import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import AbenaGamificationSystem from './components/AbenaGamificationSystem';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <AbenaGamificationSystem />
  </React.StrictMode>
); 