# 关于这个本地副本的说明

本目录是 `github.com/wwqk4444/kcp-go` 的源码副本,主模块通过 `replace` 指向这里
(见仓库根目录 `go.mod`)。

为什么不用上游模块直接依赖:

- `github.com/wwqk4444/kcp-go` 当前 HEAD 的 `go.mod` 缺少 `module` 声明行
  (提交 `2335925` 将其删除),模块模式下无法作为依赖被拉取;
- 紧接着的提交 `49f303d` 又把旧版 `sess.go`/`crypt.go` 等文件覆盖回 2021 年的
  代码树上,`UDPSession.readLoop` 在 `sess.go` 与 `readloop_linux.go` /
  `readloop_generic.go` 中重复定义,HEAD 本身也无法编译。

因此这里收录的是该 fork 在改乱之前的最后一个完整提交
`bd59cf8` (2021-10-22,对应上游 `github.com/xtaci/kcp-go` v5.6.1 之后的主线),
仅做了如下整理,协议与 API 未改动:

- `go.mod` 的模块路径修正为 `github.com/wwqk4444/kcp-go`,
  `go` 版本与依赖做了精简(去掉仅开发用的 avo/x/tools 等);
- 删除了 `examples/`、`wireshark/`、图片与 `*_test.go` 测试文件,
  以缩减依赖面(测试源码仍可在上游仓库对应提交处获取)。

原始代码版权与许可见同目录 `LICENSE` (MIT, Copyright (c) 2016 xtaci)。

若上游 `github.com/wwqk4444/kcp-go` 修复了 `go.mod`,可直接删除根 `go.mod`
中的 `replace` 行及本目录,改为正常版本依赖。
