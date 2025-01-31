jupyter nbconvert --to script *.ipynb
python player_shooting.py
python defense.py
python scrape_shooting.py
python misc.py
python player_level.py

python team_shooting.py
python update_lebron.py
python dribble.py
python underground.py
python hustle.py
python player_index.py
python new_tracking.py
python contract_data.py
python make_index.py
git add --all
git commit -m 'Daily Update'
git push origin master

#cp windex.csv ../web_app/data/windex.csv

#cp windex_ps.csv ../web_app/data/windex_ps.csv
#!/bin/bash

# Define destination directories
WEB_APP_DIR="../web_app/data"
DISCORD_DIR="../discord/data"

# Copy files to both destinations


cp lebron.csv $WEB_APP_DIR/lebron.csv
cp lebron.csv $DISCORD_DIR/lebron.csv

cp option.csv $WEB_APP_DIR/option.csv
cp option.csv $DISCORD_DIR/option.csv

cp salary.csv $WEB_APP_DIR/salary.csv
cp salary.csv $DISCORD_DIR/salary.csv

cp rimdfg.csv $WEB_APP_DIR/rimdfg.csv
cp rimdfg.csv $DISCORD_DIR/rimdfg.csv

cp rimfreq.csv $WEB_APP_DIR/rimfreq.csv
cp rimfreq.csv $DISCORD_DIR/rimfreq.csv

cp rim_acc.csv $WEB_APP_DIR/rim_acc.csv
cp rim_acc.csv $DISCORD_DIR/rim_acc.csv

cp dfg.csv $WEB_APP_DIR/dfg.csv
cp dfg.csv $DISCORD_DIR/dfg.csv

cp hustle.csv $WEB_APP_DIR/hustle.csv
cp hustle.csv $DISCORD_DIR/hustle.csv

cp hustle_ps.csv $WEB_APP_DIR/hustle_ps.csv
cp hustle_ps.csv $DISCORD_DIR/hustle_ps.csv

cp lebron.csv $WEB_APP_DIR/lebron.csv
cp lebron.csv $DISCORD_DIR/lebron.csv

#cp play_style.csv $WEB_APP_DIR/play_style.csv
#cp play_style.csv $DISCORD_DIR/play_style.csv

#cp play_style_p.csv $WEB_APP_DIR/play_style_p.csv
#cp play_style_p.csv $DISCORD_DIR/play_style_p.csv

cp playstyle.csv $WEB_APP_DIR/playstyle.csv
cp playstyle.csv $DISCORD_DIR/playstyle.csv

cp rimdfg_p.csv $WEB_APP_DIR/rimdfg_p.csv
cp rimdfg_p.csv $DISCORD_DIR/rimdfg_p.csv

cp rimfreq_p.csv $WEB_APP_DIR/rimfreq_p.csv
cp rimfreq_p.csv $DISCORD_DIR/rimfreq_p.csv

cp rim_acc_p.csv $WEB_APP_DIR/rim_acc_p.csv
cp rim_acc_p.csv $DISCORD_DIR/rim_acc_p.csv

cp dfg_p.csv $WEB_APP_DIR/dfg_p.csv
cp dfg_p.csv $DISCORD_DIR/dfg_p.csv

cp team_shooting.csv $WEB_APP_DIR/team_shooting.csv
cp team_shooting.csv $DISCORD_DIR/team_shooting.csv

cp opp_team_shooting.csv $WEB_APP_DIR/opp_team_shooting.csv
cp opp_team_shooting.csv $DISCORD_DIR/opp_team_shooting.csv

cp team_shooting_ps.csv $WEB_APP_DIR/team_shooting_ps.csv
cp team_shooting_ps.csv $DISCORD_DIR/team_shooting_ps.csv

cp opp_team_shooting_ps.csv $WEB_APP_DIR/opp_team_shooting_ps.csv
cp opp_team_shooting_ps.csv $DISCORD_DIR/opp_team_shooting_ps.csv

#cp lebron.csv $WEB_APP_DIR/lebron.csv
#cp lebron.csv $DISCORD_DIR/lebron.csv

cp passing.csv $WEB_APP_DIR/passing.csv
cp passing.csv $DISCORD_DIR/passing.csv

cp passing_ps.csv $WEB_APP_DIR/passing_ps.csv
cp passing_ps.csv $DISCORD_DIR/passing_ps.csv

