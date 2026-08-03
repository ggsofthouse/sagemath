#!/bin/bash
# =========================================================================
# VAST.AI CLOUD SETUP SCRIPT FOR 4X GPU (RTX 4096 / 5060 Ti / RTX 4090)
# Antigravity AI Engine - SageMath LLL + Multi-GPU RCKangaroo
# =========================================================================

set -e

echo "========================================================================="
echo "   PREPARANDO AMBIENTE VAST.AI (4X GPU SAGEMATH LLL + RCKANGAROO)"
echo "========================================================================="

# 1. Atualizar Pacotes e Instalar Dependências
echo "[+] Instalação de dependências do sistema Linux..."
apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    cmake \
    build-essential \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev

# 2. Instalar dependências Python
echo "[+] Instalando pacotes Python (sympy, ecdsa, requests)..."
pip3 install --upgrade pip
pip3 install sympy ecdsa requests

# 3. Verificar GPUs NVIDIA
echo "[+] Verificando GPUs NVIDIA disponíveis na instância Vast.ai:"
nvidia-smi --query-gpu=index,name,memory.total --format=csv

# 4. Localizar pasta do RCKangaroo
RCK_DIR=""
if [ -d "rckangaroo" ]; then
    RCK_DIR="rckangaroo"
elif [ -d "RCkangaroo" ]; then
    RCK_DIR="RCkangaroo"
fi

if [ -n "$RCK_DIR" ]; then
    echo "[+] Compilando RCKangaroo C++ CUDA Kernel em $RCK_DIR..."
    cd "$RCK_DIR"
    if [ -f "CMakeLists.txt" ]; then
        mkdir -p build && cd build
        cmake ..
        make -j$(nproc) || echo "[!] Compilação C++ falhou, os scripts python continuarão a rodar."
        cd ../..
        echo "[OK] Compilação finalizada!"
    else
        cd ..
    fi
else
    echo "[!] Pasta rckangaroo não encontrada."
fi

echo "========================================================================="
echo "   [SUCESSO] AMBIENTE VAST.AI CONFIGURADO E PRONTO PARA USO!"
echo "   Para rodar o Puzzle 71 em 4 GPUs: python3 vastai_multi_gpu_runner.py --puzzle 71"
echo "========================================================================="
