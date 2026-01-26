"""Setup script for SessionDocGen."""

from setuptools import setup

setup(
    name="sessiondocgen",
    version="1.0.0",
    py_modules=["sessiondocgen"],
    python_requires=">=3.8",
    author="Team Brain / ATLAS",
    author_email="logan@metaphysicsandcomputing.com",
    description="Auto-generate session summaries from tool usage, decisions, and outcomes",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/DonkRonk17/SessionDocGen",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: General",
    ],
    keywords="session documentation summary tool usage metrics report",
    entry_points={
        "console_scripts": [
            "sessiondocgen=sessiondocgen:main",
        ],
    },
)
