jupyter nbconvert --to script *.ipynb

python scrape_shooting.py
python misc.py
python player_level.py
python underground.py
python standings.py
python plusmin.py
python record.py
python tracking.py
python game_log.py
git add --all
git commit -m 'Daily Update'
git push origin main