jupyter nbconvert --to script *.ipynb

python scrape_shooting.py
python misc.py
python player_level.py
python record.py
python standings.py
python player_shooting.py
python defense.py
git add --all
git commit -m 'Daily Update'
git push origin main
