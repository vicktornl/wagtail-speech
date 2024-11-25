from wagtail import hooks


@hooks.register("after_edit_page")
def synthesize_speech(request, page):
    pass
