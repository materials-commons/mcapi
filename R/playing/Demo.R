# install.packages("culr", repos="http://cran.r-project.org")
library(curl)
# install.packages("jsonlite", repos="http://cran.r-project.org")
library(jsonlite)

base = "http://mctest.localhost/api/v2"
com1 = "/projects/"
project_id = "c2ecf9d9-ca34-4dc6-8bec-fa8661ac7b43"
com2 = "/directories/"
directory_id = "2b2ae77b-a685-4996-b61e-affaaac31485"
key_query = "?apikey=totally-bogus"

urls = c(
paste(base,"/projects",key_query,sep=""),
paste(base,com1,project_id,key_query,sep=""),
paste(base,com1,project_id,com2,directory_id,key_query,sep="")
)

for (url in urls) {
  holder = fromJSON(url)
  print(typeof(holder))
}
