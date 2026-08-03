#!/bin/bash
# =========================================================================
# SCRIPT DE ATUALIZAÇÃO GIT PULL E EXECUÇÃO LOCAL NA NUVEM (VAST.AI)
# Antigravity AI Engine
# =========================================================================

set -e

echo "========================================================================="
echo "   [GIT PULL] ATUALIZANDO REPOSITÓRIO NA NUVEM"
echo "========================================================================="

# 1. Puxar alterações mais recentes do GitHub
git pull origin main || git pull

# 2. Garantir permissões nos scripts
chmod +x vastai_setup.sh git_pull_nuvem.sh 2>/dev/null || true

# 3. Compilar RCKangaroo C++ se necessário
if [ -d "RCkangaroo" ]; then
    cd RCkangaroo
    if [ ! -f "build/RCKangaroo" ]; then
        echo "[+] Compilando RCKangaroo C++ CUDA Kernel..."
        mkdir -p build && cd build
        cmake .. && make -j$(nproc) || true
        cd ..
    fi
    cd ..
elif [ -d "rckangaroo" ]; then
    cd rckangaroo
    if [ ! -f "build/RCKangaroo" ]; then
        echo "[+] Compilando RCKangaroo C++ CUDA Kernel..."
        mkdir -p build && cd build
        cmake .. && make -j$(nproc) || true
        cd ..
    fi
    cd ..
fi

echo "========================================================================="
echo "   [SUCESSO] Código atualizado e pronto para execução local!"
echo "   Para rodar o Puzzle 71 com DP=14 em 4 GPUs:"
echo "   python3 vastai_multi_gpu_runner.py --puzzle 71 --gpus 0,1,2,3 --dp 14"
echo "========================================================================="
