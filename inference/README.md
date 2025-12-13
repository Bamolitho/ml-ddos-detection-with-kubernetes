1. Sans rien → fallback auto
python inference/predict.py

2. Avec fichier spécifique
python inference/predict.py --input data/myfile.csv

3. Avec JSON
python inference/predict.py --json '{"Source Port":1234, "Protocol":6, ...}'

4. En activant la config
use_static_input_file: true
input_file: "data/processed/test.csv"