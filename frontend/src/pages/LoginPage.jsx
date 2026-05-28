import { useUsers } from "../hooks/useUsers";

export default function LoginPage({ onLogin }) {
  const { users, loading } = useUsers();

  return (
    <div className="login-page">
      <section className="login-hero">
        <p className="eyebrow">EcoCart · inicio de sesión</p>
        <h1>Inicia sesión para seguir comprando.</h1>
        <p className="login-copy">
          Elige un usuario disponible para entrar al catálogo, revisar tu carrito y continuar tus compras donde las dejaste.
        </p>
      </section>

      <section className="login-panel">
        <h2>Usuarios disponibles</h2>
        {loading ? (
          <p className="empty-state-message">Estamos cargando las cuentas disponibles...</p>
        ) : users.length === 0 ? (
          <p className="empty-state-message">No hay usuarios disponibles por el momento. Intenta nuevamente en unos segundos.</p>
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
                <span className="user-card-action">Ingresar</span>
              </button>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}