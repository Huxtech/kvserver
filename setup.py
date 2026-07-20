from setuptools import setup, find_packages

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="kvserver-python",
    version="1.2.0",
    packages=find_packages(
        include=["kvserver", "kvserver.*"]
    ),
    install_requires=["keyboard", "qrcode_term", "watchdog", "psutil", "pyfiglet", "rich", "Pillow"],
    entry_points={
        "console_scripts": [
            "kvserver = kvserver.main:main",
        ],
    },
    author="Odudu otu",
    author_email='godspowerotu@gmail.com',
    description="A socket server that serve kivy project resources to kivydevclient apk",
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires=">=3.6",
)
