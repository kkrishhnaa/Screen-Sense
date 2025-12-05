import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div style={{ textAlign: 'center', padding: '3rem 2rem', background: '#f8f9fa', borderRadius: '15px', boxShadow: '0 8px 25px rgba(0,0,0,0.1)', margin: '2rem 0' }}>
      <h1 style={{ color: '#007bff', fontSize: '3em', marginBottom: '1rem' }}>Screen Time Advisor</h1>
      <p style={{ fontSize: '1.2em', color: '#555', marginBottom: '1rem' }}>This app helps teens (8-18) assess their screen time habits and get personalized recommendations.</p>
      <p style={{ fontSize: '1.1em', color: '#666', marginBottom: '2rem' }}>Based on your age, device, hours, and more, we'll compare to peers and suggest improvements.</p>
      <Link to="/advisor" style={{ textDecoration: 'none' }}>
        <button style={{ fontSize: '1.2em' }}>Get Started</button>
      </Link>
    </div>
  );
}