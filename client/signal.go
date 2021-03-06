// +build linux darwin freebsd

package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	kcp "github.com/wwqk4444/kcp-go"
)

func init() {
	go sigHandler()
}

func sigHandler() {
	ch := make(chan os.Signal, 1)
	signal.Notify(ch, syscall.SIGUSR1)

	for {
		switch <-ch {
		case syscall.SIGUSR1:
			log.Printf("KCP SNMP:%+v", kcp.DefaultSnmp.Copy())
		}
	}
}
