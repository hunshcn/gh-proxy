# -*- coding: utf-8 -*-
import re

import requests
from flask import Flask, Response, redirect, request
from requests.exceptions import (
    ChunkedEncodingError,
    ContentDecodingError, ConnectionError, StreamConsumedError)
from requests.utils import (
    stream_decode_response_unicode, iter_slices)
from urllib3.exceptions import (
    DecodeError, ReadTimeoutError, ProtocolError)

# config
# git使用cnpmjs镜像、分支文件使用jsDelivr镜像的开关，0为关闭，默认关闭
jsdelivr = 0
cnpmjs = 0
size_limit = 1024 * 1024 * 1024 * 999  # 允许的文件大小，默认999GB，相当于无限制了 https://github.com/hunshcn/gh-proxy/issues/8
HOST = '127.0.0.1'  # 监听地址，建议监听本地然后由web服务器反代
PORT = 80  # 监听端口
ASSET_URL = 'https://hunshcn.github.io/gh-proxy'  # 主页

app = Flask(__name__)
CHUNK_SIZE = 1024 * 10
index_html = requests.get(ASSET_URL, timeout=10).text
icon_r = requests.get(ASSET_URL + '/favicon.ico', timeout=10).content
exp1 = re.compile(r'^(?:https?://)?github\.com/.+?/.+?/(?:releases|archive)/.*$')
exp2 = re.compile(r'^(?:https?://)?github\.com/.+?/.+?/(?:blob)/.*$')
exp3 = re.compile(r'^(?:https?://)?github\.com/.+?/.+?/(?:info|git-).*$')
exp4 = re.compile(r'^(?:https?://)?raw\.githubusercontent\.com/.+?/.+?/.+?/.+$')
exp5 = re.compile(r'^(?:https?://)?gist\.(?:githubusercontent|github)\.com/.+?/.+?/.+$')


@app.route('/')
def index():
    if 'q' in request.args:
        return redirect('/' + request.args.get('q'))
    return index_html


@app.route('/favicon.ico')
def icon():
    return Response(icon_r, content_type='image/vnd.microsoft.icon')


def iter_content(self, chunk_size=1, decode_unicode=False):
    """rewrite requests function, set decode_content with False"""

    def generate():
        # Special case for urllib3.
        if hasattr(self.raw, 'stream'):
            try:
                for chunk in self.raw.stream(chunk_size, decode_content=False):
                    yield chunk
            except ProtocolError as e:
                raise ChunkedEncodingError(e)
            except DecodeError as e:
                raise ContentDecodingError(e)
            except ReadTimeoutError as e:
                raise ConnectionError(e)
        else:
            # Standard file-like object.
            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        self._content_consumed = True

    if self._content_consumed and isinstance(self._content, bool):
        raise StreamConsumedError()
    elif chunk_size is not None and not isinstance(chunk_size, int):
        raise TypeError("chunk_size must be an int, it is instead a %s." % type(chunk_size))
    # simulate reading small chunks of the content
    reused_chunks = iter_slices(self._content, chunk_size)

    stream_chunks = generate()

    chunks = reused_chunks if self._content_consumed else stream_chunks

    if decode_unicode:
        chunks = stream_decode_response_unicode(chunks, self)

    return chunks


@app.route('/<path:u>', methods=['GET', 'POST'])
def proxy(u):
    u = u if u.startswith('http') else 'https://' + u
    u = u.replace('s:/', 's://', 1)  # uwsgi会将//传递为/
    if not any([i.match(u) for i in [exp1, exp2, exp3, exp4, exp5]]):
        return Response('Invalid input.', status=403)
    if jsdelivr and exp2.match(u):
        u = u.replace('/blob/', '@', 1).replace('github.com', 'cdn.jsdelivr.net/gh', 1)
        return redirect(u)
    elif cnpmjs and exp3.match(u):
        u = u.replace('github.com', 'github.com.cnpmjs.org', 1) + request.url.replace(request.base_url, '', 1)
        return redirect(u)
    elif jsdelivr and exp4.match(u):
        u = re.sub(r'(\.com/.*?/.+?)/(.+?/)', r'\1@\2', u, 1)
        u = u.replace('raw.githubusercontent.com', 'cdn.jsdelivr.net/gh', 1)
        return redirect(u)
    else:
        if exp2.match(u):
            u = u.replace('/blob/', '/raw/', 1)
        headers = {}
        r_headers = dict(request.headers)
        if 'Host' in r_headers:
            r_headers.pop('Host')
        r_headers['Accept-Encoding'] = request.headers.get('Accept-Encoding', 'identity')
        try:
            url = u + request.url.replace(request.base_url, '', 1)
            if url.startswith('https:/') and not url.startswith('https://'):
                url = 'https://' + url[7:]
            r = requests.request(method=request.method, url=url, data=request.data, headers=r_headers, stream=True)
            headers = dict(r.headers)

            if 'Content-length' in r.headers and int(r.headers['Content-length']) > size_limit:
                return redirect(u + request.url.replace(request.base_url, '', 1))

            def generate():
                for chunk in iter_content(r, chunk_size=CHUNK_SIZE):
                    yield chunk

            return Response(generate(), headers=headers, status=r.status_code)
        except Exception as e:
            headers['content-type'] = 'text/html; charset=UTF-8'
            return Response('server error ' + str(e), status=500, headers=headers)
    # else:
    #     return Response('Illegal input', status=403, mimetype='text/html; charset=UTF-8')


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
