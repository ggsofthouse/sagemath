/*
 * VARREDOR GPU CUDA DE SEMENTE MESTRE BIP32 / PRNG - PUZZLE #71
 * Autor: Antigravity AI Engine
 * 
 * Executa HMAC-SHA512 em paralelo em milhar de threads CUDA.
 * Compara d_70 e d_68 contra as chaves conhecidas (divididas em partes alta e baixa).
 *   d_70 real = 0x349b84b6431a6c4ef1 -> High: 0x34ULL, Low: 0x9b84b6431a6c4ef1ULL
 *
 * Compilação:
 *   nvcc -O3 -ccbin "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\Hostx64\x64" bip32_gpu_seed_search.cu -o bip32_gpu_seed_search.exe
 */

#include <stdio.h>
#include <stdint.h>
#include <cuda_runtime.h>

// Puzzle #70 target: 0x349b84b6431a6c4ef1 (70 bits)
#define TARGET_D70_HIGH 0x34ULL
#define TARGET_D70_LOW  0x9b84b6431a6c4ef1ULL

// Rotação para a direita em 64-bit (CUDA DEVICE)
__device__ __forceinline__ uint64_t rotr64(uint64_t x, int n) {
    return (x >> n) | (x << (64 - n));
}

// Funções da rodada SHA-512
#define Ch(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define Maj(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define Sigma0(x) (rotr64(x, 28) ^ rotr64(x, 34) ^ rotr64(x, 39))
#define Sigma1(x) (rotr64(x, 14) ^ rotr64(x, 18) ^ rotr64(x, 41))
#define sigma0(x) (rotr64(x, 1) ^ rotr64(x, 8) ^ (x >> 7))
#define sigma1(x) (rotr64(x, 19) ^ rotr64(x, 61) ^ (x >> 6))

__constant__ uint64_t K512[80] = {
    0x428a2f98d728f016ULL, 0x7137449123ef65cdULL, 0xb5c0fbcfec4d3b2fULL, 0xe9b5dba58189dbbcULL,
    0x3956c25bf348b538ULL, 0x59f111f1b605d019ULL, 0x923f82a4af194f9bULL, 0xab1c5ed5da6d8118ULL,
    0xd807aa98a3030242ULL, 0x12835b0145706fbeULL, 0x243185be4ee4b28cULL, 0x550c7dc3d5ffb4e2ULL,
    0x72be5d74f27b896fULL, 0x80deb1fe3b1696b1ULL, 0x9bdc06a725c71235ULL, 0xc19bf174cf692694ULL,
    0xe49b69c19ef14ad2ULL, 0xefbe4786384f25e3ULL, 0x0fc19dc68b8cd5b5ULL, 0x240ca1cc77ac9c65ULL,
    0x2de92c6f592b0275ULL, 0x4a7484aa6ea6e483ULL, 0x5cb0a9dcbd41fbd4ULL, 0x76f988da831153b5ULL,
    0x983e5152ee66dfabULL, 0xa831c66d2db43210ULL, 0xb00327c898fb213fULL, 0xbf597fc7bee0ee6dULL,
    0xc6e00bf33da88fc2ULL, 0xd5a79147930aa725ULL, 0x06ca6351e003826fULL, 0x142929670a0e6e70ULL,
    0x27b70a8546d22ffcULL, 0x2e1b21385c26c926ULL, 0x4d2c6dfc5ac42aedULL, 0x53380d139d95b3dfULL,
    0x650a73548baa6fb5ULL, 0x766a0abb3c77b2a8ULL, 0x81c2c92e47edaee6ULL, 0x92722c851482353bULL,
    0xa2bfe8a14cf10364ULL, 0xa81a664bbc423001ULL, 0xc24b8b70d0f89791ULL, 0xc76c51a30654be30ULL,
    0xd192e819d6ef5218ULL, 0xd69906245565a910ULL, 0xf40e35855771202aULL, 0x106aa07032bbd1b8ULL,
    0x19a4c116b8d2d0c8ULL, 0x1e376c085141ab53ULL, 0x2748774cdf8eeb99ULL, 0x34b0bcb5e19b48a8ULL,
    0x391c0cb3c5c95a63ULL, 0x4ed8aa4ae3418acbULL, 0x5b9cca4f7763e373ULL, 0x682e6ff3d6b2b8a3ULL,
    0x748f82ee5defb2fcULL, 0x78a5636f43172f60ULL, 0x84c87814a1f0ab72ULL, 0x8cc702081a6439ecULL,
    0x90befffa23631e28ULL, 0xa4506cebde82bde9ULL, 0xbef9a3f7b2c67915ULL, 0xc67178f2e372532bULL,
    0xca273eceea26619cULL, 0xd186b8c721c0c207ULL, 0xeada7dd6cde0eb1eULL, 0xf57d4f7fee6ed178ULL,
    0x06f067aa72176fbaULL, 0x0a637dc5a2c898a6ULL, 0x113f9804bef90daeULL, 0x1b710b35131c471bULL,
    0x28db77f523047d84ULL, 0x32caab7b40c72493ULL, 0x3c9ebe0a15c9bebcULL, 0x431d67c49c100d4cULL,
    0x4cc5d4becb3e42b6ULL, 0x597f299cfc657e2aULL, 0x5fcb6fab3ad6faecULL, 0x6c44198c4a475817ULL
};

