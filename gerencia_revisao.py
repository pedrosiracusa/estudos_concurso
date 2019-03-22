
# coding: utf-8

# In[1]:


import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import timedelta
from datetime import datetime


# In[2]:


spreadsheet_name = "controle"
credentialsFile_path = "./credentials.json"


# In[187]:


# Google Drive Authentication
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(credentialsFile_path, scope)
gc = gspread.authorize(credentials)


# In[54]:


# GLobals

# Default step factor to use
STEP_FACTOR = 3

COLS_TO_UPDATE = ['LAST_REVISION','STEP'] 


# ## Importing the worksheet into a dataframe

# In[204]:


def worksheetToDf(worksheet):
    df = pd.DataFrame.from_records(worksheet.get_all_values())
    df.columns = df.loc[0]
    df.reindex(df.drop(0,inplace=True))
    df.loc[ df['STEP_FACTOR']=='', 'STEP_FACTOR' ] = STEP_FACTOR

    df['LAST_REVISION'] = pd.to_datetime(df['LAST_REVISION'])
    df['STEP_FACTOR']= df['STEP_FACTOR'].astype(int)
    df['STEP'] = df['STEP'].astype(int)
    return df


# ## Updating the worksheet using the dataframe

# In[174]:


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
    df['LAST_REVISION'] = df['LAST_REVISION'].astype(str)
    for col in columns:
        updateCells(df,worksheet,colname=col,inplace=True)


# ---

# In[7]:


def getNextRevision(df, inplace=False):
    next_revisions = df[['LAST_REVISION','STEP']].apply(lambda df: df['LAST_REVISION'] + timedelta(days=int(df['STEP'])), axis=1)
    if inplace:
        df['NEXT_REVISION'] = next_revisions
    else:
        return next_revisions
    
def isDue(df):
    currentDate = datetime.now().date()
    return df['NEXT_REVISION'] <= datetime.now()


# In[86]:


def updateStep(df, inplace=False):
    max_step = 30
    updated_steps = df[['STEP','STEP_FACTOR']].apply(lambda df: min( int(df['STEP'])*int(df['STEP_FACTOR']), max_step ) , axis=1)
    if inplace:
        df['STEP'] = updated_steps
    else:
        return updated_steps
    
def updateLastRevision(df,date=None):
    if date is None:
        date = pd.datetime.now().date().isoformat()
        
    df['LAST_REVISION'] = pd.to_datetime(date)


# ---

# In[141]:


def getRevisionSession(df, num_blocks=3):
    getNextRevision(df_revisoes, inplace=True)
    return df.loc[ isDue(df) ].sort_values(by='NEXT_REVISION')[:num_blocks]


# In[142]:


def commitRevisionSession(df,rs, worksheetToUpdate=None):
    updateStep(rs,inplace=True)
    updateLastRevision(rs)
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
    print("Aqui está sua sessão de revisão:")
    print(rs[['MATERIA','MATERIAL','LAST_REVISION']])
    
    if input("Posso confirmar? (y/n)")=='y':
        commitRevisionSession(df_revisoes, rs, worksheetToUpdate=wsh_revisoes)
        print("A tabela foi atualizada")
    else:
        print("Ok... não atualizei a tabela")

