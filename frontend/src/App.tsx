import { useMemo, useState } from "react";
import {
  Activity,
  ArrowUpRight,
  CircleHelp,
  Compass,
  ExternalLink,
  Eye,
  Filter,
  Globe2,
  Layers3,
  MapPin,
  Play,
  Radio,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Video,
} from "lucide-react";
import "./styles.css";

type Region = "All regions" | "Americas" | "Europe" | "Africa" | "Asia-Pacific";
type Footage = { id: number; title: string; location: string; region: Exclude<Region, "All regions">; country: string; type: string; duration: string; source: string; sourceUrl: string; footageUrl: string; lat: number; lon: number; accent: string; tags: string[] };

const FOOTAGE: Footage[] = [
  { id: 1, title: "Night lights over Manhattan", location: "New York, United States", region: "Americas", country: "US", type: "City aerial", duration: "01:42", source: "NASA / Wikimedia Commons", sourceUrl: "https://commons.wikimedia.org/wiki/Category:Videos_of_New_York_City", footageUrl: "https://commons.wikimedia.org/w/index.php?search=New+York+City+night+video&title=Special:MediaSearch&type=video", lat: 40.7, lon: -74, accent: "coral", tags: ["urban", "night"] },
  { id: 2, title: "Kraków old town walk", location: "Kraków, Poland", region: "Europe", country: "PL", type: "Street level", duration: "03:18", source: "Wikimedia Commons", sourceUrl: "https://commons.wikimedia.org/wiki/Category:Videos_of_Krak%C3%B3w", footageUrl: "https://commons.wikimedia.org/w/index.php?search=Krakow+street+video&title=Special:MediaSearch&type=video", lat: 50.06, lon: 19.94, accent: "amber", tags: ["heritage", "street"] },
  { id: 3, title: "Aerial view of Cape Town", location: "Cape Town, South Africa", region: "Africa", country: "ZA", type: "Coastal aerial", duration: "02:26", source: "Wikimedia Commons", sourceUrl: "https://commons.wikimedia.org/wiki/Category:Videos_of_Cape_Town", footageUrl: "https://commons.wikimedia.org/w/index.php?search=Cape+Town+aerial+video&title=Special:MediaSearch&type=video", lat: -33.92, lon: 18.42, accent: "mint", tags: ["coast", "landscape"] },
  { id: 4, title: "Tokyo from above", location: "Tokyo, Japan", region: "Asia-Pacific", country: "JP", type: "City aerial", duration: "00:58", source: "Wikimedia Commons", sourceUrl: "https://commons.wikimedia.org/wiki/Category:Videos_of_Tokyo", footageUrl: "https://commons.wikimedia.org/w/index.php?search=Tokyo+aerial+video&title=Special:MediaSearch&type=video", lat: 35.68, lon: 139.69, accent: "violet", tags: ["urban", "transit"] },
  { id: 5, title: "Amazon river basin", location: "Manaus, Brazil", region: "Americas", country: "BR", type: "Nature / river", duration: "04:12", source: "Internet Archive", sourceUrl: "https://archive.org/search?query=amazon%20river%20video", footageUrl: "https://archive.org/search?query=amazon%20river%20open%20footage", lat: -3.12, lon: -60.02, accent: "mint", tags: ["nature", "water"] },
  { id: 6, title: "Helsinki harbor cam", location: "Helsinki, Finland", region: "Europe", country: "FI", type: "Live camera", duration: "LIVE", source: "Wikimedia Commons", sourceUrl: "https://commons.wikimedia.org/wiki/Category:Videos_of_Helsinki", footageUrl: "https://commons.wikimedia.org/w/index.php?search=Helsinki+harbor+video&title=Special:MediaSearch&type=video", lat: 60.17, lon: 24.94, accent: "blue", tags: ["harbor", "live"] },
  { id: 7, title: "Kathmandu valley", location: "Kathmandu, Nepal", region: "Asia-Pacific", country: "NP", type: "Documentary", duration: "05:04", source: "Wikimedia Commons", sourceUrl: "https://commons.wikimedia.org/wiki/Category:Videos_of_Kathmandu", footageUrl: "https://commons.wikimedia.org/w/index.php?search=Kathmandu+valley+video&title=Special:MediaSearch&type=video", lat: 27.72, lon: 85.32, accent: "amber", tags: ["culture", "valley"] },
  { id: 8, title: "Iceland volcanic field", location: "Reykjanes, Iceland", region: "Europe", country: "IS", type: "Field recording", duration: "02:51", source: "Internet Archive", sourceUrl: "https://archive.org/search?query=iceland%20volcano%20video", footageUrl: "https://archive.org/search?query=iceland%20volcano%20open%20footage", lat: 63.86, lon: -22.55, accent: "coral", tags: ["geology", "field"] },
];

