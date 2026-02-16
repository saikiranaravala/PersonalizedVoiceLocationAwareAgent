"""Setup script for the Personalized Agentic Assistant."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="personalized-agentic-assistant",
    version="1.0.0",
    description="A voice-first AI assistant with location awareness and deep linking capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/personalized-agentic-assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11,<3.12",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=8.2.0",
            "pytest-cov>=5.0.0",
            "pytest-mock>=3.14.0",
            "black>=24.4.0",
            "flake8>=7.0.0",
            "mypy>=1.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "agentic-assistant=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="ai assistant voice langchain agent gps deep-linking",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/personalized-agentic-assistant/issues",
        "Source": "https://github.com/yourusername/personalized-agentic-assistant",
    },
)
