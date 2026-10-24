module github.com/wwqk4444/1

go 1.20

require (
	github.com/golang/snappy v0.0.4
	github.com/pkg/errors v0.9.1
	github.com/urfave/cli v1.22.14
	github.com/wwqk4444/kcp-go v0.0.0
	github.com/wwqk4444/kcp-go-raw v0.0.0-20231113125243-ba212e783e62
	github.com/xtaci/smux v1.5.15
	golang.org/x/crypto v0.0.0-20200728195943-123391ffb6de
)

require (
	github.com/bits-and-blooms/bitset v1.10.0 // indirect
	github.com/cpuguy83/go-md2man/v2 v2.0.2 // indirect
	github.com/google/gopacket v1.1.19 // indirect
	github.com/klauspost/cpuid v1.3.1 // indirect
	github.com/klauspost/reedsolomon v1.9.9 // indirect
	github.com/mmcloughlin/avo v0.0.0-20200803215136-443f81d77104 // indirect
	github.com/russross/blackfriday/v2 v2.1.0 // indirect
	github.com/templexxx/cpu v0.0.8 // indirect
	github.com/templexxx/xorsimd v0.4.1 // indirect
	github.com/tjfoc/gmsm v1.3.2 // indirect
	github.com/wwqk4444/ccsexyz_utils v0.0.0-20231106154748-52d06de3e032 // indirect
	github.com/wwqk4444/mulcon v0.0.0-20220211043402-b9ad835afbe4 // indirect
	github.com/wwqk4444/rawcon v0.0.0-20231113130443-2f74ef949979 // indirect
	gitlab.com/yawning/chacha20.git v0.0.0-20230427033715-7877545b1b37 // indirect
	golang.org/x/net v0.0.0-20200707034311-ab3426394381 // indirect
	golang.org/x/sys v0.0.0-20200808120158-1030fc2bf1d9 // indirect
	golang.org/x/tools v0.0.0-20200425043458-8463f397d07c // indirect
	golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543 // indirect
)

// github.com/wwqk4444/kcp-go 上游仓库的 go.mod 缺少 module 声明且 HEAD
// 代码无法编译,临时使用仓库内的本地副本,详见 third_party/kcp-go/NOTICE.md
replace github.com/wwqk4444/kcp-go => ./third_party/kcp-go
