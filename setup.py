import setuptools

with open('README.md') as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('cli-requirements.txt') as f:
    cli_requirements = f.read().splitlines()

setuptools.setup(
    name="queenbee_pollination",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Ladybug Tools",
    author_email="info@ladybug.tools",
    description="queenbee-pollination extends queenbee to interact with the Pollination API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pollination/queenbee-pollination",
    packages=setuptools.find_packages(exclude=["tests", "hack", "docs"]),
    install_requires=requirements,
    extras_require={'cli': cli_requirements},
    entry_points='''
        [queenbee.plugins]
        pollination=queenbee_pollination.cli:pollination
    ''',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: OS Independent"
    ],
)
