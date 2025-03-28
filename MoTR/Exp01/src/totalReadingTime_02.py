import csv
import pandas as pd

# Path to the CSV file
csv_file_path = r"..\outputs\initial_data_fromExp01_02.csv"
csv_intermediar = r"..\outputs\date_intermediare_readingTime_fromExp01.csv"
final_readingTime=r"..\outputs\totalReadingTimeCuvinte_fromExp01.csv"
# Read the CSV file and write to a new CSV file with only the required columns
with open(csv_file_path, mode='r', newline='', encoding='utf-8') as infile, \
    open(csv_intermediar, mode='w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.DictReader(infile)
    fieldnames = ['totalReadingTime','Index', 'Word']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    
    writer.writeheader()
    for row in reader:
       writer.writerow({field: row[field] for field in fieldnames})


df = pd.read_csv(csv_intermediar)
current_word = None
for index, row in df.iterrows():
    if type(row['Word']) !=str:
        df.at[index, 'Word'] = current_word
        # print(f"Row {index} has been updated with {current_word}")
    else:
        current_word = row['Word']
df.to_csv(csv_intermediar, index=False)

#  Read the new CSV file and extract the totalReadingTime and Word columns

tdr = {}
final_df = pd.DataFrame(columns=['Word', 'totalReadingTime'])

for index, row in df.iterrows():
    if row['Index'] == 0:
        if tdr:  # Ensure `tdr` is not empty before appending
            temp_df = pd.DataFrame(list(tdr.items()), columns=['Word', 'totalReadingTime'])
            final_df = pd.concat([final_df, temp_df], ignore_index=True)
        tdr = {}  # Reset dictionary

    if row['totalReadingTime'] > 0:
        tdr[row['Word']] = row['totalReadingTime']

# Append the last collected words
if tdr:
    temp_df = pd.DataFrame(list(tdr.items()), columns=['Word', 'totalReadingTime'])
    final_df = pd.concat([final_df, temp_df], ignore_index=True)

# Save to CSV
final_df.to_csv(final_readingTime, index=False)