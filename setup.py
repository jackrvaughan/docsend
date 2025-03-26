from setuptools import setup, find_packages

setup(
    name="docsend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "appdirs==1.4.3",
        "beautifulsoup4==4.8.1",
        "bs4==0.0.1",
        "certifi==2019.9.11",
        "chardet==3.0.4",
        "click==8.0",
        "cssselect==1.1.0",
        "fake-useragent==0.1.11",
        "idna==2.8",
        "lxml==4.9.3",
        "parse==1.12.1",
        "pillow==10.0.0",
        "pyee==6.0.0",
        "pyppeteer==0.0.25",
        "pyquery==1.4.0",
        "requests-html==0.9.0",
        "requests>=2.26.0",
        "six==1.12.0",
        "soupsieve==1.9.4",
        "tqdm==4.36.1",
        "urllib3>=2.0.0",
        "w3lib==1.21.0",
        "websockets>=10.0,<12.0",  # Allow versions 10.x and 11.x
    ],
    entry_points={
        'console_scripts': [
            'docsend=docsend.cli:main',  # Adjust this line to match your CLI entry point
        ],
    },
)