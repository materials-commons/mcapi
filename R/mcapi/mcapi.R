# install.packages("culr", repos="http://cran.r-project.org")
library(curl)
# install.packages("jsonlite", repos="http://cran.r-project.org")
library(jsonlite)

config.default.path = file.path(Sys.getenv("HOME"),".materialscommons/config.json")

config.file_exists <-
function(path=config.default.path) {
    return(file.exists(file.path(path)))
}

config.fetch_config <-
function(path=config.default.path) {
    if (! config.file_exists(path)) {
        return(NULL)
    }
    config = fromJSON(path)
    return(config)
}

connection.json_from_request<-
function(partial_url)
{
    config = config.fetch_config()
    apikey = config$apikey
    key_query = paste0("?apikey=",apikey)

    base = config$mcurl
    if (endsWith(base,"/")) {
        base = substr(base,0,length(base) - 1)
    }
    base = paste0(base,"/v2")

    if (!startsWith(partial_url,"/")) {
        partial_url = paste0("/",partial_url)
    }
    if (endsWith(partial_url,"/")) {
        partial_url = substr(base,0,nchar(partial_url) - 1)
    }
    url = paste0(base,partial_url,key_query)
    print(url)
    return(fromJSON(url))
}

projects.get_all_projects <-
function() {
    return (connection.json_from_request("/projects"))
}

projects.get_project <-
function(id) {
    request = paste0("/projects/",id)
    return (connection.json_from_request(request))
}

directories.get_top_directory_for_project <-
function (project_id) {
    request = paste0("/projects/",project_id,"/directories")
    return (connection.json_from_request(request))
}