# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 18:08:41 2020


TO DO:
    
    1) Toss? Match conditions? -- 6
    2) End of self / who won etc -- 3
    
    --- web interface
    
    3) add team selection -- 2
    5) make sexy -- 5
    
    -- additions
    
    7) Wicket keeping  -- 2
    9) Finish commentary  -- 4
    10)Bowler styles - make part of match set up -- 2
    11) Silly banter -- 5
    12) Add fielding to tactical instructions
    
    

@author: Oli
"""

import numpy as np
import pandas as pd
import os
import random
from itertools import compress
from copy import deepcopy


###############################################################

### Classes

###############################################################

class cricket:
    
    def __init__(self, teams, duration, data):
        
        self.teams    = teams
        self.duration = duration
        self.data     = data
        self.innings  = 'Team1'
        self.bowler   = ''
        self.batsman  = ''
        self.innings_number = 1
        self.current_over = {}
        
        '''
        
    Data should be a dictionary of data frames, with 'Batting' and 
    'Bowling' as the two keys, which then break into 'pred' and 'actual'
        
        '''
        
        ##############################################
        ### data structure to define the match score
        ##############################################
        
        
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
                      
        
        ## extras
        self.score['Team1']['Batting']['Extras'] = 0
        self.score['Team2']['Batting']['Extras'] = 0
        
        ### starting not out batsman
        self.score['Overall']['Team1']['Batting']['Facing'] = self.score['Overall']['Team1']['Batting']['Not out'][0]
        self.score['Overall']['Team2']['Batting']['Facing'] = self.score['Overall']['Team2']['Batting']['Not out'][0]
        
        ### wicket keepers
        
        self.WK = {'Team1': '', 'Team2': ''}
        
    
        ### Instantiate batsman and bowler
        
        if self.innings == 'Team1':
            
            self.B_innings = 'Team2'
            #self.bowler    = random.sample(self.teams[self.B_innings], 1)[0]
            
        elif self.innings == 'Team2':
            
            self.B_innings = 'Team1'
            #self.bowler    = random.sample(self.teams[self.B_innings], 1)[0]
            
        self.batsman = self.score['Overall'][self.innings]['Batting']['Facing']


        ### Commentary
        
        self.commentary_tag = []

###################################################################
        
### Evaluate fielding

###################################################################
        
        team1_fielding = {}
        
        for player in self.teams['Team1']:
            
            team1_fielding[player] = int(self.data['Batting']['pred'].loc[self.data['Batting']['pred']['id'] == player, :]['main.team'].iloc[0])
    
        team2_fielding = {}
        
        for player in self.teams['Team2']:
            
            team2_fielding[player] = int(self.data['Batting']['pred'].loc[self.data['Batting']['pred']['id'] == player, :]['main.team'].iloc[0])
    
        self.fielding = {'Team1':{'Overall': 38.5 - np.sum(list(team1_fielding.values())), 'Individual': team1_fielding}, 
                                  'Team2':{'Overall': 38.5 - np.sum(list(team2_fielding.values())), 'Individual': team2_fielding}}
    
    
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
            
            
        ### batting  - early vulnerability
         
        vulnerkey = batter_pred['main.team'].iloc[0]
        bp        = batter_dat.iloc[:, 12:18]
        bat_vul   = float(bp.iloc[:, (vulnerkey-1)])     
        
        ### batting not outs
        bp        = batter_dat.iloc[:, 23:29]
        bat_no    = float(bp.iloc[:, (vulnerkey-1)])  
        
        
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
        
                
        ################################################
        
        ### Create expectations
        
        ################################################

        bowl_ex['Overall'] = bowl_ex['SR'] * (bowl_ex['Econ'] / 6)
        
        ### adjust for not outs in batsman expectation
        
        bat_ex = bat_ex / (1-(bat_no/1.5))
        
        ### adjust batting for batsman is in
                
        bat_ex = float(((1-bat_vul)*bat_ex) + (bat_vul*bat_ex * (abs(np.random.normal(0.66, 0.5, 1)[0]) * 1/4.5 * (self.score[self.innings]['Batting'][self.batsman]['Runs'] + self.score[self.innings]['Batting'][self.batsman]['Runs'])/2)))    
 
        ##################################################
        
        ### Make combined expectation
        
        ##################################################
        
        ### weighted bowling importance
        
        bowl_team_av = {'1':24, '2':22.5, '3':21.5, '4':20.5, '5':19, '6':17}
        
        bowl_ex['Adjusted'] = bowl_ex['Overall'] - bowl_team_av[str(team_level)]
    
        Expected_outcome = {'Overall': {'Outcome':(np.max([0, bowl_ex['Adjusted'] + bat_ex]))}, 
                           'Bat': bat_ex, 'Bowl':bowl_ex}
        
        
        return(Expected_outcome)
        
        
##########################################################
        
### Determine expected duration
        
##########################################################
        
    def Strike_rate(self):
            
        '''
        Adjusts batting strike rate for settled rating and over of the innings
        '''
        
        #predictions
        batter_pred = self.data['Batting']['pred'].loc[(self.data['Batting']['pred']['id'] == self.batsman), :]
        
        #actual
        batter_dat = self.data['Batting']['actual'].loc[(self.data['Batting']['actual']['0'] == self.batsman), :]
        
        ### underlying Strike rate
         
        SRkey     = batter_pred['main.team'].iloc[0]
        bp        = batter_dat.iloc[:, 45:51]
        bat_SR    = float(bp.iloc[:, (SRkey-1)])
        
        bp        = batter_dat.iloc[:, 1:7]
        
        if float(bp.iloc[:, (SRkey-1)]) != 0 and not float(bp.iloc[:, (SRkey-1)]) == False:
            
            bat_SR    = (bat_SR / float(bp.iloc[:, (SRkey-1)])) / 3.5 ## is four the right parameter here?
       
        else:
            
            bat_SR    = float(abs(np.random.normal(0.25, 0.005, 1)[0]))
        
        
        ############################################################################
        
        ### stage of innings
        
        ############################################################################
        
        if self.score['Overall'][self.innings]['Batting']['Overs'] <= self.duration / 10:
            
            bat_SR = bat_SR * 0.5
        
        elif self.score['Overall'][self.innings]['Batting']['Overs'] <= self.duration / 4:
            
            bat_SR = bat_SR * 0.6
        
        elif self.score['Overall'][self.innings]['Batting']['Overs'] <= self.duration / 3:
            
            bat_SR = bat_SR * 0.8
        
        elif self.score['Overall'][self.innings]['Batting']['Overs'] >= self.duration * 0.75:
            
            bat_SR = bat_SR * 1.25
            
        else:
            
            pass
        
        
        #############################################################
        #adjust batsman expected return for stage of innings
        #############################################################
 
        Openerkey = batter_pred['main.team'].iloc[0]
        bp        = batter_dat.iloc[:, 45:51]
        bat_op    = float(bp.iloc[:, (Openerkey-1)])
    
        if self.score['Overall'][self.innings]['Batting']['Overs'] < 5:
            
            if bat_op >= 3.5:
            
                self.Expectation['Bat'] = self.Expectation['Bat'] * 0.66
                self.commentary_tag.append('This guy really isnt an opener.')
    
        elif self.score['Overall'][self.innings]['Batting']['Overs'] < 10:
            
            if bat_op >= 4:
            
                self.Expectation['Bat'] = self.Expectation['Bat'] * 0.8
                self.commentary_tag.append('The middle order are exposed early.')
    
            
        ### Strike rate calculations
            
        Expected_duration = (self.Expectation['Bowl']['SR'] + self.Expectation['Bat'] / bat_SR) / 2  
            
        self.bat_SR = bat_SR
        
        return(Expected_duration)


###########################################################
            
### Bowl a ball - accounts for fielding

###########################################################
            
    def ball(self):
        
        wicket = random.random() < 1/self.Expectation['Overall']['Duration']

        if wicket == True:
            
            ############
            ### account for fielding
            ############
            
            if self.fielding[self.B_innings]['Overall'] < 0:
                
                if random.random() > abs((self.fielding[self.B_innings]['Overall'] * 5 / 100)):
                    
                    return('wicket')
                    
                else:
                    
                    self.commentary_tag.append('Bad dropped catch')
                    
                    return(np.random.poisson(0.5, 1)[0])
            
            
            elif self.fielding[self.B_innings]['Overall'] == 0:
                
                if random.random() > 0.1:
                    
                    return('wicket')
                    
                else:
                    
                    self.commentary_tag.append('Bad dropped catch')
                    
                    return(np.random.poisson(0.5, 1)[0])
                
            
            else:
                
                if random.random() > float(np.min([0.025, abs((0.05/self.fielding[self.B_innings]['Overall']) / 100)])):
                    
                    return('wicket')
                    
                else:
                    
                    self.commentary_tag.append('Sharp chance goes down')
                    
                    return(np.random.poisson(0.5, 1)[0])

        elif wicket == False:
            
            runs = random.random() < self.Expectation['Overall']['Runs']/2.25 ### Is this the right constant?
            
            if runs:
                
                boundary = random.random() < 0.35
                
                if boundary:
                    
                    six  = random.random() < 0.10
                    
                    if six:
                    
                        runs = 6
                        
                    else:
                        
                        runs = 4
                        
                        
                    #######
                    ## Account for fielding
                    #######    
                    
                    if self.fielding[self.B_innings]['Overall'] > 0:
                        
                        if random.random() < (self.fielding[self.B_innings]['Overall'] * 2.5 / 100):
                            
                            runs = int(np.random.poisson(0.75, 1)[0])
                            
                            self.commentary_tag.append('Saved a boundary')
                                                           
                    return(runs)
                        
                else:
                    
                    run_rand = random.random()
                    
                    if run_rand <= 0.65:
                        
                        runs = 1
                        
                    elif run_rand <= 0.95:
                        
                        runs = 2
                        
                    else:
                        
                        runs = 3
                    
            else:
                
                runs = 0
                
            
            #######
            ## Account for fielding
            #######   
            
            if self.fielding[self.B_innings]['Overall'] > 0 and runs > 0:
                        
                ### good
                
                if random.random() < (self.fielding[self.B_innings]['Overall'] * 2.5 / 100):
                            
                    runs = np.max([0, runs - np.max([int(np.random.poisson(1, 1)[0]), 1])])
                    
                    self.commentary_tag.append('Fielding saves runs')
                    
                    
            elif self.fielding[self.B_innings]['Overall'] > 0 and runs == 0:
                
                    if random.random() < 0.001 - abs(self.fielding[self.B_innings]['Overall'] / 750):
                        
                        self.commentary_tag.append('Screamer!')
                        
                        return('wicket')
            
            
                ### bad - misfields
            
            if runs > 0:
            
                if random.random() < 0.05 - abs(self.fielding[self.B_innings]['Overall'] / 100):
                    
                    runs = np.min([4, runs + random.sample([1, 1, 1, 2, 4], 1)[0]])
                    
                    self.commentary_tag.append('A poor misfield')
                                               
                
                ### ugly - buzzers
                
                if random.random() < 0.01 - abs(self.fielding[self.B_innings]['Overall'] / 200):
    
                    runs = runs + random.sample([1, 1, 2, 4], 1)[0]
                    
                    self.commentary_tag.append('Buzzers!')
                    
            
            ### Add extras
            
            if runs == 0:
                              
                if random.random() < self.Expectation['Bowl']['Econ'] / 150:
                    
                        runs = (random.sample(['Wide', 'No Ball'], 1)[0])
                        
                elif self.bowler_tactic == 'tie him down':
                    
                    if random.random() < self.Expectation['Bowl']['Econ'] / 150:
                        
                        return('Wide')
                        
                elif self.bowler_tactic == 'bowl at the stumps':
                    
                    if random.random() < self.Expectation['Bowl']['Econ'] / 60:
                        
                        return('Wide')
                      
            return(runs)
          
########################################################################
            
### Define fall of wicket procedure
            
########################################################################
            
    def FOW(self):
    
        ''' make this more nuanced'''
    
        How_out = random.random()
    
        if How_out < 0.325:
        
            How_out = 'Bowled'
            
            self.commentary_tag.append('Bowled')
            
        elif How_out < 0.775:
        
            How_out = 'Caught'
            
            self.commentary_tag.append('Caught')
        
        elif How_out < 0.96:
        
            How_out = 'LBW'
            
            self.commentary_tag.append('LBW')
               
        elif How_out < 0.999:
        
            How_out = 'Stumped'
            
            self.commentary_tag.append('Stumped')
        
        else:
        
            How_out = 'Obstructing the Field'
            
            self.commentary_tag.append('Obstructing')
    
        return(How_out)
  


########################################################################
        
### Player tactical inputs
        
########################################################################

    def tactical_inputs(self, **kwargs):
            
        if random.random() < 0.01:
            
            self.commentary_tag.append(str('Comment about bat tactic:' + str(self.bowler_tactic)))
            
        if random.random() < 0.01:
            
            self.commentary_tag.append(str('Comment about bat tactic:' + str(self.bat_tactic)))
    
    
########################################################################
        
### Adjust for tactics
        
########################################################################
        
    def tactical_battle(self):
        
        self.straightone = False
        self.crazyrun    = False
        self.stupidshot  = False
        
        ## negative = batsman
        
        self.duration_ratio = (self.Expectation['Overall']['Duration'] - self.Expectation['Bowl']['SR']) / (self.Expectation['Overall']['Duration'] + self.Expectation['Bowl']['SR'])
        self.econ_ratio     = (self.bat_tactic - (self.Expectation['Overall']['Runs']*6)) / ((self.Expectation['Overall']['Runs']*6) + self.bat_tactic)
         
        #######################################
        
        ### bowler tactics
        
        #######################################
        
        if random.random() <= 0.5 + (1 - (self.Expectation['Overall']['Outcome'] / self.Expectation['Bowl']['Overall'])):
        
            if self.b == 'wicket':
            
                if self.duration_ratio < 0:
                
                    if self.bowler_tactic == 'tie him down':
                    
                        if random.random() < abs(self.duration_ratio):
                        
                            self.commentary_tag.append('Played and missed!')
                        
                            self.b = int(0)
             
                
            elif self.b in [1, 2, 3, 4, 6] and self.bowler_tactic == 'tie him down' and self.duration_ratio < 0:
                
                if random.random() < abs(self.duration_ratio):
                    
                    self.b = random.sample([0, 0, 0, 0, 0, 0, 1, 1, 1, 2], 1)[0]
                    
                    if self.b == 0:
                            
                        self.commentary_tag.append("Can't beat the infield")
                            
                    else:
                            
                        self.commentary_tag.append("Captain has the sweepers out")
        
                
            elif self.b == 0 and self.duration_ratio > 0:
                        
                if self.bowler_tactic == 'bowl at the stumps':
                    
                    if random.random() < abs(self.duration_ratio) / 10:
                        
                        self.commentary_tag.append('You miss, I hit!')
                        
                        self.straightone = True
                    
                        self.b = 'wicket'
                        
                elif self.bowler_tactic == 'tie him down' and self.econ_ratio < 0:
                    
                    if random.random() < 0.5:
                        
                        self.commentary_tag.append("Left alone")
                    
                        
            elif self.b == 0 and self.duration_ratio < 0:
                
                if self.bowler_tactic == 'bowl at the stumps':
                
                    if random.random() < abs(self.duration_ratio):
                        
                        self.commentary_tag.append("Too straight, that's easy runs")
                        
                        self.b = random.sample([1, 1, 1, 2, 2, 4], 1)[0]
                            
        ###############
        
        # Death bowling
        
        ###############
        
        
        
            
        #########################################################
              
        ### batsman tactics
        
        ##########################################################
        
        ### Negative
        
        else:
            
            if self.econ_ratio < 0.15:
                
                if self.b == 'wicket':
                    
                    if random.random() < 0.75 * abs(self.econ_ratio):
                        
                        self.b = 0
                        
                        self.commentary_tag.append("Dogged batting! A good nut, and well played")
                        
                if self.b in [1, 2, 3, 4, 6]:
                    
                    if random.random() < abs(self.econ_ratio):
                        
                        self.b = random.sample([0, 0, 0, 0, 0, 0, 1, 1, 1, 2], 1)[0]
                        
                        self.commentary_tag.append("Negative batting")
        
        
        ### positive
        
        
        
            elif self.econ_ratio > 0.15 and self.econ_ratio <= 0.5 and self.b == 0:
            
                who_fields = random.sample(list(self.fielding[self.B_innings]['Individual']), 1)[0]
            
                if random.random() >= 1- (self.econ_ratio*1.5):
                
                    self.b = 1
                
                    self.commentary_tag.append('Stolen single')              
                            
                elif random.random() >= 1 - ((self.econ_ratio / 100) + (6-(self.fielding[self.B_innings]['Individual'][who_fields])) / 100):               
                
                    self.b = 'wicket'
                
                    self.commentary_tag.append(['A Crazy Run!', who_fields])
                    self.crazyrun = True
                
        ### slogging
            
            elif self.econ_ratio > 0.5 and self.econ_ratio <= 1 and self.b == 0:
                
                if self.duration_ratio < 0:
            
                    if random.random() >= 1- (self.econ_ratio/3):
                
                        self.commentary_tag.append("Gone for the big shot!")
                
                        if random.random() >= 1 - 0.42:
                
                            self.b = random.sample([1, 2, 4, 4, 6], 1)[0]
                
                        elif random.random()>= 1 - 0.5:
                
                            self.commentary_tag.append('Swing and a miss!')
                
                        else: 
                
                            self.b = 'wicket'
                
                            self.commentary_tag.append('Thrown his wicket away!')
                
                            self.stupidshot  = True
                    
                    
            elif self.duration_ratio > 0:
            
                if random.random() >= 1- (self.econ_ratio/3):
                
                    self.commentary_tag.append("Gone for the big shot!")
                
                    if random.random() >= 1 - 0.33:
                
                        self.b = random.sample([1, 2, 4, 4, 6], 1)[0]
                
                    elif random.random()>= 1 - 0.5:
                
                        self.commentary_tag.append('Swing and a miss!')
                
                    else: 
                
                        self.b = 'wicket'
                
                        self.commentary_tag.append('Thrown his wicket away!')
                
                        self.stupidshot  = True
                    
         
        ### Stupid
            
            elif self.econ_ratio > 1 and self.b == 0:
                
                if self.duration_ratio < 0:
            
                    if random.random() >= 1- (self.econ_ratio/2):
                
                        self.commentary_tag.append("Gone for the big shot!")
                
                    if random.random() >= 1 - 0.5:
                
                        self.b = random.sample([1, 2, 4, 4, 6], 1)[0]
                
                    elif random.random()>= 1 - 0.33:
                
                        self.commentary_tag.append('Swing and a miss!')
                
                    else: 
                
                        self.b = 'wicket'
                
                        self.commentary_tag.append('Thrown his wicket away!')
                
                        self.stupidshot  = True
                    
                    
            elif self.duration_ratio > 0:
            
                if random.random() >= 1- (self.econ_ratio/2):
                
                    self.commentary_tag.append("Gone for the big shot!")
                
                    if random.random() >= 1 - 0.33:
                
                        self.b = random.sample([1, 2, 4, 4, 6], 1)[0]
                
                    elif random.random()>= 1 - 0.33:
                
                        self.commentary_tag.append('Swing and a miss!')
                
                    else: 
                
                        self.b = 'wicket'
                
                        self.commentary_tag.append('Thrown his wicket away!')
                
                        self.stupidshot  = True
                    
            
                            
########################################################################
        
### Bowl an over
        
########################################################################
        
        
    def over(self):
        
        self.current_over= {}
        self.commentary_tag = []
        
        ### update bowler - defined in the UI
            
        self.score['Overall'][self.innings]['Bowling']['Previous'] = self.bowler       
        self.balls_bowled = 0
        
        ##########################################
        
        ### set up match conditions
        
        ##########################################
        
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
            
            ### user tactics
            self.tactical_inputs()
            
            ### commentary
            self.commentary_tag = []
            
            ### Ball is bowled!
            self.b = self.ball()
                        
            ### user tactics updates fundamentals
            self.tactical_battle()


            #######################################################
            
            ### update scorecard
            
            #######################################################

            #####################################
            ### deal with wides and no balls
            #####################################
            
            if self.b in ['Wide', 'No Ball']:
            
                self.commentary_tag.append(self.b)
                
                if self.b == 'Wide':
                
                    self.extra = 'Wide'
                    
                if self.b == 'No Ball':
                    
                    self.extra = 'No Ball'
                    
                self.b = random.sample([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5], 1)[0]
                
                self.score[self.B_innings]['Bowling'][self.bowler]['Runs'] += self.b
                self.score[self.B_innings]['Bowling'][self.bowler]['Buzzers'] += self.b
                self.score[self.innings]['Batting']['Extras'] += self.b
                self.score['Overall'][self.innings]['Batting']['Runs'] += self.b
                
                self.current_over[str(str(self.balls_bowled) + self.extra)] = {'Delivery':round(self.score['Overall'][self.innings]['Batting']['Overs'], 1), 
                              'Bowler': self.bowler, 'Batsman':self.batsman, 'Outcome':self.b, 'Commentary': deepcopy(self.commentary_tag[0])}
                
                continue
                
                
            else:
                
                self.extra = ''
                            
        
            ###################
            ### update balls bowled
            ###################
        
            self.score['Overall'][self.innings]['Batting']['Overs'] = self.score['Overall'][self.innings]['Batting']['Overs'] + 0.1
            self.balls_bowled += 1
            
            
            ######
            # Commentary
            ######
        
            self.current_over[str(str(self.balls_bowled) + self.extra)] = {'Delivery':round(self.score['Overall'][self.innings]['Batting']['Overs'], 1), 
                              'Bowler': self.bowler, 'Batsman':self.batsman, 'Outcome':self.b}
            
        
            ##############
            
            ### Wicket?
            
            ##############
        
            if self.b == 'wicket':
                
                ### how out
                
                if self.straightone == False: ## account for tactical battle
                
                    howout = self.FOW()
                    
                elif self.crazyrun == True:
                    
                    howout = 'Run Out'
                    
                else:
                    
                    howout = random.sample(['Bowled', 'LBW'], 1)[0]
                    
                    
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']] ['How Out'] = howout
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']] ['Bowler']  = self.bowler
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']] ['Balls Faced'] += 1  
                
                ### update bowler
                self.score[self.B_innings]['Bowling'][self.bowler]['Overs'] +=0.1
        
        
            if self.b == 'wicket':
            
                ''' Add details of run outs'''
                
                self.score['Overall'][self.innings]['Batting']['Wickets'] += 1
                
                if not howout in ['Run Out', 'Obstructed the Field']:
                    
                    self.score[self.B_innings]['Bowling'][self.bowler]['Wickets'] += 1 
            
                if self.score['Overall'][self.innings]['Batting']['Wickets'] < 10:
                    
                    which = np.where(np.array(self.score['Overall'][self.innings]['Batting']['Not out']) == self.batsman)[0][0]
                    
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
                    
                    self.score['Overall'][self.innings]['Batting']['Overs'] = round(self.score['Overall'][self.innings]['Batting']['Overs'], 1)
                    
                    self.End_innings() ### How do we make this break to the highest level?
                    
                    return()
    
            #############
            
            ### Not a wicket
            
            #############
    
            else:
            
                ### update overall
                self.score['Overall'][self.innings]['Batting']['Runs'] += self.b
                
                ### update batsman
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']]['Runs'] += self.b
                self.score[self.innings]['Batting'][self.score['Overall'][self.innings]['Batting']['Facing']] ['Balls Faced'] += 1  
                
                ### update bowler
                
                self.score[self.B_innings]['Bowling'][self.bowler]['Runs'] += self.b
                self.score[self.B_innings]['Bowling'][self.bowler]['Overs'] +=0.1
                
                ''' stuff here '''
                
                
            ### update striker
                
                if self.b == 1 or self.b == 3:
                
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
               
        
            if len(self.commentary_tag) == 0:
            
                self.commentary_tag.append(' ')
            
        
            self.current_over[str(str(self.balls_bowled) + self.extra)]['Commentary'] = deepcopy(self.commentary_tag[0])


        #######################################################################
        
        ### check if innings end
        
        #######################################################################
        
            if self.innings_number == 2 and self.score['Overall'][self.innings]['Batting']['Runs'] > self.score['Overall'][self.B_innings]['Batting']['Runs']:
                
                round(self.score['Overall'][self.innings]['Batting']['Overs'], 1)
                
                self.End_innings()
                
                return
        
        if self.score['Overall'][self.innings]['Batting']['Overs'] >= self.duration:
            
            self.score['Overall'][self.innings]['Batting']['Overs'] = round(self.score['Overall'][self.innings]['Batting']['Overs'], 1)
            
            self.End_innings()
            
            return

#################################################################
            
### Translate commentary key into words

#################################################################
               
    def commentary_update(self):
        
        pass
 
               
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
            
            self.over = lambda: 2*2 ### removes bowl overs function
    
            return
    

    
    
    
    
    