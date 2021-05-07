.. manual/experiments.rst

Experiments
===========

A project in Materials Commons can contain multiple experiments. An experiment is way to further organize the research
and data in a project. The examples below assume you retrieved a project from the server. ::

    # Get all experiments in a project
    experiments = c.get_all_experiments(project.id)

    # Create a new experiment
    experiment = c.create_experiment(project.id, "experiment-name")

    # Create a new experiment with a description and summary
    req = mcapi.CreateExperimentRequest(description="experiment description", summary="experiment summary")
    experiment = c.create_experiment(project.id, "experiment-name", req)

    # Delete experiment in project
    c.delete_experiment(project.id, experiment.id)

