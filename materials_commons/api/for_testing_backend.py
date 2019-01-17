from . import api
from .make_objects import make_object

# NOTE: these methods are not stable, no code should be written that depends on them
# They are used for testing only.

# ---
#    testing template backend
# ---
def _create_new_template(template_data, apikey=None):
    results = api._create_new_template(template_data, apikey=apikey)
    template = make_object(results)
    return template


def _update_template(template_id, template_data, apikey=None):
    results = api._update_template(template_id, template_data, apikey=apikey)
    template = make_object(results)
    return template


# ---
#   testing user profile backend
# ---
def _store_in_user_profile(user_id, name, value, apikey=None):
    results = api._store_in_user_profile(user_id, name, value, apikey=apikey)
    value = results['val']
    if not value:
        return None
    return value


def _get_from_user_profile(user_id, name, apikey=None):
    results = api._get_from_user_profile(user_id, name, apikey=apikey)
    value = results['val']
    if not value:
        return None
    return value


def _clear_from_user_profile(user_id, name, apikey=None):
    results = api._clear_from_user_profile(user_id, name, apikey=apikey)
    value = results['val']
    if not value:
        return None
    return value
