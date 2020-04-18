# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 22:42:42 2020

@author: Oli
"""

from Upload_v2_18042020 import cricket
from setupsim import setupsim, setupselect

from flask import Flask, render_template, request
app = Flask(__name__)

counter = 0
teams = {}

@app.route("/teams", methods = ['GET', 'POST'])
def teams():
    
    global cricket_match
    global teg
    
    choices = setupselect()
    
    return(render_template('team_select.html', players = choices))
    
@app.route("/test", methods = ['GET', 'POST'])

def test():
    
    global counter
    print(request.form['player1_1'])
    return(str(counter))
    


@app.route("/bollox", methods = ['GET', 'POST'])
def match():

    global counter
    global cricket_match
    global teg
    global teams

    if counter == 0:
        
        teg = setupsim()
        
        teams   = {'Team1':[request.form['player1_1'], request.form['player2_2'], request.form['player3_2'], 
                            request.form['player4_1'], request.form['player5_2'], request.form['player6_2'], 
                            request.form['player7_1'], request.form['player8_2'], request.form['player9_2'], 
                            request.form['player10_1'], request.form['player11_2']],
            'Team2':[request.form['player1_2'], request.form['player2_2'], request.form['player3_2'], 
                            request.form['player4_2'], request.form['player5_2'], request.form['player6_2'], 
                            request.form['player7_2'], request.form['player8_2'], request.form['player9_2'], 
                            request.form['player10_2'], request.form['player11_2']]}
            
        cricket_match = cricket(teams = teams, duration = 40, data = teg['data'])
        counter += 1
        
        ### Build batting cards for rendering

        t1bat = []
        t2bat = []

        for bat in cricket_match.teams['Team1']:

            t1bat.append({'Name':bat, 'Runs':cricket_match.score['Team1']['Batting'][bat]['Runs'],
                      'Ballsfaced':cricket_match.score['Team1']['Batting'][bat]['Balls Faced'],
                      'Howout': cricket_match.score['Team1']['Batting'][bat]['How Out'],
                      'Bowler': cricket_match.score['Team1']['Batting'][bat]['Bowler']})

        for bat in cricket_match.teams['Team2']:

            t2bat.append({'Name':bat, 'Runs':cricket_match.score['Team2']['Batting'][bat]['Runs'],
                      'Ballsfaced':cricket_match.score['Team2']['Batting'][bat]['Balls Faced'],
                      'Howout': cricket_match.score['Team2']['Batting'][bat]['How Out'],
                      'Bowler': cricket_match.score['Team2']['Batting'][bat]['Bowler']})


    ### Build bowling cards for rendering

        t1bowl = []
        t2bowl = []

        for bowl in cricket_match.score['Team1']['Bowling']:

            cricket_match.score['Team1']['Bowling'][bowl]['Name'] = bowl
            t1bowl.append(cricket_match.score['Team1']['Bowling'][bowl])

        for bowl in cricket_match.score['Team2']['Bowling']:

            cricket_match.score['Team2']['Bowling'][bowl]['Name'] = bowl
            t2bowl.append(cricket_match.score['Team2']['Bowling'][bowl])

    ### Current over and commentary

        b_by_b = []
    
        for ball in cricket_match.current_over:

            b_by_b.append(cricket_match.current_over[ball])

    ### possible bowlers
    
        poss_bowlers = []
    
        for bowler in teams['Team2']:
        
            poss_bowlers.append(bowler)

    
    ### render
        return(render_template('bollox.html', t1score = cricket_match.score['Overall']['Team1']['Batting']['Runs'],
                           t1wickets = cricket_match.score['Overall']['Team1']['Batting']['Wickets'],
                           t1overs = cricket_match.score['Overall']['Team1']['Batting']['Overs'],
                           t2score = cricket_match.score['Overall']['Team2']['Batting']['Runs'],
                           t2wickets = cricket_match.score['Overall']['Team2']['Batting']['Wickets'],
                           t2overs = cricket_match.score['Overall']['Team2']['Batting']['Overs'],
                           t1bat    = t1bat, t2bat = t2bat,
                           t1bowl   = t1bowl, t2bowl = t2bowl,
                           ballbyball = b_by_b, bowlers = poss_bowlers))
        
        return()

    elif request.method == 'POST':

        if request.form.get("bowl over") == 'bowl over':
            
            cricket_match.bowler_tactic = request.form['bowler_tactics']
            cricket_match.bat_tactic    = int(request.form['Target_runs'])
            cricket_match.bowler = request.form['next_bowler']
            cricket_match.over()

        elif request.form.get("New Game") == "New Game" and request.form.get("bowl over") != 'bowl over':

            teg           = setupsim()
            cricket_match = cricket(teams = teams, duration = 40, data = teg['data'])

        else:

            pass

    ### Build batting cards for rendering

    t1bat = []
    t2bat = []

    for bat in cricket_match.teams['Team1']:

        t1bat.append({'Name':bat, 'Runs':cricket_match.score['Team1']['Batting'][bat]['Runs'],
                      'Ballsfaced':cricket_match.score['Team1']['Batting'][bat]['Balls Faced'],
                      'Howout': cricket_match.score['Team1']['Batting'][bat]['How Out'],
                      'Bowler': cricket_match.score['Team1']['Batting'][bat]['Bowler']})

    for bat in cricket_match.teams['Team2']:

        t2bat.append({'Name':bat, 'Runs':cricket_match.score['Team2']['Batting'][bat]['Runs'],
                      'Ballsfaced':cricket_match.score['Team2']['Batting'][bat]['Balls Faced'],
                      'Howout': cricket_match.score['Team2']['Batting'][bat]['How Out'],
                      'Bowler': cricket_match.score['Team2']['Batting'][bat]['Bowler']})


    ### Build bowling cards for rendering

    t1bowl = []
    t2bowl = []

    for bowl in cricket_match.score['Team1']['Bowling']:

        cricket_match.score['Team1']['Bowling'][bowl]['Name'] = bowl
        t1bowl.append(cricket_match.score['Team1']['Bowling'][bowl])

    for bowl in cricket_match.score['Team2']['Bowling']:

        cricket_match.score['Team2']['Bowling'][bowl]['Name'] = bowl
        t2bowl.append(cricket_match.score['Team2']['Bowling'][bowl])

    ### Current over and commentary

    b_by_b = []
    
    for ball in cricket_match.current_over:

        b_by_b.append(cricket_match.current_over[ball])

    ### possible bowlers
    
    poss_bowlers = []
    
    for bowler in cricket_match.teams[cricket_match.B_innings]:
        
        if bowler != cricket_match.score['Overall'][cricket_match.innings]['Bowling']['Previous']:
            
            if bowler != cricket_match.WK[cricket_match.B_innings]:
                
                if bowler in cricket_match.score[cricket_match.B_innings]['Bowling'].keys():
                    
                    if cricket_match.score[cricket_match.B_innings]['Bowling'][bowler]['Overs'] < cricket_match.duration / 5:
                
                        poss_bowlers.append(bowler)
                        
                else:
                    
                    poss_bowlers.append(bowler)
    
    ### render
    return(render_template('bollox.html', t1score = cricket_match.score['Overall']['Team1']['Batting']['Runs'],
                           t1wickets = cricket_match.score['Overall']['Team1']['Batting']['Wickets'],
                           t1overs = cricket_match.score['Overall']['Team1']['Batting']['Overs'],
                           t2score = cricket_match.score['Overall']['Team2']['Batting']['Runs'],
                           t2wickets = cricket_match.score['Overall']['Team2']['Batting']['Wickets'],
                           t2overs = cricket_match.score['Overall']['Team2']['Batting']['Overs'],
                           t1bat    = t1bat, t2bat = t2bat,
                           t1bowl   = t1bowl, t2bowl = t2bowl,
                           ballbyball = b_by_b, bowlers = poss_bowlers))
    
app.run()
