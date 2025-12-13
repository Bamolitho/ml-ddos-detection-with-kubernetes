## **Workflow d’entraînement**

```LESS
     ┌────────────────────────────────────────┐
     │        1. Chargement du dataset        │
     │           (merged_dataset.csv)         │
     └────────────────────────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────┐
     │     2. Pipeline de prétraitement       │
     │ (StandardScaler, OneHotEncoding, PCA,  │
     │                ICA)                    │
     │ → Entraîné et sauvegardé (.pkl)        │
     └────────────────────────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────┐
     │ 3. Transformation complète du dataset  │
     │    via le pipeline_preprocessing.pkl   │
     └────────────────────────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────┐
     │       4. Entraînement du modèle        │
     │     Decision Tree (class_weight)       │
     └────────────────────────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────┐
     │      5. Évaluation et métriques        │
     │  (precision, recall, f1, confusion...) │
     └────────────────────────────────────────┘
                         │
                         ▼
     ┌────────────────────────────────────────┐
     │     6. Sauvegarde du modèle (.pkl)     │
     └────────────────────────────────────────┘
```



```bash
project/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── splits/               # X_train, X_test, etc.
│
├── models/
│   ├── saved/                # modèles finaux, threshold, scaler, etc.
│   └── tuned/                # résultats tuning (GridSearch/RandomSearch)
│
├── src/
│   ├── preprocessing/
│   │   └── preprocess.py
│   │
│   ├── train/
│   │   └── train.py          # Entraînement DT / RF
│   │
│   ├── evaluate/
│   │   └── evaluate.py       # Toutes les métriques + benchmark + rapport
│   │
│   ├── inference/
│   │   └── predict.py        # Inférence production + threshold optimal
│   │
│   ├── tuning/
│   │   └── tune.py           # GridSearch / RandomSearch
│   │
│   ├── dashboard/
│   │   └── dashboard.py      # Dashboard automatique (Streamlit)
│   │
│   └── utils/
│       ├── io.py             # load/save helpers
│       ├── metrics.py        # fonctions métriques
│       └── plotting.py       # courbes ROC / confusion / etc.
│
├── reports/
│   ├── evaluation_report.html
│   └── benchmark.json
│
├── requirements.txt
└── README.md

```

Lancer l'orchestrateur comme ça : 

sudo -E /home/ing/amomo_venv/bin/python3 orchestrator_prediction.py
sudo -E /home/ing/amomo_venv/bin/python3 -m capture.orchestrator_prediction



```less
[ Orchestrator Worker ]
        |
        | INSERT
        v
     [ MySQL ]
        ^
        | SELECT
[ Flask Dashboard ] ---> [ Nginx ] ---> Browser
```

```less
┌────────────┐
│ Orchestrator│───► MySQL ◄─── Dashboard
│ (scapy + ML)│
└────────────┘
        │
        ▼
   Trafic réseau réel

```

```less
[ Orchestrator ]
      |
      | INSERT
      ▼
    MySQL
      ▲
      | SELECT (toutes les 5s)
[ Flask API ]  ←  GET /flows_json
      ▲
      |
[ Browser JS ]

```

