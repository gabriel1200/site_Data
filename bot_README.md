# Basket_bot commands
- _Deluxe Only_ means you can only use the command in the deluxe channel
## help

If you ever forget the formatting for the query commands, try typing help after the command. 
Doing so will return the corresponding 'how to use it' for the command.

**Example**
```
$find_clip help

$find_clip [team] [Year-Month-Day] [Quarter] [Minutes:Seconds]
Alternatively, if the game was in the current season
$find_clip [team] [Month/Day] [Quarter] [Minutes:Seconds]
```

## $shotmap
**What it does**
Creates a Goldsberry style shotmap of a player season. 

**How to use it**

$[firstname] [lastname] [season]

or

$firstname] [lastname] [season] ps

**Example**
```
$shotmap tracy mcgrady 2004

```


## $player_card
**What it does**
Displays a players metrics over multi year periods in percentile form . 

**How to use it**

$[firstname] [lastname] [end year] [span]

**Example**
```
$player_card joel embiid 2022 3
```
## $team_card
**What it does**
Displays a teams performance metrics over multi year periods in percentile form. 

**How to use it**

$[team_acronym] [end_year] [span]

**Example**
```
$team_card mil 2022 4
```

## $find_clip
**What it does**
Returns the possesion video(s) closest to the time stamp.
**How to use it**

$find_clip [team] [Year-Month-Day] [Quarter] [Minutes:Seconds]

OR

$find_clip [team] [Month/Day] [Quarter] [Minutes:Seconds]

**Examples**
```
$find_clip den 2023-1-24 4 0:07

$find_clip DEN 12/28 4 0:07
```

## $playerboard

_Deluxe Only_

**What it does**
Displays the top 10 teams by the selected team statistic(ortg,drtg,etc) for the current season, taken from the Thinking Basketball Daily Leaderboard.

For metrics with two terms in the name, replace the space with an underscore. (ie 'passer rating' should be entered as 'passer_rating') 

**How to use it**

$playerboard [stat]

**Example**
```
$playerboard passer_rating

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│      Player         Tm    MP    GP   BPM    OBPM   ScoreVal   PlayVal   Load   Pts 75   rTS%    Box Creation   Passer Rating │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│    Trae Young       ATL   351   10   2.2    3.6      -0.8       2.4     59.9    27.5    -6.5        14.7            9.5      │
│   Nikola Jokic      DEN   346   11   7.7    4.7      1.6        2.3     48.6    24.2    11.0        13.1            9.4      │
│    Ben Simmons      BKN   231   8    3.1    -1.4     -1.6       0.5     24.7    7.3     -11.8       2.5             9.3      │
│   James Harden      PHI   331   9    5.6    3.8      0.2        2.4     51.7    23.0     2.3        15.7            9.2      │
│   Ousmane Dieng     OKC   135   9    -0.2   -1.6     -1.2       0.7     20.0    8.2     -16.3       1.8             9.1      │
│    Luka Doncic      DAL   366   10   9.4    5.2      1.5        2.5     64.9    36.0     3.3        17.2            9.1      │
│    Chris Paul       PHX   302   10   3.8    1.4      -1.0       1.7     35.2    11.8    -6.3        8.3             9.0      │
│   Jrue Holiday      MIL   331   10   4.4    2.4      -0.6       1.6     46.7    21.2    -2.7        11.1            8.8      │
│ Tyrese Haliburton   IND   371   11   4.9    4.3      1.0        2.3     48.4    22.7     8.2        14.5            8.8      │
│  Andrew Nembhard    IND   200   10   0.7    0.6      -0.9       0.9     25.4    11.4    -3.6        3.7             8.7      │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
## $next_games

**What it does**

Shows the next 10 games the selected team has scheduled.

**How to use it**

$next_games [team_acronym]

**Example**
```
$next_games cle
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│       away_team          away_tag         home_team         home_tag          date         │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│  Cleveland Cavaliers       CLE       Los Angeles Lakers       LAL      2022-11-06 12:30:00 │
│  Cleveland Cavaliers       CLE           LA Clippers          LAC      2022-11-07 19:30:00 │
│  Cleveland Cavaliers       CLE        Sacramento Kings        SAC      2022-11-09 19:00:00 │
│  Cleveland Cavaliers       CLE      Golden State Warriors     GSW      2022-11-11 19:00:00 │
│ Minnesota Timberwolves     MIN       Cleveland Cavaliers      CLE      2022-11-13 18:00:00 │
│  Cleveland Cavaliers       CLE         Milwaukee Bucks        MIL      2022-11-16 19:00:00 │
│   Charlotte Hornets        CHA       Cleveland Cavaliers      CLE      2022-11-18 19:30:00 │
│       Miami Heat           MIA       Cleveland Cavaliers      CLE      2022-11-20 19:00:00 │
│     Atlanta Hawks          ATL       Cleveland Cavaliers      CLE      2022-11-21 19:00:00 │
│ Portland Trail Blazers     POR       Cleveland Cavaliers      CLE      2022-11-23 19:00:00 │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```
## $scoreboards

**What it does**

Shows the planned time if a game is scheduled for later in the day, and shows the current score, remaining time and quarter if the game is ongoing.

**How to use it**
$scoreboards

**Example**
```
$scoreboards

