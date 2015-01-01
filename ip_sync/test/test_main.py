# pylint: disable=C0111,R0903
from mock import patch
from ipaddress import IPv4Address, IPv6Address
import six
import io
import requests.exceptions

from ip_sync.test import TestBase
from ip_sync import main


class TestMain(TestBase):
    @patch('requests.get')
    def test_resolve_ipv4(self, request_mock):
        ip = '127.0.0.1'

        request_mock.return_value.status_code = 200
        request_mock.return_value.text = six.u('%s\n' % ip)

        self.assertEquals(main.resolve_ip(), IPv4Address(six.u(ip)))

    @patch('requests.get')
    def test_resolve_ipv6(self, request_mock):
        for ip in ['2001:0db8:85a3:0000:0000:8a2e:0370:7334',
                   '2001:0db8:85a3::8a2e:0370:7334',
                   '::1']:
            request_mock.return_value.status_code = 200
            request_mock.return_value.text = six.u('%s\n' % ip)

            self.assertEquals(main.resolve_ip(), IPv6Address(six.u(ip)))

    @patch('requests.get')
    def test_resolve_ip_returns_none_on_error_status_code(self, request_mock):
        request_mock.return_value.status_code = 500
        request_mock.return_value.text = six.u('An error occurred')

        self.assertIsNone(main.resolve_ip())

    @patch('requests.get')
    def test_resolve_ip_returns_none_on_exception(self, request_mock):
        request_mock.side_effect = requests.exceptions.ConnectionError

        self.assertIsNone(main.resolve_ip())

    @patch('requests.get')
    def test_resolve_ip_returns_none_on_invalid_data(self, request_mock):
        request_mock.return_value.status_code = 200
        request_mock.return_value.text = six.u('some random data\n')

        self.assertIsNone(main.resolve_ip())

    def test_load_config(self):
        config_file = io.StringIO(self._config_yaml)
        config_file.name = 'test_config.yml'
        config_data = main.load_config(config_file)
        self.assertIsNotNone(config_data.get('rackspace'))
        self.assertIsNotNone(config_data.get('namecheap'))
        self.assertIsNotNone(config_data['rackspace'].get('api_username'))
        self.assertIsNotNone(config_data['namecheap'].get('test.com'))
        self.assertIsNotNone(config_data['namecheap']['test.com'].get('hostname'))