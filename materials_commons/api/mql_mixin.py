class MQLMixin:
    def mql_load_project(self, project_id):
        self._post(f"/queries/{project_id}/load-project", {})

    def mql_reload_project(self, project_id):
        self._post(f"/queries/{project_id}/load-project", {})

    def mql_execute_query(self, project_id, statement, select_processes=True, select_samples=True):
        self.mql_load_project(project_id)
        form = {
            "statement": statement,
            "select_processes": select_processes,
            "select_samples": select_samples,
        }
        return self._post(f"/queries/{project_id}/execute-query", form)
