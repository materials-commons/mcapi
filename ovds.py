#!/usr/bin/env python3

import os
import sys

# import requests
# from xml.etree import ElementTree
import materials_commons.api as mcapi
import yaml
from urllib.parse import urlparse
import posixpath
import OpenVisus as ov
from matplotlib import pyplot as plt
from slugify import slugify


def create_ds_name_from_url(url):
    # Take off filename
    p = posixpath.dirname(url.path)

    # Now iterate over path peeling off each part of path
    # to create the dataset name. End when the basename
    # is equal to 1mb
    ds_name = ""
    while True:
        name = posixpath.basename(p)
        if name == "1mb":
            break

        if ds_name == "":
            ds_name = name
        else:
            ds_name += f"-{name}"
        p = posixpath.dirname(p)
    return slugify(ds_name)


if __name__ == "__main__":
    c = mcapi.Client(os.getenv("MCAPI_KEY"), base_url="http://localhost:8000/api")
    proj = c.get_project(77)
    c.set_debug_on()
    with open('/home/gtarcea/Dropbox/transfers/datasets.yaml') as f:
        try:
            ds = yaml.safe_load(f)
            i = 0
            for ds_entry in ds:
                if i == 1:
                    break

                remote = ds_entry["remote"]
                if remote is None:
                    continue

                with open("ov-template.ipynb", "r") as t:
                    data = t.read()
                    data = data.replace("{remote-here}", remote)
                    with open("dataset.ipynb", "w") as out:
                        out.write(data)
                url = urlparse(remote)
                key = remote[len("s3://"):]
                profile = "sealstorage"
                s3_url = f"https://maritime.sealstorage.io/api/v0/s3/{key}?profile={profile}"
                print(f"s3_url = {s3_url}")
                db = ov.LoadDataset(s3_url)
                data = db.read()
                # Remove idx file
                ds_name = create_ds_name_from_url(url)
                plt.imsave(f"{ds_name}.png", data)
                ds_dir = c.create_directory(77, ds_name, proj.root_dir.id)
                c.upload_file(77, ds_dir.id, f"./{ds_name}.png")
                c.upload_file(77, ds_dir.id, "./dataset.ipynb")
                description = f"OpenVisus Dataset\n"
                for key, value in ds_entry.items():
                    if key != "source" and key != "remote":
                        if value is not dict:
                            description += f"{key}: {value}\n"
                        else:
                            description += "{key}:\n"
                            for k, v in value.items():
                                description += f" {k}: {v}\n"
                print(f"Creating dataset {ds_name}")
                ds_request = mcapi.CreateDatasetRequest(description=description,
                                                        license="Open Database License (ODC-ODbL)")
                # tags=[{"value": "OpenVisus"}])
                created_ds = c.create_dataset(77, ds_name, ds_request)
                file_selection = {
                    "include_files": [f"/{ds_name}/{ds_name}.png", f"/{ds_name}/dataset.ipynb"],
                    "exclude_files": [],
                    "include_dirs": [],
                    "exclude_dirs": []
                }
                c.change_dataset_file_selection(77, created_ds.id, file_selection)
                os.remove(f"{ds_name}.png")
                i = 1
        except yaml.YAMLError as e:
            print(e)
            i = 1

    # c.set_debug_on()
    # r = requests.get("http://atlantis.sci.utah.edu/mod_visus?action=list")

    # tree = ElementTree.fromstring(r.content)
    # group = ""
    # for elem in tree.iter():
    #     if elem.tag == "group":
    #         group = elem.attrib["name"]
    #     elif elem.tag == "dataset":
    #         ds = elem.attrib["name"]
    #         print(f"Dataset {ds} in group {group}")
    #         mod_visus = requests.get("https://atlantis.sci.utah.edu/mod_visus?action=readdataset&dataset=" + ds)
    #         data = mod_visus.text.split('\n')[5]
    #         ds_request = mcapi.CreateDatasetRequest(description="OpenVisus Dataset\n" + "Group: " + group + "\n" + data,
    #                                                 license="Open Database License (ODC-ODbL)")
    #         # tags=[{"value": "OpenVisus"}])
    #         created_ds = c.create_dataset(77, ds, ds_request)

    # group = child.attrib["name"]
    # for ds in child:
    #     dsname = child.attrib["name"]
    #     print("Dataset " + dsname + " in group " + group)
