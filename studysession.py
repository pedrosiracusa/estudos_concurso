import config
from numpy import random

class StudySession:
    def __init__(self, df_subjects,
                       df_reviews,
                       learnBlocks=config.BLOCOS_ESTUDO, 
                       reviewBlocks=config.BLOCOS_REVISAO, 
                       memoBlocks=config.BLOCOS_ANKI,
                       questionsBlocks=config.BLOCOS_QUESTOES):
        
        self.learnBlocks=learnBlocks
        self.reviewBlocks=reviewBlocks
        self.memoBlocks=memoBlocks
        self.questionsBlocks=questionsBlocks
        
        self.subjectScores=self.calculateSubjectScores(df_subjects)
     
    @staticmethod
    def calculateSubjectScores(df, normalize=True, use_suggested=True):
        subjects = df.to_dict(orient='index')
        if use_suggested:
            scores = [ (subj,d['sugg_score']) for subj,d in subjects.items() ]

        else:
            return math.pow( df['relevancia'] * df['dificuldade'] * df['extensao'] * (df['peso']*3) / df['dominio'] * df['active'] * df['priority'], 1/smooth )

        if normalize:
            sum_scores = sum( scr for sbj,scr in scores )
            return [ (sbj,scr/sum_scores) for sbj,scr in scores  ]

        return scores
        
    def suggestSubjects(self):
        subjs = dict()
        cntr = self.learnBlocks
        while cntr > 0:
            subj = random.choice( [m[0] for m in self.subjectScores],
                           p=[m[1] for m in self.subjectScores],
                           size = 1 )[0]

            if subjs.get(subj,0) == 4:
                pass

            elif subjs.get(subj,0) >= 2:
                subjs[subj] +=1
                cntr -= 1

            else:
                subjs[subj] = 2
                cntr -= 2

            # If hours exceeded, reset and try again
            if cntr < 0:
                cntr = self.learnBlocks
                subjs = dict()

        return subjs    
    
    
    def simulateScores(self,num_of_sessions=100, normalized=True):
        simulated_scrs = {data[0]:0 for data in self.subjectScores }
        for i in range(num_of_sessions):
            for subj,num_blocks in self.suggestSubjects().items():
                simulated_scrs[subj]+=num_blocks
        
        simulated_scrs = sorted(list(simulated_scrs.items()),key=lambda x:x[1],reverse=True)
        if normalized:
            sum_scrs = sum(d[1] for d in simulated_scrs)
            return [ (subj,scr/sum_scrs) for subj,scr in simulated_scrs ]
        return simulated_scrs
        
    
    def printScores(self):
        def format_hours(hours):
            hours_int = int(hours)
            mins_int = int( (hours-hours_int)*60 )
            return f"{mins_int} min" if hours_int==0 else f"{hours_int}h {mins_int:02} min" if mins_int>0 else f"{hours_int} h"
        
        horas_estudo_semana = self.learnBlocks*0.417*5
        print("".join( [ f"\n{'(inativa) ' if score==0 else '':10}{mat:.<40}{format_hours(score*horas_estudo_semana):.>9} por semana ({score:.1%}) " for mat,score in sorted(self.subjectScores,key=lambda x:x[1],reverse=True)] ))