cp poss.csv $WEB_APP_DIR/poss.csv
cp poss.csv $DISCORD_DIR/poss.csv

cp team_avg.csv $WEB_APP_DIR/team_avg.csv
cp team_avg.csv $DISCORD_DIR/team_avg.csv

cp avg_shooting.csv $WEB_APP_DIR/avg_shooting.csv
cp avg_shooting.csv $DISCORD_DIR/avg_shooting.csv

cp player_shooting.csv $WEB_APP_DIR/player_shooting.csv
cp player_shooting.csv $DISCORD_DIR/player_shooting.csv

cp player_shooting_p.csv $WEB_APP_DIR/player_shooting_p.csv
cp player_shooting_p.csv $DISCORD_DIR/player_shooting_p.csv

cp totals.csv $WEB_APP_DIR/totals.csv
cp totals.csv $DISCORD_DIR/totals.csv

cp totals_ps.csv $WEB_APP_DIR/totals_ps.csv
cp totals_ps.csv $DISCORD_DIR/totals_ps.csv

cp scoring.csv $WEB_APP_DIR/scoring.csv
cp scoring.csv $DISCORD_DIR/scoring.csv

cp scoring_ps.csv $WEB_APP_DIR/scoring_ps.csv
cp scoring_ps.csv $DISCORD_DIR/scoring_ps.csv

cp playtype.csv $WEB_APP_DIR/playtype.csv
cp playtype.csv $DISCORD_DIR/playtype.csv

cp teamplay_p.csv $WEB_APP_DIR/teamplay_p.csv
cp teamplay_p.csv $DISCORD_DIR/teamplay_p.csv

cp teamplay.csv $WEB_APP_DIR/teamplay.csv
cp teamplay.csv $DISCORD_DIR/teamplay.csv

cp teamplayd_p.csv $WEB_APP_DIR/teamplayd_p.csv
cp teamplayd_p.csv $DISCORD_DIR/teamplayd_p.csv

cp teamplayd.csv $WEB_APP_DIR/teamplayd.csv
cp teamplayd.csv $DISCORD_DIR/teamplayd.csv

cp shotzone.csv $WEB_APP_DIR/shotzone.csv
cp shotzone.csv $DISCORD_DIR/shotzone.csv

cp shotzone_ps.csv $WEB_APP_DIR/shotzone_ps.csv
cp shotzone_ps.csv $DISCORD_DIR/shotzone_ps.csv

cp team_shotzone.csv $WEB_APP_DIR/team_shotzone.csv
cp team_shotzone.csv $DISCORD_DIR/team_shotzone.csv

cp team_shotzone_vs.csv $WEB_APP_DIR/team_shotzone_vs.csv
cp team_shotzone_vs_ps.csv $WEB_APP_DIR/team_shotzone_vs_ps.csv

cp team_shotzone_ps.csv $WEB_APP_DIR/team_shotzone_ps.csv
cp team_shotzone_ps.csv $DISCORD_DIR/team_shotzone_ps.csv

cp tracking.csv $WEB_APP_DIR/tracking.csv
cp tracking.csv $DISCORD_DIR/tracking.csv

cp tracking_p.csv $WEB_APP_DIR/tracking_p.csv
cp tracking_p.csv $DISCORD_DIR/tracking_p.csv

cp dribbleshot.csv $WEB_APP_DIR/dribbleshot.csv
cp dribbleshot.csv $DISCORD_DIR/dribbleshot.csv

cp dribbleshot_ps.csv $WEB_APP_DIR/dribbleshot_ps.csv
cp dribbleshot_ps.csv $DISCORD_DIR/dribbleshot_ps.csv

cp jumpdribble.csv $WEB_APP_DIR/jumpdribble.csv
cp jumpdribble.csv $DISCORD_DIR/jumpdribble.csv

cp jumpdribble_ps.csv $WEB_APP_DIR/jumpdribble_ps.csv
cp jumpdribble_ps.csv $DISCORD_DIR/jumpdribble_ps.csv

cp tsavg.csv $WEB_APP_DIR/tsavg.csv
cp tsavg.csv $DISCORD_DIR/tsavg.csv

cp index_master.csv $WEB_APP_DIR/index_master.csv
cp index_master.csv $DISCORD_DIR/index_master.csv

cp index_master.csv ../player_sheets/lineups/index_master.csv




