import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './components/Home';
import AdvisorForm from './components/AdvisorForm';
import FeedbackForm from './components/FeedbackForm';
import './index.css';

function App() {
  return (
    <Router>
      <div className="app">
        <nav style={{ padding: '1rem', background: '#f0f0f0', textAlign: 'center' }}>
          <Link to="/" style={{ margin: '0 1rem', color: 'blue', textDecoration: 'none' }}>Home</Link>
          <Link to="/advisor" style={{ margin: '0 1rem', color: 'blue', textDecoration: 'none' }}>Advisor</Link>
          <Link to="/feedback" style={{ margin: '0 1rem', color: 'blue', textDecoration: 'none' }}>Feedback</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/advisor" element={<AdvisorForm />} />
          <Route path="/feedback" element={<FeedbackForm />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;