"""Local-network rule syntax, routing scope and router-domain coverage."""
from pathlib import Path
import ipaddress
import unittest

ROOT = Path(__file__).resolve().parents[1]


def entries():
    return [tuple(line.split(',')) for line in (ROOT / 'LocalAreaNetwork.list').read_text().splitlines()
            if line.strip() and not line.startswith('#')]


def domain_matches(host):
    return any(host == row[1] or row[0] == 'DOMAIN-SUFFIX' and host.endswith('.' + row[1])
               for row in entries() if row[0] in ('DOMAIN', 'DOMAIN-SUFFIX'))


class LocalNetworkRules(unittest.TestCase):
    def test_syntax_and_no_duplicate_rules(self):
        rows = entries()
        self.assertEqual(len(rows), len(set(rows)))
        for row in rows:
            if row[0] in ('IP-CIDR', 'IP-CIDR6'):
                self.assertEqual(len(row), 3)
                self.assertEqual(row[2], 'no-resolve')
                net = ipaddress.ip_network(row[1])
                self.assertEqual(net.version, 4 if row[0] == 'IP-CIDR' else 6)
                self.assertGreater(net.prefixlen, 0, 'must not bypass every destination')
            else:
                self.assertIn(row[0], ('DOMAIN', 'DOMAIN-SUFFIX'))
                self.assertEqual(len(row), 2)
                self.assertRegex(row[1], r'^[a-z0-9.-]+$')

    def test_router_domains_and_boundaries(self):
        self.assertEqual(entries().count(('DOMAIN', 'www.asusrouter.com')), 1)
        self.assertTrue(domain_matches('www.asusrouter.com'))
        self.assertFalse(domain_matches('www.asusrouter.com.example.com'))
        for domain in ('tplogin.cn', 'zte.home'):
            self.assertEqual(entries().count(('DOMAIN-SUFFIX', domain)), 1)
            self.assertTrue(domain_matches(domain))
            self.assertTrue(domain_matches('admin.' + domain))
            self.assertFalse(domain_matches('not' + domain))
            self.assertFalse(domain_matches(domain + '.example.com'))
        for host in ('chatgpt.com', 'paypal.com', 'github.com', 'x.com'):
            self.assertFalse(domain_matches(host))

    def test_private_and_tailnet_ranges_retained(self):
        nets = [ipaddress.ip_network(row[1]) for row in entries() if row[0] in ('IP-CIDR', 'IP-CIDR6')]
        for value in ('10.1.2.3', '172.26.64.89', '192.168.1.1', '100.100.100.100', '127.0.0.1', '::1', 'fd7a:115c:a1e0::1'):
            address = ipaddress.ip_address(value)
            self.assertTrue(any(address in net for net in nets if net.version == address.version), value)
        for value in ('8.8.8.8', '1.1.1.1', '2606:4700:4700::1111'):
            address = ipaddress.ip_address(value)
            self.assertFalse(any(address in net for net in nets if net.version == address.version), value)


if __name__ == '__main__':
    unittest.main()
