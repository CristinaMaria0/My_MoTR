from wordfreq import zipf_frequency
import csv 
import pandas as pd
from scipy import stats

tsv_file_path=r"..\romanian_lcp.tsv"
csv_file_path = r"..\outputs\totalReadingTimeCuvinte_fromExp01.csv"
csv_frequency_score = r"..\outputs\frequencyScore.csv"
csv_detalii_potriviri_propozitii = r"..\outputs\detaliiPotriviriPropozitii.csv"

# Read the CSV file and calculate the frequency score for each word
def gaseste_propozitie_similara_corecta(propozitie_tsv, propozitii_csv):
    tokens_tsv = set(str(propozitie_tsv).lower().split())
    max_sim = -1
    best_match_df = None
    for prop_csv_df in propozitii_csv:
        # print(prop_csv_df.columns)
        tokens_csv = set(str(word).lower() for word in prop_csv_df['Word'] if isinstance(word, str))
        sim = len(tokens_tsv.intersection(tokens_csv))
        if sim > max_sim:
            max_sim = sim
            best_match_df = prop_csv_df
    return best_match_df
 
frequency_df=pd.DataFrame(columns=['Word', 'FrequencyScore', 'totalReadingTime'])

with open(csv_file_path, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    for i,row in enumerate(reader):
        word = row['Word']
        word = ''.join(char for char in word if char.isalnum())
        frequency = zipf_frequency(word, 'ro')
        frequency_df.loc[i] = [word, frequency, row['totalReadingTime']]

frequency_df.to_csv(csv_frequency_score, index=False)

frequency_df['totalReadingTime'] = pd.to_numeric(frequency_df['totalReadingTime'], errors='coerce')
frequency_df['FrequencyScore'] = pd.to_numeric(frequency_df['FrequencyScore'], errors='coerce')

# Drop NaN values that might have been introduced during conversion
# frequency_df.dropna(subset=['totalReadingTime', 'FrequencyScore'], inplace=True)

# try:
#     pearson_corr= stats.pearsonr(frequency_df['totalReadingTime'], frequency_df['FrequencyScore'])
# except ValueError:
#     pearson_corr = None
# print ("Pearson correlation coefficient intre Total reading time and Frequency Score: ", pearson_corr[0])


tsv_data = pd.read_csv(tsv_file_path, sep='\t', encoding='utf-8', 
                       names=['idx', 'limba', 'propozitie', 'cuvant', 'index_complexitate'],
                       )




# Refacem separarea corectă folosind linia explicită ",0.0," ca separator
propozitii_csv = []
current_sentence = []

for idx, row in frequency_df.iterrows():
    if pd.isna(row['totalReadingTime']):
        if current_sentence:
            # Aici definim explicit coloanele DataFrame-ului
            sentence_df = pd.DataFrame(current_sentence, columns=['Word', 'FrequencyScore', 'totalReadingTime'])
            propozitii_csv.append(sentence_df)
            current_sentence = []
    else:
        current_sentence.append(row.values)  # asigură-te că adaugi valorile

if current_sentence:
    sentence_df = pd.DataFrame(current_sentence, columns=['Word', 'FrequencyScore', 'totalReadingTime'])
    propozitii_csv.append(sentence_df)
# for sentence in propozitii_csv[:3]:
#     print(type(sentence), sentence.columns)

# verifică primele propoziții
# print(propozitii_csv[:3])


reading_times = []
complexities = []

for idx, row in tsv_data.iterrows():
    prop_tsv = row['propozitie']
    word_tsv = row['cuvant']
    complexity = row['index_complexitate']
    
    if not isinstance(word_tsv, str) or pd.isna(complexity):
        continue  # sărim peste rândurile incomplete

    match_df = gaseste_propozitie_similara_corecta(prop_tsv, propozitii_csv)

    if match_df is not None:
        matched_row = match_df[match_df['Word'].str.lower() == word_tsv.lower()]
        if not matched_row.empty and not pd.isna(matched_row['totalReadingTime'].values[0]):
            reading_time = matched_row['totalReadingTime'].values[0]
            reading_times.append(reading_time)
            complexities.append(complexity)
# Calculez Pearson correlation
correlation, p_value = stats.pearsonr(complexities, reading_times)
print(f"Pearson correlation coefficient: {correlation:.4f}, p-value: {p_value:.4f}")


detalii_potriviri = []

for idx, row in tsv_data.iterrows():
    prop_tsv = row['propozitie']
    word_tsv = row['cuvant']
    
    if not isinstance(word_tsv, str):
        continue
    
    match_df = gaseste_propozitie_similara_corecta(prop_tsv, propozitii_csv)
    
    if match_df is not None:
        prop_gasita = ' '.join(match_df['Word'].astype(str).tolist())
    else:
        prop_gasita = "Nicio potrivire găsită"
    
    detalii_potriviri.append({
        'Propozitie TSV': prop_tsv,
        'Propozitie Gasita CSV': prop_gasita,
        'Cuvant TSV': word_tsv
    })

# Convertim rezultatele într-un DataFrame pentru o afișare clară
df_detalii_potriviri = pd.DataFrame(detalii_potriviri)
df_detalii_potriviri.to_csv(csv_detalii_potriviri_propozitii, index=False)

matches = 0
total = len(df_detalii_potriviri)

for idx, row in df_detalii_potriviri.iterrows():
    if row['Cuvant TSV'].lower() in row['Propozitie Gasita CSV'].lower().split():
        matches += 1

accuracy_percentage = (matches / total) * 100 if total > 0 else 0
print(f"Procentajul de acuratețe: {accuracy_percentage:.2f}%")
