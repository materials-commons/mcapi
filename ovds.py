#!/usr/bin/env python3
import copy
import os
import posixpath
import sys
import time
from urllib.parse import urlparse

import OpenVisus as ov
import numpy as np
import yaml
from OpenVisus.pyquery import PyQuery
from matplotlib import pyplot as plt
from slugify import slugify
import shutil

# import requests
# from xml.etree import ElementTree
import materials_commons.api as mcapi

PREVIEW_MAX_PIXELS = 1024 * 768


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
    ds = slugify(ds_name)
    if len(ds) > 80:
        return ds[0:80]
    return ds


def normalize_image(data):
    assert (len(data.shape) == 2)
    data = data.astype(np.float32)
    m, M = np.min(data), np.max(data)
    return (data - m) / (M - m)


def create_ds_image(s3_url):
    print("...LoadDataset()")
    db = ov.LoadDataset(s3_url)

    access = db.createAccessForBlockQuery()
    box = db.getLogicBox()
    pdim = db.getPointDim()
    dimension_tag = f'{pdim}d'
    center = [int(0.5 * (box[0][axis] + box[1][axis])) for axis in range(pdim)]
    timestep = db.getTime()
    print("...Looping through fields")
    for field in db.getFields():
        query_boxes = []

        # in 2D a single query for the whole bounding box is enough
        if pdim == 2:
            query_boxes = [(2, box)]

        # in 3D I may want to create 3 queries, one for each direction
        elif pdim == 3:
            for axis in range(pdim):
                p1, p2 = copy.deepcopy(box)
                offset = center[axis]
                p1[axis] = offset + 0
                p2[axis] = offset + 1
                query_boxes.append([axis, [p1, p2]])
        else:
            continue  # not support (ie, 4d,5d datasets)

        try:
            print(".....Looping over query_boxes")
            for axis, query_box in query_boxes:
                print(".......Looping over PyQuery.read()")
                for data_box, data in PyQuery.read(db, access=access, timestep=timestep, field=field, logic_box=query_box,
                                                   num_refinements=1, max_pixels=PREVIEW_MAX_PIXELS):
                    # note PyQuery is already returning a 2d image  (height,width,[channel]*)
                    assert (len(data.shape) == 2 or len(data.shape) == 3)

                    # change filename as needed
                    filename = 'ds-overview.png'
                    print("Doing query", axis, "query_box", query_box, "filename", filename, "dtype", data.dtype, "shape",
                          data.shape)

                    # fig = plt.figure()

                    # special case: it's a multichannel image with only one channel: convert to single-channel
                    if len(data.shape) == 3 and data.shape[2] == 1:
                        data = data[:, :, 0]

                    # single channel image, I can apply a colormap
                    if len(data.shape) == 2:
                        data = normalize_image(data) if data.dtype != np.uint8 else data
                        plt.imshow(data, cmap='viridis')
                        plt.colorbar()

                        # multiple channel image
                    elif len(data.shape) == 3:
                        # I support uint8 or float32 imagres
                        if data.dtype != np.uint8:
                            for C in range(data.shape[2]):
                                data[:, :, C] = normalize_image(data[:, :, C])

                        # not sure if this works, in theory I can have 2,3,4,.... channels
                        plt.imshow(data)
                    else:
                        raise Exception("not supported")

                    # change as needed
                    plt.savefig(filename)
                    plt.close()
        except:
            return None
    return dimension_tag


def get_openvisus_community(c):
    communities = c.get_all_public_communities()
    for community in communities:
        if community.name == "OpenVisus":
            return community
    return None


if __name__ == "__main__":
    # c = mcapi.Client(os.getenv("MCAPI_KEY"), base_url="http://localhost:8000/api")
    c = mcapi.Client(os.getenv("MCAPI_KEY"))
    # proj = c.get_project(77)
    proj = c.get_project(772)
    # c.set_debug_on()
    ov_cache_dir = ov.GetVisusCache()

    openvisus_community = get_openvisus_community(c)
    if openvisus_community is None:
        print("No 'OpenVisus' community found. Please create one before running this")
        sys.exit(1)

    with open('/home/gtarcea/Dropbox/transfers/ds/datasets.yaml') as f:
        try:
            ds = yaml.safe_load(f)
            i = 0
            for ds_entry in ds:
                # if i == 20:
                #     # time.sleep(5)
                #     i = 0
                # if i == 5:
                #     break

                remote = ds_entry["remote"]
                if remote is None:
                    continue

                url = urlparse(remote)
                key = remote[len("s3://"):]
                profile = "sealstorage"
                s3_url = f"https://maritime.sealstorage.io/api/v0/s3/{key}"
                if s3_url == "https://maritime.sealstorage.io/api/v0/s3/utah/openvisus-commons/1mb/kflame/kflame-2ndcopy/visus.idx":
                    continue

                if s3_url == "https://maritime.sealstorage.io/api/v0/s3/utah/openvisus-commons/1mb/kflame/visus.idx":
                    continue

                print(" ")
                print(f"s3_url = {s3_url}")

                with open("ov-template.ipynb", "r") as t:
                    data = t.read()
                    data = data.replace("{ds-url-here}", s3_url)
                    with open("dataset.ipynb", "w") as out:
                        out.write(data)

                ds_name = create_ds_name_from_url(url)
                s3_url_for_ov = f"{s3_url}?profile={profile}"
                dimension_tag = create_ds_image(s3_url_for_ov)
                if dimension_tag is None:
                    continue
                # db = ov.LoadDataset(s3_url)
                # data = db.read()
                # Remove idx file

                # plt.imsave(f"{ds_name}.png", data)
                print(f"Creating directory '{ds_name}'")
                print(f"project.root_dir.id = {proj.root_dir.id}")
                ds_dir = c.create_directory(proj.id, ds_name, proj.root_dir.id)
                overview_file = c.upload_file(proj.id, ds_dir.id, "./ds-overview.png")
                # print(f"Uploaded image file {overview_file.id}")
                jf = c.upload_file(proj.id, ds_dir.id, "./dataset.ipynb")
                # print(f"Uploaded jupyter file {jf.id}")
                description = f"OpenVisus Dataset\n\nThese datasets were imported as a part of CEDMAVs work.\n"
                description += "If you would like to claim this dataset please send an email "
                description += "to info@nationalsciencedatafabric.org.\n\n"
                for key, value in ds_entry.items():
                    if value is not dict:
                        description += f"{key}: {value}\n"
                    else:
                        description += "{key}:\n"
                        for k, v in value.items():
                            description += f" {k}: {v}\n"
                print(f"Creating dataset {ds_name}")
                tags = [{"value": "OpenVisus-Commons-Import"}, {"value": dimension_tag}, {"value": "OpenVisus"}]
                ds_request = mcapi.CreateDatasetRequest(description=description,
                                                        summary=f"OpenVisus {dimension_tag} dataset",
                                                        license="Open Database License (ODC-ODbL)",
                                                        tags=tags,
                                                        file1_id=overview_file.id)
                created_ds = c.create_dataset(proj.id, ds_name, ds_request)
                file_selection = {
                    "include_files": [f"/{ds_name}/ds-overview.png", f"/{ds_name}/dataset.ipynb"],
                    "exclude_files": [],
                    "include_dirs": [],
                    "exclude_dirs": []
                }
                c.change_dataset_file_selection(proj.id, created_ds.id, file_selection)
                c.publish_dataset(proj.id, created_ds.id)
                c.add_dataset_to_community(created_ds.id, openvisus_community.id)
                os.remove("ds-overview.png")
                # shutil.rmtree(ov_cache_dir, ignore_errors=True)
                i = i+1
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
