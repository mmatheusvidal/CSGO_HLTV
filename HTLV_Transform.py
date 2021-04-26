import pandas as pd

#Read_File
data = pd.read_json('path')

## Tratamento
#Define Match_ID
data['match_id'] = data['link']
data['match_id'] = data['match_id'].str.replace('https://www.hltv.org/matches/','')
data['match_id'] = data['match_id'].str.replace('(/)[a-z0-9]+.*','', regex=True)
data['match_id'] = data['match_id'].str.replace('https:/','')

#Deleta linhas que não são jogos
delete_list = data[ data['match_id'] == ''].index
delete_list2 = data[ data['jogo'] == ''].index
data.drop(delete_list, inplace=True)
data.drop(delete_list2, inplace=True)

#Split Coluna 'jogo'
data['jogo_split'] = data['jogo'].str.split('\n')
data['time_1'] = data['jogo_split'].str[0]
data['resultado'] = data['jogo_split'].str[1]
data['time_2'] = data['jogo_split'].str[2]
data['resultado_split'] = data['resultado'].str.split(' ')
data['score_t1'] = data['resultado_split'].str[0]
data['score_t2'] = data['resultado_split'].str[2]
data['competicao'] = data['jogo_split'].str[3]
data['best_of'] = data['jogo_split'].str[4]

#Drop Columns and Drop NaN
data.drop(columns=['jogo', 'jogo_split', 'resultado', 'resultado_split'], inplace=True)
data = data.dropna()
data = data.reset_index(drop=True)

#Rename columns
data.columns = ['match_url', 'match_id', 'team_A', 'team_B', 'score_tA', 'score_tB', 'competition', 'type_of_match']

#Save File
data.to_csv('HTLV_results.csv', sep=';')
