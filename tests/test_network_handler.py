"""Unit tests for NetworkOpsTool and Antigravity Skill integration."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import google.antigravity.network_handler as handler_module
from google.antigravity.network_handler import NetworkOpsTool, network_ops_skill


class TestNetworkOpsTool(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_path = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_network_ops_skill_registration(self):
        """Verify skill attributes and registered tools."""
        self.assertEqual(network_ops_skill.name, "network_ops_automation")
        self.assertIn("generate_ansible_playbook", network_ops_skill._tools)
        self.assertIn("stage_git_pull_request", network_ops_skill._tools)

    def test_create_automation_code(self):
        """Verify playbook creation in designated directory."""
        tool = NetworkOpsTool(repo_path=self.repo_path)
        sample_content = "---\n- name: Test Playbook\n  hosts: all\n"
        res = tool.create_automation_code("test_playbook.yml", sample_content)

        expected_path = os.path.join(self.repo_path, "ansible", "playbooks", "test_playbook.yml")
        self.assertTrue(os.path.exists(expected_path))
        with open(expected_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), sample_content)
        self.assertIn("Successfully generated playbook draft", res)

    def test_create_automation_code_path_traversal_guard(self):
        """Verify that path traversal attempts are safely contained to playbooks dir."""
        tool = NetworkOpsTool(repo_path=self.repo_path)
        sample_content = "---\n# traversal test"
        tool.create_automation_code("../../outside.yml", sample_content)

        contained_path = os.path.join(self.repo_path, "ansible", "playbooks", "outside.yml")
        self.assertTrue(os.path.exists(contained_path))
        self.assertFalse(os.path.exists(os.path.join(self.repo_path, "outside.yml")))

    def test_push_and_open_pr_with_mocked_git_and_github(self):
        """Verify git operations and GitHub PR creation."""
        mock_git = MagicMock()
        mock_repo = MagicMock()
        mock_git.Repo.return_value = mock_repo
        mock_head = MagicMock()
        mock_repo.create_head.return_value = mock_head
        mock_repo.heads = {}
        mock_remote = MagicMock()
        mock_remote.name = "origin"
        mock_repo.remotes = [mock_remote]
        mock_repo.remote.return_value = mock_remote

        with patch.object(handler_module, "git", mock_git):
            tool = NetworkOpsTool(repo_path=self.repo_path, github_repo_name="org/net-infra")
            tool.gh_client = MagicMock()
            mock_gh_repo = MagicMock()
            mock_pr = MagicMock()
            mock_pr.html_url = "https://github.com/org/net-infra/pull/42"
            mock_gh_repo.create_pull.return_value = mock_pr
            tool.gh_client.get_repo.return_value = mock_gh_repo

            result = tool.push_and_open_pr(
                branch_name="netops/test-branch",
                commit_message="feat: test network change",
                pr_title="PR: Network change",
                base_branch="main",
            )

            mock_repo.create_head.assert_called_with("netops/test-branch")
            mock_head.checkout.assert_called_once()
            mock_repo.git.add.assert_called_with(A=True)
            mock_repo.index.commit.assert_called_with("feat: test network change")
            mock_remote.push.assert_called_with("netops/test-branch")
            mock_gh_repo.create_pull.assert_called_once()
            self.assertIn("https://github.com/org/net-infra/pull/42", result)


if __name__ == "__main__":
    unittest.main()
