"""Setup script for web2md."""

from setuptools import setup, find_packages

setup(
    name="web2md",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "httpx>=0.27.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
        "trafilatura>=1.12.0",
        "readability-lxml>=0.8.1",
        "markdownify>=0.13.1",
    ],
    entry_points={
        "console_scripts": [
            "web2md=web2md.cli:main",
        ],
    },
)
