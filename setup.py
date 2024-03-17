from setuptools import setup, find_packages

setup(
    name="taskrun",
    version="0.1",
    description="VS code task runner",
    url="https://github.com/roryrjb/taskrun",
    author="Rory Bradford",
    author_email="roryrjb@gmail.com",
    license="MIT",
    install_requires=["simple-term-menu"],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "taskrun=taskrun.taskrun:main",
        ],
    },
    zip_safe=False,
)
