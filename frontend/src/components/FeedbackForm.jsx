import { useState } from 'react';
import axios from 'axios';

export default function FeedbackForm() {
  const [formData, setFormData] = useState({ name: '', rating: 1, comments: '' });
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/api/feedback', formData);
      setSuccess(true);
      setFormData({ name: '', rating: 1, comments: '' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Submit failed.');
    }
  };

  if (success) {
    return (
      <div className="success-card" style={{ textAlign: 'center', padding: '3rem 2rem', background: '#d4edda', color: '#155724', borderRadius: '15px', boxShadow: '0 8px 25px rgba(40,167,69,0.2)', margin: '2rem 0' }}>
        <h1 style={{ fontSize: '2.5em', marginBottom: '1rem' }}>Thank You! 🎉</h1>
        <p style={{ fontSize: '1.2em' }}>Your feedback has been submitted. We appreciate it!</p>
      </div>
    );
  }

  return (
    <div className="form-card" style={{ maxWidth: '500px', margin: '0 auto', padding: '2rem', background: '#f8f9fa', borderRadius: '15px', boxShadow: '0 8px 25px rgba(0,0,0,0.1)' }}>
      <h1 style={{ textAlign: 'center', color: '#007bff', marginBottom: '2rem' }}>Feedback</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Name (optional):
          <input type="text" name="name" value={formData.name} onChange={handleChange} style={{ width: '100%' }} />
        </label>
        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Rating (1-5):
          <select name="rating" value={formData.rating} onChange={handleChange} style={{ width: '100%' }}>
            {[1,2,3,4,5].map(r => <option key={r}>{r}</option>)}
          </select>
        </label>
        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Comments:
          <textarea name="comments" value={formData.comments} onChange={handleChange} required style={{ width: '100%', minHeight: '100px' }} />
        </label>
        <button type="submit" style={{ width: '100%', marginTop: '1rem' }}>Submit Feedback</button>
      </form>
      {error && <p className="error" style={{ textAlign: 'center', marginTop: '1rem' }}>{error}</p>}
    </div>
  );
}