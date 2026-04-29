// RAMA G7 — Post Card (index list item) — refined with tags, thumbnail, Thai

const CATEGORY_TAGS = {
  "รังสีวิทยา": { bg: "rgba(99,102,241,0.12)", color: "#4338ca" },
  "AI":         { bg: "rgba(20,181,157,0.12)",  color: "#0E8A78" },
  "กฎหมาย":    { bg: "rgba(245,158,11,0.12)",  color: "#b45309" },
  "NLP":        { bg: "rgba(236,72,153,0.12)",  color: "#be185d" },
  "คลินิก":    { bg: "rgba(59,130,246,0.12)",  color: "#1d4ed8" },
};

const THUMB_GRADIENTS = [
  "linear-gradient(135deg,#1a1a2e 0%,#3a3a5c 40%,#6a6a9a 100%)",
  "linear-gradient(135deg,#0d3b2e 0%,#0E8A78 60%,#14B59D 100%)",
  "linear-gradient(135deg,#1a0d2e 0%,#4a1a6a 60%,#7a3a9a 100%)",
];

const PostCard = ({ post, onClick, index = 0 }) => {
  const [hovered, setHovered] = React.useState(false);
  const thumbGrad = THUMB_GRADIENTS[index % THUMB_GRADIENTS.length];
  return (
    <a href="#"
      style={{ ...pcStyles.card, ...(hovered ? pcStyles.cardHover : {}) }}
      onClick={e => { e.preventDefault(); onClick && onClick(post); }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}>
      <div style={pcStyles.content}>
        <div style={pcStyles.topRow}>
          <span style={pcStyles.num}>{String(post.num).padStart(2,"0")}</span>
          <span style={pcStyles.dot}>·</span>
          <span style={pcStyles.meta}>{post.date}</span>
          <span style={pcStyles.dot}>·</span>
          <span style={pcStyles.meta}>{post.categoryTh || post.category}</span>
          {(post.tags||[]).map(t => {
            const s = CATEGORY_TAGS[t] || { bg: "rgba(3,15,39,0.08)", color: "#5C6675" };
            return <span key={t} style={{ ...pcStyles.tag, background: s.bg, color: s.color }}>{t}</span>;
          })}
        </div>
        <div style={{ ...pcStyles.title, ...(hovered ? pcStyles.titleHover : {}) }}>{post.titleTh || post.title}</div>
        <div style={pcStyles.summary}>{post.summaryTh || post.summary}</div>
        <div style={pcStyles.author}>{post.author}, RAMA G7</div>
      </div>
      <div style={{ position: "relative", overflow: "hidden", minHeight: 120 }}>
        <div style={{ width: "100%", height: "100%", minHeight: 120, background: thumbGrad, display: "flex", alignItems: "center", justifyContent: "center" }}>
          <svg width="40" height="40" viewBox="0 0 44 44" fill="none" style={{ opacity: 0.25 }}>
            <rect x="8" y="4" width="28" height="36" rx="2" stroke="white" strokeWidth="1.5"/>
            <circle cx="22" cy="22" r="9" stroke="white" strokeWidth="1.5"/>
            <line x1="22" y1="4" x2="22" y2="40" stroke="white" strokeWidth="0.75" strokeDasharray="2 2"/>
          </svg>
        </div>
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(to right,#F4EFE6 0%,transparent 45%)" }}></div>
      </div>
    </a>
  );
};

const pcStyles = {
  card: { display: "grid", gridTemplateColumns: "1fr 130px", borderTop: "1px solid #DCD4C2", textDecoration: "none", color: "#030F27", transition: "background 160ms ease", background: "transparent", overflow: "hidden" },
  cardHover: { background: "rgba(20,181,157,0.04)" },
  content: { padding: "18px 16px 18px 4px", display: "flex", flexDirection: "column", gap: 0, minWidth: 0, overflow: "hidden" },
  topRow: { display: "flex", alignItems: "center", gap: 8, marginBottom: 12, flexWrap: "wrap" },
  num: { fontFamily: "'DM Sans','IBM Plex Sans Thai',system-ui,sans-serif", fontSize: "0.68rem", letterSpacing: "0.1em", color: "#9AA0AB", fontWeight: 500 },
  dot: { color: "#DCD4C2", fontSize: "0.7rem" },
  meta: { fontFamily: "'DM Sans','IBM Plex Sans Thai',system-ui,sans-serif", fontSize: "0.68rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "#5C6675", fontWeight: 500 },
  tag: { fontSize: "0.62rem", fontWeight: 600, letterSpacing: "0.06em", textTransform: "uppercase", padding: "2px 7px", borderRadius: 2 },
  title: { fontFamily: "'DM Sans','IBM Plex Sans Thai',system-ui,sans-serif", fontSize: "1.1rem", fontWeight: 700, lineHeight: 1.25, marginBottom: 6, color: "#030F27", letterSpacing: "-0.01em", transition: "color 120ms ease" },
  titleHover: { color: "#0E8A78" },
  summary: { color: "#5C6675", fontSize: "0.85rem", lineHeight: 1.55, fontFamily: "'IBM Plex Sans Thai','DM Sans',system-ui,sans-serif" },
  author: { fontFamily: "'DM Sans','IBM Plex Sans Thai',system-ui,sans-serif", fontSize: "0.68rem", color: "#9AA0AB", marginTop: 8, fontWeight: 500, letterSpacing: "0.04em" },
};

Object.assign(window, { PostCard, CATEGORY_TAGS });
