from materials_commons.api import get_project_by_id
from ..input import metadata


class MetadataVerification:
    def __init__(self):
        self.metadata = None
        self.verified = False
        self.failure = "Project"
        self.missing_process_list = []
        self.added_process_list = []

    def verify(self, metadata):
        self.metadata = metadata
        self.verified = True
        self.failure = None
        missing = []
        self.missing_process_list = missing
        added = []
        self.added_process_list = added
        project = get_project_by_id(metadata.project_id)
        if not project:
            print("Could not find project:", metadata.project_id)
            self.verified = False
            self.failure = "Project"
            return None
        else:
            metadata.project = project
            print("Found project:", project.name, "(" + project.id + ")")
        experiment = self.get_experiment(project, metadata.experiment_id)
        if not experiment:
            print("Could not find experiment:", metadata.experiment_id)
            self.verified = False
            self.failure = "Experiment"
            return None
        else:
            metadata.experiment = experiment
            print("Found experiment: ", experiment.name, "(" + experiment.id + ")")
        processes = experiment.get_all_processes()
        process_table = self.make_process_table(processes)
        metadata.process_table = process_table
        for process_record in metadata.process_metadata:
            if not process_record['id'] in process_table:
                missing.append(process_record['id'])
        for process_id in process_table:
            found = False
            for process_record in metadata.process_metadata:
                if process_record['id'] == process_id:
                    found = True
                    break
            if not found:
                added.append(process_id)
        if missing:
            self.verified = False
            self.failure = "Process"
            for id in missing:
                print("Could not find spreadsheet process in experiment:", id)
        if added:
            self.verified = False
            self.failure = "Process"
            for id in added:
                print("Could not find experiment process in spreadsheet:", id)
        if self.verified:
            print("Found all processes (" + str(len(process_table)) + ").")
        if not self.verified:
            return None
        return metadata

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
