jupyter nbconvert --to script *.ipynb
python player_shooting.py
python team_shooting.py
python defense.py
python scrape_shooting.py
python misc.py
python player_level.py
python record.py
python standings.py
python passing.py
python scrape_shooting.py
git add --all
git commit -m 'Daily Update'
git push origin main

cp rimdfg.csv ../discord/data/rimdfg.csv
cp rimfreq.csv ../discord/data/rimfreq.csv
cp dfg.csv ../discord/data/dfg.csv
cp team_shooting.csv ../discord/data/team_shooting.csv
cp passing.csv ../discord/data/passing.csv
cp team_avg.csv ../discord/data/team_avg.csv
cp avg_shooting.csv ../discord/data/avg_shooting.csv
cp player_shooting.csv ../discord/data/player_shooting.csv
