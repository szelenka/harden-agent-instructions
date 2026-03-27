# Expected Audit Results: terraform-infra

A Terraform infrastructure repo with `.tf` files, modules, and environment-specific tfvars. No instruction file.

## Expected Phase 2 Assessment

- **Cold-start ready:** no (no instruction file exists)
- **Repo tier:** small
- **Instruction files found:** none
- **Build system:** Terraform (`.tf` files with `required_version >= 1.7`)
- **Verification commands:** `terraform fmt -check`, `terraform validate`, `terraform plan -var-file=environments/dev.tfvars`

## Expected Phase 3 Actions

The skill should create an AGENTS.md from scratch containing:
- Hard rules section
- Commands in fenced code blocks (`terraform fmt -check`, `terraform validate`, `terraform plan`)
- Key paths with roles (`main.tf` — provider and backend config, `variables.tf` — input variables, `modules/vpc/` — VPC module, `modules/ecs/` — ECS module, `environments/dev.tfvars` — environment values)
- Architecture description noting a modular Terraform setup with VPC and ECS

## Key Signals

- The skill must use `terraform` commands, NOT `make`, `npm`, `python`, or application-level build commands
- The audit should note the module structure and environment-specific tfvars pattern
- The done checklist should use `terraform validate` and `terraform plan` as canonical verification
- The skill must NOT invent unit tests, CI workflows, or application-level architecture — this is infrastructure code
- The skill should note the S3 backend configuration as relevant operational context