const nav = ["Overview", "God's Eye", "Sources", "Collections"];
const regions: Region[] = ["All regions", "Americas", "Europe", "Africa", "Asia-Pacific"];

function project(lon: number, lat: number) {
  return { left: `${((lon + 180) / 360) * 100}%`, top: `${((90 - lat) / 180) * 100}%` };
}

function App() {
  const [activeNav, setActiveNav] = useState("God's Eye");
  const [region, setRegion] = useState<Region>("All regions");
  const [selected, setSelected] = useState<Footage>(FOOTAGE[0]);
  const [query, setQuery] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const filtered = useMemo(() => FOOTAGE.filter((item) => (region === "All regions" || item.region === region) && `${item.title} ${item.location} ${item.tags.join(" ")}`.toLowerCase().includes(query.toLowerCase())), [region, query]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Eye size={19} /></div><div><strong>Infographic<span>X</span></strong><small>VISUAL KNOWLEDGE OS</small></div></div>
        <div className="workspace-label">WORKSPACE <button aria-label="Help"><CircleHelp size={13} /></button></div>
        <div className="workspace-select"><Globe2 size={15} /><span>World Atlas</span><span className="chevron">⌄</span></div>
        <nav className="main-nav">{nav.map((item) => <button key={item} className={activeNav === item ? "active" : ""} onClick={() => setActiveNav(item)}>{item === "God's Eye" ? <Eye size={16} /> : item === "Sources" ? <Layers3 size={16} /> : item === "Collections" ? <Compass size={16} /> : <Activity size={16} />}<span>{item}</span>{item === "God's Eye" && <i />}</button>)}</nav>
        <div className="sidebar-bottom"><div className="live-card"><div className="live-head"><Radio size={14} /><span>OPEN DATA MODE</span><b>●</b></div><p>Public sources only.<br />No proprietary imagery.</p></div><div className="user-row"><div className="avatar">MG</div><div><b>mina.gayid</b><small>Personal workspace</small></div><span>•••</span></div></div>
      </aside>

      <main className="content">
        <header className="topbar"><div className="breadcrumb"><span>World Atlas</span><b>/</b><strong>God's Eye</strong></div><div className="top-actions"><span className="sync"><span className="pulse" /> Live index synced</span><button className="icon-button"><SlidersHorizontal size={16} /></button><button className="share-button"><ExternalLink size={14} /> Share view</button></div></header>
        <section className="hero"><div><div className="eyebrow"><span className="eyebrow-line" /> GLOBAL INTELLIGENCE LAYER</div><h1>See the world.<br /><em>Follow the story.</em></h1><p>Explore open maps and real-world footage by place. Every pin is traceable to a public archive.</p></div><div className="hero-stats"><div><strong>8,412</strong><span>indexed locations</span></div><div><strong>42</strong><span>open collections</span></div><div><strong>100%</strong><span>source-linked</span></div></div></section>
        <section className="toolbar"><div className="search"><Search size={16} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search locations, themes, or places…" /></div><div className="region-tabs">{regions.map((item) => <button key={item} className={region === item ? "selected" : ""} onClick={() => setRegion(item)}>{item}</button>)}</div><button className={showFilters ? "filter-button active" : "filter-button"} onClick={() => setShowFilters(!showFilters)}><Filter size={15} /> Filters</button></section>
        {showFilters && <div className="filter-note"><ShieldCheck size={15} /> Showing public, source-linked footage only <span>·</span> Map: OpenStreetMap contributors <button onClick={() => setShowFilters(false)}>Close</button></div>}

        <section className="atlas-grid"><div className="map-panel"><div className="panel-header"><div><span className="panel-kicker">LIVE ATLAS</span><h2>Global field view</h2></div><div className="map-controls"><button aria-label="Zoom in">+</button><button aria-label="Zoom out">−</button><button aria-label="Reset view"><Compass size={15} /></button></div></div><div className="map-canvas"><div className="map-glow" /><div className="landmass landmass-a" /><div className="landmass landmass-b" /><div className="landmass landmass-c" /><div className="landmass landmass-d" />{filtered.map((item) => { const pos = project(item.lon, item.lat); return <button key={item.id} className={`map-pin ${selected.id === item.id ? "selected" : ""}`} style={pos} onClick={() => setSelected(item)} aria-label={`Open ${item.title}`}><span className="pin-ring" /><span className="pin-dot" /></button>; })}<div className="map-label label-north">NORTH AMERICA</div><div className="map-label label-europe">EUROPE</div><div className="map-label label-africa">AFRICA</div><div className="map-label label-asia">ASIA-PACIFIC</div><div className="map-footer"><span><span className="legend-dot" /> Open footage</span><span><span className="legend-grid" /> OpenStreetMap</span><a href="https://www.openstreetmap.org/" target="_blank" rel="noreferrer">View full map <ArrowUpRight size={13} /></a></div></div></div>
          <aside className="detail-panel"><div className="detail-head"><div><span className="panel-kicker">SELECTED SIGNAL</span><h2>Place intelligence</h2></div><span className="source-count">{filtered.length} pins</span></div><div className={`feature-image ${selected.accent}`}><div className="image-grid" /><div className="feature-overlay"><span className="type-pill"><Video size={13} /> {selected.type}</span>{selected.duration === "LIVE" && <span className="live-pill"><span /> LIVE</span>}</div><div className="play-button"><Play size={18} fill="currentColor" /></div><span className="coordinate">{selected.lat.toFixed(2)}° {selected.lat >= 0 ? "N" : "S"} / {Math.abs(selected.lon).toFixed(2)}° {selected.lon >= 0 ? "E" : "W"}</span></div><div className="selected-copy"><div className="location-line"><MapPin size={15} /><span>{selected.location}</span><span className="country-code">{selected.country}</span></div><h3>{selected.title}</h3><div className="tag-row">{selected.tags.map((tag) => <span key={tag}>#{tag}</span>)}</div><p>Publicly available field footage selected for geographic context. Open the archive to inspect license, resolution, and original contributor.</p><div className="detail-actions"><a className="primary-action" href={selected.footageUrl} target="_blank" rel="noreferrer"><Play size={14} fill="currentColor" /> Open footage</a><a className="secondary-action" href={selected.sourceUrl} target="_blank" rel="noreferrer">Source archive <ArrowUpRight size={14} /></a></div></div></aside></section>

        <section className="footage-section"><div className="section-heading"><div><span className="panel-kicker">FIELD NOTES</span><h2>Open footage near you</h2></div><button className="view-all">View all <ArrowUpRight size={14} /></button></div><div className="footage-grid">{filtered.slice(0, 4).map((item) => <button className={`footage-card ${selected.id === item.id ? "card-selected" : ""}`} key={item.id} onClick={() => setSelected(item)}><div className={`thumb ${item.accent}`}><div className="thumb-lines" /><span className="thumb-type">{item.type}</span><span className="thumb-play"><Play size={12} fill="currentColor" /></span><span className="thumb-duration">{item.duration}</span></div><div className="card-copy"><span>{item.region} · {item.country}</span><h3>{item.title}</h3><p><MapPin size={12} /> {item.location}</p></div></button>)}</div></section>
        <footer><span>God's Eye is an open-source research layer for InfographicX.</span><span><a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap attribution</a> · <a href="https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia" target="_blank" rel="noreferrer">Check media licenses</a></span></footer>
      </main>
    </div>
  );
}

export default App;
