# Markedsoversikt

Et enkelt prosjekt for å utforske/lære om aksje- og markedsdata.

## Struktur
- src/: datainnhenting og analyse
- app/: UI 
- data/: lokale datafiler (ikke i git)
- notatbok/: eksperimenter

## Kom i gang
1. Opprett og aktiver venv
2. Installer dependencies 
3. pass på at PATH er satt slik at python i venv brukes først (source venv/scripts/activate for meg)
4. kjør python -m streamlit run app/streamlit_app.py

## slette cache
find . -type d -name "__pycache__" -exec rm -r {} +

## Test Yahoo
python -m tests.test_yahoo

