//! Dense rank mod p, IN PLACE, one u32 copy of the matrix (4 bytes/entry). Why: FLINT's nmod_mat_lu stores 8 B/entry
//! and peaks at ~2.2x the matrix (measured 2026-10-10: 18k -> 5.6 GB), which at the 27k rank-6 sector is ~13 GB on a
//! 16 GB box. Plain forward Gaussian elimination with row pivoting; rows split across threads at every pivot.
//! Multiplication mod p by Shoup's precomputed quotient (p < 2^31). FLINT (native/flint_rank) is the cross-check.
//!
//! Input "KTD1": magic, u64 nrows, u64 ncols, u64 p (little endian), then nrows*ncols u32 row-major entries < p.
//! Usage: ktdense <file> [threads]   -> one JSON line {"nrows","ncols","p","rank","nullity","seconds","threads"}
use std::fs::File;
use std::io::{BufReader, Read};
use std::time::Instant;

fn pow_mod(mut b: u64, mut e: u64, p: u64) -> u64 {
    let mut r = 1u64;
    b %= p;
    while e > 0 {
        if e & 1 == 1 { r = (r as u128 * b as u128 % p as u128) as u64; }
        b = (b as u128 * b as u128 % p as u128) as u64;
        e >>= 1;
    }
    r
}

#[inline(always)]
fn shoup(f: u64, p: u64) -> u64 { (((f as u128) << 64) / p as u128) as u64 }

#[inline(always)]
fn mul_shoup(f: u64, fs: u64, b: u64, p: u64) -> u64 {
    let q = ((fs as u128 * b as u128) >> 64) as u64;
    let r = f.wrapping_mul(b).wrapping_sub(q.wrapping_mul(p));
    if r >= p { r - p } else { r }
}

fn eliminate(rows: &mut [u32], piv: &[u32], n: usize, c: usize, p: u64) {
    for row in rows.chunks_mut(n) {
        let f = row[c] as u64;
        if f == 0 { continue; }
        let fs = shoup(f, p);
        for j in c..n {
            let t = mul_shoup(f, fs, piv[j] as u64, p);
            let a = row[j] as u64;
            row[j] = (if a >= t { a - t } else { a + p - t }) as u32;
        }
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 { eprintln!("usage: ktdense <file> [threads]"); std::process::exit(2); }
    let threads: usize = args.get(2).map(|s| s.parse().unwrap()).unwrap_or(1).max(1);
    let mut f = BufReader::new(File::open(&args[1]).expect("open"));
    let mut magic = [0u8; 4];
    f.read_exact(&mut magic).unwrap();
    assert_eq!(&magic, b"KTD1", "bad magic");
    let mut h = [0u8; 24];
    f.read_exact(&mut h).unwrap();
    let rd = |i: usize| u64::from_le_bytes(h[8 * i..8 * i + 8].try_into().unwrap());
    let (m, n, p) = (rd(0) as usize, rd(1) as usize, rd(2));
    assert!(p < (1u64 << 31), "p must be < 2^31");
    let mut a = vec![0u32; m * n];
    {
        let bytes = unsafe { std::slice::from_raw_parts_mut(a.as_mut_ptr() as *mut u8, m * n * 4) };
        f.read_exact(bytes).expect("short read");
    }
    if cfg!(target_endian = "big") { for v in a.iter_mut() { *v = u32::from_le(*v); } }
    assert!(a.iter().all(|&v| (v as u64) < p), "entry >= p");
    let t0 = Instant::now();
    let mut rank = 0usize;
    for c in 0..n {
        if rank == m { break; }
        let mut r = rank;
        while r < m && a[r * n + c] == 0 { r += 1; }
        if r == m { continue; }
        if r != rank {
            let (lo, hi) = a.split_at_mut(r * n);
            lo[rank * n..rank * n + n].swap_with_slice(&mut hi[..n]);
        }
        let inv = pow_mod(a[rank * n + c] as u64, p - 2, p);
        let is = shoup(inv, p);
        for j in c..n {
            a[rank * n + j] = mul_shoup(inv, is, a[rank * n + j] as u64, p) as u32;
        }
        let (head, tail) = a.split_at_mut((rank + 1) * n);
        let piv = &head[rank * n..rank * n + n];
        let below = m - rank - 1;
        if below > 0 {
            let per = ((below + threads - 1) / threads).max(1);
            if threads == 1 || below < 64 {
                eliminate(tail, piv, n, c, p);
            } else {
                std::thread::scope(|s| {
                    for chunk in tail.chunks_mut(per * n) {
                        s.spawn(move || eliminate(chunk, piv, n, c, p));
                    }
                });
            }
        }
        rank += 1;
    }
    println!("{{\"nrows\": {}, \"ncols\": {}, \"p\": {}, \"rank\": {}, \"nullity\": {}, \"seconds\": {:.2}, \"threads\": {}}}",
             m, n, p, rank, n - rank, t0.elapsed().as_secs_f64(), threads);
}
