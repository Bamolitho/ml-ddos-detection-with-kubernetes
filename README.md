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



```
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

