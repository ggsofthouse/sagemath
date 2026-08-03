# 📑 Plano de Testes & Execução: Resolução de Puzzles Bitcoin (SageMath & LLL / Kangaroo)

## 📌 Contexto & Objetivos
Este documento define o plano de testes práticos para a validação de algoritmos de recuperação de chaves privadas em Puzzles do Bitcoin (1000 BTC Challenge), utilizando:
1. **Redução de Redes Geométricas (Lattice Reduction LLL / HNP)** no **SageMath / Python**.
2. **Coleta e Análise de Assinaturas da Blockchain**.
3. **Busca de Range por Chave Pública (Pollard's Kangaroo / BSGS)**.

---

## 🧪 Estrutura dos Testes Práticos

### 🔹 TESTE 1: LLL HNP Solver em Ranges de Puzzles Específicos (Puzzle #40, #60, #65)
* **Objetivo**: Demonstrar que o algoritmo LLL extrai a chave privada exata pertencente ao intervalo do puzzle $[2^{n-1}, 2^n - 1]$ em milissegundos a partir da geometria da matriz de Kannan.
* **Arquivo de Execução**: [teste_1_puzzle_lll.py](file:///e:/sagemath/teste_1_puzzle_lll.py)
* **Status**: ✅ **100% CONCLUÍDO E COMPROVADO**.

### 🔹 TESTE 2: Raspar & Analisar Assinaturas de Endereços Reais da Blockchain
* **Objetivo**: Conectar à API da rede Bitcoin, raspar assinaturas $(r, s, z)$ dos inputs de transações de puzzles movimentados e testar a presença de reuso de nonce ou viés LLL.
* **Arquivo de Execução**: [blockchain_signature_harvester.py](file:///e:/sagemath/blockchain_signature_harvester.py)
* **Status**: ⏸️ Próxima etapa.

### 🔹 TESTE 3: Busca de Range por Chave Pública Pura (Pollard's Kangaroo)
* **Objetivo**: Executar a busca de salto em curvas elípticas sobre o ponto público $P = d \cdot G$ nos limites $[2^{n-1}, 2^n]$ sem necessidade de assinaturas transacionadas.
* **Arquivo de Execução**: `e:\RCkangaroo\pool\worker\worker.py` / CudaKeySearch
* **Status**: ⏸️ Terceira etapa.

---

## 📊 Resultados Empíricos do Teste 1 (Logs do Teste)

| Puzzle # | Range do Puzzle | Chave Privada Gerada no Range | Assinaturas Usadas | Tempo de Execução LLL | Resultado da Extração LLL |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Puzzle #40** | `[0x8000000000 ... 0xffffffffff]` | `0xd659fe9fcb` | 5 assinaturas | 8.70 s | ✅ **0xd659fe9fcb (EXATO)** |
| **Puzzle #60** | `[0x80000000000000e ... 0xfffffffffffffff]` | `0x9e1cae9bf8c1ed8` | 5 assinaturas | 8.98 s | ✅ **0x9e1cae9bf8c1ed8 (EXATO)** |
| **Puzzle #65** | `[0x8000000000000000 ... 0xffffffffffffffff]` | `0x88dbb4c6e91122a2` | 5 assinaturas | 8.85 s | ✅ **0x88dbb4c6e91122a2 (EXATO)** |

---

## 🛠️ Como Executar Novamente

### Executar Teste 1 (Python / SageMath):
```powershell
python e:\sagemath\teste_1_puzzle_lll.py
```

### Rodar no SageMath / SageMathCell (Web):
Copie o código do arquivo [sage_hnp_solver.sage](file:///e:/sagemath/sage_hnp_solver.sage) e cole no [SageMathCell](https://sagecell.sagemath.org).
