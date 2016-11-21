function all_the_args(normal_arg, optional_positional_arg=2; keyword_arg="foo")
    println("normal arg: $normal_arg")
    println("optional arg: $optional_positional_arg")
    println("keyword arg: $keyword_arg")
end

all_the_args(1,3,keyword_arg="boo")

ty = typeof(all_the_args)

println(typeof(all_the_args) == ty)

println(typeof(ty))
