from setuptools import setup, find_packages

setup(
    name="docsend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here
    ],
    entry_points={
        'console_scripts': [
            'docsend=docsend.cli:main',  # Adjust this line to match your CLI entry point
        ],
    },
)