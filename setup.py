#!/usr/bin/env python

import setuptools

setuptools.setup(
    name="pacmint",
    description="Pac-Mint (local and online multiplayer)",
    url="https://github.com/yannickzheng/PAC_MINT",
    packages=setuptools.find_packages(
        include=[
            "common",
            "game*",
            "server*",
            "utils*",
            "core*",
            "gameplay*",
            "menus*",
            "ui*",
        ],
        exclude=["tests*"],
    ),
    include_package_data=True,
    install_requires=[
        "pygame>=2.0.0",
        "requests>=2.25.1",
    ],
    entry_points={
        "console_scripts": [
            "pacmint=game.pacmint:main",
            "pacmint-server=server.server:main",
        ],
    },
    python_requires=">=3.8",
)
