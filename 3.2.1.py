import pandas as pd

file = input('Введите название файла: ')
df = pd.read_csv(file)

df['year'] = df['published_at'].apply(lambda x: x[0:4])
df_group = df.groupby('year')

for year, data in df_group:
    data.loc[:, data.columns != 'year'].to_csv(rf'vacancies\{year}.csv', index=False)
