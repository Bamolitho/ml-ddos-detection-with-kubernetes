Le jeu de données utilisé est CICDDoS2019. Celui-ci provient du site web accessible via le lien : [CICDDoS2019](https://www.unb.ca/cic/datasets/ddos-2019.html)

Dataset : [dataset](http://cicresearch.ca/CICDataset/CICDDoS2019/Dataset/)

Ce jeu de données réuni les deux grandes catégories d'attaques DDoS : Reflection-based et exploitation-based attacks.
![DDoS Taxonomy](../Images/ddostaxonomy.png)

J'ai téléchargé le [fichier CSV-01-12.zip](http://cicresearch.ca/CICDataset/CICDDoS2019/Dataset/CSVs/CSV-01-12.zip). Celui-ci contient11 fichiers trouvés .csv

## **Résumé des fichiers du dataset**

Tous les fichiers CSV analysés comportent une colonne cible unique : **Label**.
Cette colonne contient les catégories (types de trafic) propres à chaque fichier. Le tableau suivant synthétise le nombre d’échantillons et les labels présents dans chaque fichier :

| Fichier CSV        | Total échantillons | Labels                   | Détails par label                                      |
| ------------------ | ------------------ | ------------------------ | ------------------------------------------------------ |
| TFTP.csv           | 20,107,827         | TFTP, BENIGN             | TFTP: 20,082,580 <br />BENIGN: 25,247                  |
| DrDoS_NetBIOS.csv  | 4,094,986          | DrDoS_NetBIOS, BENIGN    | DrDoS_NetBIOS: 4,093,279<br />BENIGN: 1,707            |
| DrDoS_SSDP.csv     | 2,611,374          | DrDoS_SSDP, BENIGN       | DrDoS_SSDP: 2,610,611<br />BENIGN: 763                 |
| DrDoS_DNS.csv      | 5,074,413          | DrDoS_DNS, BENIGN        | DrDoS_DNS: 5,071,011<br />BENIGN: 3,402                |
| Syn.csv            | 1,582,681          | Syn, BENIGN              | Syn: 1,582,289<br />BENIGN: 392                        |
| DrDoS_SNMP.csv     | 5,161,377          | DrDoS_SNMP, BENIGN       | DrDoS_SNMP: 5,159,870<br />BENIGN: 1,507               |
| UDPLag.csv         | 370,605            | UDP-lag, BENIGN, WebDDoS | UDP-lag: 366,461<br />BENIGN: 3,705 <br />WebDDoS: 439 |
| DrDoS_MSSQL.csv    | 4,524,498          | DrDoS_MSSQL, BENIGN      | DrDoS_MSSQL: 4,522,492<br />BENIGN: 2,006              |
| DrDoS_UDP.csv      | 3,136,802          | DrDoS_UDP, BENIGN        | DrDoS_UDP: 3,134,645<br />BENIGN: 2,157                |
| DrDoS_LDAP.csv     | 2,181,542          | DrDoS_LDAP, BENIGN       | DrDoS_LDAP: 2,179,930<br />BENIGN: 1,612               |
| DrDoS_NTP.csv      | 1,217,007          | DrDoS_NTP, BENIGN        | DrDoS_NTP: 1,202,642<br />BENIGN: 14,365               |
| Total échantillons | 50063112           |                          |                                                        |

### **Caractéristiques du dataset (features)**

Tous les fichiers partagent la même structure :
 **87 features** + **Label**.

Les features décrivent différentes propriétés des flux réseau (flow features), comme :

- informations d’en-tête (IP source, ports, protocole, header lengths),
- statistiques sur les paquets (min/max/mean/std),
- caractéristiques temporelles (IAT, durée, débit),
- indicateurs TCP (flags FIN/SYN/ACK…),
- attributs liés aux sous-flux,
- mesures d’activité et d’inactivité.

### **Caractéristiques du dataset (Label)**

Ce dataset regroupe 12 catégories d’attaques DDoS. Chaque fichier CSV correspond à un type d’attaque particulier, ce qui facilite l’identification des catégories directement à partir du nom du fichier. À noter également que la catégorie *WebDDoS* apparaît uniquement dans le fichier **UDPLag.csv**.

On observe que le trafic **Benign** est largement minoritaire comparé aux différentes classes d’attaques, ce qui crée un déséquilibre important dans le dataset.

#### **Liste des 87 features :**

Unnamed: 0, Flow ID, Source IP, Source Port, Destination IP, Destination Port, Protocol, Timestamp, Flow Duration, Total Fwd Packets, Total Backward Packets, Total Length of Fwd Packets, Total Length of Bwd Packets, Fwd Packet Length Max, Fwd Packet Length Min, Fwd Packet Length Mean, Fwd Packet Length Std, Bwd Packet Length Max, Bwd Packet Length Min, Bwd Packet Length Mean, Bwd Packet Length Std, Flow Bytes/s, Flow Packets/s, Flow IAT Mean, Flow IAT Std, Flow IAT Max, Flow IAT Min, Fwd IAT Total, Fwd IAT Mean, Fwd IAT Std, Fwd IAT Max, Fwd IAT Min, Bwd IAT Total, Bwd IAT Mean, Bwd IAT Std, Bwd IAT Max, Bwd IAT Min, Fwd PSH Flags, Bwd PSH Flags, Fwd URG Flags, Bwd URG Flags, Fwd Header Length, Bwd Header Length, Fwd Packets/s, Bwd Packets/s, Min Packet Length, Max Packet Length, Packet Length Mean, Packet Length Std, Packet Length Variance, FIN Flag Count, SYN Flag Count, RST Flag Count, PSH Flag Count, ACK Flag Count, URG Flag Count, CWE Flag Count, ECE Flag Count, Down/Up Ratio, Average Packet Size, Avg Fwd Segment Size, Avg Bwd Segment Size, Fwd Header Length.1, Fwd Avg Bytes/Bulk, Fwd Avg Packets/Bulk, Fwd Avg Bulk Rate, Bwd Avg Bytes/Bulk, Bwd Avg Packets/Bulk, Bwd Avg Bulk Rate, Subflow Fwd Packets, Subflow Fwd Bytes, Subflow Bwd Packets, Subflow Bwd Bytes, Init_Win_bytes_forward, Init_Win_bytes_backward, act_data_pkt_fwd, min_seg_size_forward, Active Mean, Active Std, Active Max, Active Min, Idle Mean, Idle Std, Idle Max, Idle Min, SimillarHTTP, Inbound.

------

Bien sûr, je te redonne le texte exactement comme demandé — **propre, structuré, prêt à intégrer dans ton rapport**, sans rien ajouter ni retirer, et sans fioritures.

# **Le déséquilibre du dataset**

Le déséquilibre important entre la catégorie *Benign* et les différentes attaques peut entraîner un modèle biaisé, qui prédira majoritairement les classes majoritaires. Plusieurs stratégies permettent de corriger ou limiter ce problème :

## **1. Rééchantillonnage des données**

### **Oversampling de la classe minoritaire**

Dupliquer ou générer artificiellement des exemples *Benign* (ex. : SMOTE) pour équilibrer les proportions.

### **Undersampling des classes majoritaires**

Réduire le nombre d’échantillons d’attaques pour rapprocher leur volume de *Benign*.

------

## **2. Pondération des classes (class weighting)**

Ajuster la fonction de perte pour pénaliser davantage les erreurs commises sur les classes minoritaires.

**Exemples :**

- `class_weight='balanced'` dans scikit-learn
- Pondération manuelle pour XGBoost, LightGBM, etc.

------

## **3. Métriques adaptées**

L’accuracy est trompeuse dans un dataset déséquilibré.
 Il faut privilégier des métriques pertinentes pour les classes minoritaires :

- F1-score
- Precision / Recall
- Matrice de confusion
- AUC-ROC
- AUC-PR (préférable pour très fort déséquilibre)

------

## **4. Validation par stratification**

Il est important de maintenir la même proportion des classes dans tous les splits.
Utiliser :

- `train_test_split(..., stratify=...)`
- `StratifiedKFold`

------

## **5. Modèles robustes aux déséquilibres**

Certaines familles de modèles sont plus efficaces lorsqu’il existe un très fort déséquilibre :

- Gradient boosting (XGBoost, LightGBM)
- Random Forest avec class weighting
- Méthodes bayésiennes dans les cas extrêmes

------

## **6. Détection d’anomalies**

Si *Benign* est très minoritaire, on peut reformuler le problème en :

**Anomaly / One-Class Detection**

On modélise le trafic normal, puis on détecte les écarts.

------

# **L’approche la plus robuste (dans ce cas précis)**

### **Combinaison : Class Weighting + Modèles Boostés**

C’est la stratégie la plus fiable face à :

- un dataset massif
- des classes majoritaires très disproportionnées
- du bruit dans les données
- une grande diversité de types d’attaques

**Pourquoi ?**

- Aucun oversampling nécessaire (SMOTE coûte cher et perturbe les PCA/ICA).
- Les modèles boosting sont naturellement robustes au déséquilibre.
- Le *class weighting* modifie la fonction de perte et évite la manipulation du dataset.

En pratique :

- XGBoost → `scale_pos_weight`
- LightGBM → `is_unbalance=true` ou `class_weight='balanced'`
- RandomForest / LogisticRegression → `class_weight='balanced'`

C’est stable, scalable, et très performant pour les grands flux réseau comme CICDDoS.
