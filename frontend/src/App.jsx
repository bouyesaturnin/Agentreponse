import { useState, useEffect } from "react";
import axios from "axios";

const API = "https://agentreponse-production.up.railway.app/api";
const ETOILES = (n) => "★".repeat(n) + "☆".repeat(5 - n);
const NOTE_COLOR = (n) => n >= 4 ? "#10B981" : n === 3 ? "#D4A843" : "#EF4444";
const PLATEFORMES = ["google","trustpilot","tripadvisor","autre"];
const SECTEURS = ["Restaurant / Bar","Hôtel / Hébergement","Commerce de détail","Clinique / Santé","Agence immobilière","Garage / Auto","Beauté / Bien-être / Santé","Avocat","Autre"];

export default function App() {
  const [onglet, setOnglet] = useState("generer");
  const [form, setForm] = useState({ nom_entreprise:"", plateforme:"google", secteur:"", auteur_avis:"", note:"5", contenu_avis:"" });
  const [resultat, setResultat] = useState(null);
  const [loading, setLoading] = useState(false);
  const [erreur, setErreur] = useState("");
  const [historique, setHistorique] = useState([]);
  const [reponseEditee, setReponseEditee] = useState("");
  const [copie, setCopie] = useState(false);

  // Email modal
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [emailDest, setEmailDest] = useState("");
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailSuccess, setEmailSuccess] = useState("");
  const [emailErreur, setEmailErreur] = useState("");

  const upd = (k, v) => setForm(f => ({ ...f, [k]: v }));

  const chargerHistorique = async () => {
    try { const { data } = await axios.get(`${API}/historique/`); setHistorique(data); } catch {}
  };

  useEffect(() => { if (onglet === "historique") chargerHistorique(); }, [onglet]);

  const generer = async () => {
    setLoading(true); setErreur(""); setResultat(null);
    try {
      const { data } = await axios.post(`${API}/generer/`, form);
      setResultat(data); setReponseEditee(data.reponse);
    } catch (e) { setErreur(e.response?.data?.error || "Erreur de connexion"); }
    finally { setLoading(false); }
  };

  const copier = () => {
    navigator.clipboard.writeText(reponseEditee);
    setCopie(true); setTimeout(() => setCopie(false), 2000);
  };

  const envoyerEmail = async () => {
    if (!emailDest) { setEmailErreur("Entrez un email destinataire"); return; }
    setEmailLoading(true); setEmailErreur(""); setEmailSuccess("");
    try {
      await axios.post(`${API}/envoyer-email/`, {
        email_destinataire: emailDest,
        avis_id: resultat.id,
        reponse: reponseEditee,
      });
      setEmailSuccess(`Email envoyé à ${emailDest} !`);
      setTimeout(() => { setShowEmailModal(false); setEmailDest(""); setEmailSuccess(""); }, 2500);
    } catch (e) {
      setEmailErreur(e.response?.data?.error || "Erreur d'envoi");
    } finally { setEmailLoading(false); }
  };

  const marquerPubliee = async (id) => {
    await axios.patch(`${API}/historique/`, { id, publiee: true });
    chargerHistorique();
  };

  return (
    <div style={{ minHeight:"100vh", background:"var(--bg-deep)", display:"flex", flexDirection:"column" }}>

      {/* MODAL EMAIL */}
      {showEmailModal && (
        <div style={{ position:"fixed", inset:0, background:"rgba(0,0,0,0.75)", zIndex:200,
          display:"flex", alignItems:"center", justifyContent:"center" }}
          onClick={e => e.target === e.currentTarget && setShowEmailModal(false)}>
          <div className="fade-up" style={{ background:"var(--bg-card)", border:"1px solid var(--border)",
            borderRadius:14, padding:"36px", width:460, boxShadow:"0 24px 60px rgba(0,0,0,0.5)" }}>

            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:24 }}>
              <div>
                <h3 style={{ margin:0, fontFamily:"'Playfair Display',serif", fontSize:20, color:"var(--white)" }}>
                  Envoyer par email
                </h3>
                <p style={{ margin:"4px 0 0", fontSize:13, color:"var(--muted)" }}>
                  La réponse sera envoyée prête à copier-coller
                </p>
              </div>
              <button onClick={() => setShowEmailModal(false)} style={{ width:32, height:32, borderRadius:"50%",
                background:"rgba(255,255,255,0.05)", color:"var(--muted)", fontSize:16 }}>✕</button>
            </div>

            {/* Aperçu */}
            <div style={{ background:"var(--bg-input)", borderRadius:8, padding:"14px 16px",
              marginBottom:20, borderLeft:`3px solid ${NOTE_COLOR(resultat?.note||5)}` }}>
              <p style={{ margin:0, fontSize:13, color:"var(--muted)", marginBottom:4 }}>Réponse à envoyer :</p>
              <p style={{ margin:0, fontSize:14, color:"#A0C0B8", lineHeight:1.6, fontStyle:"italic" }}>
                "{reponseEditee.substring(0, 120)}{reponseEditee.length > 120 ? "..." : ""}"
              </p>
            </div>

            <Label>Email du destinataire</Label>
            <input type="email" value={emailDest} onChange={e => setEmailDest(e.target.value)}
              placeholder="client@sonentreprise.fr"
              onKeyDown={e => e.key === "Enter" && envoyerEmail()}
              style={{ marginBottom:16 }}/>

            {emailErreur && (
              <div style={{ padding:"10px 14px", background:"rgba(239,68,68,0.1)",
                border:"1px solid rgba(239,68,68,0.3)", borderRadius:6,
                color:"var(--red)", fontSize:13, marginBottom:16 }}>⚠ {emailErreur}</div>
            )}
            {emailSuccess && (
              <div style={{ padding:"10px 14px", background:"rgba(16,185,129,0.1)",
                border:"1px solid var(--emerald-dim)", borderRadius:6,
                color:"var(--emerald)", fontSize:13, marginBottom:16 }}>✓ {emailSuccess}</div>
            )}

            <div style={{ display:"flex", gap:10 }}>
              <button onClick={envoyerEmail} disabled={emailLoading || !emailDest} style={{
                flex:1, padding:"12px", borderRadius:8, fontSize:15,
                fontFamily:"'Playfair Display',serif",
                background: emailLoading ? "var(--emerald-dim)" : "linear-gradient(135deg,#065F46,#10B981)",
                color:"#fff", fontWeight:600,
                boxShadow: emailLoading ? "none" : "0 4px 20px rgba(16,185,129,0.25)"
              }}>
                {emailLoading ? "Envoi en cours..." : "✉ Envoyer"}
              </button>
              <button onClick={() => setShowEmailModal(false)} style={{
                padding:"12px 20px", borderRadius:8,
                background:"transparent", border:"1px solid var(--border)",
                color:"var(--muted)", fontSize:14
              }}>Annuler</button>
            </div>
          </div>
        </div>
      )}

      {/* HEADER */}
      <header style={{ background:"linear-gradient(180deg,#0A1F1A,var(--bg-deep))", borderBottom:"1px solid var(--border)", padding:"0 48px", display:"flex", alignItems:"center", justifyContent:"space-between", height:72, width:"100%", boxSizing:"border-box", position:"sticky", top:0, zIndex:100 }}>
        <div style={{ display:"flex", alignItems:"center", gap:14 }}>
          <div style={{ width:40, height:40, borderRadius:8, background:"linear-gradient(135deg,#065F46,#10B981)", display:"flex", alignItems:"center", justifyContent:"center", boxShadow:"0 0 20px rgba(16,185,129,0.3)", fontSize:20 }}>✦</div>
          <div>
            <div style={{ fontFamily:"'Playfair Display',serif", fontSize:19, fontWeight:700, color:"var(--white)", letterSpacing:1 }}>ReponsIA</div>
            <div style={{ fontSize:10, color:"var(--muted)", letterSpacing:3 }}>AGENT DE RÉPONSE AUX AVIS</div>
          </div>
        </div>
        <nav style={{ display:"flex", gap:4 }}>
          {[["generer","✦ Générer"],["historique","◎ Historique"]].map(([id,label]) => (
            <button key={id} onClick={() => setOnglet(id)} style={{ padding:"8px 20px", borderRadius:6, background:onglet===id?"rgba(16,185,129,0.12)":"transparent", color:onglet===id?"var(--emerald-glow)":"var(--muted)", border:onglet===id?"1px solid var(--emerald-dim)":"1px solid transparent", fontSize:14 }}>{label}</button>
          ))}
        </nav>
        <div style={{ display:"flex", alignItems:"center", gap:6, padding:"6px 14px", background:"rgba(16,185,129,0.08)", border:"1px solid var(--emerald-dim)", borderRadius:20 }}>
          <span style={{ width:7, height:7, borderRadius:"50%", background:"var(--emerald)", display:"inline-block", animation:"pulse-dot 2s infinite" }}/>
          <span style={{ fontSize:12, color:"var(--emerald)", letterSpacing:1 }}>MODE DÉMO ACTIF</span>
        </div>
      </header>

      <main style={{ flex:1, width:"100%", padding:"40px 48px", boxSizing:"border-box" }}>

        {/* ONGLET GÉNÉRER */}
        {onglet === "generer" && (
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:32, alignItems:"start" }}>

            {/* Formulaire */}
            <div className="fade-up">
              <h1 style={{ fontFamily:"'Playfair Display',serif", fontSize:32, fontWeight:600, color:"var(--white)", marginBottom:6, lineHeight:1.2 }}>
                Répondez à vos avis<br/><em style={{ color:"var(--emerald-glow)", fontStyle:"italic" }}>en 10 secondes.</em>
              </h1>
              <p style={{ color:"var(--muted)", fontSize:15, marginBottom:28 }}>Collez un avis client — l'agent génère une réponse professionnelle et personnalisée.</p>

              <div style={{ background:"var(--bg-card)", border:"1px solid var(--border)", borderRadius:12, padding:"28px" }}>
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16, marginBottom:18 }}>
                  <div><Label>Nom de l'entreprise</Label><input value={form.nom_entreprise} onChange={e=>upd("nom_entreprise",e.target.value)} placeholder="Le Petit Bistrot"/></div>
                  <div><Label>Secteur d'activité</Label><select value={form.secteur} onChange={e=>upd("secteur",e.target.value)}><option value="">-- Choisir --</option>{SECTEURS.map(s=><option key={s} value={s}>{s}</option>)}</select></div>
                </div>
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16, marginBottom:18 }}>
                  <div><Label>Plateforme</Label><select value={form.plateforme} onChange={e=>upd("plateforme",e.target.value)}>{PLATEFORMES.map(p=><option key={p} value={p}>{p.charAt(0).toUpperCase()+p.slice(1)}</option>)}</select></div>
                  <div><Label>Auteur de l'avis</Label><input value={form.auteur_avis} onChange={e=>upd("auteur_avis",e.target.value)} placeholder="Marie D."/></div>
                </div>

                <div style={{ marginBottom:18 }}>
                  <Label>Note</Label>
                  <div style={{ display:"flex", gap:8, marginTop:6 }}>
                    {[1,2,3,4,5].map(n => (
                      <button key={n} onClick={()=>upd("note",String(n))} style={{ width:44, height:44, borderRadius:8, background:parseInt(form.note)===n?NOTE_COLOR(n):"var(--bg-input)", border:`1px solid ${parseInt(form.note)===n?NOTE_COLOR(n):"var(--border)"}`, color:parseInt(form.note)===n?"#fff":"var(--muted)", fontSize:18 }}>★</button>
                    ))}
                    <span style={{ alignSelf:"center", marginLeft:8, color:NOTE_COLOR(parseInt(form.note)), fontFamily:"'Playfair Display',serif", fontSize:15 }}>
                      {["","Très négatif","Négatif","Mitigé","Positif","Excellent"][parseInt(form.note)]}
                    </span>
                  </div>
                </div>

                <div style={{ marginBottom:24 }}>
                  <Label>Contenu de l'avis</Label>
                  <textarea rows={5} value={form.contenu_avis} onChange={e=>upd("contenu_avis",e.target.value)} placeholder="Copiez-collez l'avis client ici..." style={{ resize:"vertical" }}/>
                </div>

                {erreur && <div style={{ padding:"10px 14px", background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.3)", borderRadius:6, color:"var(--red)", fontSize:14, marginBottom:16 }}>⚠ {erreur}</div>}

                <button onClick={generer} disabled={loading||!form.nom_entreprise||!form.auteur_avis||!form.contenu_avis||!form.secteur} style={{ width:"100%", padding:"14px", borderRadius:8, fontSize:15, fontFamily:"'Playfair Display',serif", letterSpacing:1, background:loading?"var(--emerald-dim)":"linear-gradient(135deg,#065F46,#10B981)", color:"#fff", fontWeight:600, boxShadow:loading?"none":"0 4px 20px rgba(16,185,129,0.25)" }}>
                  {loading ? "Génération en cours..." : "✦ Générer la réponse"}
                </button>
              </div>
            </div>

            {/* Résultat */}
            <div className="fade-up-2">
              {!resultat ? (
                <div>
                  <div style={{ background:"var(--bg-card)", border:"1px dashed var(--border)", borderRadius:12, padding:"60px 40px", textAlign:"center" }}>
                    <div style={{ fontSize:48, marginBottom:16, opacity:0.25 }}>✦</div>
                    <p style={{ fontFamily:"'Playfair Display',serif", fontSize:20, color:"var(--muted)", fontStyle:"italic" }}>La réponse générée<br/>apparaîtra ici</p>
                  </div>
                  <div style={{ marginTop:20, padding:"16px 20px", background:"rgba(16,185,129,0.05)", border:"1px solid var(--emerald-dim)", borderRadius:10 }}>
                    <div style={{ fontSize:11, letterSpacing:2, color:"var(--emerald)", marginBottom:8 }}>CONSEIL AGENT</div>
                    <p style={{ fontSize:14, color:"var(--muted)", lineHeight:1.6 }}>Répondre aux avis Google dans les <strong style={{color:"var(--white)"}}>7 jours</strong> augmente votre note de <strong style={{color:"var(--emerald)"}}>+0.3 étoile</strong> et votre taux de conversion de <strong style={{color:"var(--emerald)"}}>+18%</strong>.</p>
                  </div>
                </div>
              ) : (
                <div className="fade-up" style={{ background:"var(--bg-card)", border:`1px solid ${NOTE_COLOR(resultat.note)}40`, borderRadius:12, padding:"28px" }}>
                  <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:20 }}>
                    <div>
                      <div style={{ fontFamily:"'Playfair Display',serif", fontSize:18, color:"var(--white)", marginBottom:4 }}>Réponse générée</div>
                      <div style={{ display:"flex", alignItems:"center", gap:10 }}>
                        <span style={{ color:NOTE_COLOR(resultat.note), fontSize:18, letterSpacing:2 }}>{ETOILES(resultat.note)}</span>
                        <span style={{ fontSize:13, color:"var(--muted)" }}>— {resultat.auteur}</span>
                        {resultat.mode==="demo" && <span style={{ fontSize:11, padding:"2px 8px", background:"rgba(212,168,67,0.15)", border:"1px solid rgba(212,168,67,0.3)", borderRadius:10, color:"var(--gold)" }}>DÉMO</span>}
                      </div>
                    </div>
                    <div style={{ width:36, height:36, borderRadius:"50%", background:`${NOTE_COLOR(resultat.note)}20`, border:`1px solid ${NOTE_COLOR(resultat.note)}50`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:18, color:NOTE_COLOR(resultat.note) }}>
                      {resultat.note>=4?"✓":resultat.note===3?"~":"!"}
                    </div>
                  </div>

                  <div style={{ height:1, background:`linear-gradient(90deg,${NOTE_COLOR(resultat.note)}40,transparent)`, marginBottom:20 }}/>

                  <div style={{ background:"var(--bg-input)", borderRadius:8, padding:"12px 14px", marginBottom:20, borderLeft:`3px solid ${NOTE_COLOR(resultat.note)}` }}>
                    <div style={{ fontSize:11, letterSpacing:2, color:"var(--muted)", marginBottom:6 }}>AVIS ORIGINAL</div>
                    <p style={{ margin:0, fontSize:14, color:"#A0C0B8", lineHeight:1.6, fontStyle:"italic" }}>"{form.contenu_avis}"</p>
                  </div>

                  <div style={{ marginBottom:20 }}>
                    <div style={{ fontSize:11, letterSpacing:2, color:"var(--emerald)", marginBottom:8 }}>RÉPONSE — MODIFIABLE</div>
                    <textarea rows={6} value={reponseEditee} onChange={e=>setReponseEditee(e.target.value)} style={{ resize:"vertical", fontSize:15, lineHeight:1.7, borderColor:"var(--emerald-dim)" }}/>
                  </div>

                  {/* BOUTONS ACTION */}
                  <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:8 }}>
                    <button onClick={copier} style={{ padding:"11px 8px", borderRadius:7, background:copie?"rgba(16,185,129,0.2)":"rgba(16,185,129,0.1)", border:`1px solid ${copie?"var(--emerald)":"var(--emerald-dim)"}`, color:copie?"var(--emerald-glow)":"var(--emerald)", fontSize:13 }}>
                      {copie?"✓ Copié !":"⎘ Copier"}
                    </button>
                    <button onClick={() => { setShowEmailModal(true); setEmailErreur(""); setEmailSuccess(""); }} style={{ padding:"11px 8px", borderRadius:7, background:"rgba(212,168,67,0.1)", border:"1px solid rgba(212,168,67,0.3)", color:"var(--gold)", fontSize:13 }}>
                      ✉ Envoyer email
                    </button>
                    <button onClick={() => setResultat(null)} style={{ padding:"11px 8px", borderRadius:7, background:"transparent", border:"1px solid var(--border)", color:"var(--muted)", fontSize:13 }}>↺ Nouveau</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ONGLET HISTORIQUE */}
        {onglet === "historique" && (
          <div className="fade-up">
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:28 }}>
              <div>
                <h2 style={{ fontFamily:"'Playfair Display',serif", fontSize:26, color:"var(--white)", marginBottom:4 }}>Historique des réponses</h2>
                <p style={{ color:"var(--muted)", fontSize:14 }}>{historique.length} réponse(s) générée(s)</p>
              </div>
              <button onClick={chargerHistorique} style={{ padding:"9px 18px", borderRadius:7, background:"rgba(16,185,129,0.1)", border:"1px solid var(--emerald-dim)", color:"var(--emerald)", fontSize:14 }}>↺ Actualiser</button>
            </div>

            {historique.length === 0 ? (
              <div style={{ textAlign:"center", padding:"80px 40px", color:"var(--muted)" }}>
                <div style={{ fontSize:40, marginBottom:16, opacity:0.3 }}>◎</div>
                <p style={{ fontFamily:"'Playfair Display',serif", fontSize:18, fontStyle:"italic" }}>Aucune réponse encore générée</p>
              </div>
            ) : (
              <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
                {historique.map(a => (
                  <div key={a.id} style={{ background:"var(--bg-card)", border:`1px solid ${a.publiee?"var(--emerald-dim)":"var(--border)"}`, borderRadius:10, padding:"20px 24px", display:"grid", gridTemplateColumns:"1fr 2fr auto", gap:20, alignItems:"start" }}>
                    <div>
                      <div style={{ fontFamily:"'Playfair Display',serif", fontSize:15, color:"var(--white)", marginBottom:4 }}>{a.nom_entreprise}</div>
                      <div style={{ fontSize:13, color:"var(--muted)", marginBottom:6 }}>{a.auteur_avis} · {a.plateforme}</div>
                      <div style={{ color:NOTE_COLOR(a.note), fontSize:16, letterSpacing:2 }}>{ETOILES(a.note)}</div>
                      <div style={{ fontSize:12, color:"var(--muted)", marginTop:8 }}>{a.created_at}</div>
                    </div>
                    <div>
                      <div style={{ fontSize:11, letterSpacing:2, color:"var(--muted)", marginBottom:6 }}>RÉPONSE</div>
                      <p style={{ fontSize:14, color:"#A0C0B8", lineHeight:1.6 }}>{a.reponse_finale}</p>
                    </div>
                    <div style={{ display:"flex", flexDirection:"column", gap:8, alignItems:"flex-end" }}>
                      {a.publiee ? (
                        <span style={{ fontSize:12, padding:"4px 10px", background:"rgba(16,185,129,0.15)", border:"1px solid var(--emerald-dim)", borderRadius:10, color:"var(--emerald)" }}>✓ Publiée</span>
                      ) : (
                        <button onClick={()=>marquerPubliee(a.id)} style={{ padding:"7px 14px", borderRadius:6, fontSize:13, background:"rgba(16,185,129,0.1)", border:"1px solid var(--emerald-dim)", color:"var(--emerald)" }}>Marquer publiée</button>
                      )}
                      <button onClick={()=>navigator.clipboard.writeText(a.reponse_finale)} style={{ padding:"7px 14px", borderRadius:6, fontSize:13, background:"transparent", border:"1px solid var(--border)", color:"var(--muted)" }}>⎘ Copier</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      <footer style={{ borderTop:"1px solid var(--border)", padding:"16px 48px", display:"flex", justifyContent:"space-between" }}>
        <span style={{ fontSize:12, color:"var(--muted)" }}>ReponsIA · Agent de réponse aux avis clients</span>
        <span style={{ fontSize:12, color:"var(--muted)" }}>Django · Claude API · SendGrid · React</span>
      </footer>
    </div>
  );
}

function Label({ children }) {
  return <label style={{ display:"block", fontSize:11, letterSpacing:2, color:"var(--muted)", marginBottom:6, textTransform:"uppercase" }}>{children}</label>;
}
