from setuptools import setup

setup(
    name="route_flow",
    version="0.1.0",
    packages=["src"],
    install_requires=[
        "pygame",
    ],
    entry_points={
        "console_scripts": [
            "route_flow = src.__main__:main",
        ]
    }
)
