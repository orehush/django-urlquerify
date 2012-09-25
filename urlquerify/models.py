

class QueryState(object):
    def __init__(self, request, initial=None):
        self._state = {}
        self._state.update(initial or {})
        self._state.update(dict(request.GET.items()))

    def update(self, **kwargs):
        self._state.update(kwargs)
        return self

    def remove(self, *args):
        for key in args:
            if key in self._state:
                del self._state[key]
        return self

    def only(self, *args):
        for key in args:
            if key not in args and key in self._state:
                del self._state[key]
        return self

    def serialize(self):
        params_str = '?'

        for key in self._state:
            params_str += key

            if self._state[key] != '':
                params_str += '=' + unicode(self._state[key])
            params_str += '&'

        return params_str[:-1]
