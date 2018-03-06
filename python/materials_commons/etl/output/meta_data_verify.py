from materials_commons.api import get_project_by_id


class MetadataVerification:
    def __init__(self, target_metadata):
        self.metadata = target_metadata
        self.verified = False
        self.failure = "Project"
        self.delta_list = None
        self.missing_process_list = []
        self.added_process_list = []

    def verify_with_delta_list(self, delta_list):
        self.delta_list = delta_list
        return self.verify()

    def verify(self):
        self.verified = True
        self.failure = None
        if not self.metadata:
            print("Metadata not available.")
            self.verified = False
            self.failure = "Metadata"
            return None
        missing = []
        self.missing_process_list = missing
        added = []
        self.added_process_list = added
        project = get_project_by_id(self.metadata.project_id)
        if not project:
            print("Could not find project:", self.metadata.project_id)
            self.verified = False
            self.failure = "Project"
            return None
        else:
            print("Found project:", project.name, "(" + project.id + ")")
        experiment = self.get_experiment(project, self.metadata.experiment_id)
        if not experiment:
            print("Could not find experiment:", self.metadata.experiment_id)
            self.verified = False
            self.failure = "Experiment"
            return None
        else:
            print("Found experiment: ", experiment.name, "(" + experiment.id + ")")
        if not self.metadata.process_table:
            print("Metadata is missing process table. Expected...")
            print("  calling add_process_table_to_metadata(experiment)")
            self.add_process_table_to_metadata(experiment)
        for process_record in self.metadata.process_metadata:
            if not process_record['id'] in self.metadata.process_table:
                if self.delta_list and self.check_delta_list_for_missing_process(process_record['id']):
                    print("Verified that missing process was deleted:", process_record['id'])
                    continue
                missing.append(process_record['id'])
        for process_id in self.metadata.process_table:
            found = False
            for process_record in self.metadata.process_metadata:
                if process_record['id'] == process_id:
                    found = True
                    break
            if not found:
                if self.delta_list and self.check_delta_list_for_added_process(process_id):
                    print("Verified that additional process was added:", process_id)
                    continue
                added.append(process_id)
        if missing:
            self.verified = False
            self.failure = "Process"
            for process_id in missing:
                print("Could not find spreadsheet process in experiment:", process_id)
        if added:
            self.verified = False
            self.failure = "Process"
            for process_id in added:
                print("Could not find experiment process in spreadsheet:", process_id)
        if self.verified:
            print("Found all processes (" + str(len(self.metadata.process_table)) + ").")
        if not self.verified:
            return None
        return self.metadata

    @staticmethod
    def get_experiment(project, experiment_id):
        experiment_list = project.get_all_experiments()
        probe = None
        for experiment in experiment_list:
            if experiment.id == experiment_id:
                probe = experiment
        return probe

    def add_process_table_to_metadata(self, experiment):
        processes = experiment.get_all_processes()
        process_table = self.make_process_table(processes)
        self.metadata.process_table = process_table

    @staticmethod
    def make_process_table(processes):
        table = {}
        for process in processes:
            table[process.id] = process
        return table

    def check_delta_list_for_missing_process(self, process_id):
        for item in self.delta_list:
            if item['type'] == 'missing_process' and process_id == item['data']['process_id']:
                return True
        return False

    def check_delta_list_for_added_process(self, process_id):
        for item in self.delta_list:
            if item['type'] == 'added_process' and process_id == item['data']['process_id']:
                return True
        return False
