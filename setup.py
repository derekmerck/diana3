import setuptools
import re

with open("README.md") as f:
    long_description = f.read()

reqs = set()
for fn in ["requirements.txt", "service/requirements.txt"]:
    with open(fn) as f:
        s = set( f.read().splitlines() )
        reqs = reqs.union(s)
reqs = list(reqs)

with open("diana/__init__.py") as f:
    content = f.read()
    match = re.findall(r"__([a-z0-9_]+)__\s*=\s*\"([^\"]+)\"", content)
    print(match)
    metadata = dict(match)

setuptools.setup(
    name=metadata.get("name"),
    version=metadata.get("version"),
    author=metadata.get("author"),
    author_email=metadata.get("author_email"),
    description=metadata.get("desc"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=metadata.get("url"),
    packages=['diana', 'service'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    install_requires=reqs,
    entry_points='''
        [console_scripts]
        diana-cli=diana.cli.cli:main
    '''
)
