"""
Setup script for HybridMind Super AI Architecture
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().split('\n') 
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="hybridmind",
    version="1.0.0",
    author="HybridMind Development Team",
    author_email="contact@hybridmind.ai",
    description="A Self-Extending Super AI Architecture combining symbolic reasoning, neural networks, and safety mechanisms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hybridmind/hybridmind",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.19.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.971",
        ],
        "gpu": [
            "torch-audio>=0.12.0",
            "torch-vision>=0.13.0",
        ],
        "full": [
            "jupyter>=1.0.0",
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "hybridmind-demo=demo:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "artificial intelligence", 
        "machine learning", 
        "symbolic reasoning", 
        "neural networks",
        "hybrid ai",
        "super ai",
        "safety ai",
        "self-modifying ai"
    ],
    project_urls={
        "Bug Reports": "https://github.com/hybridmind/hybridmind/issues",
        "Documentation": "https://hybridmind.readthedocs.io/",
        "Source": "https://github.com/hybridmind/hybridmind",
    },
)