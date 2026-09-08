//! Verify a saved recording, or prove that an older execution is rejected.
use anyhow::{bail, ensure, Context, Result};
use kitu_demo_game::replay::{ExecutionVersion, Session};
use serde_json::json;
use sha2::{Digest, Sha256};

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let file = args.next().context(
        "usage: cargo run --example replay-compatibility -- <recording.tsq> [--expect-incompatible]",
    )?;
    let expect_incompatible = match args.next().as_deref() {
        None => false,
        Some("--expect-incompatible") => true,
        Some(other) => bail!("unknown option {other}"),
    };
    ensure!(args.next().is_none(), "unexpected argument");
    let bytes = std::fs::read(&file).with_context(|| format!("read recording {file}"))?;
    let sha256 = hex::encode(Sha256::digest(&bytes));
    match (Session::decode(&bytes), expect_incompatible) {
        (Err(error), true) => {
            let diagnostic = format!("{error:#}");
            ensure!(
                diagnostic.contains("incompatible Arena execution version"),
                "recording failed for a different reason: {diagnostic}"
            );
            println!(
                "{}",
                json!({"status":"rejected-incompatible-execution", "recordingSha256":sha256,
                       "currentExecution":ExecutionVersion::current(), "diagnostic":diagnostic})
            );
        }
        (Ok(_), true) => bail!("recording unexpectedly matches the current execution"),
        (Err(error), false) => return Err(error),
        (Ok(session), false) => {
            let verified = session.verify()?;
            println!(
                "{}",
                json!({"status":"verified", "recordingSha256":sha256,
                       "currentExecution":ExecutionVersion::current(), "verification":verified})
            );
        }
    }
    Ok(())
}
