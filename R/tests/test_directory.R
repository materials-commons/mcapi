test.get.top.directory.from.project <-
function() {
    all_projects = projects.get_all_projects()
    expect_equal(typeof(all_projects),"list")
    expect_true(length(all_projects) > 0)
    all_projects$select = (all_projects$files > 0)
    if (length(all_projects[all_projects$select,]$id) > 0) {
        selected_project = all_projects[all_projects$select,][1,]
        project_id = selected_project$id
        directory = directories.get_top_directory_for_project(project_id)
    } else {
        expect_true(FALSE,"For the test user, there are no projects with files.")
    }
}