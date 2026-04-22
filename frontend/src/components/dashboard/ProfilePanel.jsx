function ProfilePanel({ profile, userId, loading }) {
  return (
    <article className={`panel profile-panel ${loading ? 'is-loading' : ''}`}>
      <div className="panel-head">
        <h2>Mi perfil</h2>
        <span className="panel-subtitle">USER#{userId}</span>
      </div>
      <div className="profile-layout">
        <div className="avatar">{profile.name ? profile.name.slice(0, 1).toUpperCase() : 'U'}</div>
        <div>
          <h3>{profile.name}</h3>
          <p>{profile.email}</p>
          <div className="chips">
            {(profile.addresses || []).map((item) => (
              <span key={item} className="chip">
                {item}
              </span>
            ))}
          </div>
          <div className="chips">
            {(profile.payments || []).map((item) => (
              <span key={item} className="chip chip-alt">
                {item}
              </span>
            ))}
          </div>
        </div>
      </div>
    </article>
  )
}

export default ProfilePanel
