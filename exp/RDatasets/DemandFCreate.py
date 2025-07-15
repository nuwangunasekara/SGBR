import csv
from datetime import datetime

def process_week(week_str):
    """Convert 'YY/MM/DD' to year and week number"""
    date_obj = datetime.strptime(week_str, '%d/%m/%y')
    year = date_obj.year
    week_num = date_obj.isocalendar()[1]
    return year, week_num

def process_file(input_file, output_file):
    # First pass: find min and max year
    years = set()
    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)
        next(reader)  # skip header
        for row in reader:
            week_str = row[1]
            year, _ = process_week(week_str)
            years.add(year)

    min_year = min(years)
    max_year = max(years)

    # Second pass: process data with normalization
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Process header
        headers = next(reader)
        new_headers = headers[2:]
        new_headers.insert(0, 'week_number')
        new_headers.insert(0, 'normalized_year')
        writer.writerow(new_headers)

        # Process rows
        for row in reader:
            record_id, week, *rest = row
            year, week_num = process_week(week)
            # Normalize year between 0 and 1
            normalized_year = (year - min_year) / (max_year - min_year)

            # Add prefixes to store_id and sku_id
            new_row = [normalized_year, week_num]
            for i, value in enumerate(rest):
                if i == 0:  # store_id field
                    new_row.append(f"store_id_{value}")
                elif i == 1:  # sku_id field
                    new_row.append(f"sku_id_{value}")
                else:
                    new_row.append(value)

            writer.writerow(new_row)

    print(f"Year normalized between {min_year} (0) and {max_year} (1)")

# Example usage:
input_filename = 'DemandF_RAW.csv'
output_filename = 'DemandF.csv'
process_file(input_filename, output_filename)