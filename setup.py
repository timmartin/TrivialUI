from setuptools import setup, find_packages

NAME = "TrivialUI"
PACKAGES = find_packages(exclude=["tests*"])
CLASSIFIERS = [
    "Development Status :: 1 - Planning",
    "Intended Audience :: Developers",
    "Natural Language :: English",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Hy",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: User Interfaces"
]
INSTALL_REQUIRES = []

if __name__ == '__main__':
    setup(name=NAME,
          version="0.0.2",
          classifiers=CLASSIFIERS,
          install_requires=INSTALL_REQUIRES,
          packages=PACKAGES)
