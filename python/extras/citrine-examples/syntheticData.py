import numpy as np
from os import path
from .utilities import check_citrination_key, get_citrination_key
from citrination_client import CitrinationClient
# from citrination_client import PifQuery

if not check_citrination_key():
    exit(1)


def create_clusters(num_points=1000, num_features=2):
    """
    Create synthetic data with num_points total points and num_features input dimensionality.
    The points are grouped into four Gaussian-distributed clusters.
    """
    num_clusters = 4
    xx = np.zeros((1, num_features))
    yy = np.zeros((1, 1))
    for i in range(num_clusters):
        x = np.random.randn(num_points/num_clusters, num_features)/6.0+i
        xx = np.vstack((xx, x))
        y = np.ones((num_points/num_clusters, 1))*i
        yy = np.vstack((yy, y))
    return xx, yy


def write_cluster_csv(filename, x, y):
    """
    Write the data to a csv file
    """
    data = np.hstack((x, y))
    num_features = x.shape[1]
    #  Let's define the header for the csv:
    str1 = ""
    for i in range(num_features):
        str1 += "x" + str(i) + ","
    str1 += "y"
    #  Then write the csv:
    np.savetxt(filename, data, delimiter=',', header=str1, comments="", fmt="%.5e")


try:
    # test_dataset = '153696'  # "Weymouth - Test dataset"
    test_dataset = '153654'  # "Weymouth-MC-Test"
    client = CitrinationClient(get_citrination_key(), 'https://citrination.com')
    # response = client.create_data_set("Weymouth - Test dataset 01",
    #           "A scrap dataset for testing - Terry E Weymouth - ")
    # response = client.create_data_set_version(test_dataset)
    # print response.status_code
    # print response.content
    # test_dataset_results = response.content

    # print 'attempting upload of cluster_data.csv'
    # filepath = path.abspath("./cluster_data.csv")
    filepath = '/Users/weymouth/working/MaterialsCommons/workspace/src/github.com/' + \
               'materials-commons/mcapi/python/citrine-examples/Al4-pif.json'
    type = "unknown"
    if path.isfile(filepath):
        type = "file"
    if path.isdir(filepath):
        type = "directory"
    print(filepath)
    print(("    is a: " + type))
    response = client.upload(test_dataset, filepath)
    print(response)

except Exception as e:
    print(("Exception: ", e))

# x, y = create_clusters(100, 4)
# write_cluster_csv("cluster_data.csv", x, y)

# Lets make a plot to see how our data looks:
# plt.scatter(x[:, 0], x[:, 1], c=y[:,0])
# plt.xlabel("x1")
# plt.ylabel("x2")
# plt.title("Clustered synthetic data set")
# plt.colorbar()
# plt.show()
