from django.contrib.auth.models import User
from cabot.cabotapp.tests.tests_basic import LocalTestCase
from cabot.cabotapp.models import StatusCheck, Instance
from cabot.plugins.models import StatusCheckPluginModel
import cabot_check_icmp.plugin

class TestICMPStatusCheckPlugin(LocalTestCase):

    def setUp(self):
        super(TestICMPStatusCheckPlugin, self).setUp()

        self.icmp_check_plugin, created = StatusCheckPluginModel.objects.get_or_create(
                slug='cabot_check_icmp'
                )

        self.icmp_check = StatusCheck.objects.create(
                check_plugin=self.icmp_check_plugin,
                name = 'Default ICMP Check'
                )

        self.instance = Instance.objects.create(
                name = 'Default Instance',
                address = 'localhost'
                )

        self.instance.status_checks.add(self.icmp_check)
        self.instance.save()

    # We aren't mocking subprocess.Popen because it's more hassle than its
    # worth. The below functions should work absolutely fine.
    def test_run_success(self):
        self.instance.address = 'localhost' # Always pingable
        self.instance.save()
        result = self.icmp_check.run()
        self.assertTrue(result.succeeded)

    def test_run_failure(self):
        self.instance.address = '256.256.256.256' # Impossible IP
        self.instance.save()
        result = self.icmp_check.run()
        self.assertFalse(result.succeeded)

