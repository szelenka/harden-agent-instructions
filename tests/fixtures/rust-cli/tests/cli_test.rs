use assert_cmd::Command;

#[test]
fn test_help_flag() {
    Command::cargo_bin("rust-cli")
        .unwrap()
        .arg("--help")
        .assert()
        .success();
}
