use clap::Parser;

mod config;

#[derive(Parser)]
#[command(name = "rust-cli", about = "A small CLI tool")]
struct Cli {
    #[arg(short, long)]
    input: String,

    #[arg(short, long, default_value = "json")]
    format: String,
}

fn main() {
    let cli = Cli::parse();
    let cfg = config::load_defaults();
    println!("Processing {} with format {} (verbose={})", cli.input, cli.format, cfg.verbose);
}
