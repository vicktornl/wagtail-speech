import hashlib
import logging
import os
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
    
    # Handle SSML content - extract inner text for chunking
    if text_type == "ssml":
        if text.startswith("<speak>") and text.endswith("</speak>"):
            inner_text = text[7:-8]  # Remove <speak> and </speak>
        else:
            inner_text = text
    else:
        inner_text = text
    
    rest = inner_text
    
    # Divide the text into blocks of approximately 2500 characters for SSML
    # or 2000 characters for plain text to stay well under the limits
    max_chunk_size = 2500 if text_type == "ssml" else 2000
    textBlocks = []
    
    while len(rest) > max_chunk_size:
        begin = 0
        end = rest.find(".", max_chunk_size)
        
        if end == -1:
            end = rest.find(" ", max_chunk_size)
        
        if end == -1:
            end = max_chunk_size
        
        textBlock = rest[begin:end]
        rest = rest[end:].lstrip()
        textBlocks.append(textBlock)
    
    if rest:
        textBlocks.append(rest)
    
    logger.info(f"Split text into {len(textBlocks)} blocks")
    
    client = boto3.client("polly")
    
    temp_dir = gettempdir()
    temp_file = NamedTemporaryFile(dir=temp_dir, delete=False)
    temp_file_path = temp_file.name
    temp_file.close()
    
    try:
        for i, textBlock in enumerate(textBlocks):
            if text_type == "ssml":
                block_text = f"<speak>{textBlock}</speak>"
            else:
                block_text = textBlock
            
            logger.info(f"Synthesizing block {i + 1}/{len(textBlocks)}")
            
            res = client.synthesize_speech(
                Engine=ENGINE,
                LanguageCode=LANGUAGE_CODE,
                OutputFormat=OUTPUT_FORMAT,
                SampleRate=SAMPLE_RATE,
                Text=block_text,
                TextType=text_type,
                VoiceId=VOICE_ID,
            )
            
            if "AudioStream" in res:
                with closing(res["AudioStream"]) as stream:
                    with open(temp_file_path, "ab") as file:
                        file.write(stream.read())
            else:
                logger.error(
                    f"No audio stream found in synthesize_speech response for block {i + 1}: {str(res)}"
                )
                os.unlink(temp_file_path)
                return None
        
        final_temp_file = NamedTemporaryFile(dir=temp_dir)
        with open(temp_file_path, "rb") as source:
            final_temp_file.write(source.read())
        final_temp_file.seek(0)
        
        os.unlink(temp_file_path)
        
        return final_temp_file
        
    except IOError as error:
        logger.error("An error occurred: %s" % error)
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        return None


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
