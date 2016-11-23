# install.packages("culr", repos="http://cran.r-project.org")
library(curl)
# install.packages("jsonlite", repos="http://cran.r-project.org")
library(jsonlite)

base = "http://mctest.localhost/api/v2"
com1 = "/projects/"
com2 = "/directories/"
key_query = "?apikey=totally-bogus"


all_projects_url = paste(base,"/projects",key_query,sep="")
all_projects = fromJSON(all_projects_url)

project_id = all_projects$id[1]
project_url = paste(base,com1,project_id,key_query,sep="")
print(project_url)
project = fromJSON(project_url)
print(project$'_type')

top_directory_url = paste(base,com1,project_id,com2,'top',key_query,sep="")
print(top_directory_url)
top_directory = fromJSON(top_directory_url)
print(top_directory$'_type')

directory_id = top_directory$id
directory_url = paste(base,com1,project_id,com2,directory_id,key_query,sep="")
print(directory_url)
directory = fromJSON(directory_url)
print(directory$'_type')
