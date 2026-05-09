from django.db import models

class ReponseAvis(models.Model):
    PLATEFORMES = [('google', 'Google'), ('trustpilot', 'Trustpilot'), ('tripadvisor', 'TripAdvisor'), ('autre', 'Autre')]
    NOTES = [(1,'⭐'),(2,'⭐⭐'),(3,'⭐⭐⭐'),(4,'⭐⭐⭐⭐'),(5,'⭐⭐⭐⭐⭐')]

    nom_entreprise  = models.CharField(max_length=200)
    plateforme      = models.CharField(max_length=50, choices=PLATEFORMES)
    auteur_avis     = models.CharField(max_length=200)
    note            = models.IntegerField(choices=NOTES)
    contenu_avis    = models.TextField()
    reponse_generee = models.TextField()
    reponse_finale  = models.TextField(blank=True)
    publiee         = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nom_entreprise} — {self.auteur_avis} ({self.note}★)"