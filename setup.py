from setuptools import setup, find_packages
import os

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements file
with open("requirements.txt", encoding="utf-8") as f:
    requirements = f.read().splitlines()
    # Remove comments and empty lines
    requirements = [line for line in requirements if line and not line.startswith("#")]

setup(
    name="rebeldesk",
    version="0.1.0",
    description="A lightweight, AI-powered IDE that integrates with the RebelSUITE ecosystem",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RebelSUITE Team",
    author_email="info@rebelsuite.com",
    url="https://github.com/snowmannn129/RebelDESK",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Integrated Development Environments (IDE)",
    ],
    entry_points={
        "console_scripts": [
            "rebeldesk=rebeldesk.main:main",
        ],
    },
)
