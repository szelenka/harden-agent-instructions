use serde::Deserialize;

#[derive(Deserialize)]
pub struct AppConfig {
    pub verbose: bool,
}

pub fn load_defaults() -> AppConfig {
    AppConfig { verbose: false }
}
