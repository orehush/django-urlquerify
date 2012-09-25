from setuptools import setup, find_packages

import urlquerify

setup(
    name='django-urlquerify',
    version=urlquerify.__version__,
    author=urlquerify.__author__,
    author_email=urlquerify.__contact__,
    description=urlquerify.__doc__,
    url=urlquerify.__homepage__,
    packages=find_packages(),
    license='MIT',
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
