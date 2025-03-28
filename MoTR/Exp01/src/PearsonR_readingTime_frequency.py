from wordfreq import zipf_frequency
import csv 
import pandas as pd
from scipy import stats

csv_file_path = r"..\outputs\totalReadingTimeCuvinte_fromExp01.csv"

frequency_df=pd.DataFrame(columns=['Word', 'FrequencyScore', 'totalReadingTime'])

with open(csv_file_path, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for i,row in enumerate(reader):
        word = row['Word']
        word = ''.join(char for char in word if char.isalnum())
        frequency = zipf_frequency(word, 'ro')
        frequency_df.loc[i] = [word, frequency, row['totalReadingTime']]

frequency_df['totalReadingTime'] = pd.to_numeric(frequency_df['totalReadingTime'], errors='coerce')
frequency_df['FrequencyScore'] = pd.to_numeric(frequency_df['FrequencyScore'], errors='coerce')

# Drop NaN values 
frequency_df.dropna(subset=['totalReadingTime', 'FrequencyScore'], inplace=True)

try:
    pearson_corr, p_value= stats.pearsonr(frequency_df['totalReadingTime'], frequency_df['FrequencyScore'])
except ValueError:
    pearson_corr = None
print ("Pearson correlation coefficient intre Total reading time and Frequency Score: ", pearson_corr, round(p_value, 4))