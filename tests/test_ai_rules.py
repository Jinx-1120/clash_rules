"""Offline routing-contract tests; real Surge matching remains a separate check."""
from pathlib import Path
import fnmatch
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]

def rules(name):
    return [tuple(line.split(',')) for line in (ROOT / name).read_text().splitlines()
            if line.strip() and not line.startswith('#')]

def domain_matches(host, entries):
    return any(host == value or kind == 'DOMAIN-SUFFIX' and host.endswith('.' + value)
               for kind, value in entries)

def process_matches(path, entries):
    for _, value in entries:
        if value.startswith('/'):
            if value.endswith('/') and path.startswith(value):
                return True
            if not value.endswith('/') and fnmatch.fnmatchcase(path, value):
                return True
        elif fnmatch.fnmatchcase(path.rsplit('/', 1)[-1], value):
            return True
    return False

class AIRules(unittest.TestCase):
    def test_format_and_duplicates(self):
        combined = []
        for name in ('ai.list', 'ai-shared.list', 'ai-process-surge.list'):
            entries = rules(name)
            self.assertTrue(entries)
            self.assertEqual(len(entries), len(set(entries)), name)
            for row in entries:
                self.assertEqual(len(row), 2, row)
                kind, value = row
                if name == 'ai-process-surge.list':
                    self.assertEqual(kind, 'PROCESS-NAME')
                    self.assertFalse(value.startswith('*'), 'Surge treats this as a filename, not path')
                else:
                    self.assertIn(kind, ('DOMAIN', 'DOMAIN-SUFFIX'))
                    self.assertRegex(value, r'^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$')
                    self.assertNotIn('..', value)
            combined.extend(entries)
        self.assertEqual(len(combined), len(set(combined)))

    def test_named_app_endpoints(self):
        hosts = '''chatgpt.com ws.chatgpt.com auth.openai.com api.openai.com cdn.oaistatic.com
        files.oaiusercontent.com api.anthropic.com platform.claude.com claude.app
        bridge.claudeusercontent.com nested.frame.claudeusercontent.com widget.claudemcpcontent.com
        cloudcode-pa.googleapis.com daily-cloudcode-pa.googleapis.com
        daily-cloudcode-pa.sandbox.googleapis.com antigravity.google.com antigravity-unleash.goog
        api2.cursor.sh api5.cursor.sh marketplace.cursorapi.com downloads.cursor.com
        computer.cluster.cursorvm.com grok.com api.x.ai management-api.x.ai
        api.githubcopilot.com api.individual.githubcopilot.com api.business.githubcopilot.com
        api.enterprise.githubcopilot.com copilot-proxy.githubusercontent.com
        copilot-telemetry.githubusercontent.com gemini.google.com perplexity.ai'''.split()
        for host in hosts:
            with self.subTest(host=host):self.assertTrue(domain_matches(host, rules('ai.list')))

    def test_shared_identity_is_explicit(self):
        for host in ('challenges.cloudflare.com','accounts.google.com','oauth2.googleapis.com'):
            self.assertTrue(domain_matches(host, rules('ai-shared.list')), host)
            self.assertFalse(domain_matches(host, rules('ai.list')), host)

    def test_no_generic_cloud_social_or_developer_capture(self):
        entries = rules('ai.list') + rules('ai-shared.list')
        for host in ('google.com','mail.google.com','maps.googleapis.com','storage.googleapis.com',
                     'github.com','api.github.com','github.githubassets.com','avatars.githubusercontent.com',
                     'raw.githubusercontent.com','registry.npmjs.org','example.sentry.io',
                     'example.auth0.com','x.com','twitter.com','cloudflare.com','cdn.jsdelivr.net',
                     'notopenai.com','openai.com.evil.example','claude.ai.evil.example','127.0.0.1'):
            self.assertFalse(domain_matches(host, entries), host)
        self.assertTrue(all(kind not in ('IP-ASN','IP-CIDR','DOMAIN-KEYWORD') for kind,_ in entries))

    def test_helper_cli_and_versioned_paths(self):
        paths = ['/Applications/ChatGPT.app/Contents/Resources/codex',
                 '/Applications/ChatGPT.app/Contents/Frameworks/Codex Framework.framework/Versions/999/Helpers/Codex (Service).app/Contents/MacOS/Codex (Service)',
                 '/Applications/Claude.app/Contents/Helpers/chrome-native-host',
                 '/Users/test/.local/share/claude/versions/2.99.123',
                 '/Users/test/Applications/Cursor.app/Contents/MacOS/Cursor',
                 '/Applications/Antigravity.app/Contents/Resources/app/extensions/antigravity/bin/language_server_macos_arm',
                 '/Applications/Grok.app/Contents/MacOS/Grok',
                 '/usr/local/bin/copilot','/usr/local/bin/codex','/usr/local/bin/claude',
                 '/Users/test/.local/share/cursor-agent/versions/123/node','/usr/local/bin/agy']
        for path in paths:self.assertTrue(process_matches(path,rules('ai-process-surge.list')), path)

    def test_no_parent_inheritance_or_generic_runtime_capture(self):
        for path in ('/usr/bin/curl','/usr/local/bin/node','/usr/bin/python3','/usr/bin/ssh',
                     '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                     '/Applications/Visual Studio Code.app/Contents/MacOS/Electron',
                     '/Applications/Claude.app.evil/Contents/MacOS/helper'):
            self.assertFalse(process_matches(path,rules('ai-process-surge.list')), path)

if __name__ == '__main__':unittest.main()
