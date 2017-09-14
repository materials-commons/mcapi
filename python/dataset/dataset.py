class Dataset():

    def __init__(self, data=None):
        if not data:
            data = {}

        self.raw_data = data

