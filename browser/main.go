
package main

import (
	"log"

	"github.com/playwright-community/playwright-go"
)

func main() {
	playwright, err := playwright.Run()
	if err != nil {
		log.Fatalf("could not start playwright: %v", err)
	}

	browser, err := playwright.Chromium.ConnectOverCDP("http://localhost:9222")
	if err != nil {
		log.Fatalf("could not connect to browser: %v", err)
	}

	page, err := browser.NewPage()
	if err != nil {
		log.Fatalf("could not create page: %v", err)
	}

	if _, err = page.Goto("https://www.google.com"); err != nil {
		log.Fatalf("could not goto: %v", err)
	}

	log.Println(page.URL())

	if err = browser.Close(); err != nil {
		log.Fatalf("could not close browser: %v", err)
	}

	if err = playwright.Stop(); err != nil {
		log.Fatalf("could not stop Playwright: %v", err)
	}
}
