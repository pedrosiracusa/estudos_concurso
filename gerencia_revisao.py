
# coding: utf-8

# In[2]:


import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import timedelta
from datetime import datetime


# In[3]:


spreadsheet_name = "controle"
credentialsFile_path = "./credentials.json"


# In[4]:


# Google Drive Authentication
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentialsFile_path, scope)
gc = gspread.authorize(credentials)


# In[5]:


# GLobals

# Default step factor to use
STEP_FACTOR = 3

COLS_TO_UPDATE = ['REVISADO'] 


# ## Importing the worksheet into a dataframe

# In[6]:


def worksheetToDf(worksheet):
    df = pd.DataFrame.from_records(worksheet.get_all_values())
    df.drop( df[df[1]==''].index,inplace=True )
    df.columns = df.loc[0]
    df.reindex(df.drop(0,inplace=True))
    df.loc[ df['STEP_FACTOR']=='', 'STEP_FACTOR' ] = STEP_FACTOR

    df['LAST_REVISION'] = pd.to_datetime(df['LAST_REVISION'])
    df['REVISADO'] = df['REVISADO'].astype(int)
    df['STEP_FACTOR']= df['STEP_FACTOR'].astype(int)
    df['STEP'] = df['STEP'].astype(int)
    return df


# ## Updating the worksheet using the dataframe

# In[7]:


def getCellsFromColumn(df,worksheet,colname):
    colnames_dict = {n:i+1 for i,n in enumerate(df.columns)}
    return worksheet.range( 2,colnames_dict[colname], df.shape[0]+1, colnames_dict[colname])

def updateCells(df, worksheet, colname, inplace=False):
    """ Updates worksheet cells based on the dataframe """
    
    newvalues = list(df[colname])
    
    cells_list = getCellsFromColumn(df,worksheet,colname)
    for i,cell in enumerate(cells_list):
        cell.value = newvalues[i]
        
    if inplace: 
        worksheet.update_cells(cells_list)
        
    return cells_list

def updateWorksheet(df,worksheet,columns=COLS_TO_UPDATE):
    for col in columns:
        updateCells(df,worksheet,colname=col,inplace=True)


# ---

# ## Assembling new revision session

# In[8]:


def appendNextRevision(df):
    next_revisions = df[['LAST_REVISION','STEP']].apply(lambda df: df['LAST_REVISION'] + timedelta(days=int(df['STEP'])), axis=1)
    df['NEXT_REVISION'] = next_revisions
    return df
    
def isDue(df):
    currentDate = datetime.now().date()
    return df['NEXT_REVISION'] <= datetime.now()


# In[9]:


def getRevisionSession(df, num_blocks=3):
    appendNextRevision(df)
    return df.loc[ isDue(df) ].sort_values(by='NEXT_REVISION')[:num_blocks]

def commitRevisionSession(df,rs, worksheetToUpdate=None):
    rs['REVISADO'] = 0
    df.update(rs)
    if worksheetToUpdate:
        updateWorksheet(df,worksheetToUpdate)


# ---

# In[226]:


if __name__=='__main__':
    
    # Reading data from spreadsheet
    sprsh = gc.open(spreadsheet_name)
    wsh_revisoes = sprsh.worksheet('revisoes')

    df_revisoes = worksheetToDf(wsh_revisoes)
    rs = getRevisionSession(df_revisoes, num_blocks = 3)
    if rs.shape[0]==0:
        print("Não há revisões a fazer")
    else:
        commitRevisionSession(df_revisoes, rs, worksheetToUpdate=wsh_revisoes)
        print("Sua sessão de revisão foi atualizada.")
        print("Aqui estão as matérias:")
        print(rs[['MATERIA','MATERIAL']])

