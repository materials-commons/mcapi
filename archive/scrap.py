import requests
import sys

header_api = "http://mctest.localhost/api"
header_v2_api = "http://mctest.localhost/api/v2"

default_params = {
    "apikey" : "your api key here"
}

def get(restpath, params = default_params):
    print "get", restpath
    sys.stdout.flush()
    r = requests.get(restpath, params=params, verify=False)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def post(restpath, data, params = default_params):
    print "post", restpath, data
    sys.stdout.flush()
    r = requests.post(restpath, params=params, verify=False, json=data)
    print r.url
    sys.stdout.flush()
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()


def put(restpath, data, params = default_params):
    print "put", restpath, data
    sys.stdout.flush()
    r = requests.put(restpath, params=params, verify=False, json=data)
    if r.status_code == requests.codes.ok:
        return r.json()
    r.raise_for_status()

def create_project(name,description):
    data = {
        "name" : name,
        "description" : description
    }
    return post(header_api + "/projects",data)

def create_experiment(project_id, name, description, goal="", aim="", tasks=[]):
    data = {
        "name" : name,
        "description" : description,
        "goal" : "", # normally an array of goals [str]
        "aim" : "", # mormally an array of aims [str]
        "status": "active",
        "tasks": []
        "note": "<h2>Experiment Notes</h2>↵"
    }
    api_url = "/projects/" + project_id + "/experiments"
    return post(header_v2_api + api_url, data)

def create_process_from_template(project_id, experiment_id,template_id):
    data = {
        "id" : template_id
    }
    api_url = "/projects/" + project_id + \
        "/experiments/" + experiment_id + \
        "/processes/templates/" + template_id
    return post(header_v2_api + api_url, data)

def create_samples(project_id, process_id, sample_names):
    sample_names_data = [{"name":name} for name in sample_names]
    print "sample_name_data = ", sample_names_data
    sys.stdout.flush()
    data = {
        "process_id" : process_id,
        "samples" : sample_names_data
    }
    api_url = "/projects/" + project_id + "/samples"
    return post(header_v2_api + api_url, data)

def add_samples_to_process(project_id,experiment_id,process_id,sample_ids):
    print "sample_ids",sample_ids
    sys.stdout.flush()
    data = {
        "process_id": process_id,
        "samples": sample_ids
    }
    api_url = "/projects/" + project_id + \
        "/experiments/" + experiment_id + "/samples"
    return post(header_v2_api + api_url, data)

# # # # DEMO SCRIPT # # # #

### login

# create or select a project (*)
# http://mctest.localhost/api/projects?apikey=949045af40e942b69f5b32d15b0fb8e5
# POST with data {name: "name", description: "description"}
ids = create_project("new test","a test project generated from the api")
project_id = ids['project_id']
datadir_id = ids['datadir_id']
print "project_id = ", project_id
sys.stdout.flush()

# create or select an experiment within the project
# http://mctest.localhost/api/v2/projects/80f7991c-df55-4eee-b2c0-e455e26bd34a/experiments?apikey=949045af40e942b69f5b32d15b0fb8e5
# POST with data {name: "exp 1", goal: "", description: "description", aim: "", status: "active", tasks: []}
experiment =  create_experiment(project_id,"Experiment 1","a test experiment generated from api")
experiment_id = experiment["id"]
print "experiment_id", experiment_id
sys.stdout.flush()

### add files to the project (*)
# add a sample to the experiment with a create sample process (*)
# http://mctest.localhost/api/v2/projects/80f7991c-df55-4eee-b2c0-e455e26bd34a/experiments/4e170b90-069f-4205-a4bb-dc02d3f00654/processes/templates/global_Create%20Samples?apikey=949045af40e942b69f5b32d15b0fb8e5
# POST with data {id: "global_Create Samples"}
# --> returns process
# http://mctest.localhost/api/v2/projects/80f7991c-df55-4eee-b2c0-e455e26bd34a/samples?apikey=949045af40e942b69f5b32d15b0fb8e5
# POST with data {process_id: "d12be2fb-cb04-4948-9031-3817c344e956", samples: [{name: "Sample Name"}]}
# --> returns samples
# http://mctest.localhost/api/v2/projects/80f7991c-df55-4eee-b2c0-e455e26bd34a/experiments/a831c0b1-6185-4a63-a6c4-89caaec83a57/samples?apikey=949045af40e942b69f5b32d15b0fb8e5
# PUT with data {process_id: "d12be2fb-cb04-4948-9031-3817c344e956", samples: [{id: "d9be4d95-27db-4024-9523-95d8fd12473b", name: "Sample"}]
### need to expand steps for creating process properties !!!
template_id = "global_Create Samples"
process = create_process_from_template(project_id, experiment_id,template_id)
process_id = process["id"]
sample_names = ["Sample A"]
samples = create_samples(project_id,process_id,sample_names)
sample_ids = [sample["id"] for sample in samples["samples"] ]
ids_list = add_samples_to_process(project_id,experiment_id,process_id,sample_ids)
ids = ids_list[0]
experiment_id = ids['experiment_id']
sample_id = ids['sample_id']
print "experiment_id", experiment_id
print "sample_id", sample_id
sys.stdout.flush()

### associate previously added file(s) with the create sample process
### associate measurements with the sample
### fetch previously added file(s) from the experiment/project (*)
# fetch sample description(s) from the experiment/project
# fetch measurement(s) from the experiment/project
# perform a computation on those files, samples, measurements and record that as a computation process (*)
### add measures resulting from the computation to the sample/process
# add the new file from the computation to the project (*)
# create a Computation process and associate the create-sample version of the sample and some files with that computation
# add a created/transformed sample as output from the computational process
### logout
