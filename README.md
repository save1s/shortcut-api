# save1s 捷径服务后端api
为 https://shortcuts.save1s.com 中提供的捷径提供api服务。

## 部署情况
目前master分支已部署在 leancloud 的云引擎上，每次push都会 通过 webhook 触发一次部署。 

服务部署地址： https://shortcut-api.leanapp.cn

## 安全性与隐私
要实现一些服务必须获取你的账号密码，所以我们做了以下努力来确保服务的安全，以减少你的顾虑：

1. 接口使用 https POST 方法提供服务。
2. 程序不打印与你上传信息有关的任何日志，也不储存你上传的任何信息。
3. 服务部署在 leancloud，leancloud 的访问日志不会记录你 POST 的信息。

如果你仍然有所顾虑，你可以自行部署这个服务，然后在捷径中修改服务地址即可。
