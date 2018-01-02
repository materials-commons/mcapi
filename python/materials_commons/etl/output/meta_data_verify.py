from materials_commons.api import get_project_by_id
from ..input import input_metadata

class MetadataVerification:
    def __init__(self):
        pass

    def verify(self, metadata):
        project = get_project_by_id(metadata.project_id)
        if not project:
            print("Could not find project for metadata:", metadata.project_id)
        experiment = project.get_experiment_by_id(metadata.experiment_id)
        if not experiment:
            print("Could not fine experiment for metadata:", metadata.project_id)

if __name__ == '__main__':
    metadata = input_metadata.Metadata()
    metadata.read("/Users/weymouth/Desktop/junk.json")
    verify = MetadataVerification()
    verify.verify(metadata)