import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Optional

import yaml

from templify.logger import setup_logger

logger = setup_logger()


@dataclass
class Config:
    """Configuration class to hold settings."""

    base_path: str
    templify_repo_name: str
    email_users_repo_name: str
    templify_repo_path: str
    templates_repo_path: str

    @classmethod
    def load(cls):
        """Load configuration from YAML file."""
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config["paths"]["base_path"] = base_path

        return cls(
            base_path=base_path,
            templify_repo_name=config["paths"]["templify_repo_name"],
            email_users_repo_name=config["paths"]["email_users_repo_name"],
            templify_repo_path=os.path.join(
                base_path, config["paths"]["templify_repo_name"]
            ),
            templates_repo_path=os.path.join(
                base_path, config["paths"]["email_users_repo_name"]
            ),
        )


class GitOperations:
    """Class to handle Git operations."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def run_command(
        self, command: list, check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a git command safely."""
        try:
            return subprocess.run(
                command, cwd=self.repo_path, check=check, capture_output=True, text=True
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(command)}")
            logger.error(f"Error output: {e.stderr}")
            raise

    def get_current_branch(self) -> str:
        """Get the current git branch."""
        result = self.run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return result.stdout.strip()

    def switch_branch(self, base_branch: Optional[str], ticket_branch: str) -> None:
        """Switch to or create a new branch."""
        try:
            # Try to checkout existing branch
            self.run_command(["git", "checkout", ticket_branch])
            self.run_command(["git", "pull", "origin", ticket_branch], check=False)
        except subprocess.CalledProcessError:
            logger.info(
                f"Branch '{ticket_branch}' does not exist. Creating new branch..."
            )
            branch_out = base_branch or self.get_current_branch()
            if (
                input(f"Confirm branching out from {branch_out}? (y/n): ").lower()
                == "y"
            ):
                self.run_command(["git", "checkout", branch_out])
                self.run_command(["git", "pull", "origin", branch_out])
                self.run_command(["git", "checkout", "-b", ticket_branch])
                self.run_command(["git", "push", "-u", "origin", ticket_branch])
            else:
                logger.info(
                    f"Branch change aborted. Proceeding with {self.get_current_branch()}"
                )


class TemplateManager:
    """Class to manage template operations."""

    def __init__(self, config: Config):
        self.config = config
        self.git = GitOperations(config.templates_repo_path)

    def validate_html_content(self, html_content: str) -> None:
        """Validate the HTML content format."""
        pattern = r"^SET\s+@html_content\s*:=\s*['\"](.+?)['\"];$"
        if not re.match(pattern, html_content):
            raise ValueError(
                "Invalid HTML content format. Must be a valid SQL SET statement."
            )

    def update_template(self, template_path: str, html_content: str) -> None:
        """Update template content safely."""
        temp_path = f"{template_path}.tmp"
        try:
            with open(template_path, "r") as file:
                template_content = file.read()

            new_content = "\n".join(
                [
                    html_content if line.startswith("SET @html_content") else line
                    for line in template_content.split("\n")
                ]
            )

            # Write to temporary file first
            with open(temp_path, "w") as file:
                file.write(new_content)

            # If successful, replace original file
            os.replace(temp_path, template_path)
            logger.info(f"Successfully updated template: {template_path}")
        except Exception as e:
            logger.error(f"Failed to update template: {e}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise


def main():
    """Main function with enhanced error handling and logging."""
    try:
        config = Config.load()
        template_manager = TemplateManager(config)
        args = parse_arguments()

        # Get template details
        template_filename = args.template or get_template_selection(config)
        template_path = os.path.join(
            config.templates_repo_path, "templates", template_filename
        )

        # Handle branch operations
        if confirm_branch_switch():
            template_manager.git.switch_branch(args.base, args.ticket)

        # Update template
        html_content = get_updated_html_content(config)
        template_manager.validate_html_content(html_content)
        template_manager.update_template(template_path, html_content)

        # Handle git operations
        if confirm_action("Commit and push changes?"):
            template_manager.git.run_command(["git", "add", template_path])
            template_manager.git.run_command(
                ["git", "commit", "-m", "Update template HTML"]
            )
            template_manager.git.run_command(["git", "push"])

        if args.base and confirm_action("Create PR?"):
            template_manager.git.run_command(
                ["gh", "pr", "create", "--base", args.base]
            )

        logger.info("Template update completed successfully!")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise


def confirm_action(prompt: str) -> bool:
    """Utility function to confirm user actions."""
    return input(f"{prompt} (y/n): ").lower() == "y"


def confirm_branch_switch() -> bool:
    """Confirm before switching branches."""
    return confirm_action(
        "Warning: Any unsaved changes in your local branch will be permanently lost due to a hard reset.\n"
        "Continue?"
    )


def get_template_selection(config: Config) -> str:
    """Get template selection from user."""
    templates_dir = os.path.join(config.templates_repo_path, "templates")
    template_files = sorted(os.listdir(templates_dir))

    print("\nAvailable templates:")
    for idx, filename in enumerate(template_files, 1):
        print(f"{idx}. {filename}")

    while True:
        try:
            choice = int(input("\nEnter template number: "))
            if 1 <= choice <= len(template_files):
                return template_files[choice - 1]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def get_updated_html_content(config: Config) -> str:
    """Get updated HTML content from file."""
    content_path = os.path.join(config.templify_repo_path, "updated_template_set.sql")
    try:
        with open(content_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f"HTML content file not found: {content_path}")
        raise


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Update template with new html content."
    )
    parser.add_argument(
        "--template",
        help="The filename of the template to update. If not provided, will be prompted.",
    )
    parser.add_argument(
        "--base",
        help="The base branch to branch out and create PR to. If not provided, will be prompted.",
    )
    parser.add_argument(
        "--ticket",
        help="The git branch to switch to before updating the template. If not provided, will be prompted.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
