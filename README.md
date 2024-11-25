# Wagtail-speech

Turn Wagtail pages into lifelike speech using Amazon Polly.

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

We assume you already have setup credentials for [boto3](http://boto3.readthedocs.io/en/latest/guide/configuration.html).

## Usage

Use the ``TextToSpeechMixin`` on pages you want to be rendered as audio streams.

```python
from wagtail.models import Page
from wagtailspeech.models import TextToSpeechMixin

class HomePage(TextToSpeechMixin, Page):
    def get_tts_context(self, request):
        return self.title
```

You are completely free how to provide the text to be renderend.
In most cases you probably also want to provide values from a ``StreamField``.
For this use case we provided a ``get_tts_context_from_stream_field`` method which calls ``get_tts_context`` (if present) on your blocks and concats the content of it with breaks between them.

```python
class ExampleBlock(blocks.StructBlock):
    text = blocks.TextBlock()
    button_label = blocks.CharBlock(max_length=255)
    button_link = blocks.TextBlock()

    class Meta:
        template = 'blocks/cta.html'

    def get_tts_context(self, value):
        return "%s<break strength=\"x-strong\"/>%s" % (
            force_text(value.get('text')),
            force_text(value.get('button_label')))

class ExamplePage(TextToSpeechMixin, Page):
    content = StreamField([
        ('example', ExampleBlock()),
    ])

    content_panels = Page.content_panels + [
        StreamFieldPanel('content'),
    ]

    def get_tts_context(self, request):
        from wagtailspeech.utils import get_tts_context_from_stream_field
        return get_tts_context_from_stream_field(request, self.main_content)
```

## Settings

Available settings:

```python
WAGTAIL_SPEECH_ENGINE = 'standard'
WAGTAIL_SPEECH_LANGUAGE_CODE = 'en-EN'
WAGTAIL_SPEECH_OUTPUT_FORMAT = 'mp3'
WAGTAIL_SPEECH_SAMPLE_RATE = '8000'
WAGTAIL_SPEECH_VOICE_ID = 'Joey'
```

For other values please read the [documentation](http://boto3.readthedocs.io/en/latest/reference/services/polly.html#synthesize_speech).

## Tips

For proper pronunciations of your text and have more control over breaks, etc. we strongly advice you to read more about the supported tags of the [Speech Synthesis Markup Language](http://docs.aws.amazon.com/polly/latest/dg/ssml.html) in Polly.
