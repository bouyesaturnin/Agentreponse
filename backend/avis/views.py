import json
import urllib.request
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import ReponseAvis
from .email_service import envoyer_reponse_email


DEMO_REPONSES = {
    "professionnel": {
        5: "Nous vous remercions sincèrement pour votre retour positif, {auteur}. Votre satisfaction représente notre priorité absolue et constitue la meilleure reconnaissance de notre engagement quotidien. Nous serions ravis de vous accueillir à nouveau très prochainement.",
        4: "Nous vous remercions pour votre avis, {auteur}. Votre retour constructif nous est précieux et nous permet d'améliorer continuellement la qualité de nos services. Nous espérons avoir le plaisir de vous accueillir à nouveau.",
        3: "Nous vous remercions pour votre retour, {auteur}. Nous prenons note de vos observations et mettons tout en œuvre pour améliorer votre expérience. N'hésitez pas à nous contacter directement pour tout échange complémentaire.",
        2: "Nous vous remercions d'avoir pris le temps de partager votre expérience, {auteur}. Nous regrettons que votre visite n'ait pas répondu à vos attentes et nous vous invitons à nous contacter afin de trouver une solution adaptée.",
        1: "Nous vous présentons nos sincères excuses pour cette expérience, {auteur}. La situation décrite ne reflète pas nos standards de qualité et nous souhaitons y remédier. Veuillez nous contacter directement pour que nous puissions vous apporter une réponse appropriée.",
    },
    "chaleureux": {
        5: "Merci infiniment pour ce retour si chaleureux, {auteur} ! 🙏 Toute notre équipe est vraiment touchée par vos mots et ravie que votre expérience ait été aussi belle. On vous attend avec impatience pour une prochaine fois !",
        4: "Merci beaucoup pour votre avis positif, {auteur} ! On est vraiment contents que votre expérience se soit bien passée. Vos retours nous aident à nous améliorer chaque jour. À très bientôt !",
        3: "Merci pour votre retour honnête, {auteur}. On prend vos remarques très à cœur et on va travailler pour faire mieux. N'hésitez pas à nous écrire directement — votre avis compte vraiment pour nous !",
        2: "Merci d'avoir partagé votre vécu, {auteur}. On est vraiment désolés que ça ne se soit pas passé comme vous l'espériez. Contactez-nous directement — on tient à arranger les choses pour vous !",
        1: "On vous présente nos sincères excuses, {auteur}. Ce que vous décrivez ne nous ressemble pas du tout et on le prend très au sérieux. Appelez-nous directement — on veut vraiment comprendre et tout faire pour réparer ça.",
    },
    "formel": {
        5: "Nous vous adressons nos plus vifs remerciements pour votre témoignage, {auteur}. Votre appréciation constitue pour nos équipes une source de motivation et d'encouragement dans l'exercice de leurs missions. Nous demeurons à votre disposition pour tout futur service.",
        4: "Nous vous remercions de l'attention portée à notre établissement, {auteur}. Votre évaluation a été dûment prise en considération par nos services. Nous restons à votre entière disposition.",
        3: "Nous accusons réception de votre évaluation, {auteur}, et vous remercions de l'intérêt que vous portez à notre établissement. Vos observations feront l'objet d'un examen attentif de notre part.",
        2: "Nous avons bien pris connaissance de votre retour, {auteur}, et vous remercions de nous en avoir informés. Nous vous invitons à prendre contact avec nos services afin que nous puissions examiner votre situation dans les meilleurs délais.",
        1: "Nous accusons réception de votre signalement, {auteur}, et vous présentons nos excuses pour les désagréments occasionnés. Nous vous invitons à contacter notre service relations clientèle afin qu'une solution puisse vous être proposée dans les meilleurs délais.",
    },
    "dynamique": {
        5: "WOW, merci {auteur} ! 🌟 Ça fait vraiment plaisir de lire ça ! Toute l'équipe est aux anges — on met tout notre cœur dans ce qu'on fait et savoir que ça se ressent, c'est la meilleure récompense. On vous attend vite !",
        4: "Super retour {auteur}, merci ! 😊 Ravi que ça vous ait plu ! On est en constante amélioration et vos retours sont notre carburant. À très bientôt !",
        3: "Merci {auteur} pour ce retour franc ! On note tout ça et on s'améliore. Si vous voulez en discuter, on est là — on adore les échanges directs !",
        2: "Aïe, désolé pour ça {auteur} ! Ce n'est vraiment pas ce qu'on veut vous faire vivre. Contactez-nous vite — on va régler ça ensemble !",
        1: "Oh non {auteur}, vraiment désolés ! Ce n'est pas du tout le niveau qu'on veut offrir. Contactez-nous immédiatement — on prend ça très au sérieux et on va tout faire pour arranger la situation.",
    },
}

TONS_PROMPTS = {
    "professionnel": "professionnel et soigné, avec un vocabulaire soutenu mais accessible",
    "chaleureux": "chaleureux, humain et authentique, comme si tu parlais à un ami",
    "formel": "très formel et institutionnel, avec un vocabulaire corporate et protocolaire",
    "dynamique": "dynamique, enthousiaste et moderne, avec de l'énergie et de la spontanéité",
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
        ton = d.get("ton", "chaleureux")
        ton_description = TONS_PROMPTS.get(ton, TONS_PROMPTS["chaleureux"])

        prompt = f"""Tu es un community manager expert. Rédige une réponse {ton_description} à cet avis client.

Entreprise : {d["nom_entreprise"]} (secteur : {d["secteur"]})
Plateforme : {d["plateforme"]}
Auteur : {d["auteur_avis"]}
Note : {note}/5
Avis : {d["contenu_avis"]}

Règles strictes :
- Maximum 4 phrases
- Ton : {ton_description}
- Commence par remercier l'auteur par son prénom
- Pas d'emojis excessifs (max 1 si ton chaleureux/dynamique, aucun si professionnel/formel)
- Termine par une invitation à revenir (note >= 3) ou à contacter directement (note <= 2)

Réponds UNIQUEMENT avec la réponse, sans explication ni introduction."""

        reponse = call_claude(prompt)
        if reponse is None:
            template = DEMO_REPONSES.get(ton, DEMO_REPONSES["chaleureux"]).get(note, DEMO_REPONSES["chaleureux"][3])
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
            "ton": ton,
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
            return Response({"error": str(e)}, status=500)