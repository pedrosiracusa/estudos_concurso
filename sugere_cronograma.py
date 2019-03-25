import math, json
import gspread
from pandas import DataFrame, to_numeric
from numpy import random
from oauth2client.service_account import ServiceAccountCredentials
from gerencia_revisao import worksheetToDf, getRevisionSession, commitRevisionSession


spreadsheet_name = "controle"
credentialsFile_path = "./credentials.json"
smooth_factor=12
horas_estudo_dia = 5
horas_estudo_semana = horas_estudo_dia * 5
usando_ciclo_predefinido=True


# Google Drive Authentication
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentialsFile_path, scope)
gc = gspread.authorize(credentials)

# Reading data from spreadsheet
sprsh = gc.open(spreadsheet_name)
wsh_materias = sprsh.worksheet('materias_pesos')
wsh_revisoes = sprsh.worksheet('revisoes')

df_materias = DataFrame.from_records(wsh_materias.get_all_values())
df_materias.columns = df_materias.loc[0]
df_materias.reindex(df_materias.drop(0,inplace=True))
df_materias.set_index(['nome'],inplace=True)
df_materias = df_materias.apply(lambda df: to_numeric(df,errors='ignore')) 

df_revisoes = worksheetToDf(wsh_revisoes)


# Store data in a dict `materias` and use it to calculate scores and suggest
materias = df_materias.to_dict(orient='index')


def get_score(x, smooth=smooth_factor, use_suggested=False):
    if use_suggested:
        return x['sugg_score']
    else:
        return math.pow( x['relevancia'] * x['dificuldade'] * x['extensao'] * (x['peso']*3) / x['dominio'] * x['active'] * x['priority'], 1/smooth )

scores = [ (mat,get_score(d,use_suggested=usando_ciclo_predefinido))  for mat,d in materias.items() ]

normalize = lambda l: [i/sum(l) for i in l]
scores_normalized = list(zip( [ m for m,s in scores ], normalize([ s for m,s in scores ]) ))

# Other functions
def printScores(data):
    print("".join( [ f"\n{'(inativa) ' if score==0 else '':10}\
{mat:.<40}\
{format_hours(score*horas_estudo_semana):.>9} por semana\
 ({score:.1%}) " for mat,score in sorted(data,key=lambda x:x[1],reverse=True)] ))


def format_hours(hours):
    hours_int = int(hours)
    mins_int = int( (hours-hours_int)*60 )
    return f"{mins_int} min" if hours_int==0 else f"{hours_int}h {mins_int:02} min" if mins_int>0 else f"{hours_int} h"


# SUGGEST
print("Ranqueando scores de matérias:")
print("=============================")
if usando_ciclo_predefinido:
    print("Usando ciclo de estudos pré-definido")
print(f"Usando smooth factor = {smooth_factor}")
print(f"Total de horas estudadas por semana: {horas_estudo_semana}")
printScores(scores_normalized)

suggested = sorted(list(random.choice(
    [ m[0] for m in scores_normalized], 
    p=[ m[1] for m in scores_normalized], 
    size=horas_estudo_dia, 
    replace=True
    )))

def suggestMaterias(scores_normalized):
    mats = dict()
    cntr = horas_estudo_dia
    while cntr > 0:
        mat = random.choice( [m[0] for m in scores_normalized],
                       p=[m[1] for m in scores_normalized],
                       size = 1 )[0]
        
        if mats.get(mat,0) == 2:
            pass
        
        elif mats.get(mat,0) >= 1:
            mats[mat] +=.5
            cntr -= .5
            
        else:
            mats[mat] = 1
            cntr -= 1
        
        # If hours exceeded, reset and try again
        if cntr < 0:
            cntr = horas_estudo_dia
            mats = dict()
        
    return mats            
        

print("\nMatérias sugeridas para hoje:")
print("============================")

suggested = suggestMaterias(scores_normalized).items()
print("".join([ f"\n\t{m} ({format_hours(h)})" for m,h in suggested]))


print("\nRevisões:")
print("============================")
rs = getRevisionSession(df_revisoes,num_blocks=3)
if rs.shape[0]==0:
    print("Não há revisões a fazer")
else:
    commitRevisionSession(df_revisoes, rs, worksheetToUpdate=wsh_revisoes)
    print("Sua sessão de revisão foi atualizada")
    print("Aqui estão as matérias a revisar:")
    print(rs[['MATERIA','MATERIAL']])

input("\nPressione ENTER para terminar")
