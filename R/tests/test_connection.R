test.config.file <-
function() {
    test_that("config works", {
        expect_that(config.file_exists("~/.materialscommons/config.json"),is_true())
    })

    test_that("config default works" , {
        expect_that(config.file_exists(),is_true())
    })
}

test.load.config <-
function() {
    test_that("config content can be parsed", {
        c = config.fetch_config()
        expect_equal(typeof(c),"list")
        expect_equal(typeof(c$apikey),"character")
        expect_equal(typeof(c$mcurl),"character")
    })
}