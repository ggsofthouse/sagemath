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

# 4. Compilar RCKangaroo para Multi-GPU C++
echo "[+] Compilando RCKangaroo C++ CUDA Kernel para Linux..."
cd rckangaroo || exit 1
if [ -f "CMakeLists.txt" ]; then
    mkdir -p build && cd build
    cmake ..
    make -j$(nproc)
    echo "[OK] Compilação do RCKangaroo C++ finalizada!"
else
    echo "[!] CMakeLists.txt não encontrado em rckangaroo."
fi

cd ../..

echo "========================================================================="
echo "   [SUCESSO] AMBIENTE VAST.AI CONFIGURADO E PRONTO PARA USO!"
echo "   Para rodar o Puzzle 71 em 4 GPUs: python3 vastai_multi_gpu_runner.py --puzzle 71"
echo "========================================================================="
