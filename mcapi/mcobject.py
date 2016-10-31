class MCObject(object):
    """
    Base class for Materials Commons objects.

    Attributes
    ----------
      id: str
        ID of the object

      name: str
        Name of the object

      description: str
        Description of the object

      birthtime: int
        Creation time of the object

      mtime: int
        Last modification time

    """

    def __init__(self, data=dict()):
        attr = ['id', 'name', 'description', 'birthtime', 'mtime', '_type', 'owner']
        for a in attr:
            setattr(self, a, data.get(a, None))
