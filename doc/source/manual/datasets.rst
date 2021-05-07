.. manual/datasets.rst

Datasets
========

A dataset in Materials Commons is a way to gather files, activities, entities and their attributes together into a
bundle and eventually publish them. A published dataset is available publicly, and can be browsed. The files are
made available for download, packaged into zip file, and also available through Globus. A dataset can be annotated
with tags, authors, papers, a description and other data. A published dataset is also available in Google's Dataset
Search site. ::

    # Get a list of all datasets in a project
    datasets = c.get_all_dataset(project.id)

    # Create a new dataset in a project
    dataset = c.create_dataset(project.id, "dataset-name")

    # Create a new dataset in a project and add additional information to the dataset
    req = mcapi.CreateDatasetRequest(description="dataset description")
    dataset = c.create_dataset(project.id, "ds-name", req)

    # Have Materials Commons create a DOI and associate it with the dataset
    dataset = c.assign_doi_to_dataset(project.id, dataset.id)

    # Publish a dataset
    dataset = c.publish_dataset(project.id, dataset.id)

    # Unpublish a dataset
    dataset = c.unpublish_dataset(project.id, dataset.id)


Published Datasets
------------------
A published dataset is publicly available. The API allows you to interact with published datasets and download their
files. ::

    # Get all published datasets
    published_datasets = c.get_all_published_datasets()

    # Get file objects for published dataset
    files = c.get_published_dataset_files(published_datasets[0].id)

    # Download a single file from a published dataset to /tmp
    c.download_published_dataset_file(published_datasets[0].id, files[0].id, "/tmp/file.txt")

    # Download the published dataset's zipfile to /tmp
    c.download_published_dataset_zipfile(published_datasets[0].id, "/tmp/ds.zip")


Get Published Datasets for Author
---------------------------------

You can ask for all the published datasets by a particular author. This will do a search using the string you supplied. ::

    allison_datasets = c.get_published_datasets_for_author("allison")


Get Published Datasets That Have Tag
------------------------------------

You can get all the published datasets associated with a tag: ::

    mg_tagged_datasets = c.get_published_datasets_for_tag("mg")


Other Operations
----------------

Miscellaneous other operations: ::

    # Get all tags used in published datasets
    tags = c.list_tags_for_published_datasets()

    # Get all authors that have published on Materials Commons site
    authors = c.list_published_authors()

