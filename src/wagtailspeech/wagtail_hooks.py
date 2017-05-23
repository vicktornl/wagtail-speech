from wagtail.wagtailcore import hooks

from wagtailspeech.utils import synthesize_speech_from_page


@hooks.register('after_edit_page')
def synthesize_speech(request, page):
    synthesize_speech_from_page(request, page)
