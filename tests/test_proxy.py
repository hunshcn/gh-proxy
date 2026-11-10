import gzip
import io
import unittest
from unittest.mock import Mock, patch
from wsgiref.handlers import SimpleHandler

import requests
from urllib3.response import HTTPResponse
from werkzeug.test import EnvironBuilder


# Import without downloading the homepage or changing Requests' global defaults.
with patch('requests.get', return_value=Mock(text='', content=b'')), \
        patch('requests.sessions.default_headers'):
    from app.main import app


class ProxyResponseTests(unittest.TestCase):
    def upstream(self, body, headers, status=200):
        response = requests.Response()
        response.status_code = status
        response.headers.update(headers)
        response.raw = HTTPResponse(body=io.BytesIO(body), preload_content=False)
        self.addCleanup(response.close)
        return response

    def test_chunked_response_is_valid_wsgi(self):
        # Requests removes the HTTP chunk framing before the WSGI app sees it.
        # Forwarding Transfer-Encoding would make the WSGI server reject it.
        body = b'001e# service=git-upload-pack\n0000'
        for header in ('Transfer-Encoding', 'transfer-encoding', 'TRANSFER-ENCODING'):
            with self.subTest(header=header):
                upstream = self.upstream(body, {
                    header: 'chunked',
                    'Content-Type': 'application/x-git-upload-pack-advertisement',
                })
                environ = EnvironBuilder(
                    path='/https://github.com/owner/repo.git/info/refs',
                    query_string='service=git-upload-pack',
                ).get_environ()
                output, errors = io.BytesIO(), io.StringIO()
                handler = SimpleHandler(io.BytesIO(), output, errors, environ)
                with patch('requests.request', return_value=upstream):
                    handler.run(app)
                head, actual = output.getvalue().split(b'\r\n\r\n', 1)
                self.assertIn(b'200 OK', head, errors.getvalue())
                self.assertNotIn(b'transfer-encoding:', head.lower())
                self.assertIn(b'application/x-git-upload-pack-advertisement', head)
                self.assertEqual(actual, body)
                self.assertEqual(errors.getvalue(), '')

    def test_preserves_compressed_body_length_and_status(self):
        body = gzip.compress(b'binary git data\x00\xff')
        upstream = self.upstream(body, {
            'Content-Type': 'application/octet-stream',
            'Content-Encoding': 'gzip',
            'Content-Length': str(len(body)),
            'Content-Range': 'bytes 0-{}/1000'.format(len(body) - 1),
        }, status=206)
        with patch('requests.request', return_value=upstream):
            response = app.test_client().get(
                '/https://raw.githubusercontent.com/owner/repo/main/file.bin')
            self.assertEqual(response.status_code, 206)
            self.assertEqual(response.data, body)
            self.assertEqual(response.headers['Content-Length'], str(len(body)))
            self.assertEqual(response.headers['Content-Encoding'], 'gzip')
            self.assertEqual(response.headers['Content-Range'],
                             upstream.headers['Content-Range'])
            response.close()

    def test_git_post_keeps_request_body_and_query(self):
        upstream = self.upstream(b'pack data', {
            'Transfer-Encoding': 'chunked',
            'Content-Type': 'application/x-git-upload-pack-result',
        })
        with patch('requests.request', return_value=upstream) as send:
            response = app.test_client().post(
                '/https://github.com/owner/repo.git/git-upload-pack?key=value',
                data=b'git request\x00',
                content_type='application/x-git-upload-pack-request')
            self.assertEqual(response.data, b'pack data')
            self.assertNotIn('Transfer-Encoding', response.headers)
            self.assertEqual(send.call_args[1]['method'], 'POST')
            self.assertEqual(send.call_args[1]['data'], b'git request\x00')
            self.assertEqual(send.call_args[1]['url'],
                             'https://github.com/owner/repo.git/git-upload-pack?key=value')
            response.close()


if __name__ == '__main__':
    unittest.main()
