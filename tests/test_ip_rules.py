"""Keep voice routing separate from optional cloud-provider IP fallback."""
from pathlib import Path
import ipaddress
import unittest

ROOT = Path(__file__).resolve().parents[1]


class IPRules(unittest.TestCase):
    def test_ip_lists_have_valid_public_ranges_and_no_duplicates(self):
        for name in ('ai-voice.list', 'china-company-ip.list'):
            rows = [line.split(',') for line in (ROOT / name).read_text().splitlines()
                    if line.strip() and not line.startswith('#')]
            self.assertTrue(rows, name)
            self.assertEqual(len(rows), len({tuple(row) for row in rows}), name)
            for row in rows:
                self.assertEqual(row[0], 'IP-CIDR')
                self.assertEqual(row[2:], ['no-resolve'] if name == 'ai-voice.list' else [])
                net = ipaddress.ip_network(row[1])
                self.assertEqual(net.version, 4)
                self.assertTrue(net.is_global, row)
                self.assertGreater(net.prefixlen, 0)

    def test_voice_ranges_do_not_capture_lan_or_generic_cloud_addresses(self):
        nets = [ipaddress.ip_network(line.split(',')[1])
                for line in (ROOT / 'ai-voice.list').read_text().splitlines()
                if line.startswith('IP-CIDR,')]
        for value in ('4.151.200.38', '102.37.57.54'):
            self.assertTrue(any(ipaddress.ip_address(value) in net for net in nets), value)
        for value in ('4.151.200.39', '192.168.1.1', '100.100.100.100', '8.8.8.8'):
            self.assertFalse(any(ipaddress.ip_address(value) in net for net in nets), value)


if __name__ == '__main__':
    unittest.main()
