#!/usr/bin/env python3
"""
bitsec.py

Bitsec CLI utility for miners and validators.
Operations are signed with a Bittensor wallet hotkey.

Usage examples:

"""
import argparse
import os
from pathlib import Path

from config import settings
from loggers.logger import get_logger
from validator.platform_client import PlatformClient
from validator.models.platform import User, UserRole, AgentCode


PLATFORM_CLIENT = PlatformClient(settings.platform_url)
logger = get_logger()


def create_user(
    email: str,
    name: str | None,
    is_miner: bool = True,
) -> None:
    """Register a miner or validator (depending on role)."""

    role = "MINER" if is_miner else "VALIDATOR"

    user = User(
        email=email,
        name=name,
        role=UserRole.MINER if is_miner else UserRole.VALIDATOR,
    )
    user = PLATFORM_CLIENT.create_user(user)

    logger.info(f"{user['role']} User {user['email']} created with hotkey: {user['hotkey']}")


def submit_agent() -> None:
    agent_path = Path("miner/agent.py")
    if not agent_path.exists():
        raise FileNotFoundError(agent_path)

    code_str = agent_path.read_text(encoding="utf-8")
    agent_code = AgentCode(code=code_str)

    agent = PLATFORM_CLIENT.submit_agent(agent_code)
    logger.info(f"Agent submitted: version {agent['version']}")


def add_common_flags(parser: argparse.ArgumentParser) -> None:
    """Attach shared arguments (wallet, domain, api-base) to a command parser."""
    parser.add_argument("--wallet", required=True, help="Bittensor wallet name")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bitsec.py",
        description="Bitsec CLI for miners and validators (signed with hotkey)",
    )

    root = parser.add_subparsers(dest="group", required=True)

    # Miner commands ---------------------------------------------------
    miner = root.add_parser("miner", help="Miner operations")
    miner_sub = miner.add_subparsers(dest="action", required=True)

    # Create Miner account
    mreg = miner_sub.add_parser("create", help="Create a miner account")
    add_common_flags(mreg)
    mreg.add_argument("--email", required=True)
    mreg.add_argument("--name")

    # Miner submit
    msub = miner_sub.add_parser("submit", help="Submit a miner agent")
    add_common_flags(msub)

    # Validator commands -----------------------------------------------
    validator = root.add_parser("validator", help="Validator operations")
    validator_sub = validator.add_subparsers(dest="action", required=True)

    # Create Validator account
    vreg = validator_sub.add_parser("create", help="Create a validator account")
    add_common_flags(vreg)
    vreg.add_argument("--email", required=True)
    vreg.add_argument("--name")

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.wallet:
        PLATFORM_CLIENT.set_wallet(args.wallet)

    if args.group == "miner":
        if args.action == "create":
            create_user(
                email=args.email,
                name=args.name,
                is_miner=True,
            )
        elif args.action == "submit":
            submit_agent()

    elif args.group == "validator":
        if args.action == "create":
            create_user(
                email=args.email,
                name=args.name,
                is_miner=False,
            )


if __name__ == "__main__":
    main()
