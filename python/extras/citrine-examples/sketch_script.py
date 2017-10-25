from .utilities import check_api_keys, check_data_samples_dir
from .utilities import get_data_samples_dir, print_mc_file_or_dir
from .utilities import get_citrination_key, setup_data, create_test_project
from .utilities import get_temp_dir, path_to_temp_file
from citrination_client import CitrinationClient
# from citrination_client import PifQuery

if not check_api_keys():
    exit(1)

if not check_data_samples_dir():
    exit(1)

test_dataset = '153654'  # "Weymouth-MC-Test"
test_file_or_dir = 'Al4-pif.json'

try:
    print("")
    print("Sample data file or directory ... ")
    type, file_or_directory = setup_data(test_file_or_dir)
    print(file_or_directory)
    print("    is a: " + type)

    print("")
    print("Copied to Materials Commons project via Python API ...")
    project = create_test_project()
    print("Materials Commons project = " + project.name)

    project.local_path = get_data_samples_dir()
    if type == "file":
        mc_file_or_directory = project.add_file_by_local_path(file_or_directory)
    else:
        mc_file_or_directory = project.add_directory_tree_by_local_path(file_or_directory)
    print("Loaded into Materials Commons")
    print_mc_file_or_dir(mc_file_or_directory)

    print("")
    print("Fetched from Materials Commons project to temp directory ... ")
    mc_top_dir = project.get_top_directory()
    contents = mc_top_dir.get_children()
    found = None
    for file_or_dir in contents:
        if file_or_dir.name == test_file_or_dir:
            found = file_or_dir
    if not found:
        print(("Can not find file or directory, " + test_file_or_dir + ", in Materials Commons"))
    else:
        print(("In Materials Commons, found: " + found.name))
    temp_dir = get_temp_dir()
    filepath = None
    if type == "file":
        temp_file_path = path_to_temp_file(temp_dir, test_file_or_dir)
        project.local_path = temp_dir
        filepath = found.download_file_content(temp_file_path)
    else:
        print("Sketch of download of dir content no yet implemented.")
        exit(2)
    if filepath:
        print("Downloaded Materials commons test data to: ")
        print(filepath)

    print("")
    print("Uploaded to Citrination dataset via CitrinationClient ... ")
    client = CitrinationClient(get_citrination_key(), 'https://citrination.com')
    response = client.upload(test_dataset, filepath)
    print(response)

except Exception as e:
    print(e)
