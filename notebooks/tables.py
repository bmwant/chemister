import click
from terminaltables.other_tables import SingleTable, PorcelainTable


class Table(object):
    def __init__(self, *, header=None, data=None, porcelain=False):
        self.header = header
        self.data = data
        self.porcelain = porcelain

    def print(self):
        data = []
        if self.header is not None:
            data.append(self.header)
        if self.data is not None:
            data.extend(self.data)

        tbl = SingleTable(data)
        if self.porcelain:
            tbl = PorcelainTable(data)

        click.echo(tbl.table)
