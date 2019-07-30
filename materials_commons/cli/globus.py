import globus_sdk
import os

import materials_commons.api as mcapi
import materials_commons.cli.tree_functions as treefuncs

CLIENT_ID = '1e4aacbc-8c10-4812-a54a-8434d2030a41'


def transfer_rt():
    """Get the globus transfer refresh token, creating if necessary"""

    config = mcapi.Config()

    # return existing transfer_rt
    if config.globus.transfer_rt:
        return config.globus.transfer_rt

    # authenticate

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(refresh_tokens=True)

    authorize_url = client.oauth2_get_authorize_url()
    try:
        import webbrowser
        webbrowser.open(authorize_url)
    except:
        pass

    print('Please login. If a webpage does not open automatically, go here:\n\n{0}\n\n'.format(authorize_url))
    auth_code = input('Please enter the code you get after login here: ').strip()
    token_response = client.oauth2_exchange_code_for_tokens(auth_code)

    #globus_auth_data = token_response.by_resource_server['auth.globus.org']
    globus_transfer_data = token_response.by_resource_server['transfer.api.globus.org']
    transfer_rt = globus_transfer_data['refresh_token']

    # save the token
    config.globus.transfer_rt = transfer_rt
    config.save()

    # return the token
    return config.globus.transfer_rt


def make_transfer_client():

    client = globus_sdk.NativeAppAuthClient(CLIENT_ID)
    client.oauth2_start_flow(refresh_tokens=True)

    # authorizer = globus_sdk.RefreshTokenAuthorizer(
    #     transfer_rt, client, access_token=transfer_at, expires_at=expires_at_s)
    authorizer = globus_sdk.RefreshTokenAuthorizer(transfer_rt(), client)

    # and try using `tc` to make TransferClient calls. Everything should just
    # work -- for days and days, months and months, even years
    return globus_sdk.TransferClient(authorizer=authorizer)


def local_endpoint_id():
    """Get the local endpoint id"""
    local_endpoint = globus_sdk.LocalGlobusConnectPersonal()
    return local_endpoint.endpoint_id


def create_all_directories_on_path(req, path):
    """Create all directories on path at upload endpoint

    Arguments:
        req: GlobusUploadRequest
        path: str, Relative path inside project to a directory (excludes project directory)
    """
    tc = make_transfer_client()

    def finddir(contents, name):
        for entry in contents:
            if entry['name'] == name and entry['type'] == 'dir':
                return True
        return False

    found = True
    curr_relpath = ""
    curr_abspath = os.path.join(req.globus_endpoint_path, curr_relpath)
    for name in path.split(os.sep):

        if not len(name):
            continue

        if found:
            contents = tc.operation_ls(req.globus_endpoint_id, path=curr_abspath)
            found = finddir(contents, name)

        if found:
            print("found:", name, "in", curr_abspath)

        curr_relpath = os.path.join(curr_relpath, name)
        curr_abspath = os.path.join(req.globus_endpoint_path, curr_relpath)

        if not found:
            print("create:", curr_abspath)
            tc.operation_mkdir(req.globus_endpoint_id, curr_abspath)
    return


def globus_upload_v0(proj, paths, recursive=False, label=None):
    """

    Arguments:
        proj: Project
        paths: list of str, Materials Commons paths (include project directory)
        recursive: bool, If True, upload directories recursively
        label: str, Globus transfer label to make finding tasks simpler

    Returns:
        None or task_id: str, transfer task id. Returns nothing to transfer.
    """
    refpath = os.path.dirname(proj.local_path)
    paths = treefuncs.make_paths_for_upload(proj.local_path, paths)

    if not len(paths):
        return None

    req = proj.create_globus_upload_request()

    # https://globus-sdk-python.readthedocs.io/en/stable/clients/transfer/#globus_sdk.TransferData
    tc = make_transfer_client()
    tdata = globus_sdk.TransferData(tc, local_endpoint_id(), req.globus_endpoint_id, label=label)

    # add items
    for p in paths:

        local_abspath = os.path.join(refpath, p)
        relpath = os.path.relpath(local_abspath, proj.local_path)
        destpath = os.path.join(req.globus_endpoint_path, relpath)

        create_all_directories_on_path(req, os.path.dirname(relpath))

        tdata.add_item(local_abspath, destpath, recursive=(recursive and os.path.isdir(local_abspath)))

    # submit transfer request
    transfer_result = tc.submit_transfer(tdata)
    task_id = transfer_result["task_id"]

    # print task id
    print("task_id =", task_id)

    return task_id

def globus_download_v0(proj, paths, recursive=False, label=None, localtree=None, remotetree=None):
    """

    Arguments:
        proj: Project
        paths: list of str, Materials Commons paths (include project directory)
        recursive: bool, If True, download directories recursively
        label: str, Globus transfer label to make finding tasks simpler

    Returns:
        None or task_id: str, transfer task id. Returns nothing to transfer.
    """

    req = proj.create_globus_download_request()
    refpath = os.path.dirname(proj.local_path)

    files_data, dirs_data, child_data, non_existing = treefuncs.treecompare(proj, paths, checksum=True, localtree=localtree, remotetree=remotetree)

    # https://globus-sdk-python.readthedocs.io/en/stable/clients/transfer/#globus_sdk.TransferData
    tc = make_transfer_client()
    tdata = globus_sdk.TransferData(tc, req.globus_endpoint_id, local_endpoint_id(), label=label)

    # add items
    n_items = 0
    for p in paths:

        local_abspath = os.path.join(proj.local_path, p)
        relpath = os.path.relpath(p, proj.local_path)
        remotepath = os.path.join(req.globus_endpoint_path, relpath)
        printpath = os.path.relpath(local_abspath)
        if p in non_existing:
            print(printpath + ": No such file or directory")
            continue
        elif p in files_data:
            remote_type = files_data[p]['r_type']
        elif p in dirs_data:
            remote_type = dirs_data[p]['r_type']

        if remote_type == 'directory' and not recursive:
            print(printpath + ": is a directory")
            continue

        local_abspath = os.path.join(refpath, p)
        if os.path.exists(local_abspath):
            print(local_abspath + ": Already exists (will not overwrite)")
            continue

        local_dir = os.path.dirname(local_abspath)
        if not os.path.exists(local_dir):
            os.path.makedirs(local_dir)
        if not os.path.isdir(local_dir):
            print(local_dir + ": Not a directory")

        tdata.add_item(remotepath, local_abspath, recursive=(recursive and remote_type=='directory'))
        n_items += 1

    if not n_items:
        print("Nothing to transfer")
        return None

    # submit transfer request
    transfer_result = tc.submit_transfer(tdata)
    task_id = transfer_result["task_id"]

    # print task id
    print("task_id =", task_id)

    return task_id
