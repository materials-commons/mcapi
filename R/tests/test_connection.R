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
    test_that("config content is parsable", {
        expect_that(config.fetch_config() != null, is_true())
    })
}