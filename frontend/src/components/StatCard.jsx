function StatCard({ title, value, note, type = "blue" }) {
  return (
    <div className={`stat-card ${type}`}>
      <p>{title}</p>

      <h2>{value}</h2>

      <span>{note}</span>
    </div>
  );
}

export default StatCard;
