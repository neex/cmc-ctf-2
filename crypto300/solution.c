#include<stdio.h>
#include<stdint.h>
#include<stdlib.h>

uint32_t state[3];

#define N 6
#define logM 5

uint32_t table[N][1 << logM];

uint32_t reverse(uint32_t x)
{
    x = (((x & 0xaaaaaaaa) >> 1) | ((x & 0x55555555) << 1));
    x = (((x & 0xcccccccc) >> 2) | ((x & 0x33333333) << 2));
    x = (((x & 0xf0f0f0f0) >> 4) | ((x & 0x0f0f0f0f) << 4));
    x = (((x & 0xff00ff00) >> 8) | ((x & 0x00ff00ff) << 8));
    return((x >> 16) | (x << 16));
}

uint32_t crypt(uint32_t num) {
    int i;
    for (i = 0; i < 16; ++i) {
        reverse(num);
        num *=  0xDEADBEEF;
        ++num;
    }
    return num;
}

uint32_t generate_num() {
    state[0] = state[0] * state[1] + state[2];
    return crypt(state[0]);
}

uint32_t generate_gamma() {
    uint32_t x = generate_num();
    uint32_t inds = generate_num();
    int i;
    for (i = 0; i < N; ++i) {
        int ind = (inds & ((1 << logM) - 1) << logM * i) >> logM * i;
        x ^= table[i][ind];
        table[i][ind] ^= x;
        x ^= table[i][ind];
    }
    return x;
}

uint32_t cur;
int cur_byte = 0;

void init_cipher(uint32_t seed, uint32_t a, uint32_t b) {
    state[0] = seed;
    state[1] = a;
    state[2] = b;
    int i, j;
    for (i = 0; i < N; ++i) {
        for (j = 0; j < (1 << logM); ++j) {
            table[i][j] = generate_num();
        }
    }
    cur_byte = 0;
}

unsigned char get_next_gamma() {
    if (!cur_byte) {
        cur = generate_gamma();
        cur_byte = 4;
    }
    --cur_byte;    
    return (cur & (255 << cur_byte * 8)) >> cur_byte * 8;
}

unsigned char*encrypted;
unsigned char*plain;

int encrypted_len;
int plain_len;

void read_file(char*name, unsigned char**buffer, int*len) {
    FILE* f = fopen(name, "rb");
    fseek(f, 0, SEEK_END);
    *len = ftell(f);
    *buffer = (unsigned char*) malloc(*len);
    rewind(f);
    fread(*buffer, *len, 1, f);
    fclose(f);
}


uint32_t inverse(uint32_t x) {
    uint32_t res = 1;
    int i;
    for (i=0; i<31; ++i) {
        res = res * res;
        res = res * x;
    }
    return res;
}

uint32_t decrypt(uint32_t num) {
    int i;
    for (i = 0; i < 16; ++i) {
        --num;
        reverse(num);
        num *=  inverse(0xDEADBEEF);
    }
    return num;
}

uint32_t rewind_linear(uint32_t cur_state, uint32_t a, uint32_t b) {
    return (cur_state - b) * inverse(a);
}

uint32_t* gamma;

uint32_t* decrypted_gamma;
int gamma_len;

int main() {
    read_file("encrypted_data.bin", &encrypted, &encrypted_len);
    read_file("data.bin", &plain, &plain_len);
    int i, j;
    gamma = (uint32_t*) malloc(plain_len);
    decrypted_gamma = (uint32_t*) malloc(plain_len);    
    gamma_len = plain_len >> 2;
    for (i = 0; i < gamma_len; ++i) {
        uint32_t num = 0;
        for (j = 0; j < 4; ++j) {
            num <<= 8;
            num += encrypted[i * 4 + j] ^ plain[i * 4 + j];
        }
        gamma[i] = num;
        decrypted_gamma[i] = decrypt(num);
    }
    
    int k;
    /*  a * gamma[i] + b = gamma[j]
        a * gamma[j] + b = gamma[k]
        
        a = (gamma[j] - gamma[k]) / (gamma[i] - gamma[j])
        b = gamma[j] - a * gamma[i]
        
    */     
    
    uint32_t a;
    uint32_t b;
    uint32_t c;
    
    for (i = 0; i < gamma_len; ++i) {
        for (j = 0; j < gamma_len; ++j) {           
            uint32_t coef = decrypted_gamma[i] - decrypted_gamma[j]; 
            if (coef & 1 != 1) continue;
            for (k = 0; k < gamma_len; ++k) {
                a = (decrypted_gamma[j] - decrypted_gamma[k]) * inverse(coef);
                if ((a & 3) != 1) continue;
                b = decrypted_gamma[j] - a * decrypted_gamma[i];
                if ((b & 1) != 1) continue;
                c = decrypted_gamma[i];
                int revc = 0;
                for (revc = 0; revc < (N - 1) * (1 << logM); ++revc) {
                    c = rewind_linear(c, a, b);                
                }
                
                for (revc = 0; revc < (1 << logM); ++revc) {
                    init_cipher(c, a, b);
                    int good = 1;
                    int p;
                    for (p = 0; p < 10; ++p) {
                        if (gamma[p] != generate_gamma()) {
                            good = 0;
                            break;
                        }
                    }
                    if (good) goto found;
                    c = rewind_linear(c, a, b);
                }
            }
        }
    }       
    fprintf(stderr, "Not solved!!!!\n");
    return 0;
found: 
    fprintf(stderr, "Found the key!\n");    
    init_cipher(c, a, b);
    for (i = 0; i < encrypted_len; ++i) {
        putchar(encrypted[i] ^ get_next_gamma());
    }
    return 0;
}
