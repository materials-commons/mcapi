using .Test

include("Connection.jl")

importall Connection

set_config(appkey="totally-bogus")

@testset "Test Connection" begin
  @test get_query() == "?apikey=totally-bogus"
  actual = make_url("a")
  expected = "http://mctest.localhost/api/a"
  @test actual == expected

  actual = make_url_v2("a")
  expected = "http://mctest.localhost/api/v2/a"
  @test actual == expected
end

#println(readstring(IOBuffer(get_data(string(make_url_v2("projects"),get_query())))))
#url = "http://mctest.localhost/api/v2/projects/c2ecf9d9-ca34-4dc6-8bec-fa8661ac7b43/directories/2b2ae77b-a685-4996-b61e-affaaac31485?apikey=totally-bogus"
println(readstring(IOBuffer(get_data(url))))
