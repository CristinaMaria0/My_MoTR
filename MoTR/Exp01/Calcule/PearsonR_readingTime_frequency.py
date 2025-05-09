from wordfreq import zipf_frequency
import csv 
import pandas as pd
from scipy import stats
import os
import glob


def map_word_length(word):

    length = len(str(word).strip())
    if length <= 2:
        return 1
    elif length <= 4:
        return 2
    elif length <= 6:
        return 3
    elif length <= 8:
        return 4
    else:
        return 5

outputs_folder = r"d:/repos/My_MoTR/MoTR/Exp01/Calcule/outputs/"
# Get all CSV files in the outputs folder that end with 'totalReadingTime.csv'
csv_files = glob.glob(os.path.join(outputs_folder, '*totalReadingTime.csv'))
for csv_file in csv_files:
    file_name = os.path.basename(csv_file)
    print(f"Processing file: {file_name}")
    frequency_df=pd.DataFrame(columns=['SentenceIndex','Word', 'FrequencyScore', 'totalReadingTime'])

    with open(csv_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        for i,row in enumerate(reader):
            word = row['Word']
            word = ''.join(char for char in word if char.isalnum())
            frequency = zipf_frequency(word, 'ro')
            sentence_index = row['sentenceIndex']
            frequency_df.loc[i] = [sentence_index, word, frequency, row['totalReadingTime']]
    frequency_df['SentenceIndex'] = pd.to_numeric(frequency_df['SentenceIndex'], errors='coerce')
    frequency_df['totalReadingTime'] = pd.to_numeric(frequency_df['totalReadingTime'], errors='coerce')
    frequency_df['FrequencyScore'] = pd.to_numeric(frequency_df['FrequencyScore'], errors='coerce')
    frequency_df['WordLength'] = frequency_df['Word'].apply(map_word_length)

    # Drop NaN values 
    frequency_df.dropna(subset=['totalReadingTime', 'FrequencyScore', 'WordLength'], inplace=True)

    try:
        pearson_corr, p_value= stats.pearsonr(frequency_df['totalReadingTime'], frequency_df['FrequencyScore'])
    except ValueError:
        pearson_corr = None
    # print ("Pearson correlation (Total reading time, Frequency Score): ", pearson_corr, round(p_value, 4))

    try:
        pearson_corr_word_length, p_value_word_length= stats.pearsonr(frequency_df['totalReadingTime'], frequency_df['WordLength'])
    except ValueError:
        pearson_corr_word_length = None
    print ("Pearson correlation (Total reading time, Word Length): ", pearson_corr_word_length, round(p_value_word_length, 4))