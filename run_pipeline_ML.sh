#!/bin/bash

# ====================================
# Script d'exécution du pipeline ML
# Usage: ./run_pipeline.sh
# ====================================

set -e  # Arrêt immédiat si erreur

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ====================================
# 1. Préprocessing
# ====================================
echo -e "${BLUE}[INFO] Starting preprocessing...${NC}"
python3 preprocessed_data/preprocessed_data.py

echo -e "${GREEN}[OK] Preprocessing completed.${NC}"
echo ""
 
# ====================================
# 2. Training
# ====================================
echo -e "${BLUE}[INFO] Starting model training...${NC}"
python3 train/train_models.py

echo -e "${GREEN}[OK] Training completed.${NC}"
echo ""

# ====================================
# 3. Evaluation
# ====================================
echo -e "${BLUE}[INFO] Starting evaluation...${NC}"
python3 evaluate/evaluate_models.py

echo -e "${GREEN}[OK] Evaluation completed.${NC}"
echo ""

# ====================================
# 4. Créer un dashboard
# ====================================
echo -e "${BLUE}[INFO] Starting evaluation...${NC}"
python3 evaluate/dashboard/dashboard.py

echo -e "${GREEN}[OK] Evaluation completed.${NC}"
echo ""

# ====================================
# Fin
# ====================================
echo -e "${YELLOW}[DONE] Full pipeline executed successfully.${NC}"
