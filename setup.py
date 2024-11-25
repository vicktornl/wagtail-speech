from setuptools import find_packages, setup

install_requires = ["boto3>=1.4.4", "django>=1.8", "wagtail>=1.2"]

test_require = [
    "flake8",
    "isort",
    "pytest",
    "pytest-cov",
    "pytest-django",
    "wagtail",
]

setup(
    name="wagtail-speech",
    version="0.2.0",
    description="Turn Wagtail pages into lifelike speech using Amazon Polly.",
    author="R.Moorman <rob@vicktor.nl>",
    install_requires=install_requires,
    extras_require={
        "test": test_require,
    },
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Framework :: Wagtail :: 6",
    ],
)