Mavericks (2-3) vs. Magic (1-5)
9 - 13
Q1 8:3

Cavaliers (4-1) vs. Knicks (3-2)
80 - 87
Q3 1:25

Spurs (4-2) vs. Timberwolves (4-2)
35 - 31
Q2 8:39

Pistons (1-5) vs. Warriors (3-3)
89 - 79
Q3 4:11

Celtics (3-2) vs. Wizards (3-2)
87 - 68
Q3 0:0

Clippers (2-4) vs. Pelicans (4-2)
91 - 112
Q4 0:0

Suns (4-1) vs. Rockets (1-5)
9:00 pm ET

Lakers (0-5) vs. Nuggets (4-2)
9:30 pm ET
```
## $season


**What it does**

Shows various tb statistics(playval,scoreval, passer rating, box creation, bpm) and public statistics(LEBRON) for a player.
The user can select a single season or a multi season stretch, with the latter being determined using a weighted average by minutes played.

**How to use it**

$season [firstname] [lastname] [start year] [end year *-optional*]

**Examples**
```
$season lebron james 2012

┌────────────────────────────────────────────────────────────────────┐
│ BPM   OBPM   AuPM/g   ScoreVal   PlayVal   Load   IA Pts/75   rTS% │
├────────────────────────────────────────────────────────────────────┤
│ 7.2   5.2     5.8       2.0        1.3     50.9     30.0      7.8  │
└────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Box Creation   Passer rating   FTA / 100   LEBRON   O-LEBRON   D-LEBRON     MP   │
├──────────────────────────────────────────────────────────────────────────────────┤
│     10.0            7.2          11.4       6.3       5.4        0.9      2326.0 │
└──────────────────────────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────────┐
│ PS AuPM/g   PS BPM   PS OBPM   PS ScoreVal   PS PlayVal   PS Load │
├───────────────────────────────────────────────────────────────────┤
│    6.9       8.2       6.4         2.2          0.9        49.4   │
└───────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────────┐
│ PS aPts 75   PS rTS%   PS Box OC   PS Pass rtg   PS FTA/100   PS MP │
├─────────────────────────────────────────────────────────────────────┤
│    31.6        6.5        8.3          6.2          13.0      983.0 │
└─────────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────┐
│ Team SRS   Team Ortg   Team Drtg   PS Tm Ortg   PS Tm Drtg │
├────────────────────────────────────────────────────────────┤
│   5.7         2.0        -4.4         8.4          -3.5    │
└────────────────────────────────────────────────────────────┘
```

```
$season lebron james 2010 2011

┌────────────────────────────────────────────────────────────────────┐
│ BPM   OBPM   AuPM/g   ScoreVal   PlayVal   Load   IA Pts/75   rTS% │
├────────────────────────────────────────────────────────────────────┤
│ 7.7   5.8     6.0       1.6        1.9     53.7     29.3      5.7  │
└────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Box Creation   Passer rating   FTA / 100   LEBRON   O-LEBRON   D-LEBRON     MP   │
├──────────────────────────────────────────────────────────────────────────────────┤
│     12.4            7.9          12.5       7.5       6.2        1.4      6029.0 │
└──────────────────────────────────────────────────────────────────────────────────┘
┌───────────────────────────────────────────────────────────────────┐
│ PS AuPM/g   PS BPM   PS OBPM   PS ScoreVal   PS PlayVal   PS Load │
├───────────────────────────────────────────────────────────────────┤
│    4.6       7.5       5.3         1.4          1.0        44.0   │
└───────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────┐
│ PS aPts 75   PS rTS%   PS Box OC   PS Pass rtg   PS FTA/100   PS MP  │
├──────────────────────────────────────────────────────────────────────┤
│    25.6        5.4        8.3          6.6          10.8      1382.0 │
└──────────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────┐
│ Team SRS   Team Ortg   Team Drtg   PS Tm Ortg   PS Tm Drtg │
├────────────────────────────────────────────────────────────┤
│   6.5         4.1        -3.6         3.6          -2.6    │
```


## $wowy

**What it does**

Shows with and without you(wowy) player combinations taken from [PBP stats.](http://www.pbpstats.com/wowy-combos/nba)
Users can select any combination of players on a team, any combination of seasons within that timeframe, and chose between
regular season(rs), post season(ps) and total(all) wowy calculations. They can also chose whether to limit the calculation
to games including all of the selected players.

**How to use it**

$wowy [team_acronym] [year1,year2,year3 ....] [first-name_last-name,first-name_last-name] [season type] [common*-optional*]

**Examples**

```
$wowy cle 2015,2016,2017,2018 lebron_james ps

┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ OffRtg   DefRtg   NetRtg   Minutes        On            Off         3P%     2P%    Opp3%   Opp2% │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 102.13   109.85   -7.72     581.0                   LeBron James   33.86   46.53   34.14   49.14 │
│ 115.49   108.57    6.92    3332.0    LeBron James                  38.05   51.31   34.46   50.42 │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```
```
$wowy GSW 2017,2019 stephen_curry,kevin_durant ps common

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ OffRtg   DefRtg   NetRtg   Minutes               On                            Off                3P%     2P%    Opp3%   Opp2% │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 96.85    106.42   -9.58     279.0                                  Stephen Curry, Kevin Durant   29.38   46.73   34.91   49.67 │
│ 117.96   109.83    8.13     628.0           Stephen Curry                 Kevin Durant           37.12   55.17   35.53   48.92 │
│ 112.78   110.56    2.22     157.0           Kevin Durant                  Stephen Curry          41.67   48.89   33.66   51.12 │
│ 124.58   110.2    14.38     818.0    Stephen Curry, Kevin Durant                                 40.22   58.65   35.57   48.76 │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
```
$wowy PHI 2022,2023 james_harden,joel_embiid rs common

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ OffRtg   DefRtg   NetRtg   Minutes              On                          Off               3P%     2P%    Opp3%   Opp2% │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 109.89   112.36   -2.47    1574.0                                James Harden, Joel Embiid   34.24   51.55   34.1    53.69 │
│ 114.8    120.0     -5.2     363.0          James Harden                 Joel Embiid          37.98   50.74   37.75   59.51 │
│ 114.16   110.61    3.55    1744.0           Joel Embiid                James Harden          37.38   52.81   33.45   52.3  │
│ 123.69   109.62   14.08     760.0    James Harden, Joel Embiid                               40.35   56.48   35.51   51.8  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```
## $teamseason

**What it does**

Shows various team level metrics for the regular season(rDOtg,rORTG,SRS) and the playoffs if applicable(cORtg ,cDRtg ,cNET ).

Users can select a single season or a multi season stretch. Playoff metrics for the latter are determined via a weighted average by games played.

**How to use it**

$season [team_acronym] [start_year] [end year *-optional*] 

**Examples**
```
$teamseason gsw 2016

┌────────────────────────────────────────────────────────────────────────────┐
│  W      L    SRS    ORtg    reg_cont   eFG%   DRtg    NRtg   rORtg   rDRtg │
├────────────────────────────────────────────────────────────────────────────┤
│ 73.0   9.0   10.4   114.5     95.0     56.0   103.8   10.7    8.1    -2.6  │
└────────────────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────────────────┐
│  W      L    SRS    ORtg    reg_cont   eFG%   DRtg    NRtg   rORtg   rDRtg │
├────────────────────────────────────────────────────────────────────────────┤
│ 73.0   9.0   10.4   114.5     95.0     56.0   103.8   10.7    8.1    -2.6  │
└────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────┐
│ cORTG   cDRTG   cNET   round    G   │
├─────────────────────────────────────┤
│  4.9    -6.2    11.1    4.0    24.0 │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ cORTG   cDRTG   cNET   round    G   │
├─────────────────────────────────────┤
│  4.9    -6.2    11.1    4.0    24.0 │
```

```
$teamseason hou 2018 2019

┌────────────────────────────────────────────────────────────────────────────┐
│  W      L     SRS   ORtg    reg_cont   eFG%   DRtg    NRtg   rORtg   rDRtg │
├────────────────────────────────────────────────────────────────────────────┤
│ 59.0   23.0   6.6   115.1     64.5     54.5   108.4   6.7     5.6    -1.1  │
└────────────────────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────────────────┐
│  W      L     SRS   ORtg    reg_cont   eFG%   DRtg    NRtg   rORtg   rDRtg │
├────────────────────────────────────────────────────────────────────────────┤
│ 59.0   23.0   6.6   115.1     64.5     54.5   108.4   6.7     5.6    -1.1  │
└────────────────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────┐
│ cORTG   cDRTG   cNET   round    G   │
├─────────────────────────────────────┤
│  3.9    -5.1    9.0     2.5    28.0 │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ cORTG   cDRTG   cNET   round    G   │
├─────────────────────────────────────┤
│  3.9    -5.1    9.0     2.5    28.0 │
└─────────────────────────────────────┘
```

