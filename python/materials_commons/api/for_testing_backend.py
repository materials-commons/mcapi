from . import api
from .make_objects import make_object


# ---
#    testing template backend
# ---
def _create_new_template(template_data):
    print("Create new template")
    results = api._create_new_template(template_data)
    template = make_object(results)
    return template


def _update_template(template_id, template_data):
    print("Updating template")
    results = api._update_template(template_id, template_data)
    template = make_object(results)
    return template


# ---
#   testing user profile backend
# ---
def _store_in_user_profile(user_id, name, value):
    results = api._store_in_user_profile(user_id, name, value)
    value = results['val']
    if not value:
        return None
    return value


def _get_from_user_profile(user_id, name):
    results = api._get_from_user_profile(user_id, name)
    value = results['val']
    if not value:
        return None
    return value


def _clear_from_user_profile(user_id, name):
    results = api._clear_from_user_profile(user_id, name)
    value = results['val']
    if not value:
        return None
    return value
