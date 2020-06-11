class QueryField(object):
    def __init__(self, field, values):
        self.field = field
        self.values = values


class QueryParams(object):
    def __init__(self, fields=None, include=None, filters=None, counts=None, sort_on=None):
        if sort_on is None:
            sort_on = []
        if counts is None:
            counts = []
        if filters is None:
            filters = []
        if include is None:
            include = []
        if fields is None:
            fields = []
        self.fields = fields
        self.include = include
        self.filters = filters
        self.counts = counts
        self.sort_on = sort_on

    def to_params(self):
        query_params = {}
        if self.fields:
            for f in self.fields:
                query_params["fields[" + f.field + "]"] = ",".join(f.values)
        if self.include:
            query_params["include"] = ",".join(self.include)
        if self.filters:
            for f in self.filters:
                query_params["filter[" + f.field + "]"] = ",".join(f.values)
        if self.counts:
            count_fields = [f + "Count" for f in self.counts]
            if "include" not in query_params:
                query_params["include"] = query_params["include"] + "," + ",".join(count_fields)
            else:
                query_params["include"] = ",".join(count_fields)
        if self.sort_on:
            query_params["sort"] = ",".join(self.sort_on)

        return query_params

    @staticmethod
    def to_query_args(params):
        if params is None:
            return {}
        if type(params) is dict:
            return params
        return params.to_params()
