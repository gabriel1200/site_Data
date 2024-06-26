jupyter nbconvert --to script *.ipynb
python player_shooting.py
python defense.py
python scrape_shooting.py
python misc.py
python player_level.py
python record.py
python standings.py
python passing.py
python team_shooting.py

python underground.py
python in_season.py
git add --all
git commit -m 'Daily Update'
git push origin main

cp rimdfg.csv ../discord/data/rimdfg.csv
cp rimfreq.csv ../discord/data/rimfreq.csv
cp rim_acc.csv ../discord/data/rim_acc.csv
cp dfg.csv ../discord/data/dfg.csv


cp rimdfg_p.csv ../discord/data/rimdfg_ps.csv
cp rimfreq_p.csv ../discord/data/rimfreq_p.csv
cp rim_acc_p.csv ../discord/data/rim_acc_p.csv
cp dfg_p.csv ../discord/data/dfg_p.csv

cp team_shooting.csv ../discord/data/team_shooting.csv
cp opp_team_shooting.csv ../discord/data/opp_team_shooting.csv


cp team_shooting_ps.csv ../discord/data/team_shooting_ps.csv
cp opp_team_shooting_ps.csv ../discord/data/opp_team_shooting_ps.csv

#cp lebron.csv ../discord/data/lebron.csv

cp passing.csv ../discord/data/passing.csv
cp passing_ps.csv ../discord/data/passing_ps.csv

cp team_avg.csv ../discord/data/team_avg.csv
cp avg_shooting.csv ../discord/data/avg_shooting.csv
cp player_shooting.csv ../discord/data/player_shooting.csv
cp player_shooting_p.csv ../discord/data/player_shooting_p.csv

cp totals.csv ../discord/data/totals.csv
cp totals_ps.csv ../discord/data/totals_ps.csv

cp scoring.csv ../discord/data/scoring.csv

cp shotzone.csv ../discord/data/shotzone.csv
cp shotzone_ps.csv ../discord/data/shotzone_ps.csv

cp scoring_ps.csv ../discord/data/scoring_ps.csv

cp hustle.csv ../discord/data/hustle.csv
cp hustle_ps.csv ../discord/data/hustle_ps.csv


cp tsavg.csv ../discord/data/tsavg.csv


