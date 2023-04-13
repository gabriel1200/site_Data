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
## $playtype
**What it does**
Shares the PPP & Frequencies of a players playtypes, according to Synergy classification. 

**How to use it**

$[firstname] [lastname] [season] 

or

$firstname] [lastname] [start_season] [end_season]

or

$[firstname] [lastname] [season] [ps]

**Example**
```
$playtype james harden 2019

$playtype james harden 2019 ps

$playtype james harden 2019 2020 ps

$playtype james harden 2019 2020

```
![Playtypes](https://media.discordapp.net/attachments/1045134231707336764/1095817225820192948/playtype.jpg?width=1832&height=1145)


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



![Shotmap](https://media.discordapp.net/attachments/1088122768672948335/1095815519304691883/Tracy_McGrady_2003-04.png?width=1333&height=1145)

## $player_card
**What it does**
Displays a players metrics over multi year periods in percentile form . 

**How to use it**

$[firstname] [lastname] [end year] [span]

**Example**
```
$player_card joel embiid 2022 3
```
![Player Card ](https://media.discordapp.net/attachments/1045134231707336764/1095815927599202364/fig1.png?width=1145&height=1145)
## $team_card
**What it does**
Displays a teams performance metrics over multi year periods in percentile form. 

**How to use it**

$[team_acronym] [end_year] [span]

**Example**
```
$team_card mil 2022 4
```
![Team Card](https://media.discordapp.net/attachments/1045134231707336764/1095816188023554148/fig1.png?width=1145&height=1145)
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
[Find Clip]!(https://videos.nba.com/nba/pbp/media/2022/12/28/0022200522/656/25b2f99d-d815-c9b0-efc6-06b5f55cf9c7_960x540.mp4)
## $playerscreen

_Deluxe Only_

**What it does**
Provides customized snapshot of a players current season from thinkingbasketball.net
**How to use it**

$playerscreen [first_name] [last_name] 

**Example**
```
$player_screen Malcolm Brogdon
```
![Player Screen](https://media.discordapp.net/attachments/638116254720327680/1095773509621387264/player_snip.jpg?width=1386&height=966)
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
$season michael jordan 1992 1993
```
![Season](https://media.discordapp.net/attachments/1045134231707336764/1095821055802748979/fig1.png?width=1600&height=800)


## $wowy

**What it does**

Shows with and without you(wowy) player combinations taken from [PBP stats.](http://www.pbpstats.com/wowy-combos/nba)
Users can select any combination of players on a team, any combination of seasons within that timeframe, and chose between
regular season(rs), post season(ps) and total(all) wowy calculations. They can also chose whether to limit the calculation
to games including all of the selected players.

**How to use it**

$wowy [team_acronym] [names] [years] [season type] [common*-optional*]

**Example**

```
$wowy lal kobe bryant pau gasol 2009 ps
```
![Wowy](https://media.discordapp.net/attachments/617888289801895966/1095555436339535892/fig1.png?width=1832&height=1145)

## $teamseason

**What it does**

Shows various team level metrics for the regular season(rDOtg,rORTG,SRS) and the playoffs if applicable(cORtg ,cDRtg ,cNET ).

Users can select a single season or a multi season stretch. Playoff metrics for the latter are determined via a weighted average by games played.

**How to use it**

$season [team_acronym] [start_year] [end year *-optional*] 

**Examples**

```
$teamseason hou 2018 2019

```

![Team Season](https://media.discordapp.net/attachments/1045134231707336764/1095821466597072906/fig1.png?width=1600&height=533)
