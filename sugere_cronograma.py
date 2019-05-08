import config
import math, json
from gerencia_revisao import worksheetToDf, getRevisionSession, commitRevisionSession

from studysession import StudySession
from misc import retrieveSpreadsheetData



if __name__=='__main__':

    subj_df, df_revisoes, wsh_materias, wsh_revisoes = retrieveSpreadsheetData()
    SS = StudySession(subj_df,df_revisoes)

    print("Ranqueando scores de matérias:")
    print("=============================")
    print(f"Total de horas estudadas por semana: {config.BLOCOS_ESTUDO + config.BLOCOS_REVISAO + config.BLOCOS_REVISAO + config.BLOCOS_ANKI}")
    SS.printScores()


    print("\nMatérias sugeridas para hoje:")
    print("============================")
    print("".join([ f"\n\t{m} ({h} blocos) "for m,h in SS.suggestSubjects().items()]))


    print("\nRevisões:")
    print("============================")
    rs = getRevisionSession(df_revisoes,num_blocks=config.BLOCOS_REVISAO)
    if rs.shape[0]==0:
        print("Não há revisões a fazer")
    else:
        commitRevisionSession(df_revisoes, rs, worksheetToUpdate=wsh_revisoes)
        print("Sua sessão de revisão foi atualizada")
        print("Aqui estão as matérias a revisar:")
        print(rs[['MATERIA','MATERIAL']])

    input("\nPressione ENTER para terminar")
