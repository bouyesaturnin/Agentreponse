import json
import logging
import urllib.request
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import ReponseAvis
from .email_service import envoyer_reponse_email

logger = logging.getLogger(__name__)

DEMO_REPONSES = {
    5: "Merci infiniment pour ce retour chaleureux, {auteur} ! 🙏 Toute notre équipe est ravie que votre expérience ait été à la hauteur de vos attentes. Votre satisfaction est notre plus belle récompense. Nous vous attendons avec plaisir pour une prochaine visite !",
    4: "Merci beaucoup pour votre avis positif, {auteur} ! Nous sommes heureux que votre expérience se soit bien passée. Votre retour nous est précieux et nous aide à nous améliorer continuellement. À très bientôt !",
    3: "Merci pour votre retour, {auteur}. Nous prenons note de vos remarques et nous engageons à améliorer les points que vous avez soulevés. N'hésitez pas à nous contacter directement pour qu'on puisse échanger à ce sujet.",
    2: "Merci de nous avoir partagé votre expérience, {auteur}. Nous sommes sincèrement désolés que votre visite n'ait pas répondu à vos attentes. Pourriez-vous nous contacter directement afin que nous puissions trouver une solution ?",
    1: "Nous vous présentons nos sincères excuses, {auteur}. La situation que vous décrivez ne reflète pas nos standards de qualité. Nous vous invitons à nous contacter directement afin de comprendre ce qui s'est passé et vous apporter une réponse adaptée.",
}


def call_claude(prompt):
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        return None
    data = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 400,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        return result["content"][0]["text"]


class GenerateReponseView(APIView):
    def post(self, request):
        d = request.data
        for f in ["nom_entreprise", "auteur_avis", "note", "contenu_avis", "plateforme", "secteur"]:
            if not d.get(f):
                return Response({"error": f"Champ requis : {f}"}, status=400)

        note = int(d["note"])
        prompt = f"""Tu es un community manager expert. Rédige une réponse professionnelle, chaleureuse et personnalisée à cet avis client.

Entreprise : {d["nom_entreprise"]} (secteur : {d["secteur"]})
Plateforme : {d["plateforme"]}
Auteur : {d["auteur_avis"]}
Note : {note}/5
Avis : {d["contenu_avis"]}

Règles :
- Maximum 4 phrases
- Ton adapté à la note
- Commence par remercier l'auteur par son prénom
- Pas d'emojis excessifs (max 1)
- Termine par une invitation à revenir (note >= 3) ou à contacter directement (note <= 2)

Réponds UNIQUEMENT avec la réponse, sans explication."""

        reponse = call_claude(prompt)
        if reponse is None:
            template = DEMO_REPONSES.get(note, DEMO_REPONSES[3])
            reponse = template.format(auteur=d["auteur_avis"])

        obj = ReponseAvis.objects.create(
            nom_entreprise=d["nom_entreprise"],
            plateforme=d["plateforme"],
            auteur_avis=d["auteur_avis"],
            note=note,
            contenu_avis=d["contenu_avis"],
            reponse_generee=reponse,
            reponse_finale=reponse,
        )

        return Response({
            "id": obj.id,
            "reponse": reponse,
            "note": note,
            "auteur": d["auteur_avis"],
            "mode": "ia" if settings.ANTHROPIC_API_KEY else "demo"
        })


class HistoriqueView(APIView):
    def get(self, request):
        avis = ReponseAvis.objects.all()[:20]
        return Response([{
            "id": a.id,
            "nom_entreprise": a.nom_entreprise,
            "plateforme": a.plateforme,
            "auteur_avis": a.auteur_avis,
            "note": a.note,
            "contenu_avis": a.contenu_avis,
            "reponse_finale": a.reponse_finale,
            "publiee": a.publiee,
            "created_at": a.created_at.strftime("%d/%m/%Y %H:%M"),
        } for a in avis])

    def patch(self, request):
        avis_id = request.data.get("id")
        try:
            avis = ReponseAvis.objects.get(id=avis_id)
            if "reponse_finale" in request.data:
                avis.reponse_finale = request.data["reponse_finale"]
            if "publiee" in request.data:
                avis.publiee = request.data["publiee"]
            avis.save()
            return Response({"ok": True})
        except ReponseAvis.DoesNotExist:
            return Response({"error": "Introuvable"}, status=404)


class EnvoyerEmailView(APIView):
    def post(self, request):
        d = request.data
        destinataire = d.get("email_destinataire")
        avis_id = d.get("avis_id")
        reponse_editee = d.get("reponse")

        if not destinataire:
            return Response({"error": "Email destinataire requis"}, status=400)
        if not avis_id:
            return Response({"error": "ID de l'avis requis"}, status=400)

        try:
            avis = ReponseAvis.objects.get(id=avis_id)

            if reponse_editee:
                avis.reponse_finale = reponse_editee
                avis.save()

            # Log pour debug
            logger.error(f"RESEND_API_KEY = '{settings.RESEND_API_KEY[:10]}...'")

            status_code = envoyer_reponse_email(destinataire, {
                "nom_entreprise": avis.nom_entreprise,
                "plateforme": avis.plateforme,
                "auteur_avis": avis.auteur_avis,
                "note": avis.note,
                "contenu_avis": avis.contenu_avis,
                "reponse": avis.reponse_finale,
            })

            if status_code in [200, 201, 202]:
                return Response({"ok": True, "message": f"Email envoyé à {destinataire}"})
            else:
                return Response({"error": f"Erreur envoi : {status_code}"}, status=500)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)