#!/bin/bash

# Find all subdirectories and process each
find "$1" -type d | while read -r dir; do
    # Find all CSV files in the current directory (non-recursively)
    csv_files=$(find "$dir" -maxdepth 1 -type f -name "*.csv")

    # Check if any CSV files are found
    if [ -n "$csv_files" ]; then
        echo "$dir:"
        total_lines=0

        # Loop through each CSV file
        while read -r csv; do
            lines=$(wc -l < "$csv")
            total_lines=$((total_lines + lines))
            echo "  $(basename "$csv"): $lines lines"
        done <<< "$csv_files"

        echo "  Total CSV files: $(echo "$csv_files" | wc -l)"
        echo "  Total lines in CSVs: $total_lines"
        echo
    fi
done

