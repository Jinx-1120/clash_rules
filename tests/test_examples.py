"""Keep the shared baseline rule sets reachable from the client examples."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://raw.githubusercontent.com/Jinx-1120/clash_rules/main/'
OPTIONAL = {'ai-shared-extra.list', 'china-company-ip.list'}
MANAGED_SUBSCRIPTION_RULES = {
    'Apple.list', 'ApplePush.list', 'Bahamut.list', 'Bilibili.list', 'DisneyPlus.list',
    'Epic.list', 'Extra_CN.list', 'Extra_CN_2.list', 'Extra_CN_3.list', 'Extra_Crypto.list',
    'Extra_Proxies.list', 'Facebook.list', 'GameDownload.list', 'GlobalScholar.list',
    'Google.list', 'HBOHK.list', 'HBOUSA.list', 'HBO_Max.list', 'Microsoft.list',
    'Netflix.list', 'PayPal-Clash.list', 'PayPal.list', 'PlayStation.list', 'ProxyLite.list',
    'Speedtest.list', 'Steam.list', 'Telegram.list', 'TikTok.list', 'Twitter.list',
    'WeChat.list', 'Xbox.list', 'YouTube.list', 'myTVSUPER.list', 'proxy-explicit.list',
}


class ClientExamples(unittest.TestCase):
    def test_speedtest_keeps_the_managed_surge_matching_options(self):
        rules = [
            line for line in (ROOT / 'Speedtest.list').read_text().splitlines()
            if line and not line.startswith('#')
        ]
        self.assertEqual(rules, [
            'DOMAIN-SUFFIX,fast.com,extended-matching',
            'DOMAIN-SUFFIX,speed.cloudflare.com,extended-matching',
            'DOMAIN-SUFFIX,ooklaserver.net,extended-matching',
            'DOMAIN,speed.dler.io,extended-matching',
            'DOMAIN-SUFFIX,speedtest.co,extended-matching',
            'DOMAIN-SUFFIX,speedtest.net,extended-matching',
            'DOMAIN-SUFFIX,speedtestcustom.com,extended-matching',
            'USER-AGENT,SpeedTest*',
        ])

    def test_surge_keeps_proxy_fallback_when_ip_lookup_fails(self):
        text = (ROOT / 'examples/surge.conf').read_text()
        self.assertEqual(text.strip().splitlines()[-1], 'FINAL,Proxies,dns-failed')

    def test_all_rule_files_are_referenced_with_refresh(self):
        files = {path.name for path in ROOT.glob('*.list')} - MANAGED_SUBSCRIPTION_RULES
        for example in (ROOT / 'examples').iterdir():
            with self.subTest(example=example.name):
                text = example.read_text()
                expected = files if example.name == 'surge.conf' else files - {'ai-process-surge.list'}
                urls = re.findall(re.escape(BASE) + r'([\w.-]+\.list)', text)
                self.assertEqual(set(urls), expected)
                self.assertEqual(len(urls), len(expected))
                self.assertNotIn('/drop/', text)
                if example.suffix == '.conf':
                    lines = [line for line in text.splitlines() if BASE in line]
                    self.assertTrue(all(line.endswith(',update-interval=3600') for line in lines))
                    if example.name == 'surge.conf':
                        self.assertIn('#!MACOS-ONLY RULE-SET,' + BASE + 'ai-process-surge.list,AI,', text)
                else:
                    self.assertEqual(text.count('    interval: 3600'), len(expected))
                    self.assertEqual(text.count('    behavior: classical'), len(expected))
                    self.assertEqual(text.count('    format: text'), len(expected))
                    for filename in expected:
                        self.assertIn('- RULE-SET,' + filename.removesuffix('.list') + ',', text)

    def test_direct_and_ai_rules_precede_general_routing(self):
        for example in (ROOT / 'examples').iterdir():
            with self.subTest(example=example.name):
                text = example.read_text()
                if example.suffix == '.conf':
                    rules = text.split('[Rule]\n', 1)[1]
                    keys = [BASE + name for name in ('LocalAreaNetwork.list', 'no_proxy.list', 'ai-mainland.list', 'ai.list', 'ai-shared.list', 'ai-voice.list', 'proxy.list')]
                    final = 'FINAL,Proxies'
                else:
                    rules = text.split('\nrules:\n', 1)[1]
                    keys = ['RULE-SET,' + name + ',' for name in ('LocalAreaNetwork', 'no_proxy', 'ai-mainland', 'ai', 'ai-shared', 'ai-voice', 'proxy')]
                    final = 'MATCH,Proxies'
                positions = [rules.index(key) for key in keys]
                self.assertEqual(positions, sorted(positions))
                self.assertLess(rules.index('DOMAIN,proxy.example.com,DIRECT'), positions[0])
                self.assertGreater(rules.index(final), positions[-1])

    def test_shared_extensions_and_company_ips_require_opt_in(self):
        for example in (ROOT / 'examples').iterdir():
            with self.subTest(example=example.name):
                active = '\n'.join(line for line in example.read_text().splitlines()
                                   if not line.lstrip().startswith('#'))
                for filename in OPTIONAL:
                    self.assertNotIn(BASE + filename, active)
                    self.assertNotIn('RULE-SET,' + filename.removesuffix('.list') + ',', active)
                self.assertIn('MainlandAI', active)
                if example.suffix == '.conf':
                    self.assertIn(BASE + 'ai-mainland.list,MainlandAI,', active)
                    self.assertIn('MainlandAI = select, DIRECT, Proxies', active)
                else:
                    self.assertIn('RULE-SET,ai-mainland,MainlandAI', active)
                    self.assertIn('proxies: [DIRECT, Proxies]', active)


if __name__ == '__main__':
    unittest.main()
