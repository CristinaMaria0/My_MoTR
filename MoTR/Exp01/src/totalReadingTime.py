import csv

# Path to the CSV file
csv_file_path = r"..\outputs\initial_data_fromExp01.csv"

new_csv_file_path = r"..\outputs\initial_data_fromExp01_02.csv"

# Open and read the CSV file
with open(csv_file_path, mode='r', newline='') as csvfile:
    csvreader = csv.reader(csvfile)
    # Read the header
    header = next(csvreader)

    # Add the new column to the header
    header.insert(0, 'totalReadingTime')
    # Read the rest of the data
    rows = [row for row in csvreader]
    # Find the index of the columns we need
    index_index = header.index("Index")   
    response_time_index = header.index("responseTime")  
    for row in rows:
        if row[index_index] == -1:
            row.insert(0, "NA")  # Add "NA" in totalReadingTime
        else:
            row.insert(0, 0)  # Default placeholder value
    # print(header)
    total_reading_time = {}
    current_index = None
    start_time = None
    last_cuv = 0
    # Iterate through rows to compute total reading time
    for i, row in enumerate(rows):
        index = row[index_index]
        if index != 'NA':
            try:
                response_time = int(row[response_time_index])
            except ValueError:
                response_time = 0  # or handle it in a way that suits your needs
        if index == "-1":  # NA rows within sentence
            last_cuv=i
            continue
        elif index =='NA': # NA rows between sentences
            if current_index is not None and start_time is not None:
                rows[last_cuv][0] = str(response_time - start_time)
            current_index = None
            start_time = None

        elif index != current_index:  # New word starts
            if current_index is not None and start_time is not None:
                total_reading_time[current_index] = response_time - start_time
                rows[i-1][0] = str(total_reading_time[current_index])
            current_index = index
            start_time = response_time
    # Write the updated data back to the CSV file
    with open(new_csv_file_path, mode='w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
        csvwriter.writerows(rows)