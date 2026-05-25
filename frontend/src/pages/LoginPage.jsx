import { useUsers } from "../hooks/useUsers";

export default function LoginPage({ onLogin }) {
  const { users, loading } = useUsers();

  return (
    <div className="login-page">
      <section className="login-hero">
        <p className="eyebrow">EcoCart · inicio de sesión</p>
        <h1>Entra con un usuario real cargado desde la base de datos.</h1>
        <p className="login-copy">
          El frontend ya no usa datos simulados. Si no hay usuarios disponibles, verás un mensaje de estado.
        </p>
      </section>

      <section className="login-panel">
        <h2>Selecciona un usuario</h2>
        {loading ? (
          <p className="empty-state-message">Cargando usuarios...</p>
        ) : users.length === 0 ? (
          <p className="empty-state-message">No se encontraron usuarios.</p>
        ) : (
          <div className="user-card-list">
            {users.map((user) => (
              <button
                key={user.user_id}
                className="user-card"
                onClick={() => onLogin(user.user_id)}
              >
                {user.avatar_url ? (
                  <img src={user.avatar_url} alt={user.name} className="user-avatar" />
                ) : (
                  <span className="user-avatar avatar-placeholder">{(user.name || "?").trim().charAt(0).toUpperCase()}</span>
                )}
                <div className="user-card-body">
                  <strong>{user.name}</strong>
                  <span>{user.email}</span>
                  <span className="user-card-meta">{user.default_address}</span>
                </div>
                <span className="user-card-action">Entrar</span>
              </button>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}