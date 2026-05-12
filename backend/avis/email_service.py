import urllib.request
import urllib.error
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings

NOTE_LABEL = {1: "Très négatif ★☆☆☆☆", 2: "Négatif ★★☆☆☆", 3: "Mitigé ★★★☆☆", 4: "Positif ★★★★☆", 5: "Excellent ★★★★★"}
NOTE_COLOR = {1: "#EF4444", 2: "#F97316", 3: "#EAB308", 4: "#22C55E", 5: "#10B981"}


def build_html(data):
    note = int(data.get("note", 5))
    couleur = NOTE_COLOR.get(note, "#10B981")
    label_note = NOTE_LABEL.get(note, "")
    plateforme = data.get("plateforme", "").capitalize()
    nom_entreprise = data.get("nom_entreprise", "")
    auteur = data.get("auteur_avis", "")
    avis_original = data.get("contenu_avis", "")
    reponse = data.get("reponse", "")

    lien_plateforme = '<a href="https://business.google.com" style="display:inline-block;background:linear-gradient(135deg,#065F46,#10B981);color:#fff;text-decoration:none;padding:11px 24px;border-radius:7px;font-size:14px;font-weight:600;">→ Ouvrir Google Business</a>' if plateforme.lower() == 'google' else ''

    return f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#060D0F;font-family:Georgia,serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#060D0F;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#0F2026;border-radius:16px;overflow:hidden;border:1px solid #1A3A35;">
        <tr><td style="background:linear-gradient(135deg,#065F46,#0F2026);padding:32px 40px;border-bottom:1px solid #1A3A35;">
          <span style="font-size:22px;font-weight:700;color:#F0F7F4;letter-spacing:1px;">✦ ReponsIA</span>
        </td></tr>
        <tr><td style="padding:32px 40px 16px;">
          <h1 style="margin:0 0 8px;font-size:26px;color:#F0F7F4;">Réponse prête à publier</h1>
          <p style="margin:0;font-size:15px;color:#5A8A7A;">Pour <strong style="color:#F0F7F4;">{nom_entreprise}</strong> · Avis {plateforme} de <strong style="color:#F0F7F4;">{auteur}</strong></p>
        </td></tr>
        <tr><td style="padding:0 40px 24px;">
          <span style="display:inline-block;background:#1A3A35;border:1px solid {couleur};border-radius:8px;padding:8px 16px;font-size:14px;color:{couleur};font-weight:600;">{label_note}</span>
        </td></tr>
        <tr><td style="padding:0 40px 24px;">
          <div style="background:#081518;border-radius:10px;padding:20px;border-left:3px solid {couleur};">
            <p style="margin:0 0 8px;font-size:11px;letter-spacing:2px;color:#5A8A7A;text-transform:uppercase;">Avis original</p>
            <p style="margin:0;font-size:15px;color:#A0C0B8;line-height:1.7;font-style:italic;">"{avis_original}"</p>
          </div>
        </td></tr>
        <tr><td style="padding:0 40px 24px;">
          <div style="background:#0B1F2A;border-radius:10px;padding:24px;border:1px solid #10B98140;">
            <p style="margin:0 0 12px;font-size:11px;letter-spacing:2px;color:#10B981;text-transform:uppercase;">✦ Réponse générée — prête à copier</p>
            <p style="margin:0;font-size:16px;color:#F0F7F4;line-height:1.8;">{reponse}</p>
          </div>
        </td></tr>
        <tr><td style="padding:0 40px 32px;">
          <div style="background:#0B1719;border-radius:10px;padding:20px;border:1px solid #1A3A35;">
            <p style="margin:0 0 10px;font-size:13px;color:#5A8A7A;font-weight:600;">Comment publier :</p>
            <p style="margin:0 0 4px;font-size:13px;color:#5A8A7A;">① Copiez la réponse ci-dessus</p>
            <p style="margin:0 0 4px;font-size:13px;color:#5A8A7A;">② Connectez-vous à votre espace {plateforme}</p>
            <p style="margin:0 0 16px;font-size:13px;color:#5A8A7A;">③ Collez et publiez</p>
            {lien_plateforme}
          </div>
        </td></tr>
        <tr><td style="padding:20px 40px;border-top:1px solid #1A3A35;background:#0B1719;">
          <p style="margin:0;font-size:12px;color:#2A5A4A;text-align:center;">ReponsIA · Agent de réponse aux avis · Propulsé par Claude AI</p>
        </td></tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def envoyer_reponse_email(destinataire, data):
    note = int(data.get("note", 5))
    label_note = NOTE_LABEL.get(note, "")
    plateforme = data.get("plateforme", "").capitalize()
    auteur = data.get("auteur_avis", "")

    html = build_html(data)
    subject = f"Réponse prête — Avis {plateforme} de {auteur} ({label_note})"

    resend_api_key = getattr(settings, 'RESEND_API_KEY', '').strip()

    if resend_api_key:
        payload = json.dumps({
            "from": "ReponsIA <onboarding@resend.dev>",
            "to": [destinataire],
            "subject": subject,
            "html": html,
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=payload,
            headers={
                "Authorization": f"Bearer {resend_api_key}",
                "Content-Type": "application/json",
            }
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"Resend error {e.code}: {error_body}")

    else:
        # Fallback SMTP Gmail pour dev local
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.GMAIL_USER
        msg["To"] = destinataire
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.GMAIL_USER, settings.GMAIL_PASSWORD)
            server.sendmail(settings.GMAIL_USER, destinataire, msg.as_string())

        return 200