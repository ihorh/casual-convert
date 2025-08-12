import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from enum import IntEnum
from typing import Final, Literal, TypedDict

from finnikacc.scripts.version_help import (
    PROG_ARG_BUMP_HELP,
    PROG_ARG_VERSION_HELP,
    PROG_DESCRIPTION,
    PROG_EPILOG,
    next_steps_message,
)

# * ----------------------------------------
# * Packages Definition
# * ----------------------------------------

class PackageDef(TypedDict, total=True):
    type: Literal["uv", "npm"]
    name: str
    extra_args: str

PACKAGES: Final[list[PackageDef]] = [
    {"type": "uv", "name": "finnikacc", "extra_args": ""},
    {"type": "uv", "name": "finnikacc-api", "extra_args": "--package finnikacc-api"},
    {"type": "npm", "name": "finnikacc", "extra_args": ""},
    {"type": "npm", "name": "finnikacc-ui", "extra_args": "-w webapps/finnikacc-ui"},
]

# * ----------------------------------------
# * Supported pre-release ids
# * ----------------------------------------

SUPPORTED_PRE_IDS: Final[list[str]] = ["major", "minor", "patch", "alpha", "beta", "rc"]

# * ----------------------------------------
# * Shell commands used by this script
# * ----------------------------------------

# * ret_code = 0 if inside work tree
CMD_GIT_IS_WORK_TREE: Final[str] = "git rev-parse --is-inside-work-tree"
# * stdout empty if git tree is clean
CMD_GIT_IS_WORK_TREE_CLEAN: Final[str] = "git status --porcelain"
CMD_UV_VERSION_GET_TMPL = "uv version --output-format json {extra_args}"
CMD_UV_VERSION_SET_TMPL = "uv version {arg_version} {extra_args}"
CMD_UV_VERSION_BUMP_TMPL = "uv version --bump {arg_bump}"
CMD_NPM_VERSION_GET_TMPL = "npm pkg get name version {extra_args}"
CMD_NPM_VERSION_SET_TMPL = "npm version {arg_version} --allow-same-version --no-git-tag-version {extra_args}"


# * ----------------------------------------
# * Main functions of the script
# * ----------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(
        "version",
        description=PROG_DESCRIPTION,
        epilog=PROG_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap_g_ver_or_bump = ap.add_mutually_exclusive_group()
    ap_g_ver_or_bump.add_argument("--bump", type=str, required=False, help=PROG_ARG_BUMP_HELP)
    ap_g_ver_or_bump.add_argument(dest="version", nargs="?", help=PROG_ARG_VERSION_HELP)

    args = ap.parse_args(sys.argv[1:])
    arg_version: str = args.version
    arg_bump: str = args.bump
    return cmd_version(arg_version, arg_bump)


class RetCode(IntEnum):
    OK = 0
    UNSUPPORTED_BUMP_TYPE = 41
    GIT_REPO_NOT_CLEAN = 51
    UNDERLYING_CMD_ERROR = 61


def cmd_version(arg_version: str | None, arg_bump: str | None) -> RetCode:
    # * show version
    if not arg_version and not arg_bump:
        return cmd_version_show()

    # * update version
    update_result = cmd_version_update(arg_version, arg_bump)
    cmd_version_show()
    if not update_result.ret_code and update_result.attempted_version:
        _print_out(next_steps_message(update_result.attempted_version))

    return update_result.ret_code


# * ----------------------------------------
# * Implementation
# * ----------------------------------------


def cmd_version_show() -> RetCode:
    for p in PACKAGES:
        _print_out(get_package_version(p))
    return RetCode.OK


@dataclass(frozen=True, kw_only=True, slots=True)
class VersionUpdateResult:
    ret_code: RetCode
    attempted_version: str | None = None


