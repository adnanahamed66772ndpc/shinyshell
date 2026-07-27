"""Pipe output class for chained method calls."""


class _PipeOutput:
    """Enables chained output: sh.pipe(data).table()"""

    def __init__(self, data, shell):
        self.data = data
        self._sh = shell

    def table(self, title=None, style="single"):
        self._sh.table(self.data, title=title, style=style)
        return self

    def json(self, title=None):
        self._sh.json(self.data, title=title)
        return self

    def metrics(self):
        if isinstance(self.data, dict):
            self._sh.metrics(self.data)
        return self

    def bar(self, title=None):
        if isinstance(self.data, dict):
            self._sh.bar(self.data, title=title)
        return self

    def columns(self, cols=2):
        if isinstance(self.data, list):
            self._sh.columns([str(x) for x in self.data], cols=cols)
        return self

    def csv(self):
        if isinstance(self.data, list) and len(self.data) > 0:
            self._sh.csv(self.data)
        return self

    def sql(self):
        if isinstance(self.data, list):
            self._sh.sql_table(self.data)
        return self
