from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()


test_requirements = [
    "pytest>=3",  # PyTest
]
setup_requirements = [
    "pytest-runner",  # PyTest Runner
]

setup(
    author="Alexander & William",
    author_email="alexander@11a.se",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    description="A tool for multicamera composition.",
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords=[
        "multicamcomposepro",
        "multicam",
        "compose",
        "pro",
        "multicamcompose",
        "mccp",
    ],
    name="multicamcomposepro",
    packages=find_packages(include=["multicamcomposepro", "multicamcomposepro.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://www.github.com/wlinds/mccp",
    version="0.1.0",
    zip_safe=False,
)
