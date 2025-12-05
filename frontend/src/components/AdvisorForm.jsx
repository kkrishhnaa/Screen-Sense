import { useState } from 'react';
import axios from 'axios';
import ResultCard from './ResultCard';

export default function AdvisorForm() {
  const [formData, setFormData] = useState({
    age: '', gender: 'Male', primary_device: 'Smartphone', educational_hours: '', recreational_hours: '',
    health_impacts: '', urban_or_rural: 'Urban'
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [serverError, setServerError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (errors[e.target.name]) setErrors({ ...errors, [e.target.name]: '' });
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.age || formData.age < 8 || formData.age > 18) newErrors.age = 'Age 8-18 required';
    if (formData.educational_hours < 0) newErrors.educational_hours = 'Non-negative required';
    if (formData.recreational_hours < 0) newErrors.recreational_hours = 'Non-negative required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setServerError('');
    try {
      const res = await axios.post('http://localhost:8000/api/recommend', formData);
      setResult(res.data);
    } catch (err) {
      setServerError(err.response?.data?.detail || 'Server error—try again.');
    }
    setLoading(false);
  };

  return (
    <div className="form-card" style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem', background: '#f8f9fa', borderRadius: '15px', boxShadow: '0 8px 25px rgba(0,0,0,0.1)' }}>
      <h1 style={{ textAlign: 'center', color: '#007bff', marginBottom: '2rem' }}>Screen Time Advisor</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Age:
          <input type="number" name="age" value={formData.age} onChange={handleChange} style={{ width: '100%' }} />
          {errors.age && <span className="error">{errors.age}</span>}
        </label>

        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Gender:
          <select name="gender" value={formData.gender} onChange={handleChange} style={{ width: '100%' }}>
            <option>Male</option><option>Female</option><option>Other</option>
          </select>
        </label>

        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Primary Device:
          <select name="primary_device" value={formData.primary_device} onChange={handleChange} style={{ width: '100%' }}>
            <option>Smartphone</option><option>Laptop</option><option>TV</option><option>Tablet</option>
          </select>
        </label>

        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Educational Hours:
          <input type="number" step="0.1" name="educational_hours" value={formData.educational_hours} onChange={handleChange} style={{ width: '100%' }} />
          {errors.educational_hours && <span className="error">{errors.educational_hours}</span>}
        </label>

        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Recreational Hours:
          <input type="number" step="0.1" name="recreational_hours" value={formData.recreational_hours} onChange={handleChange} style={{ width: '100%' }} />
          {errors.recreational_hours && <span className="error">{errors.recreational_hours}</span>}
        </label>

        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Health Impacts (optional, comma-separated):
          <input type="text" name="health_impacts" value={formData.health_impacts} onChange={handleChange} style={{ width: '100%' }} />
        </label>

        <label style={{ fontWeight: 'bold', color: '#555' }}>
          Urban or Rural:
          <select name="urban_or_rural" value={formData.urban_or_rural} onChange={handleChange} style={{ width: '100%' }}>
            <option>Urban</option><option>Rural</option>
          </select>
        </label>

        <button type="submit" disabled={loading} style={{ width: '100%', marginTop: '1rem' }}>
          {loading ? 'Analyzing...' : 'Get Recommendations'}
        </button>
      </form>

      {loading && <p className="loading" style={{ textAlign: 'center', marginTop: '1rem' }}>Loading...</p>}
      {serverError && <p className="error" style={{ textAlign: 'center', marginTop: '1rem' }}>{serverError}</p>}
      {result && <ResultCard result={result} exceeded={result.exceeded} />}
    </div>
  );
}