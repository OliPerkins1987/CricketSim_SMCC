# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 11:06:03 2020

@author: Oli
"""

def setupselect():
    
    import pandas as pd


### get player names

    Batting = pd.read_csv('batting_score.csv')
    
    Players = Batting['id'].tolist()
    
    return(Players)


def setupsim():

    import numpy as np
    import pandas as pd
    import random
    from itertools import compress

###############################################################

### Load data

###############################################################

### predicted

    Bowling = pd.read_csv('bowling_scores.csv')

### predicted

    Batting = pd.read_csv('batting_score.csv')
    Batting['overallscore'] = Batting['overallscore'] * 40.4666666666666

### actual

    Batting_actual = pd.read_csv('batting.csv')
    Bowling_actual = pd.read_csv('bowling.csv')

### filter data

    Bowling = Bowling.loc[Bowling['id'].isin(Batting['id']), :]
    Bowling_actual = Bowling_actual.loc[Bowling_actual['0'].isin(Batting['id']), :]
    Batting_actual = Batting_actual.loc[Batting_actual['0'].isin(Batting['id']), :]

    Bowling_actual = Bowling_actual.drop_duplicates(subset = '0')
    Batting_actual = Batting_actual.drop_duplicates(subset = '0')



###################################################

### Fill missing preds

###################################################

    Batting= Batting.fillna('nan')

    ratios = (13.147360,  12.462483,   9.922777,   8.330223,   8.320333,) 

    def fill_da_numb(x, ratio):
    
        if str(x[3]) == 'nan' and str(x[2]) != 'nan':
        
            x[3] = str(float(x[2]) * (ratios[1] / (ratios[0]*1.2)))

        if str(x[4]) == 'nan' and str(x[3]) != 'nan':
        
            x[4] = str(float(x[3]) * (ratios[2] / (ratios[1]*1.2)))  
        
        if str(x[5]) == 'nan' and str(x[4]) != 'nan':
        
            x[5] = str(float(x[4]) * (ratios[3] / (ratios[2]*1.2)))  
        
        if str(x[6]) == 'nan' and str(x[5]) != 'nan':
        
            x[6] = str(float(x[5]) * (ratios[4] / (ratios[3]*1.2)))

        return(x)

    Batting = Batting.apply(fill_da_numb, 1, ratio = ratios)

###################################################

### compile

###################################################

    data = {'Batting': {'pred': Batting, 'actual': Batting_actual}, 
        'Bowling': {'pred': Bowling, 'actual': Bowling_actual}}
    
    
    return({'data': data})
    
    
    