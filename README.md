# Wagtail-speech

Turn Wagtail pages into lifelike speech using Amazon Polly.

[![Build Status](https://travis-ci.org/moorinteractive/wagtail-speech.svg?branch=master)](https://travis-ci.org/moorinteractive/wagtail-speech)
[![Coverage Status](https://coveralls.io/repos/github/moorinteractive/wagtail-speech/badge.svg?branch=master)](https://coveralls.io/github/moorinteractive/wagtail-speech?branch=master)

* Issues: [https://github.com/moorinteractive/wagtail-speech/issues](https://github.com/moorinteractive/wagtail-speech/issues)
* Testing: [https://travis-ci.org/moorinteractive/wagtail-speech](https://travis-ci.org/moorinteractive/wagtail-speech)
* Coverage: [https://coveralls.io/github/moorinteractive/wagtail-speech](https://coveralls.io/github/moorinteractive/wagtail-speech)

## Installation

Install the package

```
pip install wagtail-speech
```

Add `wagtailspeech` to your `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ...
    'wagtailspeech',
]
```

Now make and run your migrations

```
manage.py makemigrations
manage.py migrate
```

## Usage

Use the ``SynthesizeSpeechMixin`` on pages you want to be rendered as audio streams.
These pages triggers the ``synthesize_speech_from_page`` method when they are edited via the Wagtail admin interface.
You can find your saved audio stream on the ``page.audio_stream`` property (by default a low bitrate .mp3 file).

```python
from wagtail.wagtailcore.models import Page
from wagtailspeech.models import SynthesizeSpeechMixin

class HomePage(SynthesizeSpeechMixin, Page):
    def get_speech_text(self):
        return self.title
```

You are completely free how to provide the text to be renderend.
In most cases you probably also want to provide values from a ``StreamField``.
For this use case we provided a ``get_speech_text_from_stream_field`` method which calls ``get_speech_text`` (if present) on your blocks and concats the content of it with breaks between them.

```python
class ExampleBlock(blocks.StructBlock):
    text = blocks.TextBlock()
    button_label = blocks.CharBlock(max_length=255)
    button_link = blocks.TextBlock()

    class Meta:
        template = 'blocks/cta.html'

    def get_speech_text(self, value):
        return "%s<break strength=\"x-strong\"/>%s" % (
            force_text(value.get('text')),
            force_text(value.get('button_label')))

class ExamplePage(SynthesizeSpeechMixin, Page):
    content = StreamField([
        ('example', ExampleBlock()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('content'),
    ]

    def get_speech_text(self, request):
        from wagtailspeech.utils import get_speech_text_from_stream_field
        return get_speech_text_from_stream_field(request, self.main_content)
```

## Settings

Available settings:

```python
WAGTAIL_SPEECH_OUTPUT_FORMAT = 'mp3'
WAGTAIL_SPEECH_SAMPLE_RATE = '8000'
WAGTAIL_SPEECH_VOICE_ID = 'Joey'
```

For other values please read the [documentation](http://boto3.readthedocs.io/en/latest/reference/services/polly.html#synthesize_speech).

## Tips

For proper pronunciations of your text and have more control over breaks, etc. we strongly advice you to read more about the supported tags of the [Speech Synthesis Markup Language](http://docs.aws.amazon.com/polly/latest/dg/ssml.html) in Polly.

## Roadmap

* [ ] Solution for limitations (max. 1500 chars / 5 min audio cut-off.)
* [ ] Support for choosing text/ssml
* [ ] Add real-time streaming support
