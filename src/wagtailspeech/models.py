from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page


class TextToSpeechMixin(models.Model):
    """
    Mixin class to support synthesize speech functionalities.

    Example:
        class HomePage(TextToSpeechMixin, Page):
            def get_tts_context(self, request):
                return self.title
    """

    class Meta:
        abstract = True

    def get_tts_context(self, request):
        return None


class TextToSpeechEntry(models.Model):
    page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
    )
    hash = models.TextField()
    audio_stream = models.FileField(_("audio stream"))
    created_at = models.DateTimeField(
        verbose_name=_("created at"), auto_now_add=True, null=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.page)
