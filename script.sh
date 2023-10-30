jupyter nbconvert --to script *.ipynb
python player_shooting.py
python defense.py
python scrape_shooting.py
python misc.py
python player_level.py
python record.py
python standings.py

git add --all
git commit -m 'Daily Update'
git push origin main
