import pandas as pd

# Liste des fichiers CSV à analyser
filenames = [
    "TFTP.csv",
    "DrDoS_NetBIOS.csv",
    "DrDoS_SSDP.csv",
    "DrDoS_DNS.csv",
    "Syn.csv",
    "DrDoS_SNMP.csv",
    "UDPLag.csv",
    "DrDoS_MSSQL.csv",
    "DrDoS_UDP.csv",
    "DrDoS_LDAP.csv",
    "DrDoS_NTP.csv"
]

# Résultat final
report_rows = []

for filename in filenames:
    print(f"\nAnalyse du fichier : {filename}")

    # Lecture des colonnes
    columns = pd.read_csv(filename, nrows=0).columns.tolist()
    label_col = columns[-1]

    # Comptage total des lignes
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        total_samples = sum(1 for _ in f) - 1

    # Comptage des labels
    label_counts = {}
    chunk_size = 100000

    for chunk in pd.read_csv(filename, usecols=[label_col], chunksize=chunk_size, low_memory=False):
        for label, count in chunk[label_col].value_counts().items():
            label_counts[label] = label_counts.get(label, 0) + count

    # Format compact pour tableau : "BENIGN: 12 345 — DrDoS_NTP: 678 910"
    detailed_counts = " — ".join([f"{label}: {count:,}" for label, count in label_counts.items()])

    report_rows.append({
        "Fichier CSV": filename,
        "Échantillons": f"{total_samples:,}",
        "Labels présents": ", ".join(label_counts.keys()),
        "Détails sous-catégories": detailed_counts
    })

# Affichage du tableau
print("\n\n===== TABLEAU FINAL =====\n")

print("| Fichier CSV | Total échantillons | Labels | Détails par label |")
print("|-------------|--------------------|--------|--------------------|")

for row in report_rows:
    print(
        f"| {row['Fichier CSV']} | {row['Échantillons']} | "
        f"{row['Labels présents']} | {row['Détails sous-catégories']} |"
    )
