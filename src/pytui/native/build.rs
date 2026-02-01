// When building with `cargo test --features test`, link the test binary with libpython
// so PyO3 symbols resolve. Extension-module builds (maturin) do not use this.
fn main() {
    #[cfg(feature = "test")]
    {
        let config = pyo3_build_config::get();
        if let Some(ref lib_dir) = config.lib_dir {
            println!("cargo:rustc-link-search=native={}", lib_dir);
        }
        if let Some(ref lib_name) = config.lib_name {
            println!("cargo:rustc-link-lib={}", lib_name);
        }
    }
}
