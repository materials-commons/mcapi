import os
import sys

from materials_commons.api.base import MCObject, PrettyPrint, print_authors
from materials_commons.api.mc_object_utility import make_object

class Dataset(MCObject):
    def __init__(self, data={}):

        data['name'] = data.get('title', None)

        # list all attributes w/defaults:

        # ** base components **
        #   ['id', 'name', 'description', 'birthtime', 'mtime', 'otype', 'owner']
        super(Dataset, self).__init__(data)

        # ** core components **
        for attrname in ['include_dirs', 'exclude_dirs', 'include_files', 'exclude_files']:
            if 'file_selection' in data:
                setattr(self, attrname, data['file_selection'].get(attrname, []))
            else:
                setattr(self, attrname, [])

        self.samples = []
        if 'samples' in data:
            self.samples = [make_object(s) for s in data['samples']]
        self.processes = []
        if 'processes' in data:
            self.processes = [make_object(s) for s in data['processes']]


        # ** public & private attributes **

        # time attributes
        self.dataset_time_attr = ['embargo_date', 'published_date']
        for attrname in self.dataset_time_attr:
            setattr(self, attrname, data.get(attrname, None))

        # boolean attributes
        self.dataset_bool_attr = ['published', 'published_to_globus']
        for attrname in self.dataset_bool_attr:
            setattr(self, attrname, data.get(attrname, None))

        # str attributes
        self.dataset_str_attr = ['doi', 'title', 'funding', 'institution', 'globus_url']
        for attrname in self.dataset_str_attr:
            setattr(self, attrname, data.get(attrname, None))

        # license - object
        self.license_attr = ['link', 'name']
        self.license_link = None
        self.license_name = None
        if 'license' in data:
            self.license_link = data['license'].get('link', None)
            self.license_name = data['license'].get('name', None)

        # dataset authors - list of objects
        self.authors_attr = ['lastname', 'firstname', 'affiliation']
        self.authors = data.get('authors', {})

        # papers - list of objects
        self.papers_attr = ['title', 'authors', 'doi', 'link', 'abstract']
        self.papers = data.get('papers', {})

        # keywords - list of str
        self.keywords = data.get('keywords', [])


        # ** private - only attributes **

        # status attr - object
        self.status_attr = ['files_count', 'samples_count', 'processes_count', 'can_be_published']
        for attrname in self.status_attr:
            if 'status' in data:
                setattr(self, attrname, data['status'].get(attrname, None))
            else:
                setattr(self, attrname, None)

        # zip attr - object
        self.zip_attr = ['size', 'filename']
        self.zip_size = None
        self.zip_filename = None
        if 'zip' in data:
            self.zip_size = data['zip'].get('size', None)
            self.zip_filename = data['zip'].get('filename', None)

        # stats attr - object
        self.stats_attr = ['comment_count', 'interested_users', 'unique_view_count']
        for attrname in self.stats_attr:
            if 'status' in data:
                setattr(self, attrname, data['status'].get(attrname, None))
            else:
                setattr(self, attrname, None)

        self.stats = data.get('stats', {})

        # boolean attributes
        self.published_to_globus = data.get('published_to_globus', None)


    def get_all_samples(self):
        return self.samples

    def get_all_samples(self):
        return self.processes

    def _contains_dir(self, path):
        if path in self.include_dirs:
            return True
        elif path in self.exclude_dirs:
            return False
        else:
            parent = os.path.dirname(path)
            if parent:
                return self._contains_dir(parent)
            else:
                return False

    def contains(self, path):
        if path in self.include_files:
            return True
        elif path in self.excludes_files:
            return False
        else:
            return self._contains_dir(path)

    def pretty_print_summary(self, shift=0, indent=2, out=sys.stdout, pp=None):

        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        # standard attr
        pp.write("name: " + pp.str_or_None(self.name))
        pp.write("id: " + pp.str(self.id))
        pp.write("owner: " + pp.str_or_None(self.owner))

        # dataset-specific attr
        pp.write("doi: " + pp.str_or_None(self.doi))
        print_authors(self.authors, pp=pp, singleline=True)
        pp.write("institution: " + pp.str_or_None(self.institution))
        pp.write("funding: " + pp.str_or_None(self.funding))

        # status attr
        # pp.write("files_count: " + str(self.files_count))
        # pp.write("samples_count: " + str(self.samples_count))
        # pp.write("processes_count: " + str(self.processes_count))

    def pretty_print_description(self, shift=0, indent=2, out=sys.stdout, pp=None):
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)
        pp.write("description: " + pp.str_or_None(self.description))

    def pretty_print_file_selection(self, shift=0, indent=2, out=sys.stdout, pp=None):

        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        if not self.include_files:
            pp.write("include_files: None")
        else:
            pp.write("include_files:")
            pp.n_indent += 1
            for file in self.include_files:
                pp.write(file)
            pp.n_indent -= 1

        if not self.exclude_files:
            pp.write("exclude_files: None")
        else:
            pp.write("exclude_files:")
            pp.n_indent += 1
            for file in self.exclude_files:
                pp.write(file)
            pp.n_indent -= 1

        if not self.include_dirs:
            pp.write("include_dirs: None")
        else:
            pp.write("include_dirs:")
            pp.n_indent += 1
            for dir in self.include_dirs:
                pp.write(dir)
            pp.n_indent -= 1

        if not self.exclude_dirs:
            pp.write("exclude_dir: None")
        else:
            pp.write("exclude_dirs:")
            pp.n_indent += 1
            for dir in self.exclude_dirs:
                pp.write(dir)
            pp.n_indent -= 1

    def pretty_print_samples(self, shift=0, indent=2, out=sys.stdout, pp=None):

        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        pp.write("samples:")
        pp.n_indent += 1
        for samp in self.samples:
            pp.write(samp.name + ', ' + samp.id)
        pp.n_indent -= 1

    def pretty_print_processes(self, shift=0, indent=2, out=sys.stdout, pp=None):

        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)

        pp.write("processes:")
        pp.n_indent += 1
        for proc in self.processes:
            pp.write(proc.name + ', ' + proc.id)
        pp.n_indent -= 1

    def pretty_print(self, shift=0, indent=2, out=sys.stdout, pp=None):
        """
        Prints a nice layout of the object and all of it's values.

        :param shift: the offset from the start of the line, in increments of indent
        :param indent: the indent used for layout, in characters
        :param out: the stream to which the object in printed
        :param pp: PrettyPrint object to use. If None, constructed from other arguments.
        :return: None
        """
        if pp is None:
            pp = PrettyPrint(shift=shift, indent=indent, out=out)
        self.pretty_print_summary(pp=pp)
        self.pretty_print_description(pp=pp)
        # self.pretty_print_file_selection(pp=pp)

        # use `mc samp/proc --dataset <id>` instead
        # self.pretty_print_samples(pp=pp)
        # self.pretty_print_processes(pp=pp)
