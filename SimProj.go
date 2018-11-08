package main

import (
	"fmt"
	//"time"
)


func source(chan int toRouter){
    for i := 0; i < 1000; i++ {
        toRouter <- i
    }
}

func routerSwitch(chan int toRouter, chan int highQ, chan int lowQ, int currentSeq){

    for {
        x := <- toRouter
        if x < currentSeq {
            highQ <- x
        } else {
            currentSeq = x
            lowQ <- x
        }
    }
}

func router(chan int highQ, chan int lowQ, chan int toDest){
    select {
    case x := <- highQ:
        toDest <- x
    case x := <- lowQ:
        toDest <- x
    }
}

func destination(chan int toDest){

    for {
        item := <- toDest
        fmt.Println("%d", item)
    }
}


func main(){
    toRouter := make(chan int)
    highQ := make(chan int)
    lowQ := make(chan int)
    toDest := make(chan int)
    currentSeq := 0
    fmt.Println("Hello")
}
