pub fn render_status(state: &str) -> &'static str {
    match state {
        "ok" => "ok",
        _ => "invalid",
    }
}
