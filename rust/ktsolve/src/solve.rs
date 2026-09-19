//! The solver: split into independent blocks, eliminate each, read off the nullspace.
//!
//! A line-for-line port of scripts/_kt_fast.py (the numba reference), which it must match exactly.
//! See that file's docstring for why the free-column-indexed basis is unique -- that uniqueness is
//! what turns "does the Rust port work?" into an equality test.
//!
//! The one invariant the kernel leans on: when column c is processed, every row not yet used as a
//! pivot has zeros in all columns < c. So "row r contains c" is just `row.cols[0] == c`, and every
//! pivot row ends up in echelon form, starting at its own pivot column.

use crate::io::{Matrix, Solution};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use std::thread;
use std::time::Instant;

/// One sparse row: parallel arrays, columns strictly ascending. 8 bytes per nonzero.
#[derive(Default, Clone)]
struct Row {
    cols: Vec<u32>,
    vals: Vec<u32>,
}

/// One independent block, in local indices (0..nr rows, 0..nc columns), as sparse rows.
/// Owned by whichever worker solves it, so its memory is freed the moment it is done.
struct Block {
    gcols: Vec<u32>, // local column -> global column, ascending
    rows: Vec<Row>,
}

/// What solving one block produces.
struct BlockOut {
    gcols: Vec<u32>,
    free_local: Vec<usize>,
    v: Vec<u64>, // nc x nfree, row-major: v[k * nfree + i]
    peak: usize,
}

pub struct Stats {
    pub nnz_in: usize,
    pub blocks: usize,
    pub largest_block_cols: usize,
    pub peak_nnz_max: usize,
    pub peak_nnz_sum: usize,
    pub nullity: usize,
    pub seconds: f64,
}

fn powmod(mut a: u64, mut e: u64, p: u64) -> u64 {
    let mut r = 1u64;
    a %= p;
    while e > 0 {
        if e & 1 == 1 {
            r = r * a % p;
        }
        a = a * a % p;
        e >>= 1;
    }
    r
}

// ------------------------------------------------------------------ union-find

fn find(parent: &mut [u32], mut x: u32) -> u32 {
    while parent[x as usize] != x {
        let gp = parent[parent[x as usize] as usize];
        parent[x as usize] = gp; // path halving
        x = gp;
    }
    x
}

/// Split the matrix into independent blocks = connected components of the bipartite
/// row/column graph. Columns with no entries at all are returned separately: each is a free
/// column whose basis vector is simply e_j.
///
/// MEMORY: the coordinate arrays are taken BY VALUE and dropped as soon as the rows are built,
/// and rows are filled directly (a counting pass sizes each one exactly) -- no intermediate
/// tuple list and no CSR copy. Peak here is ~20 bytes per nonzero, then 8 once the input is gone.
fn split_blocks(nr: usize, nc: usize, ri: Vec<u32>, ci: Vec<u32>, vi: Vec<u32>) -> (Vec<Block>, Vec<usize>) {
    let mut parent: Vec<u32> = (0..(nr + nc) as u32).collect();
    for (&r, &c) in ri.iter().zip(&ci) {
        let a = find(&mut parent, r);
        let b = find(&mut parent, nr as u32 + c);
        if a != b {
            parent[a as usize] = b;
        }
    }

    // Give each component a dense block number, in order of first appearance among columns.
    let mut has_entry = vec![false; nc];
    for &c in &ci {
        has_entry[c as usize] = true;
    }
    let mut block_of_root = vec![u32::MAX; nr + nc];
    let mut gcols: Vec<Vec<u32>> = Vec::new();
    let mut col_local = vec![0u32; nc];
    let mut empty = Vec::new();
    for c in 0..nc {
        if !has_entry[c] {
            empty.push(c);
            continue;
        }
        let root = find(&mut parent, (nr + c) as u32) as usize;
        if block_of_root[root] == u32::MAX {
            block_of_root[root] = gcols.len() as u32;
            gcols.push(Vec::new());
        }
        let b = block_of_root[root] as usize;
        col_local[c] = gcols[b].len() as u32; // columns arrive ascending, so local order = global order
        gcols[b].push(c as u32);
    }
    drop(has_entry);

    // Each non-empty row: its block, its local number, and its length.
    let nb = gcols.len();
    let mut row_len = vec![0u32; nr];
    for &r in &ri {
        row_len[r as usize] += 1;
    }
    let mut row_block = vec![u32::MAX; nr];
    let mut row_local = vec![0u32; nr];
    let mut rows: Vec<Vec<Row>> = vec![Vec::new(); nb];
    for r in 0..nr {
        if row_len[r] == 0 {
            continue;
        }
        let b = block_of_root[find(&mut parent, r as u32) as usize] as usize;
        row_block[r] = b as u32;
        row_local[r] = rows[b].len() as u32;
        let n = row_len[r] as usize;
        rows[b].push(Row { cols: Vec::with_capacity(n), vals: Vec::with_capacity(n) });
    }
    drop((parent, block_of_root, row_len));

    for ((&r, &c), &v) in ri.iter().zip(&ci).zip(&vi) {
        let row = &mut rows[row_block[r as usize] as usize][row_local[r as usize] as usize];
        row.cols.push(col_local[c as usize]);
        row.vals.push(v);
    }
    drop((ri, ci, vi, row_block, row_local, col_local)); // the input is gone from here on

    // The kernel needs strictly ascending columns in every row. Input written by _kt_coo already
    // is; anything else is sorted here. A repeated (row, column) is malformed input: stop loudly.
    for row in rows.iter_mut().flatten() {
        if !row.cols.windows(2).all(|w| w[0] < w[1]) {
            let mut idx: Vec<usize> = (0..row.cols.len()).collect();
            idx.sort_unstable_by_key(|&i| row.cols[i]);
            row.cols = idx.iter().map(|&i| row.cols[i]).collect();
            row.vals = idx.iter().map(|&i| row.vals[i]).collect();
            if !row.cols.windows(2).all(|w| w[0] < w[1]) {
                panic!("duplicate (row, column) entry in the input matrix");
            }
        }
    }

    let blocks = gcols
        .into_iter()
        .zip(rows)
        .map(|(g, r)| Block { gcols: g, rows: r })
        .collect();
    (blocks, empty)
}

