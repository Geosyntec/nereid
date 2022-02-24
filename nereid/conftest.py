def pytest_addoption(parser):
    parser.addoption("--async", action="store_true", default=False)
