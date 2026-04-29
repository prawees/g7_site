// RAMA G7 — Masthead component
// Props: activePage ("editorial"|"about"|"join")

const Masthead = ({ activePage = "editorial", onNav, hideWordmark = false }) => {
  const links = [
    { id: "editorial", label: "Editorial" },
    { id: "about",     label: "About" },
    { id: "join",      label: "Join" },
  ];
  return (
    <header style={mastheadStyles.root}>
      <div style={mastheadStyles.inner}>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          {!hideWordmark && (
          <a href="#" style={mastheadStyles.mark} onClick={e => { e.preventDefault(); onNav && onNav("editorial"); }}>
            <img src="../../assets/logo.png" alt="" style={mastheadStyles.logo} />
            <div style={{ display: "flex", alignItems: "baseline", gap: 4, lineHeight: 1 }}>
              <span style={mastheadStyles.wordmarkRama}>RAMA</span><span style={mastheadStyles.wordmarkG7}>G7</span>
            </div>
          </a>
          )}
          {hideWordmark && (
          <a href="#" style={{ ...mastheadStyles.mark, pointerEvents: "all" }} onClick={e => { e.preventDefault(); onNav && onNav("editorial"); }}>
            <img src="../../assets/logo.png" alt="" style={mastheadStyles.logo} />
          </a>
          )}
          <span style={mastheadStyles.tagline}>medical innovators @ Ramathibodi</span>
        </div>
        <nav style={mastheadStyles.nav}>
          {links.map(l => (
            <a key={l.id} href="#"
              style={{ ...mastheadStyles.navLink, ...(activePage === l.id ? mastheadStyles.navActive : {}) }}
              onClick={e => { e.preventDefault(); onNav && onNav(l.id); }}>
              {l.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
};

const mastheadStyles = {
  root: { background: "#030F27", borderBottom: "1px solid rgba(20,181,157,0.3)" },
  inner: { maxWidth: 1080, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 24, padding: "14px 32px" },
  mark: { display: "flex", alignItems: "center", gap: 10, textDecoration: "none" },
  logo: { height: 30, width: "auto", opacity: 0.9 },
  wordmarkRama: { fontFamily: "'Space Grotesk',system-ui,sans-serif", fontSize: "1.25rem", fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase", color: "#F4EFE6", lineHeight: 1, marginTop: 2 },
  wordmarkG7:   { fontFamily: "'Space Grotesk',system-ui,sans-serif", fontSize: "1.25rem", fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase", color: "#14B59D", lineHeight: 1 },
  tagline: { fontFamily: "'DM Sans','IBM Plex Sans Thai',system-ui,sans-serif", fontSize: "0.68rem", letterSpacing: "0.04em", color: "#9AA0AB", fontWeight: 400, whiteSpace: "nowrap" },
  nav: { display: "flex", gap: 28, alignItems: "center", fontFamily: "'DM Sans','IBM Plex Sans Thai',system-ui,sans-serif" },
  navLink: { fontSize: "0.78rem", fontWeight: 500, letterSpacing: "0.04em", color: "#F4EFE6", textDecoration: "none", opacity: 0.6 },
  navActive: { color: "#14B59D", opacity: 1 },
};

Object.assign(window, { Masthead });
