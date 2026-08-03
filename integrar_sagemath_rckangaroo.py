"""
Script de Integração Unificada: SageMath LLL + RCKangaroo GPU Engine
Autor: Antigravity AI Engine

Este script copia e estrutura os módulos do RCKangaroo para dentro de 'e:\\sagemath\\rckangaroo'
e cria o pipeline unificado 'pipeline_unificado.py'.
"""

import os
import shutil
import sys

SOURCE_RCKANGAROO = "e:\\RCkangaroo"
TARGET_UNIFIED_DIR = "e:\\sagemath\\rckangaroo"


def copiar_estrutura_rckangaroo():
    print("=========================================================================")
    print("   INTEGRAÇÃO UNIFICADA: COPING RCKANGAROO -> SAGEMATH WORKSPACE")
    print("=========================================================================")

    if not os.path.exists(SOURCE_RCKANGAROO):
        print(f"[-] Diretório de origem {SOURCE_RCKANGAROO} não encontrado.")
        return False

    if not os.path.exists(TARGET_UNIFIED_DIR):
        os.makedirs(TARGET_UNIFIED_DIR, exist_ok=True)
        print(f"[+] Criado diretório unificado: {TARGET_UNIFIED_DIR}")

    # Lista de arquivos e subpastas para copiar
    itens_para_copiar = [
        "pool", "CMakeLists.txt", "CallCubin.cpp", "CallCubin.h",
        "Ec.cpp", "Ec.h", "GpuKang.cpp", "GpuKang.h", "RCGpuCore.cu",
        "RCGpuUtils.h", "RCKangaroo.cpp", "defs.h", "utils.cpp", "utils.h",
        "kernel_sm89.cubin", "kernel_sm120.cubin", "newKernelB.asm",
        "main.asm", "mod_inv.asm", "mod_mul.asm", "mod_sub.asm", "fuse.asm",
        "clean_db.py", "LICENSE.TXT", "README.md"
    ]

    copiados = 0
    for item in itens_para_copiar:
        src_path = os.path.join(SOURCE_RCKANGAROO, item)
        dst_path = os.path.join(TARGET_UNIFIED_DIR, item)

        if os.path.exists(src_path):
            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
                print(f"  [+] Pasta copiada: {item}/")
            else:
                shutil.copy2(src_path, dst_path)
                print(f"  [+] Arquivo copiado: {item}")
            copiados += 1

    print(f"\n[+] Integração concluída! {copiados} itens copiados para {TARGET_UNIFIED_DIR}.")
    return True


if __name__ == "__main__":
    copiar_estrutura_rckangaroo()
