// RAMA G7 — Footer component

const Footer = () => (
  <footer style={footerStyles.root}>
    <div style={footerStyles.inner}>
      <div>
        <div style={footerStyles.heading}>RAMA G7 Club | ชมรมแพทย์นวัตกรรามา</div>
        <p style={footerStyles.desc}>สำหรับนศพ.ที่สนใจสร้างนวัตกรรมทางการแพทย์<br/>คณะแพทยศาสตร์โรงพยาบาลรามาธิบดี<br/>มหาวิทยาลัยมหิดล</p>
      </div>
      <div>
        <div style={footerStyles.heading}>ติดต่อ</div>
        {["Facebook", "Instagram", "Email the editors"].map(l => (
          <a key={l} href="#" style={footerStyles.link}>{l}</a>
        ))}
      </div>
    </div>
    <div style={footerStyles.meta}>© 2026 RAMA G7 Club</div>
  </footer>
);

const footerStyles = {
  root: { background: "#030F27", color: "#9AA0AB", fontFamily: "'IBM Plex Sans','Sarabun',system-ui,sans-serif", fontSize: "0.85rem", padding: "48px 32px 24px", marginTop: 72 },
  inner: { maxWidth: 1080, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 40 },
  heading: { fontSize: "0.72rem", letterSpacing: "0.16em", textTransform: "uppercase", color: "#F4EFE6", fontWeight: 500, marginBottom: 10, fontFamily: "'DM Sans','IBM Plex Sans Thai',system-ui,sans-serif" },
  desc: { color: "#9AA0AB", fontSize: "0.82rem", lineHeight: 1.6, marginBottom: 0, fontFamily: "'IBM Plex Sans Thai','DM Sans',system-ui,sans-serif" },
  link: { color: "#9AA0AB", textDecoration: "none", display: "block", marginBottom: 6, fontSize: "0.82rem", fontFamily: "'DM Sans','IBM Plex Sans Thai',system-ui,sans-serif" },
  meta: { maxWidth: 1080, margin: "20px auto 0", paddingTop: 14, borderTop: "1px solid rgba(244,239,230,0.08)", fontSize: "0.72rem", textAlign: "center", color: "#9AA0AB" },
};

Object.assign(window, { Footer });
