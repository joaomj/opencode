#!/usr/bin/env python3
import unittest
import subprocess
import json
import sys
import os
import tempfile

TOOLS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HAS_BRAVE = False

def run_tool(name, *args, timeout=15):
    path = os.path.join(TOOLS_DIR, name)
    cmd = [sys.executable, path] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return result

def skip_unless_brave():
    result = run_tool('brave-connect', '--port', '9222', timeout=5)
    return result.returncode == 0


@unittest.skipIf(not skip_unless_brave(), 'Brave not running on port 9222')
class TestBraveConnect(unittest.TestCase):
    def test_connect_success(self):
        result = run_tool('brave-connect', '--port', '9222')
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertTrue(data['connected'])
        self.assertGreater(len(data['targets']), 0)
        self.assertIn('wsUrl', data)

    def test_connect_not_running(self):
        result = run_tool('brave-connect', '--port', '9999')
        self.assertNotEqual(result.returncode, 0)

    def test_json_output(self):
        result = run_tool('brave-connect', '--port', '9222')
        data = json.loads(result.stdout)
        self.assertIn('connected', data)


class TestBraveEvaluate(unittest.TestCase):
    @unittest.skipIf(not skip_unless_brave(), 'Brave not running')
    def test_evaluate_simple(self):
        result = run_tool('brave-evaluate', '1+1', '--port', '9222')
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn('result', data)
        self.assertEqual(data['result']['value'], 2)

    @unittest.skipIf(not skip_unless_brave(), 'Brave not running')
    def test_evaluate_string(self):
        result = run_tool('brave-evaluate', '"hello"', '--port', '9222')
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data['result']['value'], 'hello')

    def test_evaluate_no_expr(self):
        result = run_tool('brave-evaluate')
        self.assertNotEqual(result.returncode, 0)


class TestBraveScreenshot(unittest.TestCase):
    @unittest.skipIf(not skip_unless_brave(), 'Brave not running')
    def test_screenshot_png(self):
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            outpath = f.name
        try:
            result = run_tool('brave-screenshot', '--output', outpath, '--port', '9222')
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(outpath))
            self.assertGreater(os.path.getsize(outpath), 1000)
        finally:
            if os.path.exists(outpath):
                os.unlink(outpath)


class TestBraveDOM(unittest.TestCase):
    @unittest.skipIf(not skip_unless_brave(), 'Brave not running')
    def test_dom_outer_html(self):
        result = run_tool('brave-dom', '--outer-html', '--port', '9222')
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn('outerHTML', data)

    @unittest.skipIf(not skip_unless_brave(), 'Brave not running')
    def test_dom_tree(self):
        result = run_tool('brave-dom', '--tree', '--depth', '1', '--port', '9222')
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn('nodeName', data)


class TestBraveConsole(unittest.TestCase):
    @unittest.skipIf(not skip_unless_brave(), 'Brave not running')
    def test_console_clear(self):
        result = run_tool('brave-console', '--clear', '--port', '9222')
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertTrue(data.get('cleared'))

    @unittest.skipIf(not skip_unless_brave(), 'Brave not running')
    def test_console_get(self):
        result = run_tool('brave-console', '--get', '--port', '9222')
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, list)


class TestBraveNetwork(unittest.TestCase):
    @unittest.skipIf(not skip_unless_brave(), 'Brave not running')
    def test_network_enable(self):
        result = run_tool('brave-network', '--enable', '--port', '9222')
        self.assertEqual(result.returncode, 0)


class TestBraveNavigate(unittest.TestCase):
    @unittest.skipIf(not skip_unless_brave(), 'Brave not running')
    def test_navigate(self):
        result = run_tool('brave-navigate', 'https://example.com', '--port', '9222')
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn('frameId', data)

    def test_navigate_no_url(self):
        result = run_tool('brave-navigate')
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()