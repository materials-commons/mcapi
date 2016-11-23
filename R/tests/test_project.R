test.get.all.projects <-
function() {
    all_projects = projects.get_all_projects()
    expect_equal(typeof(all_projects),"list")
    expect_true(length(all_projects) > 0)
    first_id = all_projects$id[1]
    first_project = all_projects[all_projects$id == first_id,]
    expect_equal(first_project$'_type'[1],"project")
    first_project_id = first_project$id
    expect_equal(first_id,first_project_id)
}

test.get.one.project <-
function() {
    all_projects = projects.get_all_projects()
    expect_equal(typeof(all_projects),"list")
    expect_true(length(all_projects) > 0)
    if (length(all_projects$id) > 0) {
        selected_project = all_projects[1,]
        project_id = selected_project$id
        project = projects.get_project(project_id)
        expect_equal(project$'_type'[1],"project")
        expect_equal(project_id,project$id)
        expect_true(project$owner %in% project$users$user_id)
    } else {
        expect_true(FALSE,"There are no projects for the test user.")
    }
}

#test.get.file.records <-
#function() {
#    all_projects = projects.get_all_projects()
#    expect_equal(typeof(all_projects),"list")
#    expect_true(length(all_projects) > 0)
#    all_projects$select = (all_projects$files > 0)
#    if (length(all_projects[all_projects$select,]$id) > 0) {
#        selected_project = all_projects[all_projects$select,][1,]
#        project_id = selected_project$id
#        files = files.get_files_for_project(project_id)
#    } else {
#        expect_true(FALSE,"For the test user, there are no projects with files.")
#    }
#}

# (all_projects$experiments > 0) &
# (all_projects$files > 0) &
# (all_projects$samples > 0)
# library(jsonlite)