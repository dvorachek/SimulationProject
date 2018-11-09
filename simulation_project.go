package main

import (
	"fmt"
	"time"
)

var toRouter = make(chan int, 1000)
var highQ = make(chan int, 1000)
var lowQ = make(chan int, 1000)
var toDest = make(chan int, 1000)

var currentSeq = -1

// Need to add a system clock.. maybe in the form of a channel which can broadcast to all routines?

// Need to pass this instead of incremental ints from source
type Event struct {
	id   int
	data string // Can change type to whatever we want for the payload
}

// Constructor for event
func makeEvent(id int, data string) *Event {
	ev := &Event{id, data}
	return ev
}

func source() {
	for i := 0; i < 1000; i++ {
		toRouter <- i
		fmt.Println("Source sent ", i)
	}
}

func routerSwitch() {
	for {
		x := <-toRouter
		if x < currentSeq {
			highQ <- x
		} else {
			currentSeq = x
			lowQ <- x
		}
	}
}

func router() {

	// Need to change so that it prioritizes highQ

	for {
		select {
		case x := <-highQ:
			toDest <- x
		case x := <-lowQ:
			toDest <- x
		}
	}
}

func destination() {
	for {
		item := <-toDest
		fmt.Println("Destination received: ", item)
	}
}

func main() {
	go source()
	go routerSwitch()
	go router()
	go destination()

	time.Sleep(time.Second * 5)
}
