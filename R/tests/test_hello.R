test.hello <-
function()
{
    checkEquals("hello, bob", hello("bob"))
}

test.deactivation <-
function()
{
    DEACTIVATED('Deactivating this test function')
}