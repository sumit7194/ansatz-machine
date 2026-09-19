//! Reading the matrix Python writes, and writing the nullspace back.
//!
//! Both files are plain little-endian binary so the Python side needs nothing but numpy.
//!
//! Matrix  (.ktm):  b"KTM1" | u64 nrows | u64 ncols | u64 nnz | u64 p
//!                  | nnz x u32 row index | nnz x u32 col index | nnz x u32 value (already mod p)
//!
//! Result  (.kts):  b"KTS1" | u64 ncols | u64 nfree
//!                  | nfree x u64 free column | nfree x (ncols x u32) vector, one after another

use std::fs::File;
use std::io::{self, BufReader, BufWriter, Read, Write};
use std::path::Path;

/// A sparse matrix in coordinate form: entry t is (ri[t], ci[t]) = vi[t].
pub struct Matrix {
    pub nrows: usize,
    pub ncols: usize,
    pub p: u64,
    pub ri: Vec<u32>,
    pub ci: Vec<u32>,
    pub vi: Vec<u32>,
}

/// The nullspace basis: one dense vector per free column, free columns ascending.
pub struct Solution {
    pub free_cols: Vec<u64>,
    pub vectors: Vec<Vec<u32>>,
}

fn bad_data(msg: String) -> io::Error {
    io::Error::new(io::ErrorKind::InvalidData, msg)
}

fn read_u64(r: &mut impl Read) -> io::Result<u64> {
    let mut b = [0u8; 8];
    r.read_exact(&mut b)?;
    Ok(u64::from_le_bytes(b))
}

fn read_u32_vec(r: &mut impl Read, n: usize) -> io::Result<Vec<u32>> {
    let mut bytes = vec![0u8; n * 4];
    r.read_exact(&mut bytes)?;
    Ok(bytes
        .chunks_exact(4)
        .map(|c| u32::from_le_bytes([c[0], c[1], c[2], c[3]]))
        .collect())
}

pub fn read_matrix(path: &Path) -> io::Result<Matrix> {
    let mut r = BufReader::new(File::open(path)?);
    let mut magic = [0u8; 4];
    r.read_exact(&mut magic)?;
    if &magic != b"KTM1" {
        return Err(bad_data(format!("not a KTM1 matrix file (magic {magic:?})")));
    }
    let nrows = read_u64(&mut r)? as usize;
    let ncols = read_u64(&mut r)? as usize;
    let nnz = read_u64(&mut r)? as usize;
    let p = read_u64(&mut r)?;
    if p >= (1u64 << 31) {
        return Err(bad_data(format!("p = {p} does not fit the u32 value storage")));
    }
    let ri = read_u32_vec(&mut r, nnz)?;
    let ci = read_u32_vec(&mut r, nnz)?;
    let vi = read_u32_vec(&mut r, nnz)?;
    // Validate once here so the solver can index without re-checking.
    for t in 0..nnz {
        if ri[t] as usize >= nrows || ci[t] as usize >= ncols {
            return Err(bad_data(format!("entry {t} out of range: ({}, {})", ri[t], ci[t])));
        }
        if vi[t] as u64 >= p || vi[t] == 0 {
            return Err(bad_data(format!("entry {t} value {} not in 1..p", vi[t])));
        }
    }
    Ok(Matrix { nrows, ncols, p, ri, ci, vi })
}

pub fn write_result(path: &Path, ncols: usize, sol: &Solution) -> io::Result<()> {
    let mut w = BufWriter::new(File::create(path)?);
    w.write_all(b"KTS1")?;
    w.write_all(&(ncols as u64).to_le_bytes())?;
    w.write_all(&(sol.free_cols.len() as u64).to_le_bytes())?;
    for &f in &sol.free_cols {
        w.write_all(&f.to_le_bytes())?;
    }
    for v in &sol.vectors {
        for &x in v {
            w.write_all(&x.to_le_bytes())?;
        }
    }
    w.flush()
}
