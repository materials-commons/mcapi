# install.packages("httr")
library(httr)

test <- 
function(accessUrl, apiCall, apikey, get = TRUE, postBody = NULL) {
	result <- list()
    url <- paste0(accessUrl, apiCall,"?apikey=",apikey)
    print(url)
    if (get) {
        req <- GET(url)
    } else {
        req <- POST(url, body = postBody)
    }
    result$content <- content(req, "text")
    result$headers <- headers(req)
    result$status <- req$status_code
    result$statusMessage <- http_status(req)$message
    return(result)
}

base = "https://mctest.localhost/api/v2/"
probe = "projects"
apikey = "totally-bogus"

results = test(base,probe,apikey)
print(results)