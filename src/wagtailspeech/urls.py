from django.urls import path

from wagtailspeech.views import SynthesizeSpeechView

app_name = "wagtailspeech"

urlpatterns = [
    path(
        "synthesize-speech/<str:id>/",
        SynthesizeSpeechView.as_view(),
        name="synthesize-speech",
    ),
]  # noqa
