import functools
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from http.server import ThreadingHTTPServer

import app


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        Path(cls.temp.name, '.env').write_text('TEST_ONLY=fixture', encoding='utf-8')
        handler = functools.partial(app.Handler, directory=cls.temp.name)
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temp.cleanup()

    def request(self, method, path, payload=None):
        connection = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        body = json.dumps(payload) if payload is not None else None
        connection.request(method, path, body, {'Content-Type': 'application/json'})
        response = connection.getresponse()
        result = response.status, response.read()
        connection.close()
        return result

    def test_fake_cycle_never_calls_model_api(self):
        with patch.dict(os.environ, {'USE_FAKE_DATA': 'true'}), patch.object(
            app, '_call_openai', side_effect=AssertionError('fixture mode called model API')
        ):
            status, body = self.request('POST', '/api/llm', {
                'mode': 'sim_builder', 'userPrompt': 'Create a flower',
                'simulationCaseType': 'adversarial',
            })
            self.assertEqual(status, 200)
            generated = json.loads(json.loads(body)['raw_text'])
            self.assertTrue(generated['ground_truth']['should_be_flagged'])
            status, body = self.request('POST', '/api/llm', {
                'mode': 'sim_inspector', 'userPrompt': 'Create a flower',
                'generatedCode': generated['html'], 'simulationCaseType': 'adversarial',
            })
            self.assertEqual(status, 200)
            self.assertTrue(json.loads(body)['data']['detected'])

    def test_invalid_input_is_rejected_before_api(self):
        with patch.object(app, '_call_openai', side_effect=AssertionError('unexpected API call')):
            self.assertEqual(self.request('POST', '/api/llm', {'mode': 'builder'})[0], 400)

    def test_malformed_model_inspector_json_has_explicit_parse_failure(self):
        with patch.dict(os.environ, {'USE_FAKE_DATA': 'false', 'OPENAI_API_KEY': 'test-only'}), \
             patch.object(app, '_call_openai', return_value='invalid JSON'):
            status, body = self.request('POST', '/api/llm', {
                'mode': 'sim_inspector', 'userPrompt': 'Create a flower',
                'generatedCode': '<html></html>',
            })
            self.assertEqual(status, 200)
            self.assertTrue(json.loads(body)['parse_failed'])

    def test_private_static_files_are_not_served(self):
        for path in ['/.env', '/%2eenv', '/.git/config']:
            self.assertEqual(self.request('GET', path)[0], 404)

    def test_methodology_matches_fifty_run_plan(self):
        status, body = self.request('GET', '/api/methodology')
        self.assertEqual(status, 200)
        pairs = json.loads(body)['data']['models_used']['pairs']
        self.assertEqual(sum(pair['runs'] for pair in pairs), 50)


if __name__ == '__main__':
    unittest.main()
