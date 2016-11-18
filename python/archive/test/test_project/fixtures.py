import os, json
from os.path import join

projects_dir = "data"
tmp_dir = "tmp"

def read_test_cases(path):
  """
  Read 'path/test_cases.json'
  """
  return json.load(open(join(path,"test_cases.json"),'r'))