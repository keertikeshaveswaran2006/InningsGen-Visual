# InningsGen - Cricket Match Innings Simulator

InningsGen is a modern graphical user interface (GUI) application built using Python's `tkinter` library. It simulates ODI and T20I cricket matches ball-by-ball with realistic outcomes, visual over progression trackers, live statistics, and accumulated leaderboards.

## Features

- **Format Selection**: Choose between **ODI** (50 overs / 300 balls) and **T20** (20 overs / 120 balls).
- **Match Tuning**: Configure match degrees (`normal`, `close`, `dominant`) to alter boundary and wicket probabilities.
- **Roster Management**: Customize names for all 22 players. Easily assign 6 to 10 bowler checkmarks per team.
- **Player Dropdowns (CSV)**: Select player names from a dropdown box populated dynamically from `players.csv`, importing custom base weights/probabilities for simulation outcomes.
- **Live Simulator HUD**:
  - Watch live scoreboards, overs, wickets, and run rate indicators.
  - Active batsman display showing runs, balls faced, boundaries, and strike rate.
  - Active bowler display showing overs, maidens, runs, wickets, and economy rate.
  - Circular over-progression badges color-coded by outcome (e.g., green for runs, red for wickets, orange for extras).
  - Delay speed slider (0.05s to 2.0s per ball) with Play, Pause, Next Ball (step-by-step), and Abort options.
  - **Instant Sim** mode to bypass animations and compute scores immediately.
- **In-Depth Scorecard**: Dynamic table views showing full batting cards, bowling figures, partnerships, fall of wickets, and a calculated Man of the Match.
- **Tournament Leaderboards**: Sortable tables tracking session batting and bowling averages across ODI and T20 matches.
- **File Exports**: Automatically appends full scorecard printouts to `generatedStats.txt` and updates cumulative leaderboards in `Stats.txt`.

---

## Getting Started

### Prerequisites

You need **Python 3** installed on your system. The application requires the `tabulate` library for writing formatting tables to text logs.

Install `tabulate` if you don't have it:
```bash
pip install tabulate
```

### Running the App

Navigate to the project folder and run the python file:
```bash
python3 InningsGenODTkinter.py
```
