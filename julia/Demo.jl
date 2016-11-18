using Requests
using JSON

base = "http://mctest.localhost/api/v2"
com1 = "/projects/"
project_id = "c2ecf9d9-ca34-4dc6-8bec-fa8661ac7b43"
com2 = "/directories/"
directory_id = "2b2ae77b-a685-4996-b61e-affaaac31485"
key_query = "?apikey=totally-bogus"

urls = [
string(base,"/projects",key_query),
string(base,com1,project_id,key_query),
string(base,com1,project_id,com2,directory_id,key_query)
]

for url in urls
  res = get(url)
  text = readstring(IOBuffer(res.data))
  holder = JSON.parse(text)
  is_array = typeof(match(r"^Array",string(typeof(holder)))) != typeof(nothing)
  is_dict = typeof(match(r"^Dict",string(typeof(holder)))) != typeof(nothing)
  println("+++++++++++++++++")
  println(url)
  # println("==>")
  # println(text)
  # println("-->")
  # println(JSON.parse(text))
  # println("- - - >")
  println(string(typeof(holder)))
  if (is_array)
    println("Type of 'object' in first element of array: ",holder[1]["_type"])
  end
  if (is_dict)
    println("Type of 'object': ",holder["_type"])
  end
  println("----------------")
end
