import pkg_resources


def version():
    return pkg_resources.resource_string('materials_commons', 'VERSION.txt').strip().decode("utf-8")