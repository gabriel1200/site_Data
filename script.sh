jupyter nbconvert --to script *.ipynb

python scrape_shooting.py
python misc.py
python player_level.py
python underground.py
python standings.py
git add --all
git commit -m 'Daily Update'
git push origin main