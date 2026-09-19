"""Keep every published rule set reachable from the client examples."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://raw.githubusercontent.com/Jinx-1120/clash_rules/main/'


class ClientExamples(unittest.TestCase):
    def test_all_rule_files_are_referenced_with_refresh(self):
        files = {path.name for path in ROOT.glob('*.list')}
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
                    keys = [BASE + name for name in ('LocalAreaNetwork.list', 'no_proxy.list', 'ai.list', 'ai-shared.list', 'proxy.list')]
                    final = 'FINAL,Proxies'
                else:
                    rules = text.split('\nrules:\n', 1)[1]
                    keys = ['RULE-SET,' + name + ',' for name in ('LocalAreaNetwork', 'no_proxy', 'ai', 'ai-shared', 'proxy')]
                    final = 'MATCH,Proxies'
                positions = [rules.index(key) for key in keys]
                self.assertEqual(positions, sorted(positions))
                self.assertLess(rules.index('DOMAIN,proxy.example.com,DIRECT'), positions[0])
                self.assertGreater(rules.index(final), positions[-1])


if __name__ == '__main__':
    unittest.main()
