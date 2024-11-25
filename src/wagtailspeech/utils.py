import hashlib
import logging
from contextlib import closing

import boto3
from django.conf import settings
from django.core.files.temp import NamedTemporaryFile, gettempdir

logger = logging.getLogger(__name__)

ENGINE = getattr(settings, "WAGTAIL_SPEECH_ENGINE", "standard")
LANGUAGE_CODE = getattr(settings, "WAGTAIL_SPEECH_LANGUAGE_CODE", "en-EN")
OUTPUT_FORMAT = getattr(settings, "WAGTAIL_SPEECH_OUTPUT_FORMAT", "mp3")
SAMPLE_RATE = getattr(settings, "WAGTAIL_SPEECH_SAMPLE_RATE", "8000")
VOICE_ID = getattr(settings, "WAGTAIL_SPEECH_VOICE_ID", "Joey")


def get_hash_from_tts_context(value):
    hash = hashlib.md5(value.encode()).hexdigest()
    return hash


def synthesize_speech(page, text):
    """
    Synthesize speech to an audio stream.
    """
    logger.info("Synthesize speech for %s" % page)
    text_type = "ssml" if text.startswith("<speak>") else "text"
    client = boto3.client("polly")

    res = client.synthesize_speech(
        Engine=ENGINE,
        LanguageCode=LANGUAGE_CODE,
        OutputFormat=OUTPUT_FORMAT,
        SampleRate=SAMPLE_RATE,
        Text=text,
        TextType=text_type,
        VoiceId=VOICE_ID,
    )
    if "AudioStream" in res:
        with closing(res["AudioStream"]) as stream:
            try:
                temp_dir = gettempdir()
                temp_file = NamedTemporaryFile(dir=temp_dir)
                temp_file.write(stream.read())
            except IOError as error:
                logger.error("An error occured: %s" % error)
        return temp_file
    else:
        logger.error(
            "No audio stream found in synthesize_speech response %s" % str(res)
        )


def get_tts_context_from_stream_field(request, field, context=None):
    """
    Get speech text from a StreamField.

    This methods iterates over the stream field blocks which have the method
    get_tts_context implemented. It concats these values into a compatible
    multiline string value.
    """
    values = []
    for child in field:
        if hasattr(child.block, "get_tts_context"):
            values.append(child.block.get_tts_context(child.value))
    text = '<break strength="x-strong"/>'.join(values)
    return "<speak>%s</speak>" % text
