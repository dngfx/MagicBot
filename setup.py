import setuptools


with open("README.md", "r") as readme_file:
    long_description = readme_file.read()
with open("VERSION", "r") as version_file:
    version = version_file.read().strip()

setuptools.setup(
    name="magicbot",
    version=version,
    scripts=["magicbotd", "magicbotctl"],
    author="dngfx",
    author_email="email@misconfigured.link",
    description="Modular event-driven IRC bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dngfx/MagicBot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX",
        "Topic :: Communications :: Chat :: Internet Relay Chat",
    ],
    platforms=["linux"],
    python_requires=">=3.6",
)
