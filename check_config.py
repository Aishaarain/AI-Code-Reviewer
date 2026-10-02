"""Quick script to check if your configuration is valid."""

from reviewer.config import config

print("🔍 Checking your configuration...\n")

# Check GitHub token
if config.github_token:
    print(f"✅ GitHub Token: {config.github_token[:15]}..." + ("*" * 10))
else:
    print("❌ GitHub Token: NOT SET")

# Check Groq API key
if config.groq_api_key:
    print(f"✅ Groq API Key: {config.groq_api_key[:15]}..." + ("*" * 10))
else:
    print("❌ Groq API Key: NOT SET")

# Check model
print(f"✅ Model: {config.model}")

print("\n" + "=" * 60)

# Try validation
try:
    config.validate()
    print("✅ Configuration is VALID - ready to run reviews!")
except ValueError as e:
    print(f"❌ Configuration is INVALID:\n   {e}")
    print("\nPlease edit your .env file and add:")
    print("  GITHUB_TOKEN=your_github_token_here")
    print("  GROQ_API_KEY=your_groq_api_key_here")
