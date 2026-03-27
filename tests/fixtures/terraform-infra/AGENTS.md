# Agent Instructions

## Hard Rules

- Run `terraform fmt -check` before `terraform validate`
- Use `terraform plan -var-file=environments/<env>.tfvars` to preview changes
- Never run `terraform apply` without explicit approval
- Do not modify S3 backend configuration without approval
- Reference module outputs when adding dependencies between modules

## Key Paths

- `main.tf` — provider config (AWS ~> 5.0), S3 backend, Terraform >= 1.7 requirement
- `variables.tf` — root input variables (region, environment, instance_type)
- `modules/vpc/main.tf` — VPC resource definitions, outputs vpc_id
- `modules/ecs/main.tf` — ECS cluster, service, and Fargate task definitions
- `environments/dev.tfvars` — dev environment variable values

## Architecture

Modular Terraform infrastructure with separate VPC and ECS modules. Root configuration declares providers and backend, modules handle AWS resources. Environment-specific tfvars files provide runtime values.

## Verification

```bash
terraform fmt -check
terraform validate
terraform plan -var-file=environments/dev.tfvars
```

## Done Checklist

- [ ] `terraform fmt -check` passes
- [ ] `terraform validate` passes
- [ ] `terraform plan` generates without errors
- [ ] Module outputs referenced correctly if dependencies added
- [ ] Backend configuration unchanged unless approved

## Codebase Evolution

When you discover non-obvious patterns or repeated mistakes, add them to this file in the same session. Update Hard Rules or Key Paths only when the addition prevents a real failure mode.
