from .client_base import merge_dicts
from .decoder import decode_experiment, decode_experiment_list
from .requests import CreateExperimentRequest, UpdateExperimentRequest


class ExperimentMixin:
    def get_all_experiments(self, project_id, params=None):
        """
        Get all experiments for a given project.

        :param int project_id: The project id
        :param params:
        :return: A list of experiments
        :rtype: Experiment[]
        :raises MCAPIError:
        """
        return self._get(f"/projects/{project_id}/experiments", params, decoder=decode_experiment_list)

    def get_experiment(self, experiment_id, params=None):
        """
        Get an experiment.

        :param int experiment_id: The experiment id
        :param params:
        :return: The experiment
        :rtype: Experiment
        :raises MCAPIError:
        """
        return self._get(f"/experiments/{experiment_id}", params, decoder=decode_experiment)

    def create_experiment(self, project_id, name, attrs=None):
        """
        Create a new experiment in a project.

        :param int project_id: The id of the project the experiment is in
        :param str name: Name of experiment
        :param CreateExperimentRequest attrs: Additional attributes on the experiment
        :return: The created experiment
        :rtype: Experiment
        :raises MCAPIError:
        """
        if not attrs:
            attrs = CreateExperimentRequest()
        form = merge_dicts({"project_id": project_id, "name": name}, attrs.to_dict())
        return self._post("/experiments", form, decoder=decode_experiment)

    def update_experiment(self, experiment_id, attrs):
        """
        Update attributes of an experiment.

        :param int experiment_id: The experiment id
        :param UpdateExperimentRequest attrs: Attributes to update
        :return: The updated experiment
        :rtype: Experiment
        :raises MCAPIError:
        """
        form = merge_dicts({"experiment_id": experiment_id}, attrs.to_dict())
        return self._put(f"/experiments/{experiment_id}", form, decoder=decode_experiment)

    def delete_experiment(self, project_id, experiment_id):
        """
        Delete experiment in project.

        :param int project_id: The id of the project the experiment is in
        :param int experiment_id: The experiment id
        :raises MCAPIError:
        """
        self._delete(f"/projects/{project_id}/experiments/{experiment_id}")

    def update_experiment_workflows(self, project_id, experiment_id, workflow_id):
        """
        Toggle whether a workflow is in the experiment.

        :param int project_id: Id of project containing the experiment and workflow
        :param int experiment_id: Id of experiment
        :param int workflow_id: Id of workflow
        :return: The updated experiment
        :rtype: Experiment
        :raises MCAPIError:
        """
        form = {"project_id": project_id, "workflow_id": workflow_id}
        return self._put(f"/experiments/{experiment_id}/workflows/selection", form, decoder=decode_experiment)
