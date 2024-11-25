from django.conf import settings
from django.core.files import File
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from wagtail.models import Page

from wagtailspeech.models import TextToSpeechEntry, TextToSpeechMixin
from wagtailspeech.utils import get_hash_from_tts_context, synthesize_speech

OUTPUT_FORMAT = getattr(settings, "WAGTAIL_SPEECH_OUTPUT_FORMAT", "mp3")


class SynthesizeSpeechView(View):
    def get(self, request, id, *args, **kwargs):
        try:
            page = Page.objects.get(id=id)
        except Page.DoesNotExist:
            res = JsonResponse({"error": "Page not found"})
            res.status_code = 404
            return res

        specific_page = page.specific

        if not isinstance(specific_page, TextToSpeechMixin):
            res = JsonResponse({"error": "Page is not instance of TextToSpeechMixin"})
            res.status_code = 500
            return res

        tts_context = specific_page.get_tts_context(request)
        tts_hash = get_hash_from_tts_context(tts_context)

        try:
            entry = TextToSpeechEntry.objects.get(page=page, hash=tts_hash)
        except TextToSpeechEntry.DoesNotExist:
            audio_stream = synthesize_speech(page, tts_context)

            entry = TextToSpeechEntry.objects.create(
                page=page,
                hash=tts_hash,
                audio_stream=File(
                    audio_stream,
                    name="%s.%s.%s"
                    % (
                        page.id,
                        tts_hash,
                        OUTPUT_FORMAT,
                    ),
                ),
            )

        return JsonResponse(
            {
                "text": tts_context,
                "audio_stream": entry.audio_stream.url,
            }
        )
