#include<stdio.h>
#include<stdint.h>

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

void init_cipher() {    
    FILE* rand = fopen("/dev/urandom", "rb");
    fread(state, 4, 3, rand);
    fclose(rand);
    state[1] |= 1;
    state[1] &= ~(uint32_t) 2;
    state[2] |= 1;
    int i, j;
    for (i = 0; i < N; ++i) {
        for (j = 0; j < (1 << logM); ++j) {
            table[i][j] = generate_num();
        }
    }    
}

uint32_t cur;
int cur_byte = 0;

unsigned char get_next_gamma() {
    if (!cur_byte) {
        cur = generate_gamma();
        cur_byte = 4;
    }
    --cur_byte;    
    return (cur & (255 << cur_byte * 8)) >> cur_byte * 8;
}

int main(int argc, char**argv) {    
    init_cipher();
    int ch;
    while ((ch = getchar()) != EOF) {
        unsigned char g = get_next_gamma();
        putchar(g ^ ch); 
    }
}
