# Not implemented

project = create_project(
        name = "ThisProject",
        description = "is amazing")

experiment = project.create_experiment(
        name = "Experiment 1",
        description = "a test experiment generated from api")

processA = experiment.create_process_from_template(Template.create_sample)
sample = create_sample_process.create_samples(
    sample_names = ['Test Sample 1']
    )[0]

processB = experiment.\
    create_process_from_template(Template.computation).\
    add_samples_to_process([sample])