// ------------------------------------------------------------------ one block

fn eliminate_block(b: Block, p: u64) -> BlockOut {
    let nc = b.gcols.len();
    let gcols = b.gcols;
    let mut rows = b.rows; // taken over: the block's only copy
    let nr = rows.len();

    // column -> rows that may contain it. Entries can go stale; they are checked on use.
    let mut cm: Vec<Vec<u32>> = vec![Vec::new(); nc];
    for (r, row) in rows.iter().enumerate() {
        for &c in &row.cols {
            cm[c as usize].push(r as u32);
        }
    }

    let mut used = vec![false; nr];
    let mut pivrow = vec![u32::MAX; nc];
    let mut nnz: usize = rows.iter().map(|r| r.cols.len()).sum();
    let mut peak = nnz;
    let mut cand: Vec<u32> = Vec::new();
    // Scratch buffers reused for every row update, so the hot loop does not allocate.
    let mut outc: Vec<u32> = Vec::new();
    let mut outv: Vec<u32> = Vec::new();

    for c in 0..nc {
        let cu = c as u32;
        // Take the list out of cm: we own it now, and it is freed at the end of this iteration.
        let list = std::mem::take(&mut cm[c]);
        cand.clear();
        let mut best = u32::MAX;
        let mut best_len = usize::MAX;
        for &r in &list {
            if used[r as usize] {
                continue;
            }
            let row = &rows[r as usize];
            if row.cols.first() != Some(&cu) {
                continue;
            }
            cand.push(r);
            if row.cols.len() < best_len {
                best_len = row.cols.len();
                best = r;
            }
        }
        drop(list);
        if best == u32::MAX {
            continue; // free column
        }

        // Normalise the pivot row to 1 at column c. We move it OUT of `rows` while we use it, so
        // we can read it and modify other rows at the same time -- Rust will not let us hold a
        // reference into `rows` while also mutating another element of `rows`.
        let mut prow = std::mem::take(&mut rows[best as usize]);
        let inv = powmod(prow.vals[0] as u64, p - 2, p);
        if inv != 1 {
            for v in prow.vals.iter_mut() {
                *v = ((*v as u64) * inv % p) as u32;
            }
        }
        let lp = prow.cols.len();

        for &r in &cand {
            if r == best {
                continue;
            }
            let row = &mut rows[r as usize];
            if row.cols.first() != Some(&cu) {
                continue; // duplicate entry, already eliminated
            }
            let f = row.vals[0] as u64;
            let lr = row.cols.len();
            outc.clear();
            outv.clear();
            let (mut i, mut j) = (1usize, 1usize);
            while i < lr || j < lp {
                if j >= lp || (i < lr && row.cols[i] < prow.cols[j]) {
                    outc.push(row.cols[i]);
                    outv.push(row.vals[i]);
                    i += 1;
                } else if i >= lr || prow.cols[j] < row.cols[i] {
                    let t = f * prow.vals[j] as u64 % p;
                    if t != 0 {
                        let col = prow.cols[j];
                        outc.push(col);
                        outv.push((p - t) as u32);
                        cm[col as usize].push(r); // row r gained column `col`
                    }
                    j += 1;
                } else {
                    let t = f * prow.vals[j] as u64 % p;
                    let val = (row.vals[i] as u64 + p - t) % p;
                    if val != 0 {
                        outc.push(row.cols[i]);
                        outv.push(val as u32);
                    }
                    i += 1;
                    j += 1;
                }
            }
            nnz = nnz + outc.len() - lr;
            // Swap the new contents in; the old vectors become next iteration's scratch space.
            std::mem::swap(&mut row.cols, &mut outc);
            std::mem::swap(&mut row.vals, &mut outv);
        }

        rows[best as usize] = prow; // put the pivot row back
        used[best as usize] = true;
        pivrow[c] = best;
        peak = peak.max(nnz);
    }

    // Back-substitution. For each free column f the basis vector has v[f] = 1, v[other free] = 0,
    // and each pivot variable, processed from the last column to the first, is minus the dot
    // product of its (normalised) pivot row with the entries already determined.
    let free_local: Vec<usize> = (0..nc).filter(|&c| pivrow[c] == u32::MAX).collect();
    let nf = free_local.len();
    let mut v = vec![0u64; nc * nf];
    for (i, &f) in free_local.iter().enumerate() {
        v[f * nf + i] = 1;
    }
    for c in (0..nc).rev() {
        if pivrow[c] == u32::MAX {
            continue;
        }
        let row = &rows[pivrow[c] as usize];
        for t in 1..row.cols.len() {
            let k = row.cols[t] as usize;
            let a = row.vals[t] as u64;
            for i in 0..nf {
                let w = v[k * nf + i];
                if w != 0 {
                    v[c * nf + i] = (v[c * nf + i] + p - a * w % p) % p;
                }
            }
        }
    }
    BlockOut { gcols, free_local, v, peak }
}

