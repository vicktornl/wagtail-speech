from django.contrib import admin

from wagtailspeech.models import TextToSpeechEntry


class TextToSpeechEntryAdmin(admin.ModelAdmin):
    list_display = ("page", "created_at")
    list_select_related = ("page",)


admin.site.register(TextToSpeechEntry, TextToSpeechEntryAdmin)
