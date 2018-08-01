import unittest
from materials_commons.api.config import Config
from materials_commons.api.remote import RemoteWithApikey
from materials_commons.api.api import configure_remote


class BaseTest(unittest.TestCase):
    def test_config(self):
        config = Config(override_config={'apikey': 'testing1', 'mcurl': 'testing2'})
        self.assertEqual('testing1', config.mcapikey)
        self.assertEqual('testing2', config.mcurl)

    def test_remote_with_api(self):
        remote = RemoteWithApikey('testing1')
        self.assertEqual('testing1', remote.config.mcapikey)

    def test_remote_with_config(self):
        config = Config(override_config={'apikey': 'testing1', 'mcurl': 'testing2'})
        self.assertEqual('testing1', config.mcapikey)
        self.assertEqual('testing2', config.mcurl)
        remote = RemoteWithApikey('testing1', config=config)
        self.assertEqual('testing1', remote.config.mcapikey)
        self.assertEqual('testing2', remote.config.mcurl)

    def test_configure_remote1(self):
        config = Config(override_config={'apikey': 'testing1', 'mcurl': 'testing2'})
        self.assertEqual('testing1', config.mcapikey)
        self.assertEqual('testing2', config.mcurl)
        remote = RemoteWithApikey('testing1', config=config)
        self.assertEqual('testing1', remote.config.mcapikey)
        self.assertEqual('testing2', remote.config.mcurl)
        remote = configure_remote(None, "testing3")
        self.assertEqual('testing3', remote.config.mcapikey)

    def test_configure_remote2(self):
        config = Config(override_config={'apikey': 'testing1', 'mcurl': 'testing2'})
        self.assertEqual('testing1', config.mcapikey)
        self.assertEqual('testing2', config.mcurl)
        remote = RemoteWithApikey('testing1', config=config)
        self.assertEqual('testing1', remote.config.mcapikey)
        self.assertEqual('testing2', remote.config.mcurl)
        remote = configure_remote(remote, None)
        self.assertEqual('testing1', remote.config.mcapikey)
        self.assertEqual('testing2', remote.config.mcurl)

    def test_configure_remote3(self):
        config = Config(override_config={'apikey': 'testing1', 'mcurl': 'testing2'})
        self.assertEqual('testing1', config.mcapikey)
        self.assertEqual('testing2', config.mcurl)
        remote = RemoteWithApikey('testing1', config=config)
        self.assertEqual('testing1', remote.config.mcapikey)
        self.assertEqual('testing2', remote.config.mcurl)
        remote = configure_remote(remote, 'testing3')
        self.assertEqual('testing3', remote.config.mcapikey)
        self.assertEqual('testing2', remote.config.mcurl)
