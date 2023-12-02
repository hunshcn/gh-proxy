
<!DOCTYPE html>
<html lang="zh-Hans">
<style>
    html, body {
        width: 100%;
        margin: 0;
    }

    html {
        height: 100%;
    }

    body {
        min-height: 100%;
        padding: 20px;
        box-sizing: border-box;
    }

    p {
        word-break: break-all;
    }

    @media (max-width: 500px) {
        h1 {
            margin-top: 80px;
        }
    }

    .flex {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .block {
        display: block;
        position: relative;
    }

    .url {
        font-size: 18px;
        padding: 10px 10px 10px 5px;
        position: relative;
        width: 300px;
        border: none;
        border-bottom: 1px solid #bfbfbf;
    }

    input:focus {
        outline: none;
    }

    .bar {
        content: '';
        height: 2px;
        width: 100%;
        bottom: 0;
        position: absolute;
        background: #00bfb3;
        transition: 0.2s ease transform;
        -moz-transition: 0.2s ease transform;
        -webkit-transition: 0.2s ease transform;
        transform: scaleX(0);
    }

    .url:focus ~ .bar {
        transform: scaleX(1);
    }

    .btn {
        line-height: 38px;
        background-color: #00bfb3;
        color: #fff;
        white-space: nowrap;
        text-align: center;
        font-size: 14px;
        border: none;
        border-radius: 2px;
        cursor: pointer;
        padding: 5px;
        width: 160px;
        margin: 30px 0;
    }

    .tips, .example {
        color: #7b7b7b;
        position: relative;
        align-self: flex-start;
        margin-left: 7.5em;
    }

    .tips > p:first-child::before {
        position: absolute;
        left: -3em;
        content: 'PS：';
        color: #7b7b7b
    }

    .example > p:first-child::before {
        position: absolute;
        left: -7.5em;
        content: '合法输入示例：';
        color: #7b7b7b
    }
</style>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <script>
        function toSubmit(e) {
            e.preventDefault()
            window.open(location.href.substr(0, location.href.lastIndexOf('/') + 1) + document.getElementsByName('q')[0].value);
            return false
        }
    </script>
    <title>GitHub 文件加速</title>
</head>
<body class="flex">
<a style="position: absolute;top: 0;right: 0;" href="https://github.com/hunshcn/gh-proxy"><img width="149" height="149" referrerPolicy="no-referrer"
                                                                                               src="https://inews.gtimg.com/newsapp_ls/0/12025455907/0"
                                                                                               alt="Fork me on GitHub"
                                                                                               data-recalc-dims="1"></a>
<h1 style="margin-bottom: 50px">GitHub 文件加速</h1>
<form action="./" method="get" style="padding-bottom: 40px" target="_blank" class="flex" onsubmit="toSubmit(event)">
    <label class="block" style="width: fit-content">
        <input class="block url" name="q" type="text" placeholder="键入Github文件链接"
               pattern="^((https|http):\/\/)?(github\.com\/.+?\/.+?\/(?:releases|archive|blob|raw|suites)|((?:raw|gist)\.(?:githubusercontent|github)\.com))\/.+$" required>
        <div class="bar"></div>
    </label>
    <input class="block btn" type="submit" value="下载">
    <div class="tips"><p>GitHub文件链接带不带协议头都可以，支持release、archive以及文件，右键复制出来的链接都是符合标准的，更多用法、clone加速请参考<a href="https://hunsh.net/archives/23/">这篇文章</a>。</p>
        <p>release、archive使用cf加速，文件会跳转至JsDelivr</p>
        <p>注意，不支持项目文件夹</p></div>
    <div class="example">
        <p>分支源码：https://github.com/hunshcn/project/archive/master.zip</p>
        <p>release源码：https://github.com/hunshcn/project/archive/v0.1.0.tar.gz</p>
        <p>release文件：https://github.com/hunshcn/project/releases/download/v0.1.0/example.zip</p>
        <p>分支文件：https://github.com/hunshcn/project/blob/master/filename</p>
    </div>
</form>
<p style="position: sticky;top: calc(100% - 2.5em);">项目基于Cloudflare Workers，开源于GitHub <a style="color: #3294ea"
                                                                                         href="https://github.com/hunshcn/gh-proxy">hunshcn/gh-proxy</a>
</p>
</body>
</html>
