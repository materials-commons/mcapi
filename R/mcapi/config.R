config.default.path = file.path(Sys.getenv("HOME"),".materialscommons/config.json")

config.file_exists <-
function(path=config.default.path) {
    return(file.exists(file.path(path)))
}

config.fetch_config <-
function(path=config.default.path) {
    if (! config.file_exists(path))
        throw 