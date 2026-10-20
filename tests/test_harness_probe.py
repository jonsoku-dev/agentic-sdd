from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import harness_probe as hp

REPO = Path(__file__).resolve().parents[1]


def fake_plugin(root: Path, version: str, skills: list[str], manifest: str = '.claude-plugin/plugin.json'):
    (root / manifest).parent.mkdir(parents=True, exist_ok=True)
    (root / manifest).write_text(json.dumps({'name': 'pstack', 'version': version}))
    for s in skills:
        (root / 'skills' / s).mkdir(parents=True)
        (root / 'skills' / s / 'SKILL.md').write_text(f'---\nname: {s}\n---\n')


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / 'home'
        self.project = Path(self.tmp.name) / 'proj'
        self.project.mkdir(parents=True)
        self.home.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def test_highest_version_wins_and_core_is_checked(self):
        old = self.home / '.claude/plugins/cache/pstack-claude/pstack/0.9.1'
        new = self.home / '.claude/plugins/cache/pstack-claude/pstack/0.9.10'
        fake_plugin(old, '0.9.1', list(hp.COMMON_CORE))
        fake_plugin(new, '0.9.10', [s for s in hp.COMMON_CORE if s != 'interrogate'])
        out = hp.probe(self.home, self.project, 'claude')
        self.assertEqual(out['pstack_version'], '0.9.10')
        self.assertEqual(out['missing_common_core'], ['interrogate'])
        self.assertFalse(out['layers']['L2']['ok'])
        self.assertFalse(out['layers']['L5']['ok'])
        self.assertEqual(out['breadcrumbs'][0], 'pstack: 0.9.10|claude')

    def test_unavailable_host_records_breadcrumb(self):
        out = hp.probe(self.home, self.project, 'codex')
        self.assertIsNone(out['pstack_root'])
        self.assertEqual(out['breadcrumbs'][0], 'pstack: unavailable|codex')
        self.assertIn('L2 gap', out['breadcrumbs'][1])

    def test_grok_falls_back_to_claude_plugin(self):
        fake_plugin(self.home / '.claude/plugins/marketplaces/pstack-claude/plugins/pstack', '0.9.93', list(hp.COMMON_CORE))
        out = hp.probe(self.home, self.project, 'grok')
        self.assertEqual(out['pstack_version'], '0.9.93')
        self.assertTrue(out['layers']['L2']['ok'])

    def test_cursor_manifest_and_sheet(self):
        root = self.home / '.cursor/plugins/cache/cursor-public/pstack/abc'
        fake_plugin(root, '0.15.28', list(hp.COMMON_CORE), manifest='plugin.json')
        (self.home / '.cursor/rules').mkdir(parents=True)
        (self.home / '.cursor/rules/pstack-models.mdc').write_text('# budget\n')
        out = hp.probe(self.home, self.project, 'cursor')
        self.assertEqual(out['pstack_version'], '0.15.28')
        self.assertTrue(out['sheet_present'])

    def test_layer1_and_layer7_need_project_files(self):
        out = hp.probe(self.home, self.project, 'claude')
        self.assertFalse(out['layers']['L1']['ok'])
        self.assertFalse(out['layers']['L7']['ok'])
        (self.project / 'CLAUDE.md').write_text('# rules\n')
        (self.project / '.specify').mkdir()
        (self.project / 'progress.md').write_text('# Progress\n\n## Next action\nimplement T001\n')
        out = hp.probe(self.home, self.project, 'claude')
        self.assertTrue(out['layers']['L1']['ok'])
        self.assertTrue(out['layers']['L7']['ok'])

    def test_check_map_agrees_with_reference(self):
        problems = hp.check_map(REPO / 'references/pstack-integration.md', list(hp.COMMON_CORE))
        self.assertEqual(problems, [])

    def test_check_map_reports_missing_installed_skill(self):
        problems = hp.check_map(REPO / 'references/pstack-integration.md', ['poteto-mode'])
        self.assertTrue(any('lacks common-core skill `interrogate`' in p for p in problems))

    def test_cli_json_exit_codes(self):
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = hp.main(['--host', 'codex', '--home', str(self.home), '--project', str(self.project), '--json'])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(buf.getvalue())['host'], 'codex')


if __name__ == '__main__':
    unittest.main()
