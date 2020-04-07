# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 18:08:41 2020


TO DO:
    
    2) Toss?
    3) End of game / who won etc
    4) tidy up CODE!
    
    --- web interface
    
    1) Make simple GUI
    
    -- additions
    
    4) Fix score engine for bowlers - nans and infinity for bowlers
    5) Fielding and extras
    6) Batsman more likely to get out early & factor in not outs
    7) Test predictions
    8) Add: different scoring rates, different bowler styles?
    9) Team Morale
    10) Tactical instructions
    
    

@author: Oli
"""

import numpy as np
import pandas as pd
import os
import random
from itertools import compress


###############################################################

### Classes

###############################################################

class match:
    
    def __init__(self, teams, duration, data):
        
        self.teams    = teams
        self.duration = duration
        self.data     = data
        self.innings  = 'Team1'
        self.bowler   = ''
        self.batsman  = ''
        self.innings_number = 1
        
        '''
        
    Data should be a dictionary of data frames, with 'Batting' and 
    'Bowling' as the two keys, which then break into 'pred' and 'actual'
        
        '''
        
        ##############################################
        ### data structure to define the match score
        ##############################################
        
        ''' Change the data structure so keeping tally of the match score is in overall, 
        whilst individual performances are in the team1 / team2 piece of self.score'''
        
        self.score = {'Overall': {'Team1':{'Batting':{'Runs':0, 'Wickets':0, 
                                        'Overs':0, 'Not out': [self.teams['Team1'][0], self.teams['Team1'][1]]}, 
                                'Bowling':{'Current':'', 'Previous':''}}, 
                                'Team2':{'Batting':{'Runs':0, 'Wickets':0, 
                                        'Overs':0, 'Not out': [self.teams['Team2'][0], self.teams['Team2'][1]]}, 
                                'Bowling':{'Current':'', 'Previous':''}}}, 
                      'Team1':{'Batting':dict(zip(teams['Team1'], [{'Runs':0, 'How Out': str('Not out'), 'Balls Faced':0, 'Bowler':''} for x in range(11)])), 
                                'Bowling':{}}, 
                      'Team2':{'Batting':dict(zip(teams['Team2'], [{'Runs':0, 'How Out': str('Not out'), 'Balls Faced':0, 'Bowler':''} for x in range(11)])), 
                                'Bowling':{}}}
        
        self.score['Overall']['Team1']['Batting']['Facing'] = self.score['Overall']['Team1']['Batting']['Not out'][0]
        self.score['Overall']['Team2']['Batting']['Facing'] = self.score['Overall']['Team2']['Batting']['Not out'][0]
    
    
        ### Instantiate batsman and bowler
        
        if self.innings == 'Team1':
            
            self.B_innings = 'Team2'
            #self.bowler    = random.sample(self.teams[self.B_innings], 1)[0]
            
        elif self.innings == 'Team2':
            
            self.B_innings = 'Team1'
            #self.bowler    = random.sample(self.teams[self.B_innings], 1)[0]
            
        self.batsman = self.score['Overall'][self.innings]['Batting']['Facing']

    
###################################################################
        
### Determine expected outcome
        
###################################################################
        
    
    def expected_outcome(self, bowler, batsman):
        
                   
        ###############    
        ### gather data
        ###############
        
        #predictions
        batter_pred = self.data['Batting']['pred'].loc[(self.data['Batting']['pred']['id'] == batsman), :]
        bowler_pred = self.data['Bowling']['pred'].loc[(self.data['Bowling']['pred']['id'] == bowler), :]
        
        #actual
        batter_dat = self.data['Batting']['actual'].loc[(self.data['Batting']['actual']['0'] == batsman), :]
        bowler_dat = self.data['Bowling']['actual'].loc[(self.data['Bowling']['actual']['0'] == bowler), :]
        
        team_level  = np.min([batter_pred['main.team'].tolist(), bowler_pred['main.team.x'].tolist()])
        
        ##################################################
        #
        ### create expected outcome
        #
        ##################################################
        
        ### batting
        
        if batter_pred['main.team'].iloc[0] != team_level:
            
            if team_level != 1:
            
                bp      = batter_pred.iloc[:, 2:7]
                team    = 5 - team_level 
                bat_ex  = float(bp.iloc[:, team])
                
            if team_level == 1:
                
                bp      = batter_pred['overallscore']
                bat_ex  = float(bp)
            
        elif batter_pred['main.team'].iloc[0] == team_level:
            
            bp      = batter_dat.iloc[:, 1:7]
            team    = team_level - 1
            bat_ex  = float(bp.iloc[:, team])
            
        ####################
        ### Bowling - Economy
        ####################
        
        if bowler_pred['main.team.x'].iloc[0] != team_level:

            if team_level != 1:
            
                bp      = bowler_pred.iloc[:, 2:7]
                team    = 5 - team_level 
                bowl_ex = {'Econ': float(bp.iloc[:, team])}
            
            if team_level == 1:
                
                bp      = bowler_pred['finalscore.x']
                bowl_ex = {'Econ': float(bp)}


        elif bowler_pred['main.team.x'].iloc[0] == team_level:
                       
            bp      = bowler_dat.iloc[:, 23:29]
            team    = team_level - 1
            bowl_ex = {'Econ': float(bp.iloc[:, team])}
        
        
        #####################
        ### Bowling - Strike Rate
        #####################
        
        if bowler_pred['main.team.x'].iloc[0] != team_level:
            
            if team_level != 1:
            
                bp      = bowler_pred.iloc[:, 13:18]
                team    = 5 - team_level 
                bowl_ex['SR'] = float(bp.iloc[:, team])
                
            if team_level == 1:
                
                bp      = bowler_pred['finalscore.y']
                bowl_ex['SR'] = float(bp)
            
        elif bowler_pred['main.team.x'].iloc[0] == team_level:
            
            bp      = bowler_dat.iloc[:, 1:20]
            team    = team_level - 1
            
            if float(bp.iloc[:, team]) != 0.0:
                
                bowl_ex['SR'] = (float(bp.iloc[:, (team + 11)]) * 6) / float(bp.iloc[:, team])
                
            else:
                
                bowl_ex['SR'] = 0.0


        ################################################
        
        ### Deal with part time bowlers
        
        ################################################
        
        ''' need to deal with nan and infinity'''
        
       
        if bowl_ex['SR'] == 0.0 or not bowl_ex['SR'] > 0 or bowl_ex['SR'] > 999999999999999999:
            
            if bowl_ex['Econ'] == 0.0:
                
                bowl_ex['Econ'] = abs(np.random.normal(6, 3, 1).tolist()[0])
                
                bowl_ex['SR'] = abs(np.random.normal(60, 20, 1).tolist()[0])
                
            else:
                
                bowl_ex['SR'] = bowl_ex['Econ'] * np.random.poisson(15, 1).tolist()[0]
        
        print(bowl_ex)
        
        ################################################
        
        ### Create expectations
        
        ################################################

        bowl_ex['Overall'] = bowl_ex['SR'] * (bowl_ex['Econ'] / 6)
        
        Expected_outcome = {'Overall': {'Outcome':(bowl_ex['Overall']  + bat_ex) / 2}, 
                           'Bat': bat_ex, 'Bowl':bowl_ex}
        
        return(Expected_outcome)
        
        
##########################################################
        
### Determine expected duration
        
##########################################################
        
    def Strike_rate(self):
            
            '''
            Come back to this
            Takes as an argument the output 
            of the expected_outcome function
            '''
            
        ### Strike rate calculations
            
            Expected_duration = (self.Expectation['Bowl']['SR'] + self.Expectation['Bat'] / 0.75) / 2  
            
            return(Expected_duration)


###########################################################
            
### Bowl a ball

###########################################################
            
    def ball(self):
        
        wicket = random.random() < 1/self.Expectation['Overall']['Duration']

        if wicket == True:
            
            return('wicket')

        elif wicket == False:
            
            runs = random.random() < self.Expectation['Overall']['Runs']/2.175 ### exchange this for SR dependent stuff
            
            if runs:
                
                boundary = random.random() < 0.25
                
                if boundary:
                    
                    six  = random.random() < 0.25
                    
                    if six:
                    
                        runs = 6
                        
                    else:
                        
                        runs = 4
                        
                else:
                    
                    run_rand = random.random()
                    
                    if run_rand <= 0.65:
                        
                        runs = 1
                        
                    elif run_rand <= 0.9:
                        
                        runs = 2
                        
                    else:
                        
                        runs = 3
                    
            else:
                
                runs = 0
                
            return(runs)
          
########################################################################
            
### Define fall of wicket procedure
            
########################################################################
            
    def FOW(self):
    
        ''' make this more nuanced'''
    
        How_out = random.random()
    
        if How_out < 0.3:
        
            How_out = 'Bowled'
        
        elif How_out < 0.7:
        
            How_out = 'Caught'
        
        elif How_out < 0.9:
        
            How_out = 'LBW'
        
        elif How_out < 0.96:
        
            How_out = 'Run Out'
        
        elif How_out < 0.999:
        
            How_out = 'Stumped'
        
        else:
        
            How_out = 'Obstructing the Field'
    
        return(How_out)
        
            
########################################################################
        
### Bowl an over
        
########################################################################
        
        
    def over(self):
        
        ### update bowler
            
        self.score['Overall'][self.innings]['Bowling']['Previous'] = self.bowler
        self.score['Overall'][self.innings]['Bowling']['Current']  = ''
        self.bowler = ''
        
        self.balls_bowled = 0
        
        ##########################################
        
        ### set up match conditions
        
        ##########################################
        
        ''' come back to this - select the bowler'''
        
        poss_bowlers   = list(compress(self.teams[self.B_innings], [x != game.score['Overall'][game.innings]['Bowling']['Previous'] for x in game.teams[game.B_innings]]))
        self.bowler    = random.sample(poss_bowlers, 1)[0]
        self.score['Overall'][self.innings]['Bowling']['Current'] = self.bowler
        
        ### Create bowler attribute if new
        
        if not self.score[self.B_innings]['Bowling']:
            
            self.score[self.B_innings]['Bowling'][self.bowler] = {'Overs':0, 'Maidens':0, 'Runs':0, 'Wickets':0, 'Buzzers':0}
                
        if not self.bowler in self.score[self.B_innings]['Bowling'].keys():
            
            self.score[self.B_innings]['Bowling'][self.bowler] = {'Overs':0, 'Maidens':0, 'Runs':0, 'Wickets':0, 'Buzzers':0}
        
        
        ### update batsman facing
        self.batsman   = self.score['Overall'][self.innings]['Batting']['Facing']
        
        ### make expectation
        self.Expectation  = self.expected_outcome(bowler = self.bowler, 
                           batsman = self.batsman)
        
        ### Add duration
             
        self.Expectation['Overall']['Duration']   =  self.Strike_rate()
        
        self.Expectation['Overall']['Runs']       = self.Expectation['Overall']['Outcome'] / self.Expectation['Overall']['Duration']  
        
        
        ############################################
        
        ### Bowl Over
        
        ############################################
    
           
        while self.balls_bowled < 6:
            
            #print(self.balls_bowled, self.score['Overall'][self.innings]['Batting']['Overs'])
    
            b = self.ball()
            
            print(b)
        
            self.score['Overall'][self.innings]['Batting']['Overs'] = self.score['Overall'][self.innings]['Batting']['Overs'] + 0.1
        
            self.balls_bowled += 1
        
            ##############
            
            ### Wicket?
            
            ##############
        
            if b == 'wicket':
                
                ### how out
                
                howout = self.FOW()
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']] ['How Out'] = howout
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']] ['Bowler']  = self.bowler
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']] ['Balls Faced'] += 1  
                
                ### update bowler
                self.score[self.B_innings]['Bowling'][self.bowler]['Overs'] +=0.1
        
        
            if b == 'wicket':
            
                ''' Add details of run outs'''
                
                self.score['Overall'][self.innings]['Batting']['Wickets'] += 1
                
                if not howout in ['Run Out', 'Obstructed the Field']:
                    
                    self.score[self.B_innings]['Bowling'][self.bowler]['Wickets'] += 1 
            
                if self.score['Overall'][self.innings]['Batting']['Wickets'] < 10:
                    
                    which = np.where(np.array(game.score['Overall'][game.innings]['Batting']['Not out']) == self.batsman)[0][0]
                    
                    self.score['Overall'][self.innings]['Batting']['Not out'][which] = self.teams[self.innings][self.score['Overall'][self.innings]['Batting']['Wickets'] + 1]
    
                    self.score['Overall'][self.innings]['Batting']['Facing']  = self.teams[self.innings][self.score['Overall'][self.innings]['Batting']['Wickets'] + 1]
    
                    self.batsman = self.score['Overall'][self.innings]['Batting']['Facing']
                    
                    ### change of over?
                    if self.balls_bowled == 6:
                                               
                        self.score['Overall'][self.innings]['Batting']['Facing'] = self.score['Overall'][self.innings]['Batting']['Not out'][self.score['Overall'][self.innings]['Batting']['Not out'] != self.batsman]
                        self.batsman = self.score['Overall'][self.innings]['Batting']['Facing'] 
                        self.score['Overall'][self.innings]['Batting']['Overs'] = round(self.score['Overall'][self.innings]['Batting']['Overs'] + 0.4, 1)
                        
                        self.score[self.B_innings]['Bowling'][self.bowler]['Overs'] = round(self.score[self.B_innings]['Bowling'][self.bowler]['Overs'] + 0.4, 1)
                        
    
                else:
                
                    self.score['Overall'][self.innings]['Batting']['Not out'][self.score['Overall'][self.innings]['Batting']['Not out'] == self.batsman] = ''
                    
                    print('They have been bowled out. Not even using their overs. What a useless bunch of cunts.')
                    
                    self.score['Overall'][self.innings]['Batting']['Overs'] = round(self.score['Overall'][self.innings]['Batting']['Overs'], 1)
                    
                    self.End_innings() ### How do we make this break to the highest level?
                    
                    return()
    
            #############
            
            ### Not a wicket
            
            #############
    
            else:
            
                ### update overall
                self.score['Overall'][self.innings]['Batting']['Runs'] += b
                
                ### update batsman
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']]['Runs'] += b
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']] ['Balls Faced'] += 1  
                
                ### update bowler
                
                self.score[self.B_innings]['Bowling'][self.bowler]['Runs'] += b
                self.score[self.B_innings]['Bowling'][self.bowler]['Overs'] +=0.1
                
                ''' stuff here '''
                
                
            ### update striker
                
                if b == 1 or b == 3:
                
                    self.score['Overall'][self.innings]['Batting']['Facing'] = list(compress(self.score['Overall'][self.innings]['Batting']['Not out'], [x != self.batsman for x in self.score['Overall'][self.innings]['Batting']['Not out']]))[0]
                    self.batsman = self.score['Overall'][self.innings]['Batting']['Facing']
                    
                    ### update expectation
                    self.Expectation  = self.expected_outcome(bowler = self.bowler, 
                           batsman = self.batsman)
        
                    ### Add duration
             
                    self.Expectation['Overall']['Duration']   =  self.Strike_rate()
                    self.Expectation['Overall']['Runs']       = self.Expectation['Overall']['Outcome'] / self.Expectation['Overall']['Duration']  
                    
                if self.balls_bowled == 6:
                    
                    self.score['Overall'][self.innings]['Batting']['Facing'] = list(compress(self.score['Overall'][self.innings]['Batting']['Not out'], [x != self.batsman for x in self.score['Overall'][self.innings]['Batting']['Not out']]))[0]
                    self.batsman = self.score['Overall'][self.innings]['Batting']['Facing']
                    self.score['Overall'][self.innings]['Batting']['Overs'] = round(self.score['Overall'][self.innings]['Batting']['Overs'] + 0.4, 1)
                    
                    self.score[self.B_innings]['Bowling'][self.bowler]['Overs'] = round(self.score[self.B_innings]['Bowling'][self.bowler]['Overs'] + 0.4, 1)
               
                
        ### check if innings end
        
            if self.innings_number == 2 and self.score['Overall'][self.innings]['Batting']['Runs'] > self.score['Overall'][self.B_innings]['Batting']['Runs']:
                
                print('they have chased down the runs. Just as well. It was a shit target.')
                
                round(self.score['Overall'][self.innings]['Batting']['Overs'], 1)
                
                self.End_innings()
                
                return
        
        if self.score['Overall'][self.innings]['Batting']['Overs'] >= self.duration:
            
            self.score['Overall'][self.innings]['Batting']['Overs'] = round(self.score['Overall'][self.innings]['Batting']['Overs'], 1)
            
            self.End_innings()
            
            return
            
                        
                
#################################################################
                    
### End innings
                    
#################################################################
                
    def End_innings(self):
        
        if self.innings_number == 1:
            
            if self.innings == 'Team1':
                
                self.innings = 'Team2'
                self.B_innings = 'Team1'
            
            elif self.innings == 'Team2':
                
                self.innings = 'Team1'
                self.B_innings = 'Team2'
            
            self.innings_number = 2
            
        elif self.innings_number == 2:
            
            print('What a shit game of cricket; give up you fat ugly fucks.')
    
            return
    

    
    
    
    
    