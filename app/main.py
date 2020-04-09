# -*- coding: utf-8 -*-
import re

import requests
from flask import Flask, Response, redirect, request

# config
# git使用cnpmjs镜像、分支文件使用jsDelivr镜像的开关，0为关闭，默认开启
jsdelivr = 1
cnpmjs = 1
HOST = '127.0.0.1'  # 监听地址，建议监听本地然后由web服务器反代
PORT = 80  # 监听端口
ASSET_URL = 'https://hunshcn.github.io/gh-proxy'  # 主页

app = Flask(__name__)
app.debug = True
CHUNK_SIZE = 1024 * 10
index_html = requests.get(ASSET_URL, timeout=10).text
exp1 = re.compile(r'^(?:https?:\/\/)?github\.com\/.+?\/.+?\/(?:releases|archive)\/.*$')
exp2 = re.compile(r'^(?:https?:\/\/)?github\.com\/.+?\/.+?\/(?:blob)\/.*$')
exp3 = re.compile(r'^(?:https?:\/\/)?github\.com\/.+?\/.+?\/(?:info|git-upload-pack).*$')


@app.route('/')
def index():
    if 'q' in request.args:
        return redirect('/' + request.args.get('q'))
    return index_html


@app.route('/<path:u>')
def proxy(u):
    u = u if u.startswith('http') else 'https://' + u
    u = u.replace(':/g', '://g', 1)  # uwsgi会将//传递为/
    if jsdelivr and exp2.match(u):
        u = u.replace('/blob/', '@').replace('github.com', 'cdn.jsdelivr.net/gh')
        return redirect(u)
    elif cnpmjs and exp3.match(u):
        u = u.replace('github.com', 'github.com.cnpmjs.org') + request.url.replace(request.base_url, '')
        return redirect(u)
    # elif exp1.match(u):
    else:
        headers = {}
        r_headers = {}
        for i in ['Range', 'User-Agent']:
            if i in request.headers:
                r_headers[i] = request.headers.get(i)
        try:
            r = requests.get(u, headers=r_headers, stream=True)
            for i in ['Content-Type']:
                if i in r.headers:
                    headers[i] = r.headers.get(i)
            if r.status_code == 200:
                headers = dict(r.headers)

            def generate():
                for chunk in r.iter_content(chunk_size=CHUNK_SIZE):
                    yield chunk

            return Response(generate(), headers=headers, status=r.status_code)
        except Exception as e:
            headers['content-type'] = 'text/html; charset=UTF-8'
            return Response('server error' + str(e), status=500, headers=headers)
    # else:
    #     return Response('Illegal input', status=403, mimetype='text/html; charset=UTF-8')


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