def cmd_version_update(arg_version: str | None, arg_bump: str | None) -> VersionUpdateResult:
    if arg_bump and arg_bump not in SUPPORTED_PRE_IDS:
        _print_err("unsupported bump: ", arg_bump)
        return VersionUpdateResult(ret_code=RetCode.UNSUPPORTED_BUMP_TYPE)

    # ! allow to run only in project with no git OR in clean git tree
    if (
        not _run_shell(CMD_GIT_IS_WORK_TREE, check=False).returncode  # ? are we in the git tree
        and _run_shell(CMD_GIT_IS_WORK_TREE_CLEAN, check=False).stdout.strip()  # ? is this git tree clean
    ):
        _print_err("Git repo is dirty. Please commit or stash changes before running.")
        return VersionUpdateResult(ret_code=RetCode.GIT_REPO_NOT_CLEAN)

    # ! update root uv package version first
    cmd_result: subprocess.CompletedProcess[bytes]
    if arg_version:
        cmd_result = _run_shell(CMD_UV_VERSION_SET_TMPL.format(arg_version=arg_version, extra_args=""), check=False)
    elif arg_bump:
        cmd_result = _run_shell(CMD_UV_VERSION_BUMP_TMPL.format(arg_bump=arg_bump), check=False)

    if _print_if_error(cmd_result):
        return VersionUpdateResult(ret_code=RetCode.UNDERLYING_CMD_ERROR)

    # * Now, if root uv package updated succesfully, set version on all other projects

    ver = get_package_version(PACKAGES[0])["version"]

    for p in PACKAGES:
        cmd_result = set_package_version(p, ver)
        if _print_if_error(cmd_result):
            return VersionUpdateResult(ret_code=RetCode.UNDERLYING_CMD_ERROR, attempted_version=ver)

    return VersionUpdateResult(ret_code=RetCode.OK, attempted_version=ver)


def get_package_version(pkg: PackageDef) -> dict[str, str]:
    extra_args = pkg["extra_args"]
    if pkg["type"] == "uv":
        result = _run_shell(CMD_UV_VERSION_GET_TMPL.format(extra_args=extra_args))
        return json.loads(result.stdout.decode().strip().strip('"'))
    if pkg["type"] == "npm":
        result = _run_shell(CMD_NPM_VERSION_GET_TMPL.format(extra_args=extra_args))
        ver = json.loads(result.stdout.decode().strip().strip('"'))
        ver = ver.get(pkg["name"]) or ver
        return {"package_name": ver["name"], "version": ver["version"]}
    return {}


def set_package_version(pkg: PackageDef, version: str) -> subprocess.CompletedProcess[bytes]:
    extra_args = pkg["extra_args"]
    if pkg["type"] == "uv":
        return _run_shell(CMD_UV_VERSION_SET_TMPL.format(arg_version=version, extra_args=extra_args), check=False)
    if pkg["type"] == "npm":
        return _run_shell(CMD_NPM_VERSION_SET_TMPL.format(arg_version=version, extra_args=extra_args), check=False)
    msg = f"unknown package type {pkg['type']}"
    raise RuntimeError(msg)


# * ----------------------------------------
# * Internal
# * ----------------------------------------


def _run_shell(cmd: str, args: list[str] | None = None, *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    args = [cmd, *(args)] if args else [cmd]
    return subprocess.run(" ".join(args), check=check, shell=True, capture_output=True)  # noqa: S602


def _print_if_error(proc_result: subprocess.CompletedProcess[bytes]) -> RetCode:
    if proc_result.returncode:
        _print_err("uv command return code: ", proc_result.returncode)
        if proc_result.stderr:
            _print_err(proc_result.stderr.decode().strip())
        if proc_result.stdout:
            _print_out(proc_result.stdout.decode().strip())
        return RetCode.UNDERLYING_CMD_ERROR
    return RetCode.OK


def _print_out(*values: object) -> None:
    print(*values, file=sys.stdout)  # noqa: T201


def _print_err(*values: object) -> None:
    print(*values, file=sys.stderr)  # noqa: T201
