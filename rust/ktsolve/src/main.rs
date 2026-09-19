//! ktsolve -- nullspace over GF(p) of a sparse matrix, for the Killing-tensor solver.
//!
//!     ktsolve --input m.ktm --output ns.kts [--threads N]
//!
//! Python (scripts/_kt_rust.py) writes the matrix, runs this as a separate process, and reads the
//! nullspace back. A separate process keeps the heavy solve out of Python's memory, and can be
//! paused and resumed from outside (kill -STOP / kill -CONT) without either side noticing.
//! A one-line JSON summary goes to stdout.

mod io;
mod solve;

use std::path::PathBuf;
use std::process::exit;

struct Args {
    input: PathBuf,
    output: PathBuf,
    threads: usize,
}

fn parse_args() -> Result<Args, String> {
    let mut input = None;
    let mut output = None;
    let mut threads = 1usize;
    let mut it = std::env::args().skip(1);
    while let Some(a) = it.next() {
        match a.as_str() {
            "--input" => input = it.next().map(PathBuf::from),
            "--output" => output = it.next().map(PathBuf::from),
            "--threads" => {
                let v = it.next().ok_or("--threads needs a value")?;
                threads = v.parse().map_err(|e| format!("bad --threads {v:?}: {e}"))?;
            }
            other => return Err(format!("unknown argument {other:?}")),
        }
    }
    Ok(Args {
        input: input.ok_or("--input is required")?,
        output: output.ok_or("--output is required")?,
        threads: threads.max(1),
    })
}

fn main() {
    let args = parse_args().unwrap_or_else(|e| {
        eprintln!("ktsolve: {e}");
        exit(2)
    });
    let m = io::read_matrix(&args.input).unwrap_or_else(|e| {
        eprintln!("ktsolve: reading {}: {e}", args.input.display());
        exit(1)
    });
    let (nrows, ncols) = (m.nrows, m.ncols);
    let (sol, st) = solve::nullspace(m, args.threads); // the solver takes the matrix and frees it
    io::write_result(&args.output, ncols, &sol).unwrap_or_else(|e| {
        eprintln!("ktsolve: writing {}: {e}", args.output.display());
        exit(1)
    });
    println!(
        "{{\"nrows\":{},\"ncols\":{},\"nnz_in\":{},\"blocks\":{},\"largest_block_cols\":{},\
         \"peak_nnz_max\":{},\"peak_nnz_sum\":{},\"nullity\":{},\"threads\":{},\"seconds\":{:.3}}}",
        nrows, ncols, st.nnz_in, st.blocks, st.largest_block_cols, st.peak_nnz_max,
        st.peak_nnz_sum, st.nullity, args.threads, st.seconds
    );
}
