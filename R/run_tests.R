# install.packages("RUnit", repos="http://cran.r-project.org")
library('RUnit')

# Note: assuming that load('run_tests.R') from top level directory
# load the files that contain functions to be tested
source('mcapi/hello.R')

# defile test suite ...
test.suite <- defineTestSuite("hello",
dirs = file.path("tests"),
testFileRegexp = '^test_[a-z_]*\\.R')

# ... and run it
test.result <- runTestSuite(test.suite)
printTextProtocol(test.result)
