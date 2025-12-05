export default function ResultCard({ result, exceeded }) {
  const { recommendations, details, risk } = result;
  if (result.error) {
    return (
      <div className="result" style={{ background: '#f8d7da', color: '#721c24', padding: '2rem', borderRadius: '10px', textAlign: 'center', boxShadow: '0 4px 15px rgba(220,53,69,0.2)' }}>
        <h3 style={{ marginBottom: '1rem' }}>Oops!</h3>
        <p>{result.error}</p>
      </div>
    );
  }
  const summaryClass = exceeded ? 'summary exceeded' : 'summary';
  const summary = exceeded
    ? `You exceed recommended limit by ${details.exceeded_by} hrs — Risk: ${risk}. Reduce recreational screen time.`
    : `Your screen time is within limits (${risk}) — Great job!`;

  return (
    <div className="result" style={{ marginTop: '2rem', padding: '2rem', background: 'white', borderRadius: '15px', boxShadow: '0 8px 25px rgba(0,0,0,0.1)' }}>
      <p className={summaryClass} style={{ fontSize: '1.4em', fontWeight: 'bold', marginBottom: '1.5rem', padding: '1.5rem', borderRadius: '10px', textAlign: 'center' }}>
        {summary}
      </p>
      <ul style={{ paddingLeft: '1.5rem', lineHeight: '1.6', background: '#f8f9fa', padding: '1.5rem', borderRadius: '10px' }}>
        {recommendations.map((rec, i) => (
          <li key={i} style={{ marginBottom: '0.75rem', padding: '0.5rem', background: 'white', borderRadius: '5px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)' }}>
            {rec}
          </li>
        ))}
      </ul>
      <div className="details" style={{ marginTop: '2rem', background: '#e9ecef', padding: '1.5rem', borderRadius: '10px', borderLeft: '5px solid #007bff' }}>
        <strong style={{ color: '#007bff', display: 'block', marginBottom: '1rem' }}>Details:</strong>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
          <div><strong>Recommended:</strong> {details.recommended_limit} hrs</div>
          <div><strong>Your Total:</strong> {details.total_screen_time} hrs</div>
          <div><strong>Exceeded By:</strong> {details.exceeded_by} hrs</div>
          <div><strong>Risk Level:</strong> <span style={{ color: '#dc3545', fontWeight: 'bold' }}>{risk}</span></div>
          <div><strong>Peer Averages:</strong> Age {details.peer_averages.age}h, Gender {details.peer_averages.gender}h, Device {details.peer_averages.device}h</div>
        </div>
      </div>
    </div>
  );
}