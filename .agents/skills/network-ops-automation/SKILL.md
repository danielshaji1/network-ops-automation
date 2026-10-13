---
name: network-ops-automation
description: >-
  Generates multi-vendor Ansible network playbooks from intent, restricts execution to automation paths, and stages changes to GitHub via pull requests for human review.
---

# Network Operations Automation Skill

This skill governs the translation of user intent into declarative, multi-vendor Ansible playbooks, ensuring safe execution boundaries and human-in-the-loop review.

## Context Boundaries & Allowlist

The agent must only read and write within the following automation paths:
- `./ansible/playbooks/*`
- `./ansible/group_vars/*`

Direct execution or remote SSH connections to switches/routers from the agent are strictly prohibited.

## Critical Rules

1. **No Direct Execution**: Never attempt to run ad-hoc commands against physical infrastructure. All changes must be codified into Ansible playbooks.
2. **Idempotence**: Playbook tasks must use standard vendor collections (e.g. `cisco.ios`, `arista.eos`, `junipernetworks.junos`) and declare desired state idempotently.
3. **Secret Hygiene**: Sensitive credentials (SSH passwords, SNMP community strings, API keys) must reference Ansible variables or Vault, never hardcoded plaintext.
4. **Human Gate Enforcement**: Changes must be staged to a dedicated feature branch and submitted as a GitHub Pull Request for peer validation and dry-run linting before any merge.

## Operational Workflow

1. **Parse Intent**: Analyze user network change intent (e.g. VLAN provisioning, BGP peering, ACL modification).
2. **Generate Playbook**: Formulate the declarative YAML playbook in `ansible/playbooks/<change_name>.yml`.
3. **Stage Pull Request**: Run `NetworkOpsTool.push_and_open_pr()` or the git stage helper to create a feature branch (`netops/<change_name>`) and open a GitHub PR.
4. **CI/CD Validation**: The GitHub Actions workflow (`hitl_deploy.yml`) runs `ansible-lint` and check mode dry-runs against internal testbeds.
