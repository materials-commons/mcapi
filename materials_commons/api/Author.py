import sys
from materials_commons.api.base import PrettyPrint

class Author(object):
    def __init__(self, firstname=None, lastname=None, affiliation=None):
        self.firstname = firstname
        self.lastname = lastname
        self.affiliation = affiliation

    def __eq__(self, other):
        return vars(self) == vars(other)

    def _tuple(self):
        return (self.lastname, self.firstname, self.affiliation)

    def __lt__(self, other):
        return self._tuple() < other._tuple()

    def pretty_print(self, shift=0, indent=2, out=sys.stdout, pp=None, singleline=True):
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        if singleline:
            pp.write('{0} {1}, {2}'.format(self.firstname, self.lastname, self.affiliation))
        else:
            pp.write('firstname: ' + author.get('firstname', ''))
            pp.write('lastname: ' + author.get('lastname', ''))
            pp.write('affiliation: ' + author.get('affiliation', ''))

    def to_dict(self):
        return {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'affiliation': self.affiliation
        }

    def cli_input(self):
        """Prompt for and accept CLI input to set attributes"""

        self.firstname = input_or_None('Input author firstname: ')
        self.lastname = input_or_None('Input author lastname: ')
        self.affiliation = input_or_None('Input author affiliation: ')


def print_authors(authors, shift=0, indent=2, out=sys.stdout, pp=None, singleline=True):

    if pp is None:
        pp = PrettyPrint(shift=shift, indent=indent, out=out)

    if not authors:
        pp.write("authors: None")
        return

    pp.write("authors:")
    pp.n_indent += 1
    for index, author in enumerate(authors):
        if not singleline and index != 0:
            pp.write('')
        author.pretty_print(shift=shift, indent=indent, out=out, pp=pp, singleline=singleline)
    pp.n_indent -= 1
