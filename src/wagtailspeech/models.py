from django.db import models
from django.utils.translation import ugettext as _
from wagtail.wagtailcore.models import Page


class SynthesizeSpeechMixin(models.Model):
    """
    Mixin class to support synthesize speech functionalities.

    Example:
        class HomePage(SynthesizeSpeechMixin, Page):
            def get_speech_text(self):
                return self.title
    """
    audio_stream = models.FileField(_("audio stream"), blank=True, null=True)

    class Meta:
        abstract = True

    def get_speech_text(self):
        return None
