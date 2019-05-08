import config
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

from gerencia_revisao import worksheetToDf, getRevisionSession, commitRevisionSession

def retrieveSpreadsheetData(creds_file=config.CREDENTIALS_FILE, main_spreadsheet_name=config.MAIN_SPREADSHEET_NAME):
    # Google Drive Authentication
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    gc = gspread.authorize(credentials)
    
    # Reading data from spreadsheet
    sprsh = gc.open(main_spreadsheet_name)
    wsh_materias = sprsh.worksheet('materias_pesos')
    wsh_revisoes = sprsh.worksheet('revisoes')

    df_materias = pd.DataFrame.from_records(wsh_materias.get_all_values())
    df_materias.columns = df_materias.loc[0]
    df_materias.reindex(df_materias.drop(0,inplace=True))
    df_materias.set_index(['nome'],inplace=True)
    df_materias = df_materias.apply(lambda df: pd.to_numeric(df,errors='ignore')) 

    df_revisoes = worksheetToDf(wsh_revisoes)
    return df_materias, df_revisoes, wsh_materias, wsh_revisoes
