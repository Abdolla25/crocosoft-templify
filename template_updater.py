import argparse
import os
import re
import subprocess

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLIFY_REPO_NAME = "templify"
TEMPLIFY_REPO_PATH = os.path.join(BASE_PATH, TEMPLIFY_REPO_NAME)
EMAIL_USERS_REPO_NAME = "EmailUsersPackageBuilder"
TEMPLATES_REPO_PATH = os.path.join(BASE_PATH, EMAIL_USERS_REPO_NAME)


def main():
    # Parse command line arguments
    args = parse_arguments()
    template_filename = args.template or input(
        "Enter template filename (or press enter to skip): "
    )
    base_branch = args.base or input(
        "Enter base branch to branching out and process PR (or press enter to skip): "
    )
    ticket_branch = args.ticket or input(
        "Enter ticket branch -existing or new- (or press enter to skip): "
    )

    # Handle branch switch
    response = input(
        "Warning: Any unsaved changes in your local branch will be permanently lost due to a hard reset.\n"
        "Continue (y/n): "
    ).lower()
    if response != "y":
        print("Operation aborted. No changes have been made.")
        return
    switch_branch_if_needed(base_branch, ticket_branch)

    # Get template filename
    template_filename = get_template_filename(template_filename)
    template_filepath = os.path.join(
        TEMPLATES_REPO_PATH, "templates", template_filename
    )

    # Get the updated HTML content
    updated_html_set_statement = get_updated_html_set_statement()

    # Update the template
    validate_html_content_format(updated_html_set_statement)
    update_template_content(template_filepath, updated_html_set_statement)

    # Commit and push changes
    print("Summary of changes:")
    print(f"Template: {template_filename}")
    print(f"Committing and pushing changes to ticket branch: {ticket_branch}")
    input("Continue (y/n): ").lower() == "y" and push_changes(template_filepath)

    # Create PR
    print(f"Creating PR to base branch: {base_branch}")
    input("Continue (y/n): ").lower() == "y" and create_pr(base_branch)

    # Clean up
    print("Cleaning up...")
    subprocess.run(["rm", "-f", "updated_template_set.sql"], cwd=TEMPLIFY_REPO_PATH)


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


def switch_branch_if_needed(base_branch, ticket_branch):
    """Switch to a different git branch if needed."""
    subprocess.run(["git", "reset", "--hard"], cwd=TEMPLATES_REPO_PATH)
    subprocess.run(["git", "fetch"], cwd=TEMPLATES_REPO_PATH)
    subprocess.run(["git", "pull"], cwd=TEMPLATES_REPO_PATH)

    current_branch = get_current_git_branch()
    ticket_branch = ticket_branch or current_branch
    if current_branch != ticket_branch:
        print(f"Current branch: {current_branch}. Switching to {ticket_branch}")
        checkout_branch(base_branch, ticket_branch)


def get_current_git_branch():
    """Get the current git branch."""
    return (
        subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=TEMPLATES_REPO_PATH
        )
        .decode("utf-8")
        .strip()
    )


def checkout_branch(base_branch, ticket_branch):
    try:
        subprocess.run(
            ["git", "checkout", ticket_branch], cwd=TEMPLATES_REPO_PATH, check=True
        )
        subprocess.run(
            ["git", "pull", "origin", ticket_branch], cwd=TEMPLATES_REPO_PATH
        )
    except subprocess.CalledProcessError:
        print(f"The branch '{ticket_branch}' does not exist.")
        branch_out = base_branch or get_current_git_branch()
        create_new_branch = (
            input(f"Confirm branching out from {branch_out}? (y/n): ").lower() == "y"
        )
        if create_new_branch:
            subprocess.run(["git", "checkout", branch_out], cwd=TEMPLATES_REPO_PATH)
            subprocess.run(
                ["git", "pull", "origin", branch_out], cwd=TEMPLATES_REPO_PATH
            )
            subprocess.run(
                ["git", "checkout", "-b", ticket_branch], cwd=TEMPLATES_REPO_PATH
            )
            subprocess.run(
                ["git", "push", "-u", "origin", ticket_branch], cwd=TEMPLATES_REPO_PATH
            )
        else:
            print(f"Branch change aborted. proceeding with {get_current_git_branch()}")


def get_template_filename(template_filename):
    if not template_filename:
        template_filenames = list_templates_in_directory(
            os.path.join(TEMPLATES_REPO_PATH, "templates")
        )
        print("Select template to update:")
        for index, filename in enumerate(template_filenames, start=1):
            print(f"{index}. {filename}")

        choice = int(input("Enter number: "))
        if choice < 1 or choice > len(template_filenames):
            raise ValueError(f"Invalid choice: {choice}. Exiting.")

        template_filename = template_filenames[choice - 1]
    return template_filename


def list_templates_in_directory(directory):
    """List all files in the given directory."""
    return sorted(os.listdir(directory))


def get_updated_html_set_statement():
    return (
        open(os.path.join(TEMPLIFY_REPO_PATH, "updated_template_set.sql"))
        .read()
        .strip()
    )


def validate_html_content_format(html_content):
    """Validate the html content format."""
    pattern = r"^SET\s+@html_content\s*:=\s*['\"](.+?)['\"];$"
    if not re.match(pattern, html_content):
        raise ValueError(
            f"Invalid HTML content format. Must be a valid SQL SET statement. {pattern}"
        )


def update_template_content(template_filepath, updated_html_set_statement):
    """Update the given template content with the new html set statement."""
    with open(template_filepath) as file:
        template_content = file.read()
    new_template_content = "\n".join(
        [
            updated_html_set_statement if line.startswith("SET @html_content") else line
            for line in template_content.split("\n")
        ]
    )
    with open(template_filepath, "w") as file:
        file.write(new_template_content)


def push_changes(template_filepath):
    subprocess.run(["git", "add", template_filepath], cwd=TEMPLATES_REPO_PATH)
    subprocess.run(
        ["git", "commit", "-m", "Update template HTML"], cwd=TEMPLATES_REPO_PATH
    )
    subprocess.run(["git", "push"], cwd=TEMPLATES_REPO_PATH)


def create_pr(base_branch):
    if not base_branch:
        return
    subprocess.run(
        ["gh", "pr", "create", "--base", base_branch], cwd=TEMPLATES_REPO_PATH
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")
