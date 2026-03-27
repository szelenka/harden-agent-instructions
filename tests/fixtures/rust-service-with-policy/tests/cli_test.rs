use assert_cmd::Command;

#[test]
fn prints_ok_status() {
    let mut cmd = Command::cargo_bin("rust-service-with-policy").unwrap();
    cmd.assert().success();
}
