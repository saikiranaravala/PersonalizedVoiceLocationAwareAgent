#!/usr/bin/env python3
"""Quick diagnostic for OpenRouter setup."""

import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("🔍 OpenRouter Configuration Diagnostic")
    print("=" * 60)
    print()

    issues = []
    warnings = []

    # Check 1: Environment file
    print("📄 Checking configuration files...")
    env_file = Path("config/.env")
    if env_file.exists():
        print("  ✅ config/.env exists")
        with open(env_file) as f:
            content = f.read()
            if "OPENROUTER_API_KEY" in content:
                print("  ✅ OPENROUTER_API_KEY found in .env")
                # Check if it has a value
                for line in content.split('\n'):
                    if line.startswith('OPENROUTER_API_KEY='):
                        value = line.split('=', 1)[1].strip()
                        if value and value != 'your_openrouter_api_key_here':
                            if value.startswith('sk-or-v1-'):
                                print("  ✅ OPENROUTER_API_KEY has correct format")
                            else:
                                print("  ⚠️  OPENROUTER_API_KEY doesn't start with 'sk-or-v1-'")
                                warnings.append("API key should start with 'sk-or-v1-'")
                        else:
                            print("  ❌ OPENROUTER_API_KEY is not set (placeholder value)")
                            issues.append("Set your actual OpenRouter API key in config/.env")
            else:
                print("  ❌ OPENROUTER_API_KEY not found in .env")
                issues.append("Add OPENROUTER_API_KEY to config/.env")
    else:
        print("  ❌ config/.env not found")
        issues.append("Create config/.env from config/.env.example")

    print()

    # Check 2: Config YAML file
    print("📝 Checking YAML configuration...")
    config_file = Path("config/config.yaml")
    if config_file.exists():
        print("  ✅ config/config.yaml exists")
        with open(config_file) as f:
            content = f.read()
            if "use_openrouter: true" in content:
                print("  ✅ use_openrouter is enabled")
            elif "use_openrouter: false" in content:
                print("  ⚠️  use_openrouter is disabled (will use OpenAI)")
                warnings.append("Set 'use_openrouter: true' in config/config.yaml to use OpenRouter")
            
            # Check model format
            if "anthropic/" in content or "openai/" in content or "meta-llama/" in content:
                print("  ✅ Model identifier looks correct (includes provider)")
            elif "gpt-4" in content or "gpt-3.5" in content:
                if "use_openrouter: true" in content:
                    print("  ⚠️  Using OpenAI model name with OpenRouter")
                    warnings.append("For OpenRouter, use format: 'openai/gpt-4-turbo' not 'gpt-4'")
    else:
        print("  ❌ config/config.yaml not found")
        issues.append("Config file missing")

    print()

    # Check 3: Required packages
    print("📦 Checking Python packages...")
    try:
        import langchain
        version = getattr(langchain, '__version__', 'unknown')
        print(f"  ✅ langchain installed (version {version})")
    except ImportError:
        print("  ❌ langchain not installed")
        issues.append("Run: pip install -r requirements.txt")

    try:
        from langchain_openai import ChatOpenAI
        print("  ✅ langchain-openai installed")
    except ImportError:
        print("  ❌ langchain-openai not installed")
        issues.append("Run: pip install langchain-openai")

    try:
        from langchain.agents import create_tool_calling_agent
        print("  ✅ create_tool_calling_agent available")
    except ImportError:
        print("  ❌ create_tool_calling_agent not available")
        issues.append("Update langchain: pip install langchain --upgrade")

    print()

    # Check 4: API Key in environment
    print("🔑 Checking environment variables...")
    
    # Load .env file manually
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if openrouter_key:
        if openrouter_key.startswith("sk-or-v1-"):
            print("  ✅ OPENROUTER_API_KEY loaded correctly")
        else:
            print("  ⚠️  OPENROUTER_API_KEY loaded but format looks wrong")
            warnings.append("OpenRouter keys should start with 'sk-or-v1-'")
    else:
        print("  ❌ OPENROUTER_API_KEY not in environment")
        issues.append("OPENROUTER_API_KEY not loaded from .env")
    
    if openai_key:
        print("  ✅ OPENAI_API_KEY also available (good for fallback)")
    else:
        print("  ⚠️  OPENAI_API_KEY not set (can't fallback to OpenAI)")

    print()

    # Check 5: Source code
    print("💻 Checking source code...")
    core_file = Path("src/agent/core.py")
    if core_file.exists():
        with open(core_file) as f:
            content = f.read()
            if "create_tool_calling_agent" in content:
                print("  ✅ Using create_tool_calling_agent (correct)")
            elif "create_openai_functions_agent" in content:
                print("  ❌ Using deprecated create_openai_functions_agent")
                issues.append("Update src/agent/core.py to use create_tool_calling_agent")
            
            if "create_openrouter_llm" in content:
                print("  ✅ OpenRouter integration code present")
            else:
                print("  ❌ OpenRouter integration code missing")
                issues.append("Update src/agent/core.py with OpenRouter support")
    else:
        print("  ❌ src/agent/core.py not found")
        issues.append("Source file missing")

    print()
    print("=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    if not issues and not warnings:
        print("✅ All checks passed! OpenRouter should work correctly.")
        print()
        print("🚀 You're ready to run:")
        print("   python src/main.py")
    else:
        if issues:
            print(f"\n❌ {len(issues)} Critical Issue(s) Found:\n")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        
        if warnings:
            print(f"\n⚠️  {len(warnings)} Warning(s):\n")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")
        
        print("\n📖 Next Steps:")
        if issues:
            print("   1. Fix the critical issues listed above")
        if warnings:
            print("   2. Review warnings (optional but recommended)")
        print("   3. See TROUBLESHOOTING.md for detailed fixes")
        print("   4. Run this diagnostic again to verify")
    
    print()
    print("=" * 60)
    
    # Return exit code
    return 0 if not issues else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Diagnostic failed with error: {e}")
        sys.exit(1)
