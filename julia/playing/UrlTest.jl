using .Test
using Requests

mcurl = "http://mctest.localhost/api"

function make_url(restpath)
    p = string(mcurl,"/",restpath)
    return p
end

function make_url_v2(restpath)
    p = string(mcurl,"/v2/",restpath)
    return p
end

@testset begin
  actual = make_url("a")
  expected = string(mcurl,"/a")
  res = @test actual == expected
  # println("test results: ",res)

  actual = make_url_v2("a")
  expected = string(mcurl,"/v2/a")
  res = @test actual == expected
  # println("test results: ",res)

  actual = make_url("a")
  expected = string(mcurl,"/b")
  res = @test actual == expected
  # println("test results: ",res)
end
