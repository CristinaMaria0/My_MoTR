from wordfreq import zipf_frequency
import csv 
import pandas as pd
from scipy import stats
import itertools
# complexity_mapping = {
#     "foarte familiar": 1,
#     "simplu": 2,
#     "nici simplu nici complex": 3,
#     "complex": 4,
#     "nu cunosc": 5
# }

complexity_mapping = {
    "foarte familiar": 0,
    "simplu": 0.25,
    "nici simplu nici complex": 0.5,
    "complex": 0.75,
    "nu cunosc": 1
}
csv_file_path = r"..\outputs\totalReadingTimeCuvinte_fromExp01.csv"

csv_frequency_score = r"..\outputs\frequencyScore.csv"
csv_sentence_word_complexity = r"..\outputs\sentenceWordComplexity.csv"
csv_files = [
    r"..\adnotari_complexitate\victor.csv",
    r"..\adnotari_complexitate\iulia.csv",
    r"..\adnotari_complexitate\petru.csv",
    r"..\adnotari_complexitate\stadio88.csv",
    r"..\adnotari_complexitate\user.csv",
    r"..\adnotari_complexitate\sergiu.csv",
]

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

max_correlation = 0
min_correlation = 1
max_combination = None
min_combination = None
all_combinations = []
for r in range(1, len(csv_files) + 1):  # De la 1 la numărul total de elemente
    all_combinations.extend(itertools.combinations(csv_files, r))

for combination in all_combinations:
    propozitie_target={}
    users = [adnotare_complexitate_path.split('\\')[-1].split('.')[0] for adnotare_complexitate_path in combination]
    print(f"Pentru userii: {users}:")
    for adnotare_complexitate_path in combination: 
        # print(adnotare_complexitate_path)
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
       
        adnotare_data = pd.read_csv(adnotare_complexitate_path, names=['word', 'label', 'text'])
        adnotare_data['complexity'] = adnotare_data['label'].map(lambda x: complexity_mapping.get(str(x).strip().lower(), None))

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
        # verifică primele propoziții
        # print(propozitii_csv[:2])

        reading_times_per_user = []
        complexities_per_user = []
        reading_times_for_all = []
        complexities_for_all = []
        for idx, row in adnotare_data.iterrows():
            word = row['word']
            complexity = row['complexity']
            sentence = row["text"]
            match_df = gaseste_propozitie_similara_corecta(sentence, propozitii_csv)
            
            if match_df is not None:
                matched_row = match_df[match_df['Word'].str.lower() == word.lower()]
                if not matched_row.empty and not pd.isna(matched_row['totalReadingTime'].values[0]):
                    reading_time = matched_row['totalReadingTime'].values[0]
                    reading_times_per_user.append(reading_time)
                    complexities_per_user.append(complexity)

                    sentence_cleaned = sentence.replace(" ", "") 
                    key = (sentence_cleaned, word)
                    if key in propozitie_target:
                        propozitie_target[key]["total_complexity"]+=complexity
                        propozitie_target[key]["total_reading_time"]+=reading_time
                        propozitie_target[key]["count"]+=1
                    else:
                        propozitie_target[key] = {"total_complexity": complexity, "count": 1, "total_reading_time": reading_time}

                    # propozitie_target[key]["total_reading_time"] = reading_time


        # Calculez Pearson correlation
        # correlation, p_value = stats.pearsonr(complexities_per_user, reading_times_per_user)
        # user_adnotare=adnotare_complexitate_path.split('\\')[-1].split('.')[0]
        # print(f"Pearson correlation coefficient ({user_adnotare}): {correlation:.4f}, p-value: {p_value:.4f}\n")


    average_sentence_word_complexity = []
    for (sentence, word), data in propozitie_target.items():
            avg_complexity = data["total_complexity"] / data["count"]
            reading_time = data["total_reading_time"] / data["count"]
            average_sentence_word_complexity.append({"sentence": sentence, "word": word, "average_complexity": avg_complexity,'total_reading_time':reading_time})

    df_avg_sentence_word_complexity = pd.DataFrame(average_sentence_word_complexity)
    df_avg_sentence_word_complexity.to_csv(csv_sentence_word_complexity, index=False)
    correlation, p_value = stats.pearsonr(df_avg_sentence_word_complexity["average_complexity"], df_avg_sentence_word_complexity["total_reading_time"])
    print(f"{correlation:.4f}, p-value: {p_value:.4f}")
    if correlation > max_correlation:
        max_correlation = correlation
        max_combination = users
    if correlation < min_correlation:
        min_correlation = correlation
        min_combination = users
print(f"Max correlation: {max_correlation} for combination: {max_combination}")
print(f"Min correlation: {min_correlation} for combination: {min_combination}")