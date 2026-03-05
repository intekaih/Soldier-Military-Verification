#!/usr/bin/env python3
"""
Soldier Military Verification - CLI Entry Point

Usage:
    python main.py --verification-id "YOUR_ID"
    python main.py --url "https://services.sheerid.com/verify/PROG_ID/?verificationId=YOUR_ID"
    python main.py --verification-id "YOUR_ID" --status VETERAN --organization 4070
"""
import sys
import json
import logging
import argparse

from sheerid_verifier import MilitaryVerifier
import config


def setup_logging():
    """Configure logging to console"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Soldier Military Verification using SheerID API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --verification-id "abc123def456"
  python main.py --url "https://services.sheerid.com/verify/PROG/?verificationId=abc123"
  python main.py --verification-id "abc123" --status VETERAN --organization 4070
  python main.py --verification-id "abc123" --first-name John --last-name Doe

Supported Organizations:
  4070     - Army
  4073     - Air Force
  4072     - Navy
  4071     - Marine Corps
  4074     - Coast Guard
  4544268  - Space Force

Supported Statuses:
  VETERAN         - Military veteran (default)
  ACTIVE_DUTY     - Currently serving
  MILITARY_FAMILY - Military family member
        """
    )

    # Verification ID source (mutually exclusive)
    id_group = parser.add_mutually_exclusive_group(required=True)
    id_group.add_argument("--verification-id", "-i", type=str,
                          help="SheerID verification ID")
    id_group.add_argument("--url", "-u", type=str,
                          help="SheerID verification URL (verificationId will be extracted)")

    # Military status
    parser.add_argument("--status", "-s", type=str, default="VETERAN",
                        choices=config.MILITARY_STATUSES,
                        help="Military status (default: VETERAN)")

    # Optional personal info
    parser.add_argument("--first-name", type=str, default=None,
                        help="First name (auto-generated if not provided)")
    parser.add_argument("--last-name", type=str, default=None,
                        help="Last name (auto-generated if not provided)")
    parser.add_argument("--email", type=str, default=None,
                        help="Email address (auto-generated if not provided)")
    parser.add_argument("--birth-date", type=str, default=None,
                        help="Birth date in YYYY-MM-DD format (auto-generated if not provided)")
    parser.add_argument("--discharge-date", type=str, default=None,
                        help="Discharge date (auto-generated if not provided)")
    parser.add_argument("--organization", "-o", type=int, default=None,
                        help="Organization ID (random if not provided). See --help for list.")

    return parser.parse_args()


def main():
    setup_logging()

    args = parse_args()

    # Get verification ID
    if args.url:
        verification_id = MilitaryVerifier.parse_verification_id(args.url)
        if not verification_id:
            print(f"\n❌ Error: Could not extract verificationId from URL: {args.url}")
            print("  Make sure the URL contains 'verificationId=' parameter")
            sys.exit(1)
        print(f"Extracted verificationId: {verification_id}")
    else:
        verification_id = args.verification_id

    # Create verifier and run
    try:
        verifier = MilitaryVerifier(
            verification_id=verification_id,
            status=args.status
        )

        result = verifier.verify(
            first_name=args.first_name,
            last_name=args.last_name,
            birth_date=args.birth_date,
            email=args.email,
            organization_id=args.organization,
            discharge_date=args.discharge_date
        )

        # Print final result
        print("\n" + "=" * 60)
        print("  RESULT")
        print("=" * 60)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        sys.exit(0 if result["success"] else 1)

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
