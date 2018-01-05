from materials_commons.api import get_project_by_id
from ..input import metadata

class MetadataVerification:
    def __init__(self):
        pass

    def verify(self, metadata):
        verified = True
        project = get_project_by_id(metadata.project_id)
        if not project:
            print("Could not find project:", metadata.project_id)
            verified = False
        else:
            metadata.project = project
            print("Found project:", project.name)
        experiment = self.get_experiment(project, metadata.experiment_id)
        if not experiment:
            print("Could not find experiment:", metadata.experiment_id)
            verified = False
        else:
            metadata.experiment = experiment
            print("Found experiment:", experiment.name)
        processes = experiment.get_all_processes()
        process_table = self.make_process_table(processes)
        missing = []
        for process_record in metadata.process_metadata:
            if not process_record['id'] in process_table:
                missing.append(process_record['id'])
        if missing:
            verified = False
            for id in missing:
                print("Could not find process: ", id)
        else:
            print("Found all processes (" + str(len(process_table)) + ").")
            metadata.process_table = process_table
        if verified:
            return metadata
        return None

    def get_experiment(self, project, experiment_id):
        experiment_list = project.get_all_experiments()
        probe = None
        for experiment in experiment_list:
            if experiment.id == experiment_id:
                probe = experiment
        return probe

    def make_process_table(self, processes):
        table = {}
        for process in processes:
            table[process.id] = process
        return table

if __name__ == '__main__':
    metadata = metadata.Metadata()
    metadata.read("/Users/weymouth/Desktop/junk.json")
    verify = MetadataVerification()
    verify.verify(metadata)