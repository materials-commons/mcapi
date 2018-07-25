# incorporate Path in a version 2/3 compatible way
try:
    # noinspection PyCompatibility
    from pathlib import Path
    Path().expanduser()
except (ImportError, AttributeError):
    # noinspection PyCompatibility
    from pathlib2 import Path