// ------------------------------------------------------------------ driver

pub fn nullspace(m: Matrix, threads: usize) -> (Solution, Stats) {
    let t0 = Instant::now();
    let (nr, ncols, p, nnz_in) = (m.nrows, m.ncols, m.p, m.ri.len());
    let (blocks, empty) = split_blocks(nr, ncols, m.ri, m.ci, m.vi);
    let nb = blocks.len();
    let largest = blocks.iter().map(|b| b.gcols.len()).max().unwrap_or(0);

    // Largest blocks first, so the long ones start early and small ones fill the gaps.
    let mut order: Vec<usize> = (0..nb).collect();
    order.sort_by_key(|&b| std::cmp::Reverse(blocks[b].gcols.len()));

    // Each block sits in a slot a worker TAKES it from: the worker then owns it, and it is freed
    // as soon as it is solved. Workers pull the next block number from a shared counter;
    // `thread::scope` lets them borrow the slots because it guarantees they finish first.
    let slots: Vec<Mutex<Option<Block>>> = blocks.into_iter().map(|b| Mutex::new(Some(b))).collect();
    let next = AtomicUsize::new(0);
    let results: Vec<Mutex<Option<BlockOut>>> = (0..nb).map(|_| Mutex::new(None)).collect();
    thread::scope(|s| {
        for _ in 0..threads.min(nb).max(1) {
            s.spawn(|| loop {
                let i = next.fetch_add(1, Ordering::Relaxed);
                if i >= order.len() {
                    break;
                }
                let b = order[i];
                let block = slots[b].lock().unwrap().take().expect("each block is taken once");
                let out = eliminate_block(block, p);
                *results[b].lock().unwrap() = Some(out);
            });
        }
    });

    // Assemble one dense global vector per free column.
    let mut pairs: Vec<(u64, Vec<u32>)> = Vec::new();
    for &j in &empty {
        let mut e = vec![0u32; ncols];
        e[j] = 1;
        pairs.push((j as u64, e));
    }
    let (mut peak_max, mut peak_sum) = (0usize, 0usize);
    for cell in results {
        let out = cell.into_inner().unwrap().expect("every block is solved");
        peak_max = peak_max.max(out.peak);
        peak_sum += out.peak;
        let nf = out.free_local.len();
        for (i, &fl) in out.free_local.iter().enumerate() {
            let mut g = vec![0u32; ncols];
            for (k, &gc) in out.gcols.iter().enumerate() {
                g[gc as usize] = out.v[k * nf + i] as u32;
            }
            pairs.push((out.gcols[fl] as u64, g));
        }
    }
    pairs.sort_by_key(|pr| pr.0);

    let stats = Stats {
        nnz_in,
        blocks: nb,
        largest_block_cols: largest,
        peak_nnz_max: peak_max,
        peak_nnz_sum: peak_sum,
        nullity: pairs.len(),
        seconds: t0.elapsed().as_secs_f64(),
    };
    let (free_cols, vectors) = pairs.into_iter().unzip();
    (Solution { free_cols, vectors }, stats)
}
