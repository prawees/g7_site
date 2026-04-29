// RAMA G7 — Article View
// Props: post { date, category, readTime, title, lede, author, body, references }

const ArticleView = ({ post, onBack }) => (
  <div style={articleStyles.wrap}>
    <div style={articleStyles.article}>
      <button onClick={onBack} style={articleStyles.back}>← All articles</button>
      <header style={articleStyles.header}>
        <div style={articleStyles.meta}>
          <span>{post.date}</span>
          <span style={{ color: "#9AA0AB" }}>·</span>
          <span>{post.category}</span>
          <span style={{ color: "#9AA0AB" }}>·</span>
          <span>{post.readTime} min read</span>
        </div>
        <h1 style={articleStyles.title}>{post.title}</h1>
        <p style={articleStyles.lede}>{post.lede}</p>
        <p style={articleStyles.byline}>By <strong>{post.author}</strong>, RAMA G7</p>
      </header>
      <div style={articleStyles.banner}>
        <div style={articleStyles.bannerInner}></div>
        <div style={articleStyles.bannerOverlay}></div>
      </div>
      <div style={articleStyles.body}>
        {post.body.map((para, i) => (
          typeof para === "string"
            ? <p key={i} style={{ ...articleStyles.para, ...(i > 0 ? articleStyles.indented : {}) }}>{para}</p>
            : para.type === "h2"
              ? <h2 key={i} style={articleStyles.h2}>{para.text}</h2>
              : null
        ))}
      </div>
      {post.references && (
        <div style={articleStyles.refs}>
          <div style={articleStyles.refsLabel}>References</div>
          <ol style={articleStyles.refList}>
            {post.references.map((r, i) => <li key={i} style={articleStyles.refItem}>{r}</li>)}
          </ol>
        </div>
      )}
    </div>
  </div>
);

const articleStyles = {
  wrap: { padding: "48px 32px 96px", background: "#F4EFE6", minHeight: "100vh" },
  article: { maxWidth: "68ch", margin: "0 auto" },
  banner: { width: "100%", height: 220, marginBottom: 28, overflow: "hidden", position: "relative" },
  bannerInner: { width: "100%", height: "100%", background: "linear-gradient(135deg,#0d1f3c 0%,#0E8A78 55%,#14B59D 100%)" },
  bannerOverlay: { position: "absolute", inset: 0, background: "linear-gradient(to bottom,transparent 60%,#F4EFE6 100%)" },
  header: { paddingBottom: 20, marginBottom: 20 },
  meta: { fontFamily: "'IBM Plex Sans',system-ui,sans-serif", fontSize: "0.72rem", letterSpacing: "0.16em", textTransform: "uppercase", color: "#5C6675", marginBottom: 16, display: "flex", gap: 12, flexWrap: "wrap" },
  title: { fontFamily: "'Source Serif 4','Noto Serif Thai',Georgia,serif", fontSize: "clamp(1.8rem,3.5vw,2.6rem)", fontWeight: 600, lineHeight: 1.1, marginBottom: 14, color: "#030F27", letterSpacing: "-0.01em" },
  lede: { fontSize: "1.15rem", lineHeight: 1.55, color: "#5C6675", fontFamily: "'Source Serif 4','Noto Serif Thai',Georgia,serif", fontStyle: "italic", marginBottom: 0 },
  byline: { fontFamily: "'IBM Plex Sans',system-ui,sans-serif", fontSize: "0.82rem", color: "#030F27", marginTop: 14, marginBottom: 0 },
  body: { fontSize: "1.05rem", lineHeight: 1.7, fontFamily: "'Source Serif 4','Noto Serif Thai',Georgia,serif" },
  para: { marginBottom: 16, color: "#030F27" },
  indented: { textIndent: "1.25em" },
  h2: { fontFamily: "'Source Serif 4','Noto Serif Thai',Georgia,serif", fontSize: "1.5rem", fontWeight: 600, color: "#030F27", borderTop: "1px solid #DCD4C2", paddingTop: 24, marginTop: 40, marginBottom: 16, letterSpacing: "-0.01em" },
  refs: { marginTop: 56, paddingTop: 20, borderTop: "2px solid #030F27" },
  refsLabel: { fontFamily: "'IBM Plex Sans',system-ui,sans-serif", fontSize: "0.78rem", fontWeight: 500, letterSpacing: "0.14em", textTransform: "uppercase", color: "#030F27", marginBottom: 14 },
  refList: { marginLeft: 20, fontFamily: "'Source Serif 4',Georgia,serif" },
  refItem: { marginBottom: 10, color: "#5C6675", fontSize: "0.88rem", lineHeight: 1.55 },
};

Object.assign(window, { ArticleView });
