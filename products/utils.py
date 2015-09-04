class FileResponseBuilder(object):

    def __init__(self, content=None, content_type=None,
                 filename=None, response_class=None):

        self._content = content
        self._content_type = content_type
        self._filename = filename
        self._response_class = response_class

    @property
    def _content_disposition(self):
        return 'attachment; filename="{}"'.format(self._filename)

    @property
    def _content_length(self):
        return len(self._content)

    def build(self):
        response = self._response_class(
            content=self._content,
            content_type=self._content_type
        )

        response['Content-Disposition'] = self._content_disposition
        response['Content-Length'] = self._content_length

        return response

