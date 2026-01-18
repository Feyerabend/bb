#include "pico/stdlib.h"
#include <stdio.h>
#include <string.h>
#include <stdint.h>

/* SHA256 implementation (tiny, stripped-down) */

#define ROTR(x,n) (((x) >> (n)) | ((x) << (32-(n))))
#define CH(x,y,z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x,y,z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTR(x,2) ^ ROTR(x,13) ^ ROTR(x,22))
#define EP1(x) (ROTR(x,6) ^ ROTR(x,11) ^ ROTR(x,25))
#define SIG0(x) (ROTR(x,7) ^ ROTR(x,18) ^ ((x) >> 3))
#define SIG1(x) (ROTR(x,17) ^ ROTR(x,19) ^ ((x) >> 10))

static const uint32_t k[64] = {
  0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};

typedef struct {
    uint8_t data[64];
    uint32_t datalen;
    unsigned long long bitlen;
    uint32_t state[8];
} SHA256_CTX;

void sha256_transform(SHA256_CTX *ctx, const uint8_t data[]) {
    uint32_t a,b,c,d,e,f,g,h,i,j,t1,t2,m[64];
    for (i=0,j=0; i < 16; ++i, j+=4)
        m[i] = (data[j]<<24)|(data[j+1]<<16)|(data[j+2]<<8)|(data[j+3]);
    for (; i < 64; ++i)
        m[i] = SIG1(m[i-2]) + m[i-7] + SIG0(m[i-15]) + m[i-16];
    a=ctx->state[0]; b=ctx->state[1]; c=ctx->state[2]; d=ctx->state[3];
    e=ctx->state[4]; f=ctx->state[5]; g=ctx->state[6]; h=ctx->state[7];
    for (i=0;i<64;++i) {
        t1 = h + EP1(e) + CH(e,f,g) + k[i] + m[i];
        t2 = EP0(a) + MAJ(a,b,c);
        h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    ctx->state[0]+=a; ctx->state[1]+=b; ctx->state[2]+=c; ctx->state[3]+=d;
    ctx->state[4]+=e; ctx->state[5]+=f; ctx->state[6]+=g; ctx->state[7]+=h;
}

void sha256_init(SHA256_CTX *ctx) {
    ctx->datalen=0; ctx->bitlen=0;
    ctx->state[0]=0x6a09e667; ctx->state[1]=0xbb67ae85;
    ctx->state[2]=0x3c6ef372; ctx->state[3]=0xa54ff53a;
    ctx->state[4]=0x510e527f; ctx->state[5]=0x9b05688c;
    ctx->state[6]=0x1f83d9ab; ctx->state[7]=0x5be0cd19;
}

void sha256_update(SHA256_CTX *ctx,const uint8_t data[],size_t len){
    for (size_t i=0;i<len;++i){
        ctx->data[ctx->datalen]=data[i];
        ctx->datalen++;
        if (ctx->datalen==64){
            sha256_transform(ctx,ctx->data);
            ctx->bitlen+=512;
            ctx->datalen=0;
        }
    }
}

void sha256_final(SHA256_CTX *ctx,uint8_t hash[]){
    unsigned i=ctx->datalen;
    if (ctx->datalen<56){
        ctx->data[i++]=0x80;
        while(i<56) ctx->data[i++]=0;
    } else {
        ctx->data[i++]=0x80;
        while(i<64) ctx->data[i++]=0;
        sha256_transform(ctx,ctx->data);
        memset(ctx->data,0,56);
    }
    ctx->bitlen+=ctx->datalen*8;
    ctx->data[63]=ctx->bitlen;
    ctx->data[62]=ctx->bitlen>>8;
    ctx->data[61]=ctx->bitlen>>16;
    ctx->data[60]=ctx->bitlen>>24;
    ctx->data[59]=ctx->bitlen>>32;
    ctx->data[58]=ctx->bitlen>>40;
    ctx->data[57]=ctx->bitlen>>48;
    ctx->data[56]=ctx->bitlen>>56;
    sha256_transform(ctx,ctx->data);
    for(i=0;i<4;++i){
        for(unsigned j=0;j<8;++j){
            hash[i+4*j]=(ctx->state[j]>>(24-i*8))&0xff;
        }
    }
}

/* PBKDF2-HMAC-SHA256 */

void hmac_sha256(const uint8_t *key, size_t key_len,
                 const uint8_t *data, size_t data_len,
                 uint8_t *out) {
    uint8_t k_ipad[64], k_opad[64], tk[32];
    uint8_t temp[32];
    size_t i;
    if (key_len > 64) {
        SHA256_CTX tctx;
        sha256_init(&tctx);
        sha256_update(&tctx, key, key_len);
        sha256_final(&tctx, tk);
        key = tk;
        key_len = 32;
    }
    memset(k_ipad, 0x36, 64);
    memset(k_opad, 0x5c, 64);
    for (i=0;i<key_len;i++){
        k_ipad[i]^=key[i];
        k_opad[i]^=key[i];
    }
    SHA256_CTX ctx;
    sha256_init(&ctx);
    sha256_update(&ctx,k_ipad,64);
    sha256_update(&ctx,data,data_len);
    sha256_final(&ctx,temp);
    sha256_init(&ctx);
    sha256_update(&ctx,k_opad,64);
    sha256_update(&ctx,temp,32);
    sha256_final(&ctx,out);
}

void pbkdf2_sha256(const uint8_t *password,size_t pass_len,
                   const uint8_t *salt,size_t salt_len,
                   int iterations,uint8_t *out,size_t out_len){
    uint32_t i, j, k;
    uint8_t U[32], T[32];
    uint8_t salt_buf[128];
    for (i=1; out_len>0; i++) {
        memcpy(salt_buf,salt,salt_len);
        salt_buf[salt_len+0]=(i>>24)&0xff;
        salt_buf[salt_len+1]=(i>>16)&0xff;
        salt_buf[salt_len+2]=(i>>8)&0xff;
        salt_buf[salt_len+3]=i&0xff;
        hmac_sha256(password,pass_len,salt_buf,salt_len+4,U);
        memcpy(T,U,32);
        for (j=1;j<iterations;j++){
            hmac_sha256(password,pass_len,U,32,U);
            for (k=0;k<32;k++) T[k]^=U[k];
        }
        size_t l = out_len<32 ? out_len:32;
        memcpy(out,(uint8_t*)T,l);
        out+=l; out_len-=l;
    }
}

/* Similarity check (Levenshtein) */
int levenshtein(const char *s1, const char *s2){
    int len1=strlen(s1), len2=strlen(s2);
    int v0[len2+1], v1[len2+1];
    for(int i=0;i<=len2;i++) v0[i]=i;
    for(int i=0;i<len1;i++){
        v1[0]=i+1;
        for(int j=0;j<len2;j++){
            int cost=(s1[i]==s2[j])?0:1;
            int deletion=v0[j+1]+1;
            int insertion=v1[j]+1;
            int substitution=v0[j]+cost;
            int min=deletion<insertion?deletion:insertion;
            v1[j+1]=min<substitution?min:substitution;
        }
        for(int j=0;j<=len2;j++) v0[j]=v1[j];
    }
    return v0[len2];
}

double similarity_ratio(const char *s1, const char *s2){
    int maxlen=strlen(s1)>strlen(s2)?strlen(s1):strlen(s2);
    if(maxlen==0) return 1.0;
    int dist=levenshtein(s1,s2);
    return 1.0 - (double)dist/maxlen;
}

/* demo */
int main() {
    stdio_init_all();

    const char *old_pw="Summer2024!";
    const char *new_pw="Summer2025!";

    double sim = similarity_ratio(old_pw,new_pw);
    printf("Similarity ratio=%.2f\n", sim);
    if(sim > 0.7){
        printf("Rejected: too similar.\n");
        return 1;
    }

    // Salt
    const uint8_t salt[8]={'p','i','c','o','2','s','a','l'};
    uint8_t hash[32];
    pbkdf2_sha256((const uint8_t*)new_pw,strlen(new_pw),
                  salt,sizeof(salt),10000,hash,32);

    printf("Stored hash: ");
    for(int i=0;i<32;i++) printf("%02x",hash[i]);
    printf("\n");

    return 0;
}
