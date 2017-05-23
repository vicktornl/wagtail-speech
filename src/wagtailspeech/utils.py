import logging

import boto3

from contextlib import closing

from django.conf import settings
from django.core.files.temp import gettempdir, NamedTemporaryFile

client = boto3.client('polly')
logger = logging.getLogger(__name__)


def synthesize_speech_from_page(request, page):
    """
    Synthesize speech from a specific Wagtail page.
    """
    if hasattr(page, 'get_speech_text'):
        logger.info("Synthesize speech for %s" % page)
        text = page.get_speech_text(request)
        if not text:
            logger.warning("No speech text found for %s" % page)
            return False
        text_type = 'ssml' if text.startswith('<speak>') else 'text'
        output_format = getattr(
            settings, 'WAGTAIL_SPEECH_OUTPUT_FORMAT', 'mp3')
        response = client.synthesize_speech(
            OutputFormat=output_format,
            SampleRate=getattr(settings, 'WAGTAIL_SPEECH_SAMPLE_RATE', '8000'),
            Text=text,
            TextType=text_type,
            VoiceId=getattr(settings, 'WAGTAIL_SPEECH_VOICE_ID', 'Joey'),
        )
        if 'AudioStream' in response and hasattr(page, 'audio_stream'):
            with closing(response['AudioStream']) as stream:
                output = '/tmp/%s.mp3' % page.slug
                try:
                    temp_dir = gettempdir()
                    temp_file = NamedTemporaryFile(dir=temp_dir)
                    temp_file.write(stream.read())
                    page.audio_stream.save("%s.%s" % (
                        page.slug, output_format[:3]), temp_file)
                except IOError as error:
                    logger.error("An error occured: %s" % error)


def get_speech_text_from_stream_field(request, field, context=None):
    """
    Get speech text from a StreamField.

    This methods iterates over the stream field blocks which have the method
    get_speech_text implemented. It concats these values into a compatible
    multiline string value.
    """
    values = []
    for child in field:
        if hasattr(child.block, 'get_speech_text'):
            values.append(child.block.get_speech_text(child.value))
    text = '<break strength=\"x-strong\"/>'.join(values)
    return "<speak>%s</speak>" % text
