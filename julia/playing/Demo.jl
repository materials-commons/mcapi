using Requests
using JSON

base = "http://mctest.localhost/api/v2"
com1 = "/projects/"
com2 = "/directories/"
key_query = "?apikey=totally-bogus"

url_all_projects = string(base,"/projects",key_query)

res = get(url_all_projects)
text = readstring(IOBuffer(res.data))
holder = JSON.parse(text)
is_array = typeof(match(r"^Array",string(typeof(holder)))) != typeof(nothing)

if (is_array)
  println("+++++++++++++++++")
  println("Type of 'object' in first element of array: ",holder[1]["_type"])
end

project_id = "c2ecf9d9-ca34-4dc6-8bec-fa8661ac7b43"

details_of_project = string(base,com1,project_id,key_query)

res = get(details_of_project)
text = readstring(IOBuffer(res.data))
holder = JSON.parse(text)
is_dict = typeof(match(r"^Dict",string(typeof(holder)))) != typeof(nothing)

if (is_dict)
  println("+++++++++++++++++")
  println("Type of 'object': ",holder["_type"])
end

directory_id = "2b2ae77b-a685-4996-b61e-affaaac31485"
content_of_directroy = string(base,com1,project_id,com2,directory_id,key_query)

res = get(content_of_directroy)
text = readstring(IOBuffer(res.data))
holder = JSON.parse(text)
is_dict = typeof(match(r"^Dict",string(typeof(holder)))) != typeof(nothing)

if (is_dict)
  println("+++++++++++++++++")
  println("Type of 'object': ",holder["_type"])
end
