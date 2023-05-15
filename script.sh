    jupyter nbconvert --to script *.ipynb

    python scrape_shooting.py
    python misc.py
    python player_level.py
    python underground.py

    python record.py
    python tracking.py
    python game_log.py
    python defense.py
    cp rim_acc_p.csv ../discord/data/rim_acc_p.csv
    cp rimfreq_p.csv ../discord/data/rimfreq_p.csv
    cp dfg_p.csv ../discord/data/dfg_p.csv
    git add --all
    git commit -m 'Daily Update'
    git push origin main


#python standings.py
#python plusmin.py