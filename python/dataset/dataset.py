from DatasetAuthor import DatasetAuthor

class Dataset:


    def __init__(self, data=None):
        if not data:
            data = {}

        self.raw_data = data

        attr = ['authors', 'birthtime', 'description', 'doi', 'embargo_date', 'files',
                'funding', 'id', 'institution', 'keywords', 'license', 'mtime', 'other_datasets',
                'owner', 'papers', 'processes', 'published', 'published_date', 'publisher',
                'samples', 'tags', 'title', 'zip']
        for a in attr:
            setattr(self, a, data.get(a, None))

        self.author = [DatasetAuthor(data=data) for data in self.author]