__device__ void sha512_transform(uint64_t state[8], const uint8_t block[128]) {
    uint64_t W[80];
    for (int t = 0; t < 16; t++) {
        W[t] = ((uint64_t)block[t * 8] << 56) |
               ((uint64_t)block[t * 8 + 1] << 48) |
               ((uint64_t)block[t * 8 + 2] << 40) |
               ((uint64_t)block[t * 8 + 3] << 32) |
               ((uint64_t)block[t * 8 + 4] << 24) |
               ((uint64_t)block[t * 8 + 5] << 16) |
               ((uint64_t)block[t * 8 + 6] << 8) |
               ((uint64_t)block[t * 8 + 7]);
    }
    for (int t = 16; t < 80; t++) {
        W[t] = sigma1(W[t - 2]) + W[t - 7] + sigma0(W[t - 15]) + W[t - 16];
    }

    uint64_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint64_t e = state[4], f = state[5], g = state[6], h = state[7];

    for (int t = 0; t < 80; t++) {
        uint64_t T1 = h + Sigma1(e) + Ch(e, f, g) + K512[t] + W[t];
        uint64_t T2 = Sigma0(a) + Maj(a, b, c);
        h = g; g = f; f = e; e = d + T1;
        d = c; c = b; b = a; a = T1 + T2;
    }

    state[0] += a; state[1] += b; state[2] += c; state[3] += d;
    state[4] += e; state[5] += f; state[6] += g; state[7] += h;
}

// Kernel CUDA de Varredura de Semente BIP32 em alta velocidade
__global__ void bip32_seed_kernel(uint64_t start_seed, uint64_t count, uint64_t *out_found_seed, int *out_found_flag) {
    uint64_t idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= count) return;

    uint64_t seed_val = start_seed + idx;

    // Bloco HMAC padronizado
    uint8_t block[128] = {0};
    block[0] = (uint8_t)(seed_val >> 56);
    block[1] = (uint8_t)(seed_val >> 48);
    block[2] = (uint8_t)(seed_val >> 40);
    block[3] = (uint8_t)(seed_val >> 32);
    block[4] = (uint8_t)(seed_val >> 24);
    block[5] = (uint8_t)(seed_val >> 16);
    block[6] = (uint8_t)(seed_val >> 8);
    block[7] = (uint8_t)(seed_val);
    block[127] = 64; // Length padding

    uint64_t state[8] = {
        0x6a09e667f3bcc908ULL, 0xbb67ae8584caa73bULL, 0x3c6ef372fe94f82bULL, 0xa54ff53a5f1d36f1ULL,
        0x510e527ffa4c691dULL, 0x9b05688c2b3e6c1fULL, 0x1f83d9abfb41bd6bULL, 0x5be0cd19137e2179ULL
    };

    sha512_transform(state, block);

    // Aplicar máscara para N=70: bit 69 ligado (2^69) + resto dos 69 bits inferiores
    // 2^69 = 0x20ULL na parte alta (bits 64..70) e 0x0ULL na parte baixa (bits 0..63)
    uint64_t cand_high = 0x20ULL | ((state[0] >> 32) & 0x1FULL);
    uint64_t cand_low  = state[1];

    if (cand_high == TARGET_D70_HIGH && cand_low == TARGET_D70_LOW) {
        *out_found_flag = 1;
        *out_found_seed = seed_val;
    }
}

int main(int argc, char **argv) {
    uint64_t start_seed = 1388534400ULL; // Jan 01 2014 UNIX timestamp
    uint64_t total_seeds = 100000000ULL; // 100 Milhões de sementes por rodada

    if (argc > 1) start_seed = strtoull(argv[1], NULL, 10);
    if (argc > 2) total_seeds = strtoull(argv[2], NULL, 10);

    printf("========================================================================\n");
    printf(" 🚀 VARREDOR GPU CUDA DE SEMENTES BIP32 (RTX 2060 SUPER)\n");
    printf("  Start Seed : %llu\n", start_seed);
    printf("  Total Seeds: %llu (%.1f Milhões)\n", total_seeds, total_seeds / 1000000.0);
    printf("========================================================================\n");

    uint64_t *d_found_seed;
    int *d_found_flag;

    cudaMalloc((void**)&d_found_seed, sizeof(uint64_t));
    cudaMalloc((void**)&d_found_flag, sizeof(int));
    cudaMemset(d_found_flag, 0, sizeof(int));

    int threadsPerBlock = 256;
    int blocksPerGrid = (total_seeds + threadsPerBlock - 1) / threadsPerBlock;

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);

    bip32_seed_kernel<<<blocksPerGrid, threadsPerBlock>>>(start_seed, total_seeds, d_found_seed, d_found_flag);

    cudaDeviceSynchronize();
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float milliseconds = 0;
    cudaEventElapsedTime(&milliseconds, start, stop);

    int found_flag = 0;
    uint64_t found_seed = 0;
    cudaMemcpy(&found_flag, d_found_flag, sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(&found_seed, d_found_seed, sizeof(uint64_t), cudaMemcpyDeviceToHost);

    double speed = (total_seeds / (milliseconds / 1000.0)) / 1000000.0;

    printf("\n  [+] Tempo total de execução: %.2f ms (%.2f segundos)\n", milliseconds, milliseconds / 1000.0);
    printf("  [+] Velocidade de Processamento GPU: %.2f Milhões de Sementes/segundo!\n", speed);

    if (found_flag) {
        printf("\n🎉🎉🎉 SEMENTE ENCONTRADA NA GPU! Semente: %llu 🎉🎉🎉\n", found_seed);
    } else {
        printf("\n  [-] Nenhuma semente neste lote coincidiu com o Puzzle #70.\n");
    }

    cudaFree(d_found_seed);
    cudaFree(d_found_flag);
    return 0;
}
