package main

import (
	"crypto/sha256"
	"encoding/csv"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"strings"
	"time"
	"unicode/utf8"
)

// CleanedRecord adalah struktur data hasil validasi yang siap dilabeli.
// Field "Hash" dipakai untuk deteksi duplikat, "Source" untuk lacak asal data.
type CleanedRecord struct {
	ID         string    `json:"id"`
	Text       string    `json:"text"`
	Source     string    `json:"source"`
	Hash       string    `json:"hash"`
	IngestedAt time.Time `json:"ingested_at"`
}

// ValidationStats merekap berapa banyak baris yang lolos/gagal dan kenapa.
// Ini penting untuk laporan kualitas data di README nanti.
type ValidationStats struct {
	TotalRows       int `json:"total_rows"`
	Empty           int `json:"rejected_empty"`
	TooShort        int `json:"rejected_too_short"`
	TooLong         int `json:"rejected_too_long"`
	InvalidEncoding int `json:"rejected_invalid_encoding"`
	Duplicate       int `json:"rejected_duplicate"`
	Accepted        int `json:"accepted"`
}

const (
	minTextLength = 5   // pesan lebih pendek dari ini biasanya noise
	maxTextLength = 500 // batas wajar untuk SMS/chat
)

func main() {
	inputPath := flag.String("input", "data/raw/raw_sms.csv", "path ke file CSV mentah")
	outputPath := flag.String("output", "data/processed/cleaned.jsonl", "path output JSONL bersih")
	sourceName := flag.String("source", "sms-dataset-v1", "label sumber data untuk tracing")
	flag.Parse()

	records, stats := ingestAndValidate(*inputPath, *sourceName)

	if err := writeJSONL(*outputPath, records); err != nil {
		log.Fatalf("gagal menulis output: %v", err)
	}

	printReport(stats)
}

// ingestAndValidate membaca CSV, menjalankan validasi per baris, dan
// mengembalikan data yang lolos beserta statistiknya.
func ingestAndValidate(path, source string) ([]CleanedRecord, ValidationStats) {
	f, err := os.Open(path)
	if err != nil {
		log.Fatalf("gagal buka file input: %v", err)
	}
	defer f.Close()

	reader := csv.NewReader(f)
	reader.FieldsPerRecord = -1 // toleransi jumlah kolom tidak seragam

	header, err := reader.Read()
	if err != nil {
		log.Fatalf("gagal baca header: %v", err)
	}
	textColIdx := findColumnIndex(header, "text")
	if textColIdx == -1 {
		log.Fatalf("kolom 'text' tidak ditemukan di header: %v", header)
	}

	seenHashes := make(map[string]bool)
	var results []CleanedRecord
	stats := ValidationStats{}

	rowNum := 0
	for {
		row, err := reader.Read()
		if err != nil {
			break // EOF atau selesai
		}
		rowNum++
		stats.TotalRows++

		if textColIdx >= len(row) {
			stats.Empty++
			continue
		}
		text := strings.TrimSpace(row[textColIdx])

		// Validasi 1: kosong
		if text == "" {
			stats.Empty++
			continue
		}
		// Validasi 2: encoding tidak valid (bukan UTF-8 yang benar)
		if !utf8.ValidString(text) {
			stats.InvalidEncoding++
			continue
		}
		// Validasi 3: terlalu pendek
		if utf8.RuneCountInString(text) < minTextLength {
			stats.TooShort++
			continue
		}
		// Validasi 4: terlalu panjang (kemungkinan bukan SMS/chat wajar)
		if utf8.RuneCountInString(text) > maxTextLength {
			stats.TooLong++
			continue
		}
		// Validasi 5: duplikat (berdasarkan hash isi teks)
		hash := hashText(text)
		if seenHashes[hash] {
			stats.Duplicate++
			continue
		}
		seenHashes[hash] = true

		results = append(results, CleanedRecord{
			ID:         fmt.Sprintf("%s-%06d", source, rowNum),
			Text:       text,
			Source:     source,
			Hash:       hash,
			IngestedAt: time.Now().UTC(),
		})
		stats.Accepted++
	}

	return results, stats
}

func findColumnIndex(header []string, name string) int {
	for i, h := range header {
		if strings.EqualFold(strings.TrimSpace(h), name) {
			return i
		}
	}
	return -1
}

func hashText(text string) string {
	sum := sha256.Sum256([]byte(strings.ToLower(strings.TrimSpace(text))))
	return hex.EncodeToString(sum[:])[:16]
}

func writeJSONL(path string, records []CleanedRecord) error {
	if err := os.MkdirAll(dirOf(path), 0755); err != nil {
		return err
	}
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()

	enc := json.NewEncoder(f)
	for _, r := range records {
		if err := enc.Encode(r); err != nil {
			return err
		}
	}
	return nil
}

func dirOf(path string) string {
	idx := strings.LastIndex(path, "/")
	if idx == -1 {
		return "."
	}
	return path[:idx]
}

func printReport(s ValidationStats) {
	fmt.Println("=== Ingestion & Validation Report ===")
	fmt.Printf("Total baris dibaca      : %d\n", s.TotalRows)
	fmt.Printf("Ditolak (kosong)        : %d\n", s.Empty)
	fmt.Printf("Ditolak (terlalu pendek): %d\n", s.TooShort)
	fmt.Printf("Ditolak (terlalu panjang): %d\n", s.TooLong)
	fmt.Printf("Ditolak (encoding rusak): %d\n", s.InvalidEncoding)
	fmt.Printf("Ditolak (duplikat)      : %d\n", s.Duplicate)
	fmt.Printf("Diterima (bersih)       : %d\n", s.Accepted)
}
