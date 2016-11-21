module Connection

using Requests

export set_config, make_url, make_url_v2, get_query, get_data

mcapikey = "junk"
mcurl = "http://mctest.localhost/api"

function make_url(restpath)
  p = string(mcurl,"/",restpath)
  return p
end

function make_url_v2(restpath)
  p = string(mcurl,"/v2/",restpath)
  return p
end

function set_config(;appkey=nothing)
  global mcapikey
  println("before set mcapikey = ", mcapikey)
  mcapikey = appkey
  if (typeof(mcapikey) == typeof(nothing))
    throw(Exception("Key must be assigned"))
  end
  println("set mcapikey = ", mcapikey)
end

function get_query()
  println("get mcapikey =",mcapikey)
  ret = string("?apikey=",mcapikey)
  println("Return = ", ret)
  return ret
end

function get_data(url)
  res = get(url)
  return res.data
end

end # of Connection
