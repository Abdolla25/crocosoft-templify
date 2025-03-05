from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

with open("dev-requirements.txt", "r", encoding="utf-8") as fh:
    dev_requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="templify",
    version="0.1.0",
    author="Abdulla Zahran",
    author_email="abdullah.zahran@crocosoft.net",
    description="A tool for updating templates with new HTML content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Abdolla25/crocosoft-templify",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
    },
    entry_points={
        "console_scripts": [
            "templify=templify.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "templify": ["config.yaml"],
    },
) 