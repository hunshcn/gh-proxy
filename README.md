# gh-proxy
## 简介

利用Cloudflare Workers对github release、archive以及项目文件进行加速，部署无需服务器且自带cdn。

## 使用

直接在copy出来的url前加`https://shrill-pond-3e81.hunsh.workers.dev/`即可

也可以直接访问，在input输入

注意，如果是项目文件会302到jsdeliver，由国内加速会更快。

***大量使用请自行部署，以上域名仅为演示使用。***

以下都是合法输入：

 - 分支源码：https://github.com/hunshcn/project/archive/master.zip
   
 - release源码：https://github.com/hunshcn/project/archive/v0.1.0.tar.gz
   
 - release文件：https://github.com/hunshcn/project/releases/download/v0.1.0/example.zip
   
 - 分支文件：https://github.com/hunshcn/project/blob/master/filename

 - commit文件：https://github.com/hunshcn/project/blob/1111111111111111111111111111/filename

## 部署

首页：https://workers.cloudflare.com

注册，登陆，`Start building`，取一个子域名，`Create a Worker`。

复制 [index.js](https://cdn.jsdeliver.net/hunshcn/gh-proxy@master/index.js) 到左侧代码框，`Save and deploy`。如果正常，右侧应显示首页。

## 计费

到 `overview` 页面可参看使用情况。免费版每天有 10 万次免费请求，并且有每分钟1000次请求的限制。

如果不够用，可升级到 $5 的高级版本，每月可用 1000 万次请求（超出部分 $0.5/百万次请求）。

## 链接

[我的博客](https://hunsh.net)

## 参考

[jsproxy](https://github.com/EtherDream/jsproxy/)
