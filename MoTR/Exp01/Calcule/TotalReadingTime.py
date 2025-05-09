import csv
import os
import pandas as pd

# Path to the folder containing CSV files
data_folder = r"d:/repos/My_MoTR/MoTR/Exp01/Calcule/data"
outputs_folder = r"d:/repos/My_MoTR/MoTR/Exp01/Calcule/outputs/"
# Iterate through all CSV files in the folder
for file_name in os.listdir(data_folder):
    
    # Path to the current CSV file
    csv_file_path = os.path.join(data_folder, file_name)
    print(f"Processing file: {csv_file_path}")
    # Extract the word from the file name that stops at the first '.' or '_'
    file_name = os.path.basename(csv_file_path)
    word = file_name.split('.')[0].split('_')[0]
    new_csv_file_path = os.path.join(os.path.dirname(outputs_folder), f"{word}_02.csv")
    csv_intermediar = os.path.join(os.path.dirname(outputs_folder), f"{word}_intermediar.csv")
    final_readingTime = os.path.join(os.path.dirname(outputs_folder), f"{word}_totalReadingTime.csv")

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
            true_ans=row[header.index("TrueAnswer")]
            word=row[header.index("Word")]
            if index != 'NA':
                try:
                    if word != "":
                        # print (f"Row {i} has an invalid word: {word}")
                        response_time = int(row[response_time_index])
                except ValueError:
                    response_time = 0  # or handle it in a way that suits your needs

            if index == "-1":  # NA rows within sentence
                last_cuv=i
                continue
            elif index =='NA' : # NA rows between sentences
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
        
    # Încarcă fișierul CSV original
    df = pd.read_csv(new_csv_file_path)
    saved_word = None
    saved_index = None
    saved_prop_index = None
    for index, row in df.iterrows():
        if row['totalReadingTime'] == 0 and saved_word is None and row['Index']!= -1:
            # Dacă totalReadingTime este 0, salvează cuvântul și indexul
            saved_word = row['Word']
            saved_index = row['Index']
            saved_prop_index = row['sentenceIndex']
        elif row['totalReadingTime'] == 0 and index != saved_index:
            df.at[index, 'Word'] = saved_word
            df.at[index, 'Index'] = saved_index
            df.at[index, 'sentenceIndex'] = saved_prop_index
        elif row['totalReadingTime'] != 0:
            if row['Index'] == -1:
                df.at[index, 'Word'] = saved_word
                df.at[index, 'Index'] = saved_index
                df.at[index, 'sentenceIndex'] =saved_prop_index
            saved_word= None
            saved_index = None
            saved_prop_index = None

    # Salvează modificările în același fișier CSV
    df = df[['sentenceIndex', 'totalReadingTime', 'Index', 'Word' ]]
    df.to_csv(csv_intermediar, index=False)

    # Filter rows where totalReadingTime > 0
    df_filtered = df[df['totalReadingTime'] > 0]

    # Save the filtered rows to another CSV file
    df_filtered.to_csv(final_readingTime, index=False)
    # print(f"Filtered CSV file saved as: {final_readingTime}")