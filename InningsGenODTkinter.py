# InningsGenODTkinter.py
# A beautiful, modern Tkinter GUI application for ODI & T20I Cricket Match Simulation.

import random
import threading
import queue
import time
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import datetime
import csv
import os
from operator import itemgetter
from tabulate import tabulate

# ---------------------------------------------------------
# CONSTANTS & DEFAULTS
# ---------------------------------------------------------
DARK_BG = "#1e1e2e"       # Deep charcoal/navy
CARD_BG = "#252538"       # Slightly lighter for containers
TEXT_FG = "#cdd6f4"       # Soft white text
ACCENT_BLUE = "#89b4fa"   # Primary highlight
ACCENT_GREEN = "#a6e3a1"  # Success/runs
ACCENT_RED = "#f38ba8"    # Wickets
ACCENT_YELLOW = "#f9e2af" # Milestones
BORDER_COLOR = "#313244"  # Subtle borders


# ---------------------------------------------------------
# GLOBAL TOURNAMENT STATS
# ---------------------------------------------------------
battingStatsODI = {}
bowlingStatsODI = {}
battingStatsT20 = {}
bowlingStatsT20 = {}
matchImpactBatting = {}
matchImpactBowling = {}

# ---------------------------------------------------------
# CUMULATIVE STATS HELPERS
# ---------------------------------------------------------
def generateScorecard(innings):
    global battingStatsODI, battingStatsT20, matchImpactBatting
    scorecard = []
    for batter, prog in innings['batting_xi'].items():
        if prog:
            name = prog[0]
            team = innings['team']
            runs = sum([p for p in prog if isinstance(p, int)])
            balls = len(prog) - 1
            singles = prog.count(1)
            doubles = prog.count(2)
            triples = prog.count(3)
            fours = prog.count(4)
            sixes = prog.count(6)
            out_status = "not out" if prog[-1] != "W" else "out"
            out = 1 if out_status == "out" else 0
            fifty = 1 if 50 <= runs < 100 else 0
            century = 1 if runs >= 100 else 0
            sr = round((runs / balls) * 100, 2) if balls > 0 else 0.0
            
            if balls > 0:
                runsAdjustment = (runs / innings['runs']) * 100
                SRAdjustment = (runs / balls - 100) / 2
                milestoneBonus = 0
                if 50 <= runs < 100:
                    milestoneBonus = 10
                elif runs >= 100:
                    milestoneBonus = 20
                battingImpact = runsAdjustment + SRAdjustment + milestoneBonus
                matchImpactBatting[name] = battingImpact
                
                scorecard.append([
                    name, runs, balls, fours, sixes, sr, out_status
                ])
                
                if innings['mode'] == 'ODI':
                    if name not in battingStatsODI:
                        battingStatsODI[name] = [team, 1, runs, balls, singles, doubles, triples, fours, sixes, out, fifty, century]
                    else:
                        battingStatsODI[name][1] += 1
                        battingStatsODI[name][2] += runs
                        battingStatsODI[name][3] += balls
                        battingStatsODI[name][4] += singles
                        battingStatsODI[name][5] += doubles
                        battingStatsODI[name][6] += triples
                        battingStatsODI[name][7] += fours
                        battingStatsODI[name][8] += sixes
                        battingStatsODI[name][9] += out
                        battingStatsODI[name][10] += fifty
                        battingStatsODI[name][11] += century
                else:  # T20
                    if name not in battingStatsT20:
                        battingStatsT20[name] = [team, 1, runs, balls, singles, doubles, triples, fours, sixes, out, fifty, century]
                    else:
                        battingStatsT20[name][1] += 1
                        battingStatsT20[name][2] += runs
                        battingStatsT20[name][3] += balls
                        battingStatsT20[name][4] += singles
                        battingStatsT20[name][5] += doubles
                        battingStatsT20[name][6] += triples
                        battingStatsT20[name][7] += fours
                        battingStatsT20[name][8] += sixes
                        battingStatsT20[name][9] += out
                        battingStatsT20[name][10] += fifty
                        battingStatsT20[name][11] += century
    return scorecard

def BowlingFigures(innings):
    global bowlingStatsODI, bowlingStatsT20, matchImpactBowling
    bowlingFigures = []
    maiden = ['dot', 'dot', 'dot', 'dot', 'dot', 'dot']
    for bowler, item in innings['bowlers'].items():
        name = item['prog'][0]
        runs = 0
        maidens = 0
        balls = item['balls']
        overs = f"{item['overs']}.{item['balls'] % 6}"
        wickets = item['wickets']
        noballs = item['no balls']
        wides = item['wides']
        team = innings['opp']
        wick5 = 1 if wickets >= 5 else 0
        
        for i in item['prog']:
            if i == 'single': runs += 1
            elif i == 'double': runs += 2
            elif i == 'triple': runs += 3
            elif i == 'four': runs += 4
            elif i == 'six': runs += 6
            elif i == 'noball': runs += 1
            elif i == 'wide': runs += 1
            
        for i in range(len(item['prog']) - 5):
            if item['prog'][i:i+6] == maiden:
                maidens += 1
                
        if balls > 0:
            wicketAdjustment = (wickets / innings['wickets']) * 10 if innings['wickets'] > 0 else 0
            economyAdjustment = ((innings['runs'] / (innings['balls']) * 6) - (runs / (balls) * 6) * 5)
            bowlingImpact = wicketAdjustment + economyAdjustment
            matchImpactBowling[name] = bowlingImpact
            
            bowlingFigures.append([name, overs, maidens, runs, wickets, noballs, wides])
            
            if innings['mode'] == 'ODI':
                if name not in bowlingStatsODI:
                    bowlingStatsODI[name] = [team, 1, balls, maidens, runs, wickets, noballs, wides, wick5]
                else:
                    bowlingStatsODI[name][1] += 1
                    bowlingStatsODI[name][2] += balls
                    bowlingStatsODI[name][3] += maidens
                    bowlingStatsODI[name][4] += runs
                    bowlingStatsODI[name][5] += wickets
                    bowlingStatsODI[name][6] += noballs
                    bowlingStatsODI[name][7] += wides
                    bowlingStatsODI[name][8] += wick5
            else:  # T20
                if name not in bowlingStatsT20:
                    bowlingStatsT20[name] = [team, 1, balls, maidens, runs, wickets, noballs, wides, wick5]
                else:
                    bowlingStatsT20[name][1] += 1
                    bowlingStatsT20[name][2] += balls
                    bowlingStatsT20[name][3] += maidens
                    bowlingStatsT20[name][4] += runs
                    bowlingStatsT20[name][5] += wickets
                    bowlingStatsT20[name][6] += noballs
                    bowlingStatsT20[name][7] += wides
                    bowlingStatsT20[name][8] += wick5
    return bowlingFigures

def getManOfTheMatch():
    global matchImpactBatting, matchImpactBowling
    impactList = {}
    for i, j in matchImpactBatting.items():
        impactList[i] = j
    for i, j in matchImpactBowling.items():
        if i in impactList:
            impactList[i] += j
        else:
            impactList[i] = j
    if not impactList:
        return "N/A"
    MOTM = max(impactList, key=impactList.get)
    
    # Write Man of the Match details to generatedStats.txt
    with open("generatedStats.txt", "a", encoding="utf-8") as f:
        f.write("Man of the match: " + MOTM + "\n")
        f.write("---------------------------------------------------------------------------------------------------\n")
        
    matchImpactBatting.clear()
    matchImpactBowling.clear()
    return MOTM

# ---------------------------------------------------------
# FILE SAVE UTILITIES
# ---------------------------------------------------------
def saveScorecard(team, innings, scorecard, bowlingFigures, session_name=None):
    with open("generatedStats.txt", "a", encoding="utf-8") as f:
        if session_name:
            f.write(f"\n{session_name}:\n")
        f.write(f"\n{team} innings {innings['balls']//6}.{innings['balls']%6} overs\n")
        f.write(f"{innings['runs']}/{innings['wickets']}\n\n")
        headers = ["Batsman", "Runs", "Balls", "4s", "6s", "SR", "Status"]
        f.write(tabulate(scorecard, headers=headers, tablefmt="pretty"))
        f.write("\n")
        did_not_bat = [prog[0] for prog in innings['batting_xi'].values() if len(prog) - 1 == 0]
        if did_not_bat:
            f.write("Did not bat: " + ", ".join(did_not_bat) + "\n")
        f.write(f"Extras: {innings['no balls']} nb, {innings['wides']} wd, "
              f"{innings['leg byes']} lb, {innings['byes']} b\n")
        
        fow = []
        runs = 0
        legal_deliveries = 0
        for i, ball in enumerate(innings['balls progression'], 1):
            if ball == "single":
                runs += 1
                legal_deliveries += 1
            elif ball == "double":
                runs += 2
                legal_deliveries += 1
            elif ball == "triple":
                runs += 3
                legal_deliveries += 1
            elif ball == "four":
                runs += 4
                legal_deliveries += 1
            elif ball == "six":
                runs += 6
                legal_deliveries += 1
            elif ball == "noball":
                runs += 1
            elif ball == "wide":
                runs += 1
            elif ball.startswith("legbye"):
                r = int(ball.replace("legbye", ""))
                runs += r
                legal_deliveries += 1
            elif ball.startswith("bye"):
                r = int(ball.replace("bye", ""))
                runs += r
                legal_deliveries += 1
            elif isinstance(ball, int):
                runs += ball
                legal_deliveries += 1
            elif ball == "wicket":
                legal_deliveries += 1
                fow.append(f"{runs}/{len(fow)+1} ({legal_deliveries//6}.{legal_deliveries%6} ov)")
        if fow:
            f.write("Fall of wickets: " + ", ".join(fow) + "\n")
        if innings['partnerships']:
            f.write("Partnerships: \n")
            p_headers = ["Batsman 1", "Batsman 2", "Runs", "Balls"]
            f.write(tabulate(innings['partnerships'], headers=p_headers, tablefmt="pretty"))
            f.write("\n")
        f.write("Bowling: \n")
        b_headers = ["Bowler","Overs","Maidens","Runs","Wickets","No balls","Wides"]
        f.write(tabulate(bowlingFigures, headers=b_headers, tablefmt="pretty"))
        f.write("\n\n")

