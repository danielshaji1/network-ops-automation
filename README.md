# Antigravity Network Operations Automation (HITL GitOps)

An AI Agent framework built with the **Google Antigravity SDK**, translating plain-text network intent into declarative Ansible playbooks and gating infrastructure deployments behind a **Human-in-the-Loop (HITL)** GitHub Actions workflow.

---

## Architectural Overview

```
                                              +---------------------------------------+
                                              |       Network Engineer Intent         |
                                              |  "Configure VLAN 10 & 20 on edge"     |
                                              +---------------------------------------+
                                                                  |
                                                                  v
+-------------------------------------------------------------------------------------------------------------------------+
| Antigravity AI Agent Framework                                                                                          |
|                                                                                                                         |
|   +----------------------------------+        +-----------------------------------+                                     |
|   |  Skill Definition                |        |  Context & Security Boundaries    |                                     |
|   |  - skills/network_ops.yaml       | -----> |  - Allowlist: ./ansible/*         |                                     |
|   |  - .agents/skills/SKILL.md       |        |  - Never direct SSH / CLI         |                                     |
|   +----------------------------------+        +-----------------------------------+                                     |
|                                                                  |                                                      |
|                                                                  v                                                      |
|   +--------------------------------------------------------------------------------+                                    |
|   |  Network Context Engine (google/antigravity/network_handler.py)                |                                    |
|   |  - generate_ansible_playbook  -> Generates idempotent YAML to ansible/playbooks/ |                                  |
|   |  - stage_git_pull_request    -> Creates feature branch & opens GitHub PR       |                                    |
|   +--------------------------------------------------------------------------------+                                    |
+-------------------------------------------------------------------------------------------------------------------------+
                                                                  |
                                                                  v
                                                 +----------------------------------+
                                                 | GitHub Repository (Branch + PR)  |
                                                 +----------------------------------+
                                                                  |
                                                                  v
+-------------------------------------------------------------------------------------------------------------------------+
| GitHub Actions Human Gate (.github/workflows/hitl_deploy.yml)                                                           |
|                                                                                                                         |
|   [On Pull Request]                                                                                                     |
|     1. ansible-lint validation                                                                                          |
|     2. Dry-Run Simulation: `ansible-playbook --check` (No live state mutation)                                          |
|                                                                                                                         |
|   [Human Review & Gate]                                                                                                 |
|     3. Certified Network Engineer verifies dry-run diff & merges PR                                                     |
|                                                                                                                         |
|   [On Merge to Main]                                                                                                    |
|     4. Live Production Deployment via self-hosted internal runner                                                        |
+-------------------------------------------------------------------------------------------------------------------------+
```

---

## Project Structure

```
network-ops-automation/
├── .agents/
│   └── skills/
│       └── network-ops-automation/
│           └── SKILL.md                 # Native Antigravity CLI/IDE/SDK Skill
├── .github/
│   └── workflows/
│       └── hitl_deploy.yml             # GitHub Actions Human-in-the-Loop pipeline
├── ansible/
│   ├── ansible.cfg                     # Network CLI connection settings
│   ├── inventory.ini                   # Target network devices (Cisco, Arista)
│   ├── group_vars/
│   │   └── all.yml                     # Variable placeholders for secrets
│   └── playbooks/
│       └── deploy_vlans.yml            # Declarative, idempotent playbook
├── google/
│   └── antigravity/
│       ├── __init__.py                 # Skill definitions & SDK classes
│       └── network_handler.py          # NetworkOpsTool handler implementation
├── skills/
│   └── network_ops.yaml                # Custom YAML skill specification
├── tests/
│   └── test_network_handler.py         # Unit tests for handler & safety bounds
├── agent_runner.py                     # Demo CLI runner for intent-to-PR pipeline
├── requirements.txt                    # Python dependencies
└── README.md
```

---

## Safety & Governance Rules

1. **Zero Direct Execution**: The agent never connects via SSH or executes direct CLI commands against network hardware.
2. **Idempotent Code**: All tasks use standard collections (`cisco.ios`, `arista.eos`) declaring desired states (`state: merged`).
3. **Secret Hygiene**: Passwords and community strings strictly use environment variable lookups and Ansible Vault placeholders.
4. **Human Gate**: Pull Requests trigger dry-run check mode (`--check`); deployments to production only occur after human approval and merge.

---

## Getting Started

### 1. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible-galaxy collection install cisco.ios arista.eos ansible.netcommon
```

### 2. Environment Variables

```bash
export GITHUB_TOKEN="ghp_your_personal_access_token"
export GITHUB_REPOSITORY="your-org/network-infrastructure"
export ANSIBLE_NET_USER="netops_admin"
export ANSIBLE_NET_PASSWORD="your_secure_password"
```

### 3. Run the Demonstration Pipeline

```bash
python3 agent_runner.py \
  --intent "Provision edge access VLAN 10 and 20" \
  --filename "deploy_edge_vlans.yml" \
  --branch "netops/vlan-provisioning-10" \
  --pr-title "NetOps: Deploy Edge VLANs 10 and 20"
```

### 4. Run Unit Tests

```bash
pytest -v
```
