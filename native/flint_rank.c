/* Dense rank mod p of a matrix on disk, via FLINT (nmod_mat_lu, in place: ONE copy in memory).
 * File format "KTD1": 4-byte magic, then little-endian u64 nrows, u64 ncols, u64 p, then nrows*ncols u32 entries (row-major, < p).
 * Usage: flint_rank <file> [threads]      prints one JSON line: {"nrows":..,"ncols":..,"p":..,"rank":..,"nullity":..,"seconds":..}
 * nullity = ncols - rank (the dimension of the right kernel). Rank mod p never exceeds the rank over Q of an integer
 * matrix reducing to it, and a sampled (row-compressed) matrix never exceeds the full one: so this is a rigorous LOWER
 * bound on the true rank, i.e. an UPPER bound on the true nullity. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <flint/flint.h>
#include <flint/nmod_mat.h>

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: flint_rank <file> [threads]\n"); return 2; }
    int threads = argc > 2 ? atoi(argv[2]) : 1;
    flint_set_num_threads(threads);
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("open"); return 2; }
    char magic[4]; uint64_t hdr[3];
    if (fread(magic, 1, 4, f) != 4 || memcmp(magic, "KTD1", 4) || fread(hdr, 8, 3, f) != 3) { fprintf(stderr, "bad header\n"); return 2; }
    slong m = (slong) hdr[0], n = (slong) hdr[1]; ulong p = (ulong) hdr[2];
    nmod_mat_t A; nmod_mat_init(A, m, n, p);
    uint32_t *buf = malloc(sizeof(uint32_t) * (size_t) n);
    for (slong i = 0; i < m; i++) {
        if (fread(buf, 4, (size_t) n, f) != (size_t) n) { fprintf(stderr, "short read at row %ld\n", (long) i); return 2; }
        for (slong j = 0; j < n; j++) {
            if (buf[j] >= p) { fprintf(stderr, "entry >= p at (%ld,%ld)\n", (long) i, (long) j); return 2; }
            nmod_mat_entry(A, i, j) = buf[j];
        }
    }
    free(buf); fclose(f);
    slong *P = flint_malloc(sizeof(slong) * m);
    struct timespec t0, t1; clock_gettime(CLOCK_MONOTONIC, &t0);
    slong r = nmod_mat_lu(P, A, 0);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double sec = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    printf("{\"nrows\": %ld, \"ncols\": %ld, \"p\": %lu, \"rank\": %ld, \"nullity\": %ld, \"seconds\": %.2f, \"threads\": %d}\n",
           (long) m, (long) n, p, (long) r, (long) (n - r), sec, threads);
    flint_free(P); nmod_mat_clear(A);
    return 0;
}