def saveStats():
    global battingStatsODI, bowlingStatsODI, battingStatsT20, bowlingStatsT20
    with open("Stats.txt", "w", encoding="utf-8") as x:
        x.write("ODI Stats: \n")
        headers = ["Batsman","Team","Inns","Runs","Balls","1s","2s","3s","4s","6s","Outs","50s","100s","Avg","S/R"]
        statTable = []
        for batter, figures in battingStatsODI.items():
            stat = [batter] + figures
            stat.append(round(figures[2]/figures[9], 2) if figures[9] != 0 else '∞')
            stat.append(round(figures[2]/figures[3]*100, 2) if figures[3] != 0 else 0.0)
            statTable.append(stat)
        x.write(tabulate(sorted(statTable, key=itemgetter(3), reverse=True), headers=headers, tablefmt="pretty"))
        x.write("\n\n")
        
        headers = ["Bowlers","Team","Inns","Ovrs","Mdns","Runs","Ws","NBs","WDs","5fers","Avg","S/R"]
        statTable = []
        for bowler, figures in bowlingStatsODI.items():
            stat = [bowler]
            stat.extend(figures[0:2])
            stat.append(str(figures[2]//6)+'.'+str(figures[2]%6))
            stat.extend(figures[3:])
            stat.append(round(figures[4]/figures[5], 2) if figures[5] != 0 else '∞')
            stat.append(round(figures[2]/figures[5], 2) if figures[5] != 0 else '∞')
            statTable.append(stat)
        x.write(tabulate(sorted(statTable, key=lambda s: (-s[6], s[5])), headers=headers, tablefmt="pretty"))
        x.write("\n\n")
        
        x.write("T20I Stats: \n")
        headers = ["Batsman","Team","Inns","Runs","Balls","1s","2s","3s","4s","6s","Outs","50s","100s","Avg","S/R"]
        statTable = []
        for batter, figures in battingStatsT20.items():
            stat = [batter] + figures
            stat.append(round(figures[2]/figures[9], 2) if figures[9] != 0 else '∞')
            stat.append(round(figures[2]/figures[3]*100, 2) if figures[3] != 0 else 0.0)
            statTable.append(stat)
        x.write(tabulate(sorted(statTable, key=itemgetter(3), reverse=True), headers=headers, tablefmt="pretty"))
        x.write("\n\n")
        
        headers = ["Bowlers","Team","Inns","Ovrs","Mdns","Runs","Ws","NBs","WDs","5fers","Avg","S/R"]
        statTable = []
        for bowler, figures in bowlingStatsT20.items():
            stat = [bowler]
            stat.extend(figures[0:2])
            stat.append(str(figures[2]//6)+'.'+str(figures[2]%6))
            stat.extend(figures[3:])
            stat.append(round(figures[4]/figures[5], 2) if figures[5] != 0 else '∞')
            stat.append(round(figures[2]/figures[5], 2) if figures[5] != 0 else '∞')
            statTable.append(stat)
        x.write(tabulate(sorted(statTable, key=lambda s: (-s[6], s[5])), headers=headers, tablefmt="pretty"))
        x.write("\n\n")

# ---------------------------------------------------------
# SIMULATION ENGINE (RUNS IN THREAD)
# ---------------------------------------------------------
class SimulationState:
    def __init__(self):
        self.delay_seconds = 0.5
        self.pause_event = threading.Event()
        self.pause_event.set()  # set means running
        self.stop_event = threading.Event()
        self.step_event = threading.Event()
        self.instant_simulation = False

def simulate_innings_ball_by_ball(queue, team, oppTeam, teamXI, bowlers, degree, mode, inning_num, target, sim_state, players_database=None, placeholder_weights=None):
    batting_xi = {idx+1: [name] for idx, name in enumerate(teamXI)}
    bowling_list = list(bowlers.keys())
    striker = 1
    non_striker = 2
    next_batter = 3

    balls = 0
    maxQuota = 4 if mode == 'T20' else 10
    totalBalls = 120 if mode == 'T20' else 300
    runs = 0
    wickets = 0
    dots = singles = doubles = triples = fours = sixes = noballs = wides = legbyes = byes = 0
    ballsProgression = []
    free_hit = False
    balls_in_over = 0
    partnerships = []
    currentPartnershipRuns = 0
    currentPartnershipBalls = 0

    # Initialize bowlers
    currentBowler = len(bowling_list) - 1
    currentBowlerOtherEnd = len(bowling_list) - 2

    current_over_balls = []

    queue.put(("inning_start", {
        "inning_num": inning_num,
        "team": team,
        "oppTeam": oppTeam,
        "mode": mode,
        "target": target
    }))

    while balls < totalBalls and wickets < 10 and (target is None or runs <= target):
        if sim_state.stop_event.is_set():
            return None

        # Pause handling
        if not sim_state.pause_event.is_set() and not sim_state.instant_simulation:
            while not sim_state.pause_event.is_set() and not sim_state.stop_event.is_set():
                stepped = sim_state.step_event.wait(timeout=0.05)
                if stepped:
                    sim_state.step_event.clear()
                    break

        if sim_state.stop_event.is_set():
            return None

        # Track the batsman who is facing the delivery before any replacements/rotations
        facing_batsman = striker

        # Determine outcome
        outcomes = ['dot','single','double','triple','four','six','wicket','noball','wide','legbye','bye']
        
        striker_name = batting_xi[striker][0]
        if players_database and striker_name in players_database:
            stats = players_database[striker_name]
        else:
            stats = placeholder_weights if placeholder_weights else {"Dot": 45.0, "Run": 40.0, "Double": 12.0, "Four": 8.0, "Six": 5.0, "Out": 2.0}
            
        weights = [
            float(stats.get("Dot", 45.0)),
            float(stats.get("Run", 40.0)),
            float(stats.get("Double", 12.0)),
            1.0,   # triple
            float(stats.get("Four", 8.0)),
            float(stats.get("Six", 5.0)),
            float(stats.get("Out", 2.0)),
            1.0,   # noball
            2.0,   # wide
            1.0,   # legbye
            1.0    # bye
        ]
            
        if wickets >= 6:
            # Tail-end adjustment: Dot +5, Four -2, Six -2, Wicket +(2 if T20 else 1)
            weights[0] += 5.0
            weights[4] = max(0.0, weights[4] - 2.0)
            weights[5] = max(0.0, weights[5] - 2.0)
            weights[6] += 2.0 if mode == 'T20' else 1.0
        
        if degree == 'dominant':
            weights[4] += 5
            weights[5] += 5
            weights[6] = max(0.0, weights[6] - 1.0)
        elif degree == 'close':
            weights[4] = max(0.0, weights[4] - 2.0)
            weights[5] = max(0.0, weights[5] - 1.0)
            

        if free_hit:
            if "wicket" in outcomes:
                idx = outcomes.index("wicket")
                outcomes.pop(idx)
                weights.pop(idx)
            free_hit = False

        outcome = random.choices(outcomes, weights=weights, k=1)[0]
        bowler_key = bowling_list[currentBowler]
        bowler = bowlers[bowler_key]

        ball_description = ""
        runs_this_ball = 0
        legal_delivery = True

        if outcome == 'dot':
            balls += 1
            dots += 1
            batting_xi[striker].append(0)
            balls_in_over += 1
            currentPartnershipBalls += 1
            ballsProgression.append(outcome)
            bowler['prog'].append(outcome)
            bowler['balls'] += 1
            ball_description = "plays a solid defensive shot."

        elif outcome == 'single':
            balls += 1
            runs += 1
            runs_this_ball = 1
            singles += 1
            batting_xi[striker].append(1)
            balls_in_over += 1
            currentPartnershipRuns += 1
            currentPartnershipBalls += 1
            ballsProgression.append(outcome)
            bowler['prog'].append(outcome)
            bowler['balls'] += 1
            ball_description = "nudges it to the outfield for a single."

        elif outcome == 'double':
            balls += 1
            runs += 2
            runs_this_ball = 2
            doubles += 1
            batting_xi[striker].append(2)
            balls_in_over += 1
            currentPartnershipRuns += 2
            currentPartnershipBalls += 1
            ballsProgression.append(outcome)
            bowler['prog'].append(outcome)
            bowler['balls'] += 1
            ball_description = "clips it away through midwicket for a brace."

        elif outcome == 'triple':
            balls += 1
            runs += 3
            runs_this_ball = 3
            triples += 1
            batting_xi[striker].append(3)
            balls_in_over += 1
            currentPartnershipRuns += 3
            currentPartnershipBalls += 1
            ballsProgression.append(outcome)
            bowler['prog'].append(outcome)
            bowler['balls'] += 1
            ball_description = "places it beautifully! They scramble back for three runs."

        elif outcome == 'four':
            balls += 1
            runs += 4
            runs_this_ball = 4
            fours += 1
            batting_xi[striker].append(4)
            balls_in_over += 1
            currentPartnershipRuns += 4
            currentPartnershipBalls += 1
            ballsProgression.append(outcome)
            bowler['prog'].append(outcome)
            bowler['balls'] += 1
            ball_description = "FOUR! Pierces the cover gap with a majestic boundary!"

        elif outcome == 'six':
            balls += 1
            runs += 6
            runs_this_ball = 6
            sixes += 1
            batting_xi[striker].append(6)
            balls_in_over += 1
            currentPartnershipRuns += 6
            currentPartnershipBalls += 1
            ballsProgression.append(outcome)
            bowler['prog'].append(outcome)
            bowler['balls'] += 1
            ball_description = "SIX! Sails high and handsome over long-on!"

        elif outcome == 'noball':
            runs += 1
            noballs += 1
            batting_xi[striker].append("NB")
            currentPartnershipRuns += 1
            currentPartnershipBalls += 1
            ballsProgression.append(outcome)
            bowler['prog'].append(outcome)
            bowler['no balls'] += 1
            free_hit = True
            legal_delivery = False
            ball_description = "NO BALL! Bowler overstepped. Free hit coming up!"

        elif outcome == 'wide':
            runs += 1
            wides += 1
            currentPartnershipRuns += 1
            ballsProgression.append(outcome)
            bowler['prog'].append(outcome)
            bowler['wides'] += 1
            legal_delivery = False
            ball_description = "WIDE! Wayward delivery outside the guideline."

        elif outcome == 'legbye':
            run = random.choice([1,2,4])
            runs += run
            runs_this_ball = run
            balls += 1
            legbyes += 1
            balls_in_over += 1
            currentPartnershipRuns += run
            currentPartnershipBalls += 1
            ballsProgression.append(outcome+str(run))
            bowler['prog'].append(outcome+str(run))
            bowler['balls'] += 1
            ball_description = f"Leg bye. Off the pads for {run}."

        elif outcome == 'bye':
            run = random.choice([1,2,4])
            runs += run
            runs_this_ball = run
            balls += 1
            byes += 1
            balls_in_over += 1
            currentPartnershipRuns += run
            currentPartnershipBalls += 1
            ballsProgression.append(outcome+str(run))
            bowler['prog'].append(outcome+str(run))
            bowler['balls'] += 1
            ball_description = f"Bye. Sneaks past the wicketkeeper for {run}."

        elif outcome == 'wicket':
            balls += 1
            dots += 1
            wickets += 1
            batting_xi[striker].append("W")
            currentPartnershipBalls += 1
            partnerships.append([batting_xi[striker][0], batting_xi[non_striker][0], currentPartnershipRuns, currentPartnershipBalls])
            
            ball_description = f"WICKET! {batting_xi[striker][0]} has been dismissed!"
            
            if next_batter <= 11:
                striker = next_batter
                next_batter += 1
            currentPartnershipRuns = 0
            currentPartnershipBalls = 0
            ballsProgression.append(outcome)
            bowler['prog'].append(outcome)
            bowler['balls'] += 1
            bowler['wickets'] += 1
            balls_in_over += 1

        # Format visual badge representations
        if outcome == 'dot': code = '•'
        elif outcome == 'single': code = '1'
        elif outcome == 'double': code = '2'
        elif outcome == 'triple': code = '3'
        elif outcome == 'four': code = '4'
        elif outcome == 'six': code = '6'
        elif outcome == 'noball': code = 'nb'
        elif outcome == 'wide': code = 'wd'
        elif outcome == 'legbye': code = f'lb{runs_this_ball}'
        elif outcome == 'bye': code = f'b{runs_this_ball}'
        elif outcome == 'wicket': code = 'W'
        current_over_balls.append(code)

        # Generate the commentary line using the actual batsman facing the delivery (facing_batsman)
        over_str = f"{balls // 6}.{balls % 6}" if legal_delivery else f"{balls // 6}.{(balls % 6) + 1} (ext)"
        comm_line = f"[{over_str}] {bowler['prog'][0]} to {batting_xi[facing_batsman][0]} : {ball_description}"

        # Bowler's maidens calculation
        b_maidens = 0
        maiden_check = ['dot', 'dot', 'dot', 'dot', 'dot', 'dot']
        for i in range(len(bowler['prog']) - 5):
            if bowler['prog'][i:i+6] == maiden_check:
                b_maidens += 1

        b_balls = bowler['balls']
        b_overs = f"{b_balls // 6}.{b_balls % 6}"
        b_wickets = bowler['wickets']
        
        b_runs = 0
        for x in bowler['prog'][1:]:
            if x == 'single': b_runs += 1
            elif x == 'double': b_runs += 2
            elif x == 'triple': b_runs += 3
            elif x == 'four': b_runs += 4
            elif x == 'six': b_runs += 6
            elif x == 'noball': b_runs += 1
            elif x == 'wide': b_runs += 1

        # Perform strike rotations for the runs scored on this delivery
        if outcome in ('single', 'triple'):
            striker, non_striker = non_striker, striker
        elif outcome in ('legbye', 'bye'):
            if runs_this_ball % 2 == 1:
                striker, non_striker = non_striker, striker

        # Check for over completion
        over_completed = (balls_in_over == 6 and legal_delivery)
        if over_completed:
            # End of over strike rotation
            striker, non_striker = non_striker, striker

        # Live stats computations (calculated AFTER strike rotation and batsman replacements)
        # This aligns batsman names with their corresponding stats in the GUI
        if striker in batting_xi:
            s_runs = sum([p for p in batting_xi[striker] if isinstance(p, int)])
            s_balls = len(batting_xi[striker]) - 1
            s_4s = batting_xi[striker].count(4)
            s_6s = batting_xi[striker].count(6)
            s_name = batting_xi[striker][0]
        else:
            s_runs = s_balls = s_4s = s_6s = 0
            s_name = "N/A"
            
        if non_striker in batting_xi:
            ns_runs = sum([p for p in batting_xi[non_striker] if isinstance(p, int)])
            ns_balls = len(batting_xi[non_striker]) - 1
            ns_4s = batting_xi[non_striker].count(4)
            ns_6s = batting_xi[non_striker].count(6)
            ns_name = batting_xi[non_striker][0]
        else:
            ns_runs = ns_balls = ns_4s = ns_6s = 0
            ns_name = "N/A"

        # Send state update to GUI
        queue.put(("ball_update", {
            "inning_num": inning_num,
            "runs": runs,
            "wickets": wickets,
            "balls": balls,
            "total_balls": totalBalls,
            "striker_name": s_name,
            "striker_runs": s_runs,
            "striker_balls": s_balls,
            "striker_4s": s_4s,
            "striker_6s": s_6s,
            "non_striker_name": ns_name,
            "non_striker_runs": ns_runs,
            "non_striker_balls": ns_balls,
            "non_striker_4s": ns_4s,
            "non_striker_6s": ns_6s,
            "bowler_name": bowler['prog'][0],
            "bowler_overs": b_overs,
            "bowler_maidens": b_maidens,
            "bowler_runs": b_runs,
            "bowler_wickets": b_wickets,
            "over_balls": list(current_over_balls),
            "commentary": comm_line,
            "commentary_tag": outcome,
            "target": target
        }))

        # Handle over completion bowler change and signals
        if over_completed:
            bowler['prog'].append('over')
            bowler['overs'] += 1
            
            queue.put(("over_end", {
                "runs": runs,
                "wickets": wickets,
                "overs": balls // 6,
                "team": team
            }))

            def find_next_bowler(exclude):
                l = []
                for i, b in enumerate(bowling_list):
                    if i not in exclude and bowlers[b]['overs'] < maxQuota:
                        l.append(i)
                if len(l) > 0:
                    return random.choice(l)
                else:
                    return exclude[0]

            if bowlers[bowling_list[currentBowlerOtherEnd]]['overs'] < maxQuota:
                if random.random() < 0.15:
                    replacement = find_next_bowler([currentBowler, currentBowlerOtherEnd])
                    currentBowler, currentBowlerOtherEnd = replacement, currentBowler
                else:
                    currentBowler, currentBowlerOtherEnd = currentBowlerOtherEnd, currentBowler
            else:
                replacement = find_next_bowler([currentBowler, currentBowlerOtherEnd])
                currentBowler, currentBowlerOtherEnd = replacement, currentBowler
                
            balls_in_over = 0
            current_over_balls = []

        # Simulation speed control sleep
        if not sim_state.instant_simulation:
            sleep_time = sim_state.delay_seconds
            sleep_slept = 0.0
            while sleep_slept < sleep_time and sim_state.pause_event.is_set() and not sim_state.stop_event.is_set():
                time.sleep(0.05)
                sleep_slept += 0.05

    # Append last partnership
    if balls == totalBalls or (target is not None and runs > target) or wickets == 10:
        p_runs = f"{currentPartnershipRuns}*" if target is None or runs <= target else f"{currentPartnershipRuns}"
        partnerships.append([batting_xi[striker][0], batting_xi[non_striker][0], p_runs, currentPartnershipBalls])

    return {
        'mode': mode,
        'team': team,
        'opp': oppTeam,
        'balls': balls,
        'runs': runs,
        'wickets': wickets,
        'dots': dots,
        'singles': singles,
        'doubles': doubles,
        'triples': triples,
        'fours': fours,
        'sixes': sixes,
        'no balls': noballs,
        'wides': wides,
        'leg byes': legbyes,
        'byes': byes,
        'balls progression': ballsProgression,
        'batting_xi': batting_xi,
        'inningCounter': inning_num,
        'partnerships': partnerships,
        'bowlers': bowlers
    }

def run_full_match_thread(queue, match_info, sim_state):
    teamA = match_info['teamA']
    teamB = match_info['teamB']
    teamAplayers = match_info['teamAplayers']
    teamBplayers = match_info['teamBplayers']
    posA = match_info['posA']
    posB = match_info['posB']
    deg = match_info['degree']
    mode = match_info['mode']
    players_database = match_info.get('players_database', {})
    placeholder_weights = match_info.get('placeholder_weights', None)
    series_count = match_info.get('series_count', 1)
    
    for match_idx in range(1, series_count + 1):
        if sim_state.stop_event.is_set():
            return
            
        # 1. Build bowler dicts
        teamAbowlers = {}
        for pos in posA:
            teamAbowlers[pos] = {
                'prog': [teamAplayers[pos-1]],
                'balls': 0, 'overs': 0, 'wickets': 0, 'no balls': 0, 'wides': 0
            }
            
        teamBbowlers = {}
        for pos in posB:
            teamBbowlers[pos] = {
                'prog': [teamBplayers[pos-1]],
                'balls': 0, 'overs': 0, 'wickets': 0, 'no balls': 0, 'wides': 0
            }
            
        if series_count > 1:
            queue.put(("series_match_start", {"match_idx": match_idx, "series_count": series_count}))
            
        # 2. Simulate Innings 1
        innings1 = simulate_innings_ball_by_ball(queue, teamA, teamB, teamAplayers, teamBbowlers, deg, mode, 1, None, sim_state, players_database=players_database, placeholder_weights=placeholder_weights)
        
        if sim_state.stop_event.is_set():
            return
            
        # Push innings1 data
        queue.put(("innings1_complete", innings1))
        
        # Sleep/pause between innings (3 seconds)
        sleep_slept = 0.0
        while sleep_slept < 3.0 and not sim_state.stop_event.is_set():
            if not sim_state.instant_simulation:
                time.sleep(0.1)
                sleep_slept += 0.1
            else:
                break
            
        if sim_state.stop_event.is_set():
            return
            
        # 3. Simulate Innings 2
        innings2 = simulate_innings_ball_by_ball(queue, teamB, teamA, teamBplayers, teamAbowlers, deg, mode, 2, innings1['runs'], sim_state, players_database=players_database, placeholder_weights=placeholder_weights)
        
        if sim_state.stop_event.is_set():
            return
            
        if series_count == 1:
            # Match complete payload
            queue.put(("match_complete", {
                "innings1": innings1,
                "innings2": innings2
            }))
        else:
            # Series Match complete payload
            queue.put(("series_match_complete", {
                "match_idx": match_idx,
                "innings1": innings1,
                "innings2": innings2
            }))
            
            # Short sleep between matches in the series
            if match_idx < series_count:
                sleep_slept = 0.0
                while sleep_slept < 2.0 and not sim_state.stop_event.is_set():
                    if not sim_state.instant_simulation:
                        time.sleep(0.1)
                        sleep_slept += 0.1
                    else:
                        break
                        
    if series_count > 1:
        queue.put(("series_complete", {}))

def load_players_csv():
    players_data = {}
    csv_paths = ["players.csv", "/Users/keertikeshaveswaran/Documents/players.csv", "/Users/keertikeshaveswaran/Documents/InningsGen/players.csv"]
    path_to_use = None
    for path in csv_paths:
        if os.path.exists(path):
            path_to_use = path
            break
            
    if not path_to_use:
        return {}
        
    try:
        with open(path_to_use, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("Name")
                if name:
                    players_data[name.strip()] = {
                        "Team": row.get("Team", "Unknown").strip(),
                        "Dot": float(row.get("Dot", 45)),
                        "Run": float(row.get("Run", 40)),
                        "Double": float(row.get("Double", 12)),
                        "Four": float(row.get("Four", 8)),
                        "Six": float(row.get("Six", 5)),
                        "Out": float(row.get("Out", 2))
                    }
    except Exception as e:
        print("Error loading CSV:", e)
    return players_data

# ---------------------------------------------------------
# GUI INTERFACE CLASS
# ---------------------------------------------------------
class CricketSimulatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cricket Match Innings Simulator (ODI & T20I)")
        self.root.geometry("1180x820")
        self.root.configure(bg=DARK_BG)
        
        self.queue = queue.Queue()
        self.sim_state = SimulationState()
        self.worker_thread = None
        self.active_innings = None
        
        # Load CSV database
        self.players_database = load_players_csv()
        self.csv_player_names = sorted(list(self.players_database.keys()))
        
        # Setup modern dark styling
        self.setup_styles()
        
        # Match State variables
        self.session_var = tk.StringVar(value=f"Session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.format_var = tk.StringVar(value="ODI")
        self.degree_var = tk.StringVar(value="normal")
        self.random_deg_var = tk.BooleanVar(value=False)
        self.team_a_var = tk.StringVar(value="")
        self.team_b_var = tk.StringVar(value="")
        
        # Placeholder weights variables
        self.placeholder_dot = tk.DoubleVar(value=45.0)
        self.placeholder_run = tk.DoubleVar(value=40.0)
        self.placeholder_double = tk.DoubleVar(value=12.0)
        self.placeholder_four = tk.DoubleVar(value=8.0)
        self.placeholder_six = tk.DoubleVar(value=5.0)
        self.placeholder_out = tk.DoubleVar(value=2.0)
        
        # Series variables
        self.series_matches_var = tk.StringVar(value="1")
        self.active_series_matches = []
        self.active_series_summary = None

        
        # Team player inputs
        self.players_a = [tk.StringVar() for _ in range(11)]
        self.bowlers_a = [tk.BooleanVar() for _ in range(11)]
        self.players_b = [tk.StringVar() for _ in range(11)]
        self.bowlers_b = [tk.BooleanVar() for _ in range(11)]
        
        # Build Notebook layout
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_setup = tk.Frame(self.notebook, bg=DARK_BG)
        self.tab_live = tk.Frame(self.notebook, bg=DARK_BG)
        self.tab_scorecard = tk.Frame(self.notebook, bg=DARK_BG)
        self.tab_leaderboards = tk.Frame(self.notebook, bg=DARK_BG)
        
        self.notebook.add(self.tab_setup, text="Match Setup")
        self.notebook.add(self.tab_live, text="Live Simulator")
        self.notebook.add(self.tab_scorecard, text="Scorecard")
        self.notebook.add(self.tab_leaderboards, text="Leaderboards")
        
        # Build frames
        self.build_setup_tab()
        self.build_live_tab()
        self.build_scorecard_tab()
        self.build_leaderboard_tab()
        
        # Queue listener
        self.root.after(100, self.poll_queue)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Tabs
        style.configure("TNotebook", background=DARK_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=CARD_BG, foreground=TEXT_FG, 
                        padding=[18, 8], font=("Helvetica", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", DARK_BG)])
                  
        # Treeview (Scorecards/Leaderboards)
        style.configure("Treeview",
                        background=CARD_BG,
                        foreground=TEXT_FG,
                        fieldbackground=CARD_BG,
                        rowheight=25,
                        font=("Helvetica", 9),
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=DARK_BG,
                        foreground=ACCENT_BLUE,
                        font=("Helvetica", 9, "bold"),
                        borderwidth=1,
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", ACCENT_BLUE)],
                  foreground=[("selected", DARK_BG)])
                  
        # Scrollbars
        style.configure("Vertical.TScrollbar", gripcount=0, background=DARK_BG, borderwidth=0, arrowsize=10)
        
    def create_custom_button(self, parent, text, command, bg_color, fg_color, font=("Helvetica", 10, "bold"), **kwargs):
        btn = tk.Button(parent, text=text, command=command, bg=bg_color, fg=fg_color,
                        activebackground=ACCENT_GREEN, activeforeground=DARK_BG,
                        font=font, relief="flat", bd=0, highlightthickness=0, padx=12, pady=6, **kwargs)
        def on_enter(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=ACCENT_GREEN, fg=DARK_BG)
        def on_leave(e):
            if btn['state'] != tk.DISABLED:
                btn.config(bg=bg_color, fg=fg_color)
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def setup_autocomplete(self, cb):
        def on_keyrelease(event):
            if event.keysym in ("Up", "Down", "Left", "Right", "Return", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Meta_L", "Meta_R", "Tab", "Escape", "Caps_Lock"):
                return
                
            typed = cb.get()
            if typed == "":
                data = self.csv_player_names
            else:
                data = [name for name in self.csv_player_names if typed.lower() in name.lower()]
                
            cb['values'] = data
            
            if data:
                try:
                    cb.tk.call(cb, 'post')
                except Exception:
                    pass
            else:
                try:
                    cb.tk.call(cb, 'unpost')
                except Exception:
                    pass

        def reset_values(event):
            cb['values'] = self.csv_player_names

        cb.bind('<KeyRelease>', on_keyrelease)
        cb.bind('<FocusIn>', reset_values)
        cb.bind('<<ComboboxSelected>>', reset_values)



    # ---------------------------------------------------------
    # MATCH SETUP TAB BUILD
    # ---------------------------------------------------------
    def build_setup_tab(self):
        # Top Settings Header
        top_frame = tk.Frame(self.tab_setup, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR)
        top_frame.pack(fill="x", padx=15, pady=15)
        
        tk.Label(top_frame, text="Session Name:", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(top_frame, textvariable=self.session_var, bg=DARK_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", bd=4, font=("Helvetica", 10), width=25).grid(row=0, column=1, padx=5, pady=10)
        
        tk.Label(top_frame, text="Format:", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=15, pady=10, sticky="w")
        cb_format = ttk.Combobox(top_frame, textvariable=self.format_var, values=["ODI", "T20"], width=8, state="readonly")
        cb_format.grid(row=0, column=3, padx=5, pady=10)
        
        tk.Label(top_frame, text="Match Type:", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 10, "bold")).grid(row=0, column=4, padx=15, pady=10, sticky="w")
        cb_deg = ttk.Combobox(top_frame, textvariable=self.degree_var, values=["normal", "close", "dominant"], width=10, state="readonly")
        cb_deg.grid(row=0, column=5, padx=5, pady=10)
        
        tk.Checkbutton(top_frame, text="Choose Randomly", variable=self.random_deg_var, bg=CARD_BG, fg=TEXT_FG, selectcolor=DARK_BG, activebackground=CARD_BG, activeforeground=TEXT_FG).grid(row=0, column=6, padx=15, pady=10)
        
        tk.Label(top_frame, text="Series Matches:", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 10, "bold")).grid(row=0, column=7, padx=15, pady=10, sticky="w")
        cb_series = ttk.Combobox(top_frame, textvariable=self.series_matches_var, values=["1 (Single Match)", "2", "3", "4", "5", "6", "7"], width=14, state="readonly")
        cb_series.grid(row=0, column=8, padx=5, pady=10)
        
        # Teams container
        teams_frame = tk.Frame(self.tab_setup, bg=DARK_BG)
        teams_frame.pack(fill="both", expand=True, padx=15, pady=5)
        teams_frame.grid_columnconfigure(0, weight=1)
        teams_frame.grid_columnconfigure(1, weight=1)
        
        # Team A setup frame
        self.build_team_setup_panel(teams_frame, "Team A (Home)", self.team_a_var, self.players_a, self.bowlers_a, 0)
        # Team B setup frame
        self.build_team_setup_panel(teams_frame, "Team B (Away)", self.team_b_var, self.players_b, self.bowlers_b, 1)
        
        # Bottom controls
        bottom_frame = tk.Frame(self.tab_setup, bg=DARK_BG)
        bottom_frame.pack(fill="x", side="bottom", pady=15)
        
        # Global Placeholder Player Weights Frame
        weights_lf = tk.LabelFrame(bottom_frame, text="Global Placeholder Player Weights (Used for custom players not in database)", bg=CARD_BG, fg=ACCENT_BLUE, font=("Helvetica", 10, "bold"), bd=1, relief="solid", highlightbackground=BORDER_COLOR)
        weights_lf.pack(fill="x", padx=15, pady=(0, 10))
        weights_lf.columnconfigure((0,1,2,3,4,5,6,7,8,9,10,11), weight=1)
        
        tk.Label(weights_lf, text="Dot (%):", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9)).grid(row=0, column=0, padx=5, pady=8, sticky="e")
        tk.Entry(weights_lf, textvariable=self.placeholder_dot, bg=DARK_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", bd=2, font=("Helvetica", 9), width=6).grid(row=0, column=1, padx=5, pady=8, sticky="w")
        
        tk.Label(weights_lf, text="Run (%):", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9)).grid(row=0, column=2, padx=5, pady=8, sticky="e")
        tk.Entry(weights_lf, textvariable=self.placeholder_run, bg=DARK_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", bd=2, font=("Helvetica", 9), width=6).grid(row=0, column=3, padx=5, pady=8, sticky="w")
        
        tk.Label(weights_lf, text="Double (%):", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9)).grid(row=0, column=4, padx=5, pady=8, sticky="e")
        tk.Entry(weights_lf, textvariable=self.placeholder_double, bg=DARK_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", bd=2, font=("Helvetica", 9), width=6).grid(row=0, column=5, padx=5, pady=8, sticky="w")
        
        tk.Label(weights_lf, text="Four (%):", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9)).grid(row=0, column=6, padx=5, pady=8, sticky="e")
        tk.Entry(weights_lf, textvariable=self.placeholder_four, bg=DARK_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", bd=2, font=("Helvetica", 9), width=6).grid(row=0, column=7, padx=5, pady=8, sticky="w")
        
        tk.Label(weights_lf, text="Six (%):", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9)).grid(row=0, column=8, padx=5, pady=8, sticky="e")
        tk.Entry(weights_lf, textvariable=self.placeholder_six, bg=DARK_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", bd=2, font=("Helvetica", 9), width=6).grid(row=0, column=9, padx=5, pady=8, sticky="w")
        
        tk.Label(weights_lf, text="Out (%):", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9)).grid(row=0, column=10, padx=5, pady=8, sticky="e")
        tk.Entry(weights_lf, textvariable=self.placeholder_out, bg=DARK_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", bd=2, font=("Helvetica", 9), width=6).grid(row=0, column=11, padx=5, pady=8, sticky="w")
        
        self.btn_start = self.create_custom_button(bottom_frame, "Start Simulation Match", self.start_simulation_match, ACCENT_BLUE, DARK_BG, font=("Helvetica", 12, "bold"))
        self.btn_start.pack(anchor="center")


    def build_team_setup_panel(self, parent, panel_title, name_var, players_list, bowlers_list, column):
        frame = tk.Frame(parent, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, padx=15, pady=15)
        frame.grid(row=0, column=column, padx=10, sticky="nsew")
        
        # Title
        header = tk.Frame(frame, bg=CARD_BG)
        header.pack(fill="x", pady=(0, 10))
        
        tk.Label(header, text=panel_title, bg=CARD_BG, fg=ACCENT_BLUE, font=("Helvetica", 12, "bold")).pack(side="left")
        
        # Team Name
        name_frm = tk.Frame(frame, bg=CARD_BG)
        name_frm.pack(fill="x", pady=5)
        tk.Label(name_frm, text="Team Name:", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 10)).pack(side="left")
        tk.Entry(name_frm, textvariable=name_var, bg=DARK_BG, fg=TEXT_FG, insertbackground=TEXT_FG, relief="flat", bd=3, font=("Helvetica", 10, "bold"), width=15).pack(side="left", padx=10)
        
        # Headers for rows
        row_headers = tk.Frame(frame, bg=CARD_BG)
        row_headers.pack(fill="x", pady=5)
        tk.Label(row_headers, text="No. Player Name", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9, "italic")).pack(side="left", padx=10)
        tk.Label(row_headers, text="Bowler?", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9, "italic")).pack(side="right", padx=15)
        
        # 11 player rows
        for i in range(11):
            row_frame = tk.Frame(frame, bg=CARD_BG)
            row_frame.pack(fill="x", pady=2)
            
            tk.Label(row_frame, text=f"{i+1:2d}.", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 10)).pack(side="left")
            cb = ttk.Combobox(row_frame, textvariable=players_list[i], values=self.csv_player_names, font=("Helvetica", 9), width=22)
            cb.pack(side="left", padx=10)
            self.setup_autocomplete(cb)
            
            tk.Checkbutton(row_frame, variable=bowlers_list[i], bg=CARD_BG, activebackground=CARD_BG, selectcolor=DARK_BG).pack(side="right", padx=20)

    # ---------------------------------------------------------
    # LIVE SIMULATOR TAB BUILD
    # ---------------------------------------------------------
    def build_live_tab(self):
        # 3 Panels: Left (Scoreboard HUD), Right (Commentary Log), Bottom (Controls)
        self.tab_live.columnconfigure(0, weight=6)
        self.tab_live.columnconfigure(1, weight=4)
        self.tab_live.rowconfigure(0, weight=1)
        
        # --- LEFT PANEL: HUD ---
        left_panel = tk.Frame(self.tab_live, bg=DARK_BG)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Summary Header
        self.match_hdr_label = tk.Label(left_panel, text="No active simulation. Configure in Match Setup.", bg=DARK_BG, fg=TEXT_FG, font=("Helvetica", 12, "bold"))
        self.match_hdr_label.pack(fill="x", pady=(5, 15))
        
        # Score HUD Card
        hud_card = tk.Frame(left_panel, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, padx=15, pady=15)
        hud_card.pack(fill="x", pady=5)
        
        self.lbl_hud_runs = tk.Label(hud_card, text="0 / 0", bg=CARD_BG, fg=ACCENT_GREEN, font=("Helvetica", 36, "bold"))
        self.lbl_hud_runs.pack(anchor="w")
        
        hud_row = tk.Frame(hud_card, bg=CARD_BG)
        hud_row.pack(fill="x", pady=5)
        
        self.lbl_hud_overs = tk.Label(hud_row, text="Overs: 0.0 / 0", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 14))
        self.lbl_hud_overs.pack(side="left")
        
        self.lbl_hud_rr = tk.Label(hud_row, text="Run Rate: 0.00", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 12, "bold"))
        self.lbl_hud_rr.pack(side="right")
        
        # Second Innings Target Alert Frame
        self.target_frame = tk.Frame(hud_card, bg=DARK_BG, bd=1, relief="sunken", pady=6)
        self.lbl_target_info = tk.Label(self.target_frame, text="", bg=DARK_BG, fg=ACCENT_YELLOW, font=("Helvetica", 11, "bold"))
        self.lbl_target_info.pack(fill="x")
        
        # Batter Cards
        batters_frm = tk.Frame(left_panel, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, padx=15, pady=15)
        batters_frm.pack(fill="x", pady=10)
        tk.Label(batters_frm, text="Batting", bg=CARD_BG, fg=ACCENT_BLUE, font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.lbl_striker = tk.Label(batters_frm, text="* Striker: -", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 11, "bold"))
        self.lbl_striker.pack(anchor="w", pady=2)
        
        self.lbl_non_striker = tk.Label(batters_frm, text="  Non-Striker: -", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 11))
        self.lbl_non_striker.pack(anchor="w", pady=2)
        
        # Bowler Card
        bowler_frm = tk.Frame(left_panel, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, padx=15, pady=15)
        bowler_frm.pack(fill="x", pady=5)
        tk.Label(bowler_frm, text="Bowling", bg=CARD_BG, fg=ACCENT_BLUE, font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.lbl_bowler = tk.Label(bowler_frm, text="Bowler: -", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 11))
        self.lbl_bowler.pack(anchor="w")
        
        # Over Progression circles canvas
        prog_frm = tk.Frame(bowler_frm, bg=CARD_BG)
        prog_frm.pack(fill="x", pady=(10, 0))
        tk.Label(prog_frm, text="Current Over:", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9, "italic")).pack(side="left", padx=(0, 10))
        
        self.over_canvas = tk.Canvas(prog_frm, width=280, height=35, bg=CARD_BG, bd=0, highlightthickness=0)
        self.over_canvas.pack(side="left")
        
        # Controls box
        ctrl_card = tk.Frame(left_panel, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, padx=15, pady=15)
        ctrl_card.pack(fill="both", expand=True, pady=10)
        
        btn_frm = tk.Frame(ctrl_card, bg=CARD_BG)
        btn_frm.pack(fill="x", pady=(0, 10))
        
        self.btn_pause = self.create_custom_button(btn_frm, "Pause", self.pause_simulation, ACCENT_BLUE, DARK_BG)
        self.btn_pause.grid(row=0, column=0, padx=4)
        
        self.btn_next = self.create_custom_button(btn_frm, "Next Ball", self.step_simulation, bg_color=DARK_BG, fg_color=TEXT_FG)
        self.btn_next.grid(row=0, column=1, padx=4)
        self.btn_next.config(state="disabled")
        
        self.btn_instant = self.create_custom_button(btn_frm, "Instant Sim", self.trigger_instant_simulation, ACCENT_YELLOW, DARK_BG)
        self.btn_instant.grid(row=0, column=2, padx=4)
        
        self.btn_stop = self.create_custom_button(btn_frm, "Abort Match", self.stop_simulation, ACCENT_RED, DARK_BG)
        self.btn_stop.grid(row=0, column=3, padx=4)
        self.btn_stop.config(state="disabled")
        
        # Speed Slider
        speed_frm = tk.Frame(ctrl_card, bg=CARD_BG)
        speed_frm.pack(fill="x", pady=5)
        tk.Label(speed_frm, text="Simulation Delay (sec):", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9)).pack(side="left")
        
        self.slider_speed = tk.Scale(speed_frm, from_=0.05, to=2.0, resolution=0.05, orient="horizontal", command=self.update_simulation_speed, bg=CARD_BG, fg=TEXT_FG, troughcolor=DARK_BG, activebackground=ACCENT_BLUE, highlightthickness=0, relief="flat", length=180)
        self.slider_speed.set(0.5)
        self.slider_speed.pack(side="left", padx=10)
        
        # --- RIGHT PANEL: COMMENTARY LOG ---
        right_panel = tk.Frame(self.tab_live, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, padx=15, pady=15)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        tk.Label(right_panel, text="Live commentary", bg=CARD_BG, fg=ACCENT_BLUE, font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        # ScrolledText with tag configurations
        self.txt_commentary = scrolledtext.ScrolledText(right_panel, bg=DARK_BG, fg=TEXT_FG, font=("Courier New", 10), insertbackground=TEXT_FG, relief="flat", bd=0, wrap="word")
        self.txt_commentary.pack(fill="both", expand=True)
        
        self.txt_commentary.tag_config("wicket", foreground=ACCENT_RED, font=("Courier New", 10, "bold"))
        self.txt_commentary.tag_config("four", foreground=ACCENT_BLUE, font=("Courier New", 10, "bold"))
        self.txt_commentary.tag_config("six", foreground=ACCENT_YELLOW, font=("Courier New", 10, "bold"))
        self.txt_commentary.tag_config("noball", foreground="#e67e22", font=("Courier New", 10))
        self.txt_commentary.tag_config("wide", foreground="#e67e22", font=("Courier New", 10))
        self.txt_commentary.tag_config("system", foreground=ACCENT_GREEN, font=("Courier New", 10, "bold"))

    # ---------------------------------------------------------
    # SCORECARD TAB BUILD
    # ---------------------------------------------------------
    def build_scorecard_tab(self):
        self.tab_scorecard.grid_columnconfigure(0, weight=1)
        self.tab_scorecard.grid_rowconfigure(1, weight=1)
        
        # MOTM / Result Banner at top
        self.banner_frame = tk.Frame(self.tab_scorecard, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, padx=15, pady=10)
        self.banner_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        # Left side containing results
        left_frm = tk.Frame(self.banner_frame, bg=CARD_BG)
        left_frm.pack(side="left", fill="both", expand=True)
        
        self.lbl_result_msg = tk.Label(left_frm, text="No match scorecard loaded yet.", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 13, "bold"))
        self.lbl_result_msg.pack(anchor="center")
        
        self.lbl_motm_msg = tk.Label(left_frm, text="", bg=CARD_BG, fg=ACCENT_YELLOW, font=("Helvetica", 11, "bold"))
        self.lbl_motm_msg.pack(anchor="center", pady=(2, 0))
        
        # Right side containing Match Selector and PDF button
        right_frm = tk.Frame(self.banner_frame, bg=CARD_BG)
        right_frm.pack(side="right", fill="y", padx=10)
        
        # Two PDF buttons: Save Match PDF and Save Series PDF
        self.btn_match_pdf = self.create_custom_button(
            right_frm, "Save PDF Scorecard", self.export_match_to_pdf_handler,
            bg_color=DARK_BG, fg_color=TEXT_FG, font=("Helvetica", 10, "bold")
        )
        self.btn_match_pdf.pack(side="right", padx=5)
        self.btn_match_pdf.config(state="disabled")
        
        self.btn_series_pdf = self.create_custom_button(
            right_frm, "Save Series PDF", self.export_series_to_pdf,
            bg_color=DARK_BG, fg_color=TEXT_FG, font=("Helvetica", 10, "bold")
        )
        # Packed dynamically when series completes
        self.btn_series_pdf.config(state="disabled")
        
        # Container for Notebooks
        self.scorecard_container = tk.Frame(self.tab_scorecard, bg=DARK_BG)
        self.scorecard_container.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Sub-notebook for single match scorecards
        self.single_match_nb = ttk.Notebook(self.scorecard_container)
        self.single_match_nb.pack(fill="both", expand=True)
        
        self.tab_inn1 = tk.Frame(self.single_match_nb, bg=DARK_BG)
        self.tab_inn2 = tk.Frame(self.single_match_nb, bg=DARK_BG)
        
        self.single_match_nb.add(self.tab_inn1, text="Innings 1")
        self.single_match_nb.add(self.tab_inn2, text="Innings 2")
        
        # Build tables inside Innings 1 and Innings 2 tabs
        self.scorecard_tables_inn1 = self.build_innings_scorecard_ui(self.tab_inn1)
        self.scorecard_tables_inn2 = self.build_innings_scorecard_ui(self.tab_inn2)
        
        # Notebook for series matches
        self.series_matches_nb = ttk.Notebook(self.scorecard_container)
        # Packed dynamically when series completes

    def build_innings_scorecard_ui(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.columnconfigure(1, weight=1)
        parent_frame.rowconfigure(1, weight=1)
        
        # Title of team
        team_lbl = tk.Label(parent_frame, text="Innings Scorecard", bg=DARK_BG, fg=TEXT_FG, font=("Helvetica", 11, "bold"))
        team_lbl.grid(row=0, column=0, columnspan=2, pady=5, sticky="w")
        
        # --- LEFT SIDE: Batting + FOW ---
        left_sub = tk.Frame(parent_frame, bg=DARK_BG)
        left_sub.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        left_sub.rowconfigure(1, weight=1)
        left_sub.columnconfigure(0, weight=1)
        
        tk.Label(left_sub, text="Batting", bg=DARK_BG, fg=ACCENT_BLUE, font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        
        # Batting Treeview
        bat_cols = ("Batsman", "Status", "Runs", "Balls", "4s", "6s", "S/R")
        bat_tree = ttk.Treeview(left_sub, columns=bat_cols, show="headings", height=8)
        bat_tree.grid(row=1, column=0, sticky="nsew")
        
        # Scrollbar for Batting
        bat_scroll = ttk.Scrollbar(left_sub, orient="vertical", command=bat_tree.yview)
        bat_scroll.grid(row=1, column=1, sticky="ns")
        bat_tree.configure(yscrollcommand=bat_scroll.set)
        
        for c in bat_cols:
            bat_tree.heading(c, text=c)
            # Alignment/Width
            if c == "Batsman":
                bat_tree.column(c, anchor="w", width=140)
            elif c == "Status":
                bat_tree.column(c, anchor="w", width=110)
            else:
                bat_tree.column(c, anchor="center", width=50)
                
        # Extras & FOW text box
        bottom_desc = tk.Frame(left_sub, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, padx=10, pady=8)
        bottom_desc.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        
        lbl_extras = tk.Label(bottom_desc, text="Extras: -", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9, "bold"))
        lbl_extras.pack(anchor="w")
        
        lbl_fow = tk.Label(bottom_desc, text="Fall of Wickets: -", bg=CARD_BG, fg=TEXT_FG, font=("Helvetica", 9), justify="left", wrap=450)
        lbl_fow.pack(anchor="w", pady=(5, 0))
        
        # --- RIGHT SIDE: Bowling + Partnerships ---
        right_sub = tk.Frame(parent_frame, bg=DARK_BG)
        right_sub.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        right_sub.rowconfigure(1, weight=1)
        right_sub.rowconfigure(3, weight=1)
        right_sub.columnconfigure(0, weight=1)
        
        # Bowling Figures
        tk.Label(right_sub, text="Bowling", bg=DARK_BG, fg=ACCENT_BLUE, font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        
        bowl_cols = ("Bowler", "Overs", "Maidens", "Runs", "Wickets", "NBs", "WDs")
        bowl_tree = ttk.Treeview(right_sub, columns=bowl_cols, show="headings", height=5)
        bowl_tree.grid(row=1, column=0, sticky="nsew")
        
        bowl_scroll = ttk.Scrollbar(right_sub, orient="vertical", command=bowl_tree.yview)
        bowl_scroll.grid(row=1, column=1, sticky="ns")
        bowl_tree.configure(yscrollcommand=bowl_scroll.set)
        
        for c in bowl_cols:
            bowl_tree.heading(c, text=c)
            if c == "Bowler":
                bowl_tree.column(c, anchor="w", width=140)
            else:
                bowl_tree.column(c, anchor="center", width=55)
                
        # Partnerships table
        tk.Label(right_sub, text="Partnerships", bg=DARK_BG, fg=ACCENT_BLUE, font=("Helvetica", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 2))
        
        part_cols = ("Batsman 1", "Batsman 2", "Runs", "Balls")
        part_tree = ttk.Treeview(right_sub, columns=part_cols, show="headings", height=4)
        part_tree.grid(row=3, column=0, sticky="nsew")
        
        part_scroll = ttk.Scrollbar(right_sub, orient="vertical", command=part_tree.yview)
        part_scroll.grid(row=3, column=1, sticky="ns")
        part_tree.configure(yscrollcommand=part_scroll.set)
        
        for c in part_cols:
            part_tree.heading(c, text=c)
            if c in ("Batsman 1", "Batsman 2"):
                part_tree.column(c, anchor="w", width=120)
            else:
                part_tree.column(c, anchor="center", width=60)
                
        return {
            "title_lbl": team_lbl,
            "bat_tree": bat_tree,
            "lbl_extras": lbl_extras,
            "lbl_fow": lbl_fow,
            "bowl_tree": bowl_tree,
            "part_tree": part_tree
        }

    # ---------------------------------------------------------
    # LEADERBOARDS TAB BUILD
    # ---------------------------------------------------------
    def build_leaderboard_tab(self):
        # Format toggle at top
        hdr = tk.Frame(self.tab_leaderboards, bg=DARK_BG)
        hdr.pack(fill="x", padx=15, pady=10)
        
        self.lbl_leaderboard_title = tk.Label(hdr, text="Aggregated Session Leaderboard", bg=DARK_BG, fg=TEXT_FG, font=("Helvetica", 12, "bold"))
        self.lbl_leaderboard_title.pack(side="left")
        
        self.ldr_format_var = tk.StringVar(value="ODI")
        cb_fmt = ttk.Combobox(hdr, textvariable=self.ldr_format_var, values=["ODI", "T20"], width=10, state="readonly")
        cb_fmt.pack(side="right", padx=10)
        cb_fmt.bind("<<ComboboxSelected>>", lambda e: self.update_leaderboards_display())
        
        self.ldr_scope_var = tk.StringVar(value="Session Cumulative")
        cb_scope = ttk.Combobox(hdr, textvariable=self.ldr_scope_var, values=["Session Cumulative", "Current Series"], width=18, state="readonly")
        cb_scope.pack(side="right", padx=10)
        cb_scope.bind("<<ComboboxSelected>>", lambda e: self.update_leaderboards_display())
        
        clear_btn = self.create_custom_button(hdr, "Clear Stats", self.clear_leaderboard_stats, ACCENT_RED, DARK_BG, font=("Helvetica", 9, "bold"))
        clear_btn.pack(side="right", padx=5)
        
        # Sub-container for side-by-side batting/bowling leaderboards
        sub = tk.Frame(self.tab_leaderboards, bg=DARK_BG)
        sub.pack(fill="both", expand=True, padx=15, pady=5)
        sub.rowconfigure(0, weight=1)
        sub.columnconfigure(0, weight=1)
        sub.columnconfigure(1, weight=1)
        
        # Batting Leaderboard
        bat_frame = tk.Frame(sub, bg=DARK_BG)
        bat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        bat_frame.rowconfigure(1, weight=1)
        bat_frame.columnconfigure(0, weight=1)
        
        tk.Label(bat_frame, text="Top Batting Leaders (Runs)", bg=DARK_BG, fg=ACCENT_BLUE, font=("Helvetica", 11, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        
        bat_cols = ("Player", "Team", "Inns", "Runs", "Balls", "1s", "2s", "3s", "4s", "6s", "Outs", "50s", "100s", "Avg", "SR")
        self.ldr_bat_tree = ttk.Treeview(bat_frame, columns=bat_cols, show="headings")
        self.ldr_bat_tree.grid(row=1, column=0, sticky="nsew")
        
        bat_scroll = ttk.Scrollbar(bat_frame, orient="vertical", command=self.ldr_bat_tree.yview)
        bat_scroll.grid(row=1, column=1, sticky="ns")
        self.ldr_bat_tree.configure(yscrollcommand=bat_scroll.set)
        
        for c in bat_cols:
            self.ldr_bat_tree.heading(c, text=c, command=lambda _c=c: self.sort_treeview(self.ldr_bat_tree, _c, False))
            if c == "Player":
                self.ldr_bat_tree.column(c, anchor="w", width=120)
            elif c == "Team":
                self.ldr_bat_tree.column(c, anchor="w", width=80)
            else:
                self.ldr_bat_tree.column(c, anchor="center", width=40)
                
        # Bowling Leaderboard
        bowl_frame = tk.Frame(sub, bg=DARK_BG)
        bowl_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        bowl_frame.rowconfigure(1, weight=1)
        bowl_frame.columnconfigure(0, weight=1)
        
        tk.Label(bowl_frame, text="Top Bowling Leaders (Wickets)", bg=DARK_BG, fg=ACCENT_BLUE, font=("Helvetica", 11, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        
        bowl_cols = ("Player", "Team", "Inns", "Overs", "Maidens", "Runs", "Wickets", "NBs", "WDs", "5w", "Avg", "SR")
        self.ldr_bowl_tree = ttk.Treeview(bowl_frame, columns=bowl_cols, show="headings")
        self.ldr_bowl_tree.grid(row=1, column=0, sticky="nsew")
        
        bowl_scroll = ttk.Scrollbar(bowl_frame, orient="vertical", command=self.ldr_bowl_tree.yview)
        bowl_scroll.grid(row=1, column=1, sticky="ns")
        self.ldr_bowl_tree.configure(yscrollcommand=bowl_scroll.set)
        
        for c in bowl_cols:
            self.ldr_bowl_tree.heading(c, text=c, command=lambda _c=c: self.sort_treeview(self.ldr_bowl_tree, _c, False))
            if c == "Player":
                self.ldr_bowl_tree.column(c, anchor="w", width=120)
            elif c == "Team":
                self.ldr_bowl_tree.column(c, anchor="w", width=80)
            else:
                self.ldr_bowl_tree.column(c, anchor="center", width=40)

    # ---------------------------------------------------------
    # INTERACTIVE CONTROLS / CALLBACKS
    # ---------------------------------------------------------
    def update_simulation_speed(self, val):
        self.sim_state.delay_seconds = float(val)

    def pause_simulation(self):
        if self.sim_state.pause_event.is_set():
            self.sim_state.pause_event.clear()
            self.btn_pause.config(text="Resume")
            self.btn_next.config(state="normal")
        else:
            self.sim_state.pause_event.set()
            self.btn_pause.config(text="Pause")
            self.btn_next.config(state="disabled")

    def step_simulation(self):
        self.sim_state.step_event.set()

    def trigger_instant_simulation(self):
        self.sim_state.instant_simulation = True
        self.sim_state.pause_event.set()
        self.btn_pause.config(text="Pause", state="disabled")
        self.btn_next.config(state="disabled")
        self.btn_instant.config(state="disabled")

    def stop_simulation(self):
        if messagebox.askyesno("Confirm Stop", "Do you want to abort the match?"):
            self.sim_state.stop_event.set()
            self.sim_state.pause_event.set()
            self.reset_live_hud()
            self.log_commentary("Match simulation aborted by user.", "system")

    def reset_live_hud(self):
        self.btn_start.config(state="normal")
        self.btn_pause.config(text="Pause", state="disabled")
        self.btn_next.config(state="disabled")
        self.btn_instant.config(state="disabled")
        self.btn_stop.config(state="disabled")
        self.over_canvas.delete("all")
        self.target_frame.pack_forget()

    def log_commentary(self, text, tag=None):
        self.txt_commentary.config(state="normal")
        self.txt_commentary.insert(tk.END, text + "\n", tag)
        self.txt_commentary.see(tk.END)
        self.txt_commentary.config(state="disabled")

    def clear_leaderboard_stats(self):
        global battingStatsODI, bowlingStatsODI, battingStatsT20, bowlingStatsT20
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all accumulated session stats?"):
            battingStatsODI.clear()
            bowlingStatsODI.clear()
            battingStatsT20.clear()
            bowlingStatsT20.clear()
            self.update_leaderboards_display()
            saveStats()
            messagebox.showinfo("Success", "Accumulated session leaderboards cleared.")

    def sort_treeview(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children("")]
        
        # Sort helper to handle numbers vs strings
        def sort_key(item):
            val = item[0]
            if val == '∞':
                return 999999.0
            try:
                return float(val)
            except ValueError:
                return val
                
        l.sort(key=sort_key, reverse=reverse)
        for index, (val, k) in enumerate(l):
            tree.move(k, "", index)
            
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))

    # ---------------------------------------------------------
    # VALIDATE & START SIMULATION
    # ---------------------------------------------------------
    def start_simulation_match(self):
        # 1. Gather & Validate inputs
        teamA = self.team_a_var.get().strip()
        teamB = self.team_b_var.get().strip()
        
        if not teamA or not teamB:
            messagebox.showerror("Roster Error", "Team Names cannot be empty!")
            return
            
        teamA_players = [p.get().strip() for p in self.players_a]
        teamB_players = [p.get().strip() for p in self.players_b]
        
        if any(len(p) == 0 for p in teamA_players) or any(len(p) == 0 for p in teamB_players):
            messagebox.showerror("Roster Error", "All 11 player entries must be filled for both teams!")
            return
            
        posA = [i+1 for i, var in enumerate(self.bowlers_a) if var.get()]
        posB = [i+1 for i, var in enumerate(self.bowlers_b) if var.get()]
        
        if not (6 <= len(posA) <= 10):
            messagebox.showerror("Bowler Check", f"Team A must select between 6 and 10 bowlers (Currently checked: {len(posA)})")
            return
        if not (6 <= len(posB) <= 10):
            messagebox.showerror("Bowler Check", f"Team B must select between 6 and 10 bowlers (Currently checked: {len(posB)})")
            return
            
        # 2. Match Settings
        mode = self.format_var.get()
        session = self.session_var.get().strip()
        if not session:
            session = f"Session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.session_var.set(session)
            
        degree = determineDegree() if self.random_deg_var.get() else self.degree_var.get()
        
        # 3. Setup control flags
        self.sim_state.stop_event.clear()
        self.sim_state.pause_event.set()
        self.sim_state.step_event.clear()
        self.sim_state.instant_simulation = False
        
        # Toggle GUI states
        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal")
        self.btn_instant.config(state="normal")
        self.btn_stop.config(state="normal")
        self.btn_match_pdf.config(state="disabled")
        self.btn_series_pdf.config(state="disabled")
        
        # Clear live commentary
        self.txt_commentary.config(state="normal")
        self.txt_commentary.delete("1.0", tk.END)
        self.txt_commentary.config(state="disabled")
        
        # Reset Scorecard banner
        self.lbl_result_msg.config(text="Simulation in progress...")
        self.lbl_motm_msg.config(text="")
        
        # Reset active series matches list
        self.active_series_matches = []
        self.active_series_summary = None
        
        # Switch tab to Live Simulator
        self.notebook.select(self.tab_live)
        
        # Extract series matches count
        series_count_str = self.series_matches_var.get()
        if series_count_str.startswith("1"):
            series_count = 1
        else:
            series_count = int(series_count_str)
            
        # Extract placeholder weights
        p_weights = {
            "Dot": self.placeholder_dot.get(),
            "Run": self.placeholder_run.get(),
            "Double": self.placeholder_double.get(),
            "Four": self.placeholder_four.get(),
            "Six": self.placeholder_six.get(),
            "Out": self.placeholder_out.get(),
        }
        
        # Package match data
        match_info = {
            "teamA": teamA,
            "teamB": teamB,
            "teamAplayers": teamA_players,
            "teamBplayers": teamB_players,
            "posA": posA,
            "posB": posB,
            "degree": degree,
            "mode": mode,
            "players_database": self.players_database,
            "placeholder_weights": p_weights,
            "series_count": series_count
        }
        
        # Start Worker Thread
        self.worker_thread = threading.Thread(target=run_full_match_thread, args=(self.queue, match_info, self.sim_state))
        self.worker_thread.start()

    # ---------------------------------------------------------
    # QUEUE LISTENER & UI UPDATE CORE
    # ---------------------------------------------------------
    def poll_queue(self):
        try:
            while True:
                try:
                    msg = self.queue.get_nowait()
                except queue.Empty:
                    break
                
                try:
                    msg_type = msg[0]
                    data = msg[1]
                    
                    if msg_type == "inning_start":
                        team_name = data["team"]
                        opp_name = data["oppTeam"]
                        target_txt = f"Chasing: {data['target']} runs" if data["target"] else ""
                        self.match_hdr_label.config(text=f"Innings {data['inning_num']}: {team_name} Batting vs {opp_name}")
                        
                        if data["target"]:
                            self.lbl_target_info.config(text=f"TARGET: {data['target'] + 1} runs (Need {data['target'] + 1} from {300 if data['mode'] == 'ODI' else 120} balls)")
                            self.target_frame.pack(fill="x", pady=(10, 0))
                        else:
                            self.target_frame.pack_forget()
                            
                        self.log_commentary(f"=== Innings {data['inning_num']} Start: {team_name} innings ===", "system")
                        
                    elif msg_type == "ball_update":
                        # Score summary
                        tot_overs = 50 if data["inning_num"] == 1 and data["total_balls"] == 300 else (20 if data["total_balls"] == 120 else 50)
                        overs_disp = f"{data['balls'] // 6}.{data['balls'] % 6}"
                        
                        self.lbl_hud_runs.config(text=f"{data['runs']} / {data['wickets']}")
                        self.lbl_hud_overs.config(text=f"Overs: {overs_disp} / {tot_overs}")
                        
                        # Run rates
                        legal_balls = data["balls"]
                        crr = (data["runs"] / legal_balls * 6) if legal_balls > 0 else 0.00
                        
                        if data["target"] is not None:
                            needed = (data["target"] + 1) - data["runs"]
                            rem_balls = data["total_balls"] - data["balls"]
                            
                            if needed <= 0:
                                self.lbl_target_info.config(text="Target Chased Successfully!")
                                rrr = 0.00
                            else:
                                rrr = (needed / rem_balls * 6) if rem_balls > 0 else 99.99
                                self.lbl_target_info.config(text=f"TARGET: {data['target'] + 1} | Need {needed} runs from {rem_balls} balls (Required RR: {rrr:.2f})")
                            
                            self.lbl_hud_rr.config(text=f"CRR: {crr:.2f} | RRR: {rrr:.2f}")
                        else:
                            self.lbl_hud_rr.config(text=f"Run Rate: {crr:.2f}")
                        
                        # Batters Info
                        self.lbl_striker.config(text=f"* Striker: {data['striker_name']} - {data['striker_runs']} ({data['striker_balls']})  4s: {data['striker_4s']} | 6s: {data['striker_6s']}  SR: {(data['striker_runs']/data['striker_balls']*100 if data['striker_balls']>0 else 0.0):.2f}")
                        self.lbl_non_striker.config(text=f"  Non-Striker: {data['non_striker_name']} - {data['non_striker_runs']} ({data['non_striker_balls']})  4s: {data['non_striker_4s']} | 6s: {data['non_striker_6s']}")
                        
                        # Bowler Info
                        parts = data['bowler_overs'].split('.')
                        total_bowled = int(parts[0])*6 + int(parts[1])
                        econ = (data['bowler_runs'] / total_bowled * 6) if total_bowled > 0 else 0.00
                        
                        self.lbl_bowler.config(text=f"Bowler: {data['bowler_name']} - {data['bowler_overs']} ov | {data['bowler_maidens']} md | {data['bowler_runs']} runs | {data['bowler_wickets']} wkts | Econ: {econ:.2f}")
                        
                        # Commentary
                        self.log_commentary(data["commentary"], data["commentary_tag"])
                        
                        # Redraw Canvas badges for current over
                        self.draw_over_progression(data["over_balls"])
                        
                    elif msg_type == "over_end":
                        self.log_commentary(f"--- End of Over {data['overs']}: {data['team']} {data['runs']}/{data['wickets']} ---", "system")
                        
                    elif msg_type == "innings1_complete":
                        inn1 = data
                        self.log_commentary(f"=== Innings 1 Complete: {inn1['team']} scored {inn1['runs']}/{inn1['wickets']} in {inn1['balls']//6}.{inn1['balls']%6} overs ===", "system")
                        self.over_canvas.delete("all")
                        
                    elif msg_type == "series_match_start":
                        self.log_commentary(f"\n=== MATCH {data['match_idx']} OF {data['series_count']} STARTING ===", "system")
                        self.txt_commentary.config(state="normal")
                        self.txt_commentary.delete("1.0", tk.END)
                        self.txt_commentary.config(state="disabled")
                        self.match_hdr_label.config(text=f"Match {data['match_idx']} of {data['series_count']}: Preparing teams...")
                        
                    elif msg_type == "series_match_complete":
                        innings1 = data["innings1"]
                        innings2 = data["innings2"]
                        scorecard1 = generateScorecard(innings1)
                        bowling1 = BowlingFigures(innings1)
                        scorecard2 = generateScorecard(innings2)
                        bowling2 = BowlingFigures(innings2)
                        MOTM = getManOfTheMatch()
                        
                        match_entry = {
                            "innings1": innings1,
                            "innings2": innings2,
                            "scorecard1": scorecard1,
                            "bowling1": bowling1,
                            "scorecard2": scorecard2,
                            "bowling2": bowling2,
                            "motm": MOTM
                        }
                        self.active_series_matches.append(match_entry)
                        
                        teamA = innings1['team']
                        teamB = innings2['team']
                        if innings1['runs'] > innings2['runs']:
                            res = f"{teamA} won by {(innings1['runs'] - innings2['runs'])} runs"
                        elif innings1['runs'] < innings2['runs']:
                            res = f"{teamB} won by {10 - innings2['wickets']} wickets"
                        else:
                            res = "Match tied"
                            
                        # Save scorecards to generatedStats.txt
                        session = self.session_var.get().strip()
                        saveScorecard(teamA, innings1, scorecard1, bowling1, session_name=f"{session}_Match_{data['match_idx']}")
                        saveScorecard(teamB, innings2, scorecard2, bowling2)
                        
                        with open("generatedStats.txt", "a", encoding="utf-8") as f:
                            f.write(f"Match {data['match_idx']}: {res}\n\n")
                            
                        saveStats()
                        self.log_commentary(f"\n=== MATCH COMPLETE: {res} | MOTM: {MOTM} ===\n", "system")
                        
                    elif msg_type == "series_complete":
                        self.process_series_completion()
                        
                    elif msg_type == "match_complete":
                        # Sim complete
                        innings1 = data["innings1"]
                        innings2 = data["innings2"]
                        
                        self.process_match_completion(innings1, innings2)
                except Exception as inner_e:
                    print(f"Error processing queue message: {inner_e}")
                    import traceback
                    traceback.print_exc()
        finally:
            self.root.after(100, self.poll_queue)

    def draw_over_progression(self, balls_list):
        self.over_canvas.delete("all")
        # Draw circular badges
        x_offset = 15
        for ball in balls_list:
            bg = "#585b70"  # grey default
            fg = TEXT_FG
            
            if ball == '•' or ball == '0':
                bg = "#313244"
            elif ball in ('1', '2', '3'):
                bg = "#4b7d5a"  # forest green
            elif ball == '4':
                bg = "#1e66f5"  # bright blue
            elif ball == '6':
                bg = "#8839ef"  # purple
            elif ball == 'W':
                bg = ACCENT_RED
                fg = DARK_BG
            elif ball in ('nb', 'wd', 'lb1', 'lb2', 'lb4', 'b1', 'b2', 'b4') or 'lb' in ball or 'b' in ball:
                bg = "#fe640b"  # orange
                
            # Circle drawing
            self.over_canvas.create_oval(x_offset, 2, x_offset + 26, 28, fill=bg, outline=BORDER_COLOR)
            self.over_canvas.create_text(x_offset + 13, 15, text=ball, fill=fg, font=("Helvetica", 8, "bold"))
            x_offset += 32

    def export_match_to_pdf_handler(self):
        # Determine if we are in series mode
        if len(self.active_series_matches) > 0:
            try:
                selected_idx = self.series_matches_nb.index("current")
                self.export_match_to_pdf(match_idx=selected_idx)
            except Exception as e:
                messagebox.showerror("Error", f"Could not determine active series match tab:\n{e}")
        else:
            self.export_match_to_pdf(match_idx=None)

    def export_match_to_pdf(self, match_idx=None):
        if match_idx is not None:
            if match_idx < 0 or match_idx >= len(self.active_series_matches):
                messagebox.showerror("Error", "Invalid match index selected!")
                return
            match_data = self.active_series_matches[match_idx]
            inn1 = match_data["innings1"]
            inn2 = match_data["innings2"]
            scorecard1 = match_data["scorecard1"]
            scorecard2 = match_data["scorecard2"]
            bowling1 = match_data["bowling1"]
            bowling2 = match_data["bowling2"]
            result_str = match_data.get("result", "")
            motm = match_data.get("motm", "N/A")
            
            title = f"Save Match {match_idx+1} Scorecard PDF"
            initialfile = f"Scorecard_Match{match_idx+1}_{inn1['team']}_vs_{inn2['team']}.pdf"
        else:
            if not self.active_innings:
                messagebox.showerror("Error", "No match data available to export!")
                return
            inn1 = self.active_innings["innings1"]
            inn2 = self.active_innings["innings2"]
            scorecard1 = self.active_innings["scorecard1"]
            scorecard2 = self.active_innings["scorecard2"]
            bowling1 = self.active_innings["bowling1"]
            bowling2 = self.active_innings["bowling2"]
            result_str = self.active_innings["result"]
            motm = self.active_innings["motm"]
            
            title = "Save Match Scorecard PDF"
            initialfile = f"Scorecard_{inn1['team']}_vs_{inn2['team']}.pdf"
            
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title=title,
            initialfile=initialfile
        )
        if not file_path:
            return
            
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            
            doc = SimpleDocTemplate(file_path, pagesize=letter,
                                    rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            
            # Styles matching the application colors
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=colors.HexColor("#1e1e2e"),
                spaceAfter=6,
                alignment=1
            )
            subtitle_style = ParagraphStyle(
                'DocSubTitle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor("#585b70"),
                spaceAfter=15,
                alignment=1
            )
            h2_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=13,
                textColor=colors.HexColor("#1e1e2e"),
                spaceBefore=10,
                spaceAfter=6
            )
            normal_bold = ParagraphStyle(
                'NormalBold',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor("#1e1e2e")
            )
            normal_bold_white = ParagraphStyle(
                'NormalBoldWhite',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor("#cdd6f4")
            )
            normal_text = ParagraphStyle(
                'NormalText',
                parent=styles['Normal'],
                fontSize=8.5,
                textColor=colors.HexColor("#252538")
            )
            normal_text_white = ParagraphStyle(
                'NormalTextWhite',
                parent=styles['Normal'],
                fontSize=8.5,
                textColor=colors.HexColor("#cdd6f4")
            )
            bold_label = ParagraphStyle(
                'BoldLabel',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor("#252538")
            )
            
            elements = []
            
            # Define local helper for building innings scorecard tables
            def build_innings_tables(inn_data, scorecard_data, bowling_data):
                inn_elements = []
                team = inn_data['team']
                runs_val = inn_data['runs']
                wkts_val = inn_data['wickets']
                overs_val = f"{inn_data['balls'] // 6}.{inn_data['balls'] % 6}"
                
                # Title
                inn_elements.append(Paragraph(f"<b>{team.upper()} INNINGS: {runs_val}/{wkts_val} ({overs_val} Overs)</b>", h2_style))
                inn_elements.append(Spacer(1, 5))
                
                # Batting Scorecard
                bat_headers = [
                    Paragraph("<b>Batsman</b>", normal_bold_white),
                    Paragraph("<b>Status</b>", normal_bold_white),
                    Paragraph("<b>Runs</b>", normal_bold_white),
                    Paragraph("<b>Balls</b>", normal_bold_white),
                    Paragraph("<b>4s</b>", normal_bold_white),
                    Paragraph("<b>6s</b>", normal_bold_white),
                    Paragraph("<b>S/R</b>", normal_bold_white)
                ]
                bat_rows = [bat_headers]
                for r_item in scorecard_data:
                    bat_rows.append([
                        Paragraph(r_item[0], normal_text_white),
                        Paragraph(r_item[6], normal_text_white),
                        Paragraph(str(r_item[1]), normal_text_white),
                        Paragraph(str(r_item[2]), normal_text_white),
                        Paragraph(str(r_item[3]), normal_text_white),
                        Paragraph(str(r_item[4]), normal_text_white),
                        Paragraph(f"{r_item[5]:.2f}" if isinstance(r_item[5], float) else str(r_item[5]), normal_text_white)
                    ])
                
                # Did Not Bat
                did_not_bat = [prog[0] for prog in inn_data['batting_xi'].values() if len(prog) - 1 == 0]
                dnb_text = "<b>Did Not Bat:</b> " + (", ".join(did_not_bat) if did_not_bat else "None")
                
                # Extras
                ext = inn_data
                extras_text = f"<b>Extras:</b> {ext['wides']+ext['no balls']+ext['leg byes']+ext['byes']} (wd {ext['wides']}, nb {ext['no balls']}, lb {ext['leg byes']}, b {ext['byes']})"
                
                # Extras row
                bat_rows.append([Paragraph(extras_text, normal_text_white), "", "", "", "", "", ""])
                # DNB row
                bat_rows.append([Paragraph(dnb_text, normal_text_white), "", "", "", "", "", ""])
                
                bat_tbl = Table(bat_rows, colWidths=[150, 130, 50, 50, 40, 40, 80])
                
                bat_tbl_style = [
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#252538")),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#313244")),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('ALIGN', (0,0), (1,-1), 'LEFT'), # player name and status
                    ('SPAN', (0, -2), (6, -2)), # extras
                    ('SPAN', (0, -1), (6, -1)), # dnb
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ]
                
                # Add alternating row backgrounds
                for idx in range(1, len(bat_rows) - 2):
                    bg = "#1e1e2e" if idx % 2 == 1 else "#252538"
                    bat_tbl_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor(bg)))
                # Set extras & dnb background
                bat_tbl_style.append(('BACKGROUND', (0, -2), (-1, -1), colors.HexColor("#1e1e2e")))
                
                bat_tbl.setStyle(TableStyle(bat_tbl_style))
                inn_elements.append(bat_tbl)
                inn_elements.append(Spacer(1, 10))
                
                # Bowling Card
                bowl_headers = [
                    Paragraph("<b>Bowler</b>", normal_bold_white),
                    Paragraph("<b>Overs</b>", normal_bold_white),
                    Paragraph("<b>Maidens</b>", normal_bold_white),
                    Paragraph("<b>Runs</b>", normal_bold_white),
                    Paragraph("<b>Wickets</b>", normal_bold_white),
                    Paragraph("<b>NBs</b>", normal_bold_white),
                    Paragraph("<b>WDs</b>", normal_bold_white)
                ]
                bowl_rows = [bowl_headers]
                for r_item in bowling_data:
                    bowl_rows.append([
                        Paragraph(r_item[0], normal_text_white),
                        Paragraph(str(r_item[1]), normal_text_white),
                        Paragraph(str(r_item[2]), normal_text_white),
                        Paragraph(str(r_item[3]), normal_text_white),
                        Paragraph(str(r_item[4]), normal_text_white),
                        Paragraph(str(r_item[5]), normal_text_white),
                        Paragraph(str(r_item[6]), normal_text_white)
                    ])
                
                bowl_tbl = Table(bowl_rows, colWidths=[180, 60, 60, 60, 60, 60, 60])
                bowl_tbl_style = [
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#252538")),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#313244")),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('ALIGN', (0,0), (0,-1), 'LEFT'), # bowler name
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ]
                for idx in range(1, len(bowl_rows)):
                    bg = "#1e1e2e" if idx % 2 == 1 else "#252538"
                    bowl_tbl_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor(bg)))
                    
                bowl_tbl.setStyle(TableStyle(bowl_tbl_style))
                inn_elements.append(bowl_tbl)
                inn_elements.append(Spacer(1, 10))
                
                # FOW & Partnerships
                fow_list = []
                runs_accum = 0
                legal_deliveries = 0
                for ball in inn_data['balls progression']:
                    if ball == "single":
                        runs_accum += 1
                        legal_deliveries += 1
                    elif ball == "double":
                        runs_accum += 2
                        legal_deliveries += 1
                    elif ball == "triple":
                        runs_accum += 3
                        legal_deliveries += 1
                    elif ball == "four":
                        runs_accum += 4
                        legal_deliveries += 1
                    elif ball == "six":
                        runs_accum += 6
                        legal_deliveries += 1
                    elif ball == "noball":
                        runs_accum += 1
                    elif ball == "wide":
                        runs_accum += 1
                    elif ball.startswith("legbye"):
                        r = int(ball.replace("legbye", ""))
                        runs_accum += r
                        legal_deliveries += 1
                    elif ball.startswith("bye"):
                        r = int(ball.replace("bye", ""))
                        runs_accum += r
                        legal_deliveries += 1
                    elif isinstance(ball, int):
                        runs_accum += ball
                        legal_deliveries += 1
                    elif ball == "wicket":
                        legal_deliveries += 1
                        fow_list.append(f"{runs_accum}/{len(fow_list)+1} ({legal_deliveries//6}.{legal_deliveries%6} ov)")
                
                fow_text = "<b>Fall of Wickets:</b> " + (", ".join(fow_list) if fow_list else "None")
                fow_para = Paragraph(fow_text, ParagraphStyle('FOW', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor("#252538"), leading=11))
                
                # Partnerships
                part_rows = [[Paragraph("<b>Batsman 1</b>", normal_bold), Paragraph("<b>Batsman 2</b>", normal_bold), Paragraph("<b>Runs</b>", normal_bold), Paragraph("<b>Balls</b>", normal_bold)]]
                for p in inn_data['partnerships']:
                    part_rows.append([
                        Paragraph(p[0], normal_text),
                        Paragraph(p[1], normal_text),
                        Paragraph(str(p[2]), normal_text),
                        Paragraph(str(p[3]), normal_text)
                    ])
                
                part_tbl = Table(part_rows, colWidths=[160, 160, 110, 110])
                part_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e6e9ef")),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#d3d7e0")),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('ALIGN', (0,0), (1,-1), 'LEFT'), # batsmen names
                    ('TOPPADDING', (0,0), (-1,-1), 3),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ]))
                
                inn_elements.append(fow_para)
                inn_elements.append(Spacer(1, 10))
                inn_elements.append(Paragraph("<b>Partnerships:</b>", bold_label))
                inn_elements.append(Spacer(1, 3))
                inn_elements.append(part_tbl)
                
                return inn_elements

            # 1. Header Card
            m_header_title = "CRICKET SIMULATOR MATCH REPORT" if match_idx is None else f"MATCH {match_idx+1} REPORT"
            header_data = [
                [Paragraph(f"<b>{m_header_title}</b>", title_style)],
                [Paragraph(f"Format: {self.format_var.get()} | Session: {self.session_var.get()} | Match Type: {self.degree_var.get().capitalize()}", subtitle_style)]
            ]
            header_tbl = Table(header_data, colWidths=[540])
            header_tbl.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            elements.append(header_tbl)
            
            # 2. Result Banner
            banner_text = f"<b>RESULT: {result_str.upper()}</b><br/>★ Man of the Match: {motm} ★"
            banner_tbl = Table([[Paragraph(banner_text, ParagraphStyle('BannerStyle', parent=styles['Normal'], fontSize=11, alignment=1, textColor=colors.HexColor("#1e1e2e")))]], colWidths=[540])
            banner_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#a6e3a1")), # Success green
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#89b4fa")),
            ]))
            elements.append(banner_tbl)
            elements.append(Spacer(1, 15))
            
            # Innings 1
            elements.append(Paragraph("<b>FIRST INNINGS SCORECARD</b>", ParagraphStyle('InnsHeader1_single', parent=styles['Heading2'], fontSize=15, textColor=colors.HexColor("#1e1e2e"), spaceBefore=10, spaceAfter=10)))
            elements.extend(build_innings_tables(inn1, scorecard1, bowling1))
            
            # Page Break
            elements.append(PageBreak())
            
            # Innings 2
            elements.append(Paragraph("<b>SECOND INNINGS SCORECARD</b>", ParagraphStyle('InnsHeader2_single', parent=styles['Heading2'], fontSize=15, textColor=colors.HexColor("#1e1e2e"), spaceBefore=10, spaceAfter=10)))
            elements.extend(build_innings_tables(inn2, scorecard2, bowling2))
            
            doc.build(elements)
            messagebox.showinfo("Export Successful", f"Match scorecard successfully saved to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred during PDF generation:\n{e}")
            import traceback
            traceback.print_exc()

    def export_series_to_pdf(self):
        if not self.active_series_matches:
            messagebox.showerror("Error", "No series data available to export!")
            return
            
        teamA = self.team_a_var.get().strip()
        teamB = self.team_b_var.get().strip()
        title = "Save Series Report PDF"
        initialfile = f"Series_{teamA}_vs_{teamB}.pdf"
        
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title=title,
            initialfile=initialfile
        )
        if not file_path:
            return
            
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            
            doc = SimpleDocTemplate(file_path, pagesize=letter,
                                    rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            
            # Styles matching the application colors
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=22,
                textColor=colors.HexColor("#1e1e2e"),
                spaceAfter=6,
                alignment=1
            )
            subtitle_style = ParagraphStyle(
                'DocSubTitle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor("#585b70"),
                spaceAfter=15,
                alignment=1
            )
            h2_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=13,
                textColor=colors.HexColor("#1e1e2e"),
                spaceBefore=10,
                spaceAfter=6
            )
            normal_bold = ParagraphStyle(
                'NormalBold',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor("#1e1e2e")
            )
            normal_bold_white = ParagraphStyle(
                'NormalBoldWhite',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor("#cdd6f4")
            )
            normal_text = ParagraphStyle(
                'NormalText',
                parent=styles['Normal'],
                fontSize=8.5,
                textColor=colors.HexColor("#252538")
            )
            normal_text_white = ParagraphStyle(
                'NormalTextWhite',
                parent=styles['Normal'],
                fontSize=8.5,
                textColor=colors.HexColor("#cdd6f4")
            )
            bold_label = ParagraphStyle(
                'BoldLabel',
                parent=styles['Normal'],
                fontSize=9,
                fontName='Helvetica-Bold',
                textColor=colors.HexColor("#252538")
            )
            
            elements = []
            
            # Define local helper for building innings scorecard tables
            def build_innings_tables(inn_data, scorecard_data, bowling_data):
                inn_elements = []
                team = inn_data['team']
                runs_val = inn_data['runs']
                wkts_val = inn_data['wickets']
                overs_val = f"{inn_data['balls'] // 6}.{inn_data['balls'] % 6}"
                
                # Title
                inn_elements.append(Paragraph(f"<b>{team.upper()} INNINGS: {runs_val}/{wkts_val} ({overs_val} Overs)</b>", h2_style))
                inn_elements.append(Spacer(1, 5))
                
                # Batting Scorecard
                bat_headers = [
                    Paragraph("<b>Batsman</b>", normal_bold_white),
                    Paragraph("<b>Status</b>", normal_bold_white),
                    Paragraph("<b>Runs</b>", normal_bold_white),
                    Paragraph("<b>Balls</b>", normal_bold_white),
                    Paragraph("<b>4s</b>", normal_bold_white),
                    Paragraph("<b>6s</b>", normal_bold_white),
                    Paragraph("<b>S/R</b>", normal_bold_white)
                ]
                bat_rows = [bat_headers]
                for r_item in scorecard_data:
                    bat_rows.append([
                        Paragraph(r_item[0], normal_text_white),
                        Paragraph(r_item[6], normal_text_white),
                        Paragraph(str(r_item[1]), normal_text_white),
                        Paragraph(str(r_item[2]), normal_text_white),
                        Paragraph(str(r_item[3]), normal_text_white),
                        Paragraph(str(r_item[4]), normal_text_white),
                        Paragraph(f"{r_item[5]:.2f}" if isinstance(r_item[5], float) else str(r_item[5]), normal_text_white)
                    ])
                
                # Did Not Bat
                did_not_bat = [prog[0] for prog in inn_data['batting_xi'].values() if len(prog) - 1 == 0]
                dnb_text = "<b>Did Not Bat:</b> " + (", ".join(did_not_bat) if did_not_bat else "None")
                
                # Extras
                ext = inn_data
                extras_text = f"<b>Extras:</b> {ext['wides']+ext['no balls']+ext['leg byes']+ext['byes']} (wd {ext['wides']}, nb {ext['no balls']}, lb {ext['leg byes']}, b {ext['byes']})"
                
                # Extras row
                bat_rows.append([Paragraph(extras_text, normal_text_white), "", "", "", "", "", ""])
                # DNB row
                bat_rows.append([Paragraph(dnb_text, normal_text_white), "", "", "", "", "", ""])
                
                bat_tbl = Table(bat_rows, colWidths=[150, 130, 50, 50, 40, 40, 80])
                
                bat_tbl_style = [
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#252538")),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#313244")),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('ALIGN', (0,0), (1,-1), 'LEFT'), # player name and status
                    ('SPAN', (0, -2), (6, -2)), # extras
                    ('SPAN', (0, -1), (6, -1)), # dnb
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ]
                
                # Add alternating row backgrounds
                for idx in range(1, len(bat_rows) - 2):
                    bg = "#1e1e2e" if idx % 2 == 1 else "#252538"
                    bat_tbl_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor(bg)))
                # Set extras & dnb background
                bat_tbl_style.append(('BACKGROUND', (0, -2), (-1, -1), colors.HexColor("#1e1e2e")))
                
                bat_tbl.setStyle(TableStyle(bat_tbl_style))
                inn_elements.append(bat_tbl)
                inn_elements.append(Spacer(1, 10))
                
                # Bowling Card
                bowl_headers = [
                    Paragraph("<b>Bowler</b>", normal_bold_white),
                    Paragraph("<b>Overs</b>", normal_bold_white),
                    Paragraph("<b>Maidens</b>", normal_bold_white),
                    Paragraph("<b>Runs</b>", normal_bold_white),
                    Paragraph("<b>Wickets</b>", normal_bold_white),
                    Paragraph("<b>NBs</b>", normal_bold_white),
                    Paragraph("<b>WDs</b>", normal_bold_white)
                ]
                bowl_rows = [bowl_headers]
                for r_item in bowling_data:
                    bowl_rows.append([
                        Paragraph(r_item[0], normal_text_white),
                        Paragraph(str(r_item[1]), normal_text_white),
                        Paragraph(str(r_item[2]), normal_text_white),
                        Paragraph(str(r_item[3]), normal_text_white),
                        Paragraph(str(r_item[4]), normal_text_white),
                        Paragraph(str(r_item[5]), normal_text_white),
                        Paragraph(str(r_item[6]), normal_text_white)
                    ])
                
                bowl_tbl = Table(bowl_rows, colWidths=[180, 60, 60, 60, 60, 60, 60])
                bowl_tbl_style = [
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#252538")),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#313244")),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('ALIGN', (0,0), (0,-1), 'LEFT'), # bowler name
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                ]
                for idx in range(1, len(bowl_rows)):
                    bg = "#1e1e2e" if idx % 2 == 1 else "#252538"
                    bowl_tbl_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor(bg)))
                    
                bowl_tbl.setStyle(TableStyle(bowl_tbl_style))
                inn_elements.append(bowl_tbl)
                inn_elements.append(Spacer(1, 10))
                
                # FOW & Partnerships
                fow_list = []
                runs_accum = 0
                legal_deliveries = 0
                for ball in inn_data['balls progression']:
                    if ball == "single":
                        runs_accum += 1
                        legal_deliveries += 1
                    elif ball == "double":
                        runs_accum += 2
                        legal_deliveries += 1
                    elif ball == "triple":
                        runs_accum += 3
                        legal_deliveries += 1
                    elif ball == "four":
                        runs_accum += 4
                        legal_deliveries += 1
                    elif ball == "six":
                        runs_accum += 6
                        legal_deliveries += 1
                    elif ball == "noball":
                        runs_accum += 1
                    elif ball == "wide":
                        runs_accum += 1
                    elif ball.startswith("legbye"):
                        r = int(ball.replace("legbye", ""))
                        runs_accum += r
                        legal_deliveries += 1
                    elif ball.startswith("bye"):
                        r = int(ball.replace("bye", ""))
                        runs_accum += r
                        legal_deliveries += 1
                    elif isinstance(ball, int):
                        runs_accum += ball
                        legal_deliveries += 1
                    elif ball == "wicket":
                        legal_deliveries += 1
                        fow_list.append(f"{runs_accum}/{len(fow_list)+1} ({legal_deliveries//6}.{legal_deliveries%6} ov)")
                
                fow_text = "<b>Fall of Wickets:</b> " + (", ".join(fow_list) if fow_list else "None")
                fow_para = Paragraph(fow_text, ParagraphStyle('FOW', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor("#252538"), leading=11))
                
                # Partnerships
                part_rows = [[Paragraph("<b>Batsman 1</b>", normal_bold), Paragraph("<b>Batsman 2</b>", normal_bold), Paragraph("<b>Runs</b>", normal_bold), Paragraph("<b>Balls</b>", normal_bold)]]
                for p in inn_data['partnerships']:
                    part_rows.append([
                        Paragraph(p[0], normal_text),
                        Paragraph(p[1], normal_text),
                        Paragraph(str(p[2]), normal_text),
                        Paragraph(str(p[3]), normal_text)
                    ])
                
                part_tbl = Table(part_rows, colWidths=[160, 160, 110, 110])
                part_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e6e9ef")),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#d3d7e0")),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('ALIGN', (0,0), (1,-1), 'LEFT'), # batsmen names
                    ('TOPPADDING', (0,0), (-1,-1), 3),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ]))
                
                inn_elements.append(fow_para)
                inn_elements.append(Spacer(1, 10))
                inn_elements.append(Paragraph("<b>Partnerships:</b>", bold_label))
                inn_elements.append(Spacer(1, 3))
                inn_elements.append(part_tbl)
                
                return inn_elements

            # 1. Series Header Card
            series_res = self.active_series_summary["result"]
            header_data = [
                [Paragraph("<b>CRICKET SIMULATOR SERIES REPORT</b>", title_style)],
                [Paragraph(f"Format: {self.format_var.get()} | Series: {self.session_var.get().strip()}", subtitle_style)]
            ]
            header_tbl = Table(header_data, colWidths=[540])
            header_tbl.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            elements.append(header_tbl)
            
            # 2. Series Result Banner
            banner_text = f"<b>SERIES RESULT: {series_res.upper()}</b><br/>★ Series Winners: {self.active_series_summary['winner_team']} ★"
            banner_tbl = Table([[Paragraph(banner_text, ParagraphStyle('BannerStyle', parent=styles['Normal'], fontSize=11, alignment=1, textColor=colors.HexColor("#1e1e2e")))]], colWidths=[540])
            banner_tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#a6e3a1")), # Success green
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                ('TOPPADDING', (0,0), (-1,-1), 8),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#89b4fa")),
            ]))
            elements.append(banner_tbl)
            elements.append(Spacer(1, 15))
            
            # 3. Series Aggregated Stats (Leaderboards)
            elements.append(Paragraph("<b>SERIES LEADING RUN SCORERS</b>", h2_style))
            bat_headers = [
                Paragraph("<b>Batsman</b>", normal_bold_white),
                Paragraph("<b>Innings</b>", normal_bold_white),
                Paragraph("<b>Runs</b>", normal_bold_white),
                Paragraph("<b>Balls</b>", normal_bold_white),
                Paragraph("<b>4s</b>", normal_bold_white),
                Paragraph("<b>6s</b>", normal_bold_white),
                Paragraph("<b>S/R</b>", normal_bold_white)
            ]
            bat_rows = [bat_headers]
            for name, stats in self.active_series_summary["batting_stats"]:
                sr = (stats["runs"] / stats["balls"] * 100) if stats["balls"] > 0 else 0.0
                bat_rows.append([
                    Paragraph(name, normal_text_white),
                    Paragraph(f"{stats['matches']} Inns", normal_text_white),
                    Paragraph(str(stats['runs']), normal_text_white),
                    Paragraph(str(stats['balls']), normal_text_white),
                    Paragraph(str(stats['4s']), normal_text_white),
                    Paragraph(str(stats['6s']), normal_text_white),
                    Paragraph(f"{sr:.2f}", normal_text_white)
                ])
            bat_tbl = Table(bat_rows, colWidths=[150, 130, 50, 50, 40, 40, 80])
            bat_tbl_style = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#252538")),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#313244")),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('ALIGN', (0,0), (1,-1), 'LEFT'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]
            for idx in range(1, len(bat_rows)):
                bg = "#1e1e2e" if idx % 2 == 1 else "#252538"
                bat_tbl_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor(bg)))
            bat_tbl.setStyle(TableStyle(bat_tbl_style))
            elements.append(bat_tbl)
            elements.append(Spacer(1, 15))
            
            elements.append(Paragraph("<b>SERIES LEADING WICKET TAKERS</b>", h2_style))
            bowl_headers = [
                Paragraph("<b>Bowler</b>", normal_bold_white),
                Paragraph("<b>Overs</b>", normal_bold_white),
                Paragraph("<b>Maidens</b>", normal_bold_white),
                Paragraph("<b>Runs</b>", normal_bold_white),
                Paragraph("<b>Wickets</b>", normal_bold_white),
                Paragraph("<b>NBs</b>", normal_bold_white),
                Paragraph("<b>WDs</b>", normal_bold_white)
            ]
            bowl_rows = [bowl_headers]
            for name, stats in self.active_series_summary["bowling_stats"]:
                overs_str = f"{stats['balls']//6}.{stats['balls']%6}"
                bowl_rows.append([
                    Paragraph(name, normal_text_white),
                    Paragraph(overs_str, normal_text_white),
                    Paragraph(str(stats['maidens']), normal_text_white),
                    Paragraph(str(stats['runs']), normal_text_white),
                    Paragraph(str(stats['wickets']), normal_text_white),
                    Paragraph(str(stats['noballs']), normal_text_white),
                    Paragraph(str(stats['wides']), normal_text_white)
                ])
            bowl_tbl = Table(bowl_rows, colWidths=[180, 60, 60, 60, 60, 60, 60])
            bowl_tbl_style = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#252538")),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#313244")),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('ALIGN', (0,0), (0,-1), 'LEFT'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]
            for idx in range(1, len(bowl_rows)):
                bg = "#1e1e2e" if idx % 2 == 1 else "#252538"
                bowl_tbl_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor(bg)))
            bowl_tbl.setStyle(TableStyle(bowl_tbl_style))
            elements.append(bowl_tbl)
            elements.append(Spacer(1, 15))
            
            # Page break before individual match scorecards
            elements.append(PageBreak())
            
            # 4. Individual Match Reports
            for match_idx, m in enumerate(self.active_series_matches, 1):
                mi1 = m["innings1"]
                mi2 = m["innings2"]
                m_teamA = mi1["team"]
                m_teamB = mi2["team"]
                if mi1["runs"] > mi2["runs"]:
                    m_res = f"{m_teamA} won by {mi1['runs'] - mi2['runs']} runs"
                elif mi1["runs"] < mi2["runs"]:
                    m_res = f"{m_teamB} won by {10 - mi2['wickets']} wickets"
                else:
                    m_res = "Match tied"
                    
                elements.append(Paragraph(f"<b>MATCH {match_idx} REPORT: {m_teamA} vs {m_teamB}</b>", ParagraphStyle(f'MReport_{match_idx}', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor("#1e1e2e"), spaceBefore=10, spaceAfter=5)))
                
                m_banner_text = f"<b>RESULT: {m_res.upper()}</b><br/>★ Man of the Match: {m['motm']} ★"
                m_banner_tbl = Table([[Paragraph(m_banner_text, ParagraphStyle(f'MBannerStyle_{match_idx}', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.HexColor("#1e1e2e")))]], colWidths=[540])
                m_banner_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f9e2af")), # Warm yellow
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#fab387")),
                ]))
                elements.append(m_banner_tbl)
                elements.append(Spacer(1, 10))
                
                # Innings 1 Scorecard
                elements.append(Paragraph("<b>FIRST INNINGS SCORECARD</b>", ParagraphStyle(f'InnsHeader1_{match_idx}', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor("#1e1e2e"), spaceBefore=10, spaceAfter=10)))
                elements.extend(build_innings_tables(mi1, m['scorecard1'], m['bowling1']))
                
                elements.append(PageBreak())
                
                # Innings 2 Scorecard
                elements.append(Paragraph("<b>SECOND INNINGS SCORECARD</b>", ParagraphStyle(f'InnsHeader2_{match_idx}', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor("#1e1e2e"), spaceBefore=10, spaceAfter=10)))
                elements.extend(build_innings_tables(mi2, m['scorecard2'], m['bowling2']))
                
                if match_idx < len(self.active_series_matches):
                    elements.append(PageBreak())
                    
            doc.build(elements)
            messagebox.showinfo("Export Successful", f"Series report successfully saved to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred during PDF generation:\n{e}")
            import traceback
            traceback.print_exc()

    # ---------------------------------------------------------
    # SERIES COMPLETION STATS & UI MANAGEMENT
    # ---------------------------------------------------------
    def calculate_series_stats(self):
        self.active_series_batting_stats = {}
        self.active_series_bowling_stats = {}
        
        for m in self.active_series_matches:
            # 1. Batting Innings 1
            inn1 = m["innings1"]
            for batter, prog in inn1['batting_xi'].items():
                if prog:
                    name = prog[0]
                    team = inn1['team']
                    runs = sum([p for p in prog if isinstance(p, int)])
                    balls = len(prog) - 1
                    singles = prog.count(1)
                    doubles = prog.count(2)
                    triples = prog.count(3)
                    fours = prog.count(4)
                    sixes = prog.count(6)
                    out_status = "not out" if prog[-1] != "W" else "out"
                    out = 1 if out_status == "out" else 0
                    fifty = 1 if 50 <= runs < 100 else 0
                    century = 1 if runs >= 100 else 0
                    
                    if name not in self.active_series_batting_stats:
                        self.active_series_batting_stats[name] = [team, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    
                    self.active_series_batting_stats[name][1] += 1        # Inns
                    self.active_series_batting_stats[name][2] += runs     # Runs
                    self.active_series_batting_stats[name][3] += balls    # Balls
                    self.active_series_batting_stats[name][4] += singles  # 1s
                    self.active_series_batting_stats[name][5] += doubles  # 2s
                    self.active_series_batting_stats[name][6] += triples  # 3s
                    self.active_series_batting_stats[name][7] += fours    # 4s
                    self.active_series_batting_stats[name][8] += sixes    # 6s
                    self.active_series_batting_stats[name][9] += out      # Outs
                    self.active_series_batting_stats[name][10] += fifty   # 50s
                    self.active_series_batting_stats[name][11] += century # 100s
            
            # 2. Batting Innings 2
            inn2 = m["innings2"]
            for batter, prog in inn2['batting_xi'].items():
                if prog:
                    name = prog[0]
                    team = inn2['team']
                    runs = sum([p for p in prog if isinstance(p, int)])
                    balls = len(prog) - 1
                    singles = prog.count(1)
                    doubles = prog.count(2)
                    triples = prog.count(3)
                    fours = prog.count(4)
                    sixes = prog.count(6)
                    out_status = "not out" if prog[-1] != "W" else "out"
                    out = 1 if out_status == "out" else 0
                    fifty = 1 if 50 <= runs < 100 else 0
                    century = 1 if runs >= 100 else 0
                    
                    if name not in self.active_series_batting_stats:
                        self.active_series_batting_stats[name] = [team, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                    
                    self.active_series_batting_stats[name][1] += 1
                    self.active_series_batting_stats[name][2] += runs
                    self.active_series_batting_stats[name][3] += balls
                    self.active_series_batting_stats[name][4] += singles
                    self.active_series_batting_stats[name][5] += doubles
                    self.active_series_batting_stats[name][6] += triples
                    self.active_series_batting_stats[name][7] += fours
                    self.active_series_batting_stats[name][8] += sixes
                    self.active_series_batting_stats[name][9] += out
                    self.active_series_batting_stats[name][10] += fifty
                    self.active_series_batting_stats[name][11] += century

            # 3. Bowling Innings 1 (Bowlers in Innings 1)
            maiden_seq = ['dot', 'dot', 'dot', 'dot', 'dot', 'dot']
            for bowler, item in inn1['bowlers'].items():
                name = item['prog'][0]
                team = inn1['opp']
                balls = item['balls']
                wickets = item['wickets']
                noballs = item['no balls']
                wides = item['wides']
                wick5 = 1 if wickets >= 5 else 0
                
                runs = 0
                for i in item['prog']:
                    if i == 'single': runs += 1
                    elif i == 'double': runs += 2
                    elif i == 'triple': runs += 3
                    elif i == 'four': runs += 4
                    elif i == 'six': runs += 6
                    elif i == 'noball': runs += 1
                    elif i == 'wide': runs += 1
                    
                maidens = 0
                for i in range(len(item['prog']) - 5):
                    if item['prog'][i:i+6] == maiden_seq:
                        maidens += 1
                
                if balls > 0:
                    if name not in self.active_series_bowling_stats:
                        self.active_series_bowling_stats[name] = [team, 0, 0, 0, 0, 0, 0, 0, 0]
                        
                    self.active_series_bowling_stats[name][1] += 1        # Inns
                    self.active_series_bowling_stats[name][2] += balls     # Balls
                    self.active_series_bowling_stats[name][3] += maidens   # Maidens
                    self.active_series_bowling_stats[name][4] += runs      # Runs
                    self.active_series_bowling_stats[name][5] += wickets   # Wickets
                    self.active_series_bowling_stats[name][6] += noballs   # NBs
                    self.active_series_bowling_stats[name][7] += wides     # WDs
                    self.active_series_bowling_stats[name][8] += wick5     # 5w

            # 4. Bowling Innings 2 (Bowlers in Innings 2)
            for bowler, item in inn2['bowlers'].items():
                name = item['prog'][0]
                team = inn2['opp']
                balls = item['balls']
                wickets = item['wickets']
                noballs = item['no balls']
                wides = item['wides']
                wick5 = 1 if wickets >= 5 else 0
                
                runs = 0
                for i in item['prog']:
                    if i == 'single': runs += 1
                    elif i == 'double': runs += 2
                    elif i == 'triple': runs += 3
                    elif i == 'four': runs += 4
                    elif i == 'six': runs += 6
                    elif i == 'noball': runs += 1
                    elif i == 'wide': runs += 1
                    
                maidens = 0
                for i in range(len(item['prog']) - 5):
                    if item['prog'][i:i+6] == maiden_seq:
                        maidens += 1
                
                if balls > 0:
                    if name not in self.active_series_bowling_stats:
                        self.active_series_bowling_stats[name] = [team, 0, 0, 0, 0, 0, 0, 0, 0]
                        
                    self.active_series_bowling_stats[name][1] += 1
                    self.active_series_bowling_stats[name][2] += balls
                    self.active_series_bowling_stats[name][3] += maidens
                    self.active_series_bowling_stats[name][4] += runs
                    self.active_series_bowling_stats[name][5] += wickets
                    self.active_series_bowling_stats[name][6] += noballs
                    self.active_series_bowling_stats[name][7] += wides
                    self.active_series_bowling_stats[name][8] += wick5

        # For legacy compatibility in PDFs:
        legacy_bat = {}
        for name, figs in self.active_series_batting_stats.items():
            legacy_bat[name] = {
                "team": figs[0],
                "matches": figs[1],
                "runs": figs[2],
                "balls": figs[3],
                "4s": figs[7],
                "6s": figs[8],
                "outs": figs[9]
            }
        legacy_bowl = {}
        for name, figs in self.active_series_bowling_stats.items():
            legacy_bowl[name] = {
                "team": figs[0],
                "matches": figs[1],
                "balls": figs[2],
                "maidens": figs[3],
                "runs": figs[4],
                "wickets": figs[5],
                "noballs": figs[6],
                "wides": figs[7]
            }
        sorted_bat = sorted(legacy_bat.items(), key=lambda x: x[1]["runs"], reverse=True)
        sorted_bowl = sorted(legacy_bowl.items(), key=lambda x: (x[1]["wickets"], -x[1]["runs"]), reverse=True)
        
        return {
            "batting": sorted_bat,
            "bowling": sorted_bowl
        }

    def on_series_tab_changed(self, event=None):
        if not self.active_series_matches:
            return
        try:
            idx = self.series_matches_nb.index("current")
            if idx < 0 or idx >= len(self.active_series_matches):
                return
            match_data = self.active_series_matches[idx]
            res = match_data.get("result", "")
            if not res:
                i1 = match_data["innings1"]
                i2 = match_data["innings2"]
                teamA = i1["team"]
                teamB = i2["team"]
                if i1["runs"] > i2["runs"]:
                    res = f"{teamA} won by {i1['runs'] - i2['runs']} runs"
                elif i1["runs"] < i2["runs"]:
                    res = f"{teamB} won by {10 - i2['wickets']} wickets"
                else:
                    res = "Match tied"
            
            motm = match_data.get("motm", "N/A")
            self.lbl_result_msg.config(text=f"MATCH {idx+1} RESULT: {res.upper()}")
            self.lbl_motm_msg.config(text=f"★ Man of the Match: {motm} ★")
        except Exception as e:
            pass

    def process_series_completion(self):
        # 1. Calculate series winner
        wins_a = 0
        wins_b = 0
        teamA = self.team_a_var.get().strip()
        teamB = self.team_b_var.get().strip()
        
        for m in self.active_series_matches:
            i1 = m["innings1"]
            i2 = m["innings2"]
            if i1["runs"] > i2["runs"]:
                wins_a += 1
            elif i1["runs"] < i2["runs"]:
                wins_b += 1
                
        if wins_a > wins_b:
            result_str = f"{teamA} won the series {wins_a}-{wins_b}"
            winner_team = teamA
        elif wins_b > wins_a:
            result_str = f"{teamB} won the series {wins_b}-{wins_a}"
            winner_team = teamB
        else:
            result_str = f"Series drawn {wins_a}-{wins_b}"
            winner_team = "No one"
            
        # 2. Calculate aggregated statistics
        stats = self.calculate_series_stats()
        self.active_series_format = self.format_var.get()
        
        self.active_series_summary = {
            "result": result_str,
            "winner_team": winner_team,
            "batting_stats": stats["batting"],
            "bowling_stats": stats["bowling"]
        }
        
        # Hide single match notebook, show series matches notebook
        self.single_match_nb.pack_forget()
        self.series_matches_nb.pack(fill="both", expand=True)
        
        # Clear any existing tabs in series_matches_nb
        for tab in self.series_matches_nb.tabs():
            self.series_matches_nb.forget(tab)
            
        # Dynamically build Match Tabs
        self.series_match_uis = []
        for idx, match_data in enumerate(self.active_series_matches):
            match_frame = tk.Frame(self.series_matches_nb, bg=DARK_BG)
            self.series_matches_nb.add(match_frame, text=f"Match {idx+1}")
            
            # Sub-notebook for Innings 1 vs Innings 2 scorecards
            sub_nb = ttk.Notebook(match_frame)
            sub_nb.pack(fill="both", expand=True, padx=5, pady=5)
            
            tab_inn1_frame = tk.Frame(sub_nb, bg=DARK_BG)
            tab_inn2_frame = tk.Frame(sub_nb, bg=DARK_BG)
            
            sub_nb.add(tab_inn1_frame, text="Innings 1")
            sub_nb.add(tab_inn2_frame, text="Innings 2")
            
            # Build scorecard tables
            tables_inn1 = self.build_innings_scorecard_ui(tab_inn1_frame)
            tables_inn2 = self.build_innings_scorecard_ui(tab_inn2_frame)
            
            # Populate tables for this specific match
            self.populate_scorecard_treeview(tables_inn1, match_data["innings1"], match_data["scorecard1"], match_data["bowling1"])
            self.populate_scorecard_treeview(tables_inn2, match_data["innings2"], match_data["scorecard2"], match_data["bowling2"])
            
            # Save the UI elements references
            self.series_match_uis.append({
                "sub_nb": sub_nb,
                "tables_inn1": tables_inn1,
                "tables_inn2": tables_inn2
            })
            
        # Bind Tab change event to update results banner and MOTM card
        self.series_matches_nb.bind("<<NotebookTabChanged>>", self.on_series_tab_changed)
        
        # Trigger banner update for the first tab
        self.on_series_tab_changed()
        
        # Enable PDF export buttons
        self.btn_match_pdf.config(text="Save Match PDF", state="normal")
        self.btn_series_pdf.pack(side="right", padx=5)
        self.btn_series_pdf.config(state="normal")
        
        # Populate leaderboards with the series summary if scope is "Current Series"
        self.update_leaderboards_display()
        
        # Switch to scorecard tab
        self.reset_live_hud()
        self.notebook.select(self.tab_scorecard)
        
        # Show complete dialog
        messagebox.showinfo("Series Simulation Complete", f"Series Finished!\n{result_str}")

    # ---------------------------------------------------------
    # MATCH COMPLETION STATS & FILE EXPORTS
    # ---------------------------------------------------------
    def process_match_completion(self, innings1, innings2):
        # 1. Update stats & generate scorecards lists
        scorecard1 = generateScorecard(innings1)
        bowling1 = BowlingFigures(innings1)
        scorecard2 = generateScorecard(innings2)
        bowling2 = BowlingFigures(innings2)
        
        # Result text
        teamA = innings1['team']
        teamB = innings2['team']
        if innings1['runs'] > innings2['runs']:
            result_str = f"{teamA} won the match by {(innings1['runs'] - innings2['runs'])} runs"
        elif innings1['runs'] < innings2['runs']:
            result_str = f"{teamB} won the match by {10 - innings2['wickets']} wickets"
        else:
            result_str = "Match tied"
            
        MOTM = getManOfTheMatch()
        
        # Store active match data for PDF export
        self.active_innings = {
            "innings1": innings1,
            "scorecard1": scorecard1,
            "bowling1": bowling1,
            "innings2": innings2,
            "scorecard2": scorecard2,
            "bowling2": bowling2,
            "result": result_str,
            "motm": MOTM
        }
        
        # Hide series matches notebook, show single match notebook
        self.series_matches_nb.pack_forget()
        self.single_match_nb.pack(fill="both", expand=True)
        
        # Hide Save Series PDF, set text of match PDF to "Save PDF Scorecard"
        self.btn_series_pdf.pack_forget()
        self.btn_match_pdf.config(text="Save PDF Scorecard", state="normal")
        
        # Save scorecards to generatedStats.txt
        session = self.session_var.get().strip()
        saveScorecard(teamA, innings1, scorecard1, bowling1, session_name=session)
        saveScorecard(teamB, innings2, scorecard2, bowling2)
        
        with open("generatedStats.txt", "a", encoding="utf-8") as f:
            f.write(result_str + "\n\n")
            
        # Update Stats file
        saveStats()
        
        # 2. Display results
        self.lbl_result_msg.config(text=result_str)
        self.lbl_motm_msg.config(text=f"★ Man of the Match: {MOTM} ★")
        
        # Log to commentary
        self.log_commentary("=======================================", "system")
        self.log_commentary(f"Match Finished: {result_str}", "system")
        self.log_commentary(f"Man of the Match: {MOTM}", "system")
        self.log_commentary("=======================================", "system")
        
        # Populate tables
        self.populate_scorecard_treeview(self.scorecard_tables_inn1, innings1, scorecard1, bowling1)
        self.populate_scorecard_treeview(self.scorecard_tables_inn2, innings2, scorecard2, bowling2)
        
        # Update cumulative leaderboard displays
        self.update_leaderboards_display()
        
        # Prompt user & Reset HUD
        self.reset_live_hud()
        self.notebook.select(self.tab_scorecard)
        messagebox.showinfo("Simulation Complete", f"Match Finished!\n{result_str}\nMan of the Match: {MOTM}")

    def populate_scorecard_treeview(self, tables, innings, scorecard_data, bowling_data):
        # Title Team
        tables["title_lbl"].config(text=f"{innings['team']} innings : {innings['runs']}/{innings['wickets']} in {innings['balls']//6}.{innings['balls']%6} overs")
        
        # Clear previous rows
        tables["bat_tree"].delete(*tables["bat_tree"].get_children())
        tables["bowl_tree"].delete(*tables["bowl_tree"].get_children())
        tables["part_tree"].delete(*tables["part_tree"].get_children())
        
        # Batting
        for row in scorecard_data:
            tables["bat_tree"].insert("", tk.END, values=(row[0], row[6], row[1], row[2], row[3], row[4], f"{row[5]:.2f}"))
            
        # Extras Display
        tables["lbl_extras"].config(text=f"Extras: {innings['no balls'] + innings['wides'] + innings['leg byes'] + innings['byes']} (nb {innings['no balls']}, wd {innings['wides']}, lb {innings['leg byes']}, b {innings['byes']})")
        
        # Fall of Wickets text
        fow = []
        runs = 0
        legal_deliveries = 0
        for i, ball in enumerate(innings['balls progression'], 1):
            if ball == "single":
                runs += 1
                legal_deliveries += 1
            elif ball == "double":
                runs += 2
                legal_deliveries += 1
            elif ball == "triple":
                runs += 3
                legal_deliveries += 1
            elif ball == "four":
                runs += 4
                legal_deliveries += 1
            elif ball == "six":
                runs += 6
                legal_deliveries += 1
            elif ball == "noball":
                runs += 1
            elif ball == "wide":
                runs += 1
            elif ball.startswith("legbye"):
                r = int(ball.replace("legbye", ""))
                runs += r
                legal_deliveries += 1
            elif ball.startswith("bye"):
                r = int(ball.replace("bye", ""))
                runs += r
                legal_deliveries += 1
            elif isinstance(ball, int):
                runs += ball
                legal_deliveries += 1
            elif ball == "wicket":
                legal_deliveries += 1
                fow.append(f"{runs}/{len(fow)+1} ({legal_deliveries//6}.{legal_deliveries%6} ov)")
        fow_text = "Fall of Wickets: " + (", ".join(fow) if fow else "None")
        tables["lbl_fow"].config(text=fow_text)
        
        # Bowling
        for row in bowling_data:
            tables["bowl_tree"].insert("", tk.END, values=row)
            
        # Partnerships
        for row in innings["partnerships"]:
            tables["part_tree"].insert("", tk.END, values=row)

    def update_leaderboards_display(self):
        global battingStatsODI, bowlingStatsODI, battingStatsT20, bowlingStatsT20
        
        # Clear tables
        self.ldr_bat_tree.delete(*self.ldr_bat_tree.get_children())
        self.ldr_bowl_tree.delete(*self.ldr_bowl_tree.get_children())
        
        selected_fmt = self.ldr_format_var.get()
        selected_scope = self.ldr_scope_var.get()
        
        if selected_scope == "Current Series":
            self.lbl_leaderboard_title.config(text="Current Series Leaderboard")
            series_fmt = getattr(self, "active_series_format", None)
            if series_fmt == selected_fmt:
                bat_source = getattr(self, 'active_series_batting_stats', {})
                bowl_source = getattr(self, 'active_series_bowling_stats', {})
            else:
                bat_source = {}
                bowl_source = {}
        else:
            self.lbl_leaderboard_title.config(text="Aggregated Session Leaderboard")
            if selected_fmt == "ODI":
                bat_source = battingStatsODI
                bowl_source = bowlingStatsODI
            else:
                bat_source = battingStatsT20
                bowl_source = bowlingStatsT20
            
        # Batting Leaderboard
        # stats keys: [team, Inns, Runs, Balls, singles, doubles, triples, 4s, 6s, Outs, 50s, 100s]
        sorted_bat = sorted(bat_source.items(), key=lambda item: item[1][2], reverse=True)
        for name, figs in sorted_bat:
            inns = figs[1]
            runs = figs[2]
            balls = figs[3]
            singles = figs[4]
            doubles = figs[5]
            triples = figs[6]
            fours = figs[7]
            sixes = figs[8]
            outs = figs[9]
            fifty = figs[10]
            century = figs[11]
            avg = round(runs / outs, 2) if outs > 0 else '∞'
            sr = round(runs / balls * 100, 2) if balls > 0 else 0.0
            
            self.ldr_bat_tree.insert("", tk.END, values=(
                name, figs[0], inns, runs, balls, singles, doubles, triples, fours, sixes, outs, fifty, century, avg, sr
            ))
            
        # Bowling Leaderboard
        # stats keys: [team, Inns, Balls, Maidens, Runs, Wickets, NBs, WDs, 5w]
        sorted_bowl = sorted(bowl_source.items(), key=lambda item: (-item[1][5], item[1][4]))
        for name, figs in sorted_bowl:
            inns = figs[1]
            balls = figs[2]
            maidens = figs[3]
            runs = figs[4]
            wkts = figs[5]
            nb = figs[6]
            wd = figs[7]
            fivew = figs[8]
            
            overs = f"{balls // 6}.{balls % 6}"
            avg = round(runs / wkts, 2) if wkts > 0 else '∞'
            sr = round(balls / wkts, 2) if wkts > 0 else '∞'
            
            self.ldr_bowl_tree.insert("", tk.END, values=(
                name, figs[0], inns, overs, maidens, runs, wkts, nb, wd, fivew, avg, sr
            ))

# ---------------------------------------------------------
# CLI PORTED HELPER DEFINITIONS
# ---------------------------------------------------------
def determineDegree():
    return random.choice(['dominant', 'close', 'normal'])

# ---------------------------------------------------------
# APPLICATION BOOT
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CricketSimulatorApp(root)
    root.mainloop()
