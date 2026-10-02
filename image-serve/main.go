package main

import (
	"flag"
	"log"
	"net/http"
	"os"
	"path/filepath"
)

var imagePath = flag.String("image_path", "/data/images/", "image path")

// ServeFile serves files by the "image" parameter returning it as image
func ServeFile(w http.ResponseWriter, r *http.Request) {
	image := r.URL.Query().Get("image")
	log.Printf("Serving file %s", image)
	if image == "" {
		http.Error(w, "No image specified", http.StatusBadRequest)
		return
	}
	fileName := filepath.Join(*imagePath, image)
	file, err := os.Open(fileName)

	if err != nil {
		log.Print("error opening file: ", err)
		http.Error(w, "cannon serve file " + fileName, http.StatusNotFound)
		return
	}
	defer file.Close()
	st, err := file.Stat()
	if err != nil {
		log.Print("stat file error: ", err)
		http.Error(w, "cannon serve file" + fileName, http.StatusNotFound)
		return
	}
	http.ServeContent(w, r, fileName, st.ModTime(), file)
}

func main() {
	flag.Parse()
	http.HandleFunc("/", ServeFile)

	port := "18080"
	log.Printf("Server starting on port %s...", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
