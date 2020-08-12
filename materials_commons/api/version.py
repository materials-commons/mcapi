import pkg_resources


def version():
    return pkg_resources.get_distribution("materials_commons-api").version
