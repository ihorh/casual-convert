from typing import Final

PROG_DESCRIPTION: Final[str] = """
Proprietary tool to simultenously update monorepo package versions
in both npm and uv (python) packages.

Examples:

    uv run version                      Show curren packages versions
    uv run version <version>            Set version on all packages
    uv run version --bump <bump_type>   Bump version on all packages

Example (unsupported bump type):

    uv run version --bump dev           This command should fail
"""

PROG_EPILOG: Final[str] = """
If successful, this command will always try to set same version
on all packages (even in case of bump).
"""

PROG_ARG_VERSION_HELP: Final[str] = """
Version to set (SemVer)
"""

PROG_ARG_BUMP_HELP: Final[str] = """
Supported bump types: major, minor, patch, alpha, beta, rc
"""

def next_steps_message(new_version: str) -> str:
    return f"""
    You should have run this command on a clean git tree. So now you
    repository should only contain changes related to versioning.

    Please, review updated version of packages carefully.

    If unhappy rollback changes with this command:

        git reset --hard

    If happy, commit your changes and (optionally) manually create
    git tags using these commands:

        git tag v{new_version}

    To deploy to render.com production environment, add one of
    (or both) following tags:

        git tag prod-ui-v{new_version}
        git tag prod-api-v{new_version}

    Don't forget to push your tags:

        git push origin v{new_version} prod-ui-v{new_version} prod-api-v{new_version}

    or even simpler (to push ALL tags):

        git push origin --tags
    """
