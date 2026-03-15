"""
AutoApply Setup Verification Script
Run this to confirm all components are configured correctly before Day 1 development.

Usage: python scripts/verify_setup.py
"""

import sys
import os

def check(name: str, condition: bool, hint: str = ""):
    icon = "✓" if condition else "✗"
    color = "\033[92m" if condition else "\033[91m"
    reset = "\033[0m"
    print(f"  {color}{icon}{reset} {name}")
    if not condition and hint:
        print(f"      → {hint}")
    return condition


def main():
    print("\n🚀 AutoApply Setup Verification\n")
    results = []

    # ── Python version ─────────────────────────────────────────────────────
    print("Python Environment:")
    results.append(check(
        f"Python 3.11+ (found {sys.version.split()[0]})",
        sys.version_info >= (3, 11),
        "Install Python 3.11 or higher"
    ))

    # ── Required packages ──────────────────────────────────────────────────
    print("\nRequired Packages:")
    packages = {
        "fastapi": "pip install fastapi",
        "uvicorn": "pip install uvicorn[standard]",
        "boto3": "pip install boto3",
        "pdfplumber": "pip install pdfplumber",
        "pydantic": "pip install pydantic",
    }
    for pkg, install_hint in packages.items():
        try:
            __import__(pkg)
            results.append(check(pkg, True))
        except ImportError:
            results.append(check(pkg, False, install_hint))

    # Nova Act
    try:
        import nova_act
        results.append(check("nova-act SDK", True))
    except ImportError:
        results.append(check("nova-act SDK", False, "pip install nova-act"))

    # ── Environment variables ──────────────────────────────────────────────
    print("\nEnvironment Variables:")

    nova_key = os.getenv("NOVA_ACT_API_KEY", "")
    results.append(check(
        "NOVA_ACT_API_KEY set",
        bool(nova_key and nova_key != "your_nova_act_api_key_here"),
        "Get your key at https://nova.amazon.com"
    ))

    aws_key = os.getenv("AWS_ACCESS_KEY_ID", "")
    results.append(check(
        "AWS_ACCESS_KEY_ID set",
        bool(aws_key),
        "Configure AWS credentials: aws configure"
    ))

    aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    results.append(check(
        "AWS_SECRET_ACCESS_KEY set",
        bool(aws_secret),
        "Configure AWS credentials: aws configure"
    ))

    # ── AWS Bedrock connectivity ───────────────────────────────────────────
    print("\nAWS Bedrock:")
    if aws_key and aws_secret:
        try:
            import boto3
            bedrock = boto3.client(
                "bedrock-runtime",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
            )
            # Just test connectivity, don't actually invoke
            boto3.client(
                "bedrock",
                region_name="us-east-1",
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
            ).list_foundation_models(byProvider="Amazon")
            results.append(check("Bedrock API accessible", True))
        except Exception as e:
            results.append(check(
                "Bedrock API accessible",
                False,
                f"Error: {str(e)[:80]} — ensure Bedrock access is enabled in us-east-1"
            ))
    else:
        results.append(check("Bedrock API accessible", False, "AWS credentials not set"))

    # ── Nova Act quick test ────────────────────────────────────────────────
    print("\nNova Act:")
    if nova_key and nova_key != "your_nova_act_api_key_here":
        try:
            from nova_act import NovaAct
            results.append(check("Nova Act SDK importable", True))
            print("      → SDK imported successfully. Full test requires running a session.")
        except Exception as e:
            results.append(check("Nova Act SDK importable", False, str(e)))
    else:
        results.append(check("Nova Act API key configured", False, "Set NOVA_ACT_API_KEY environment variable"))

    # ── Summary ────────────────────────────────────────────────────────────
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"\n{'='*40}")
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print("\033[92m✓ All checks passed! Ready to build.\033[0m")
        print("\nNext steps:")
        print("  cd backend && uvicorn main:app --reload")
        print("  cd frontend && npm install && npm run dev")
    else:
        print(f"\033[91m{total - passed} check(s) failed. Resolve issues above before starting.\033[0m")
        print("\nMost common fix: copy .env.example to .env and fill in your API keys")


if __name__ == "__main__":
    main()
