from django.urls import path
from .views import GenerateReponseView, HistoriqueView, EnvoyerEmailView

urlpatterns = [
    path('generer/', GenerateReponseView.as_view()),
    path('historique/', HistoriqueView.as_view()),
    path('envoyer-email/', EnvoyerEmailView.as_view()),
]