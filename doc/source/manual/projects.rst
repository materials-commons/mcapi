.. manual/projects.rst

Projects
=========

A project in Materials Commons is place to store data, such as files and other meta data. It is also the means to
control access to your data. You can have an unlimited number of projects. Each project can have a different list of
people who have access to it. The Materials Commons API provides multiple ways to interact with projects. Below are
some examples: ::

    # First create a client instance
    import materials_commons.api as mcapi
    import os

    c = mcapi.Client(os.getenv("MC_API_TOKEN"))

    # Get a list of all your projects
    projects = c.get_all_projects()

    # Get a particular project by its id
    project = c.get_project(3)

    # Create a project with a description
    project = c.create_project("project-name", mcapi.CreateProjectRequest(description="project description"))

    # Create a project without a description
    project = c.create_project("project-name")

    # Pretty print the created projects attributes
    project.pretty_print()

    # Add user to project
    user = c.get_user_by_email("example-user@example.com")
    project = c.add_user_to_project(project.id, user.id)

    # Delete the project
    c.delete_project(project.id)

