import sys

try:
    from setuptools import setup, find_packages
    from setuptools import Command
    from setuptools import Extension
except ImportError:
    sys.exit(
        "We need the Python library setuptools to be installed. "
        "Try running: python -m ensurepip"
    )

if "bdist_wheel" in sys.argv:
    try:
        import wheel  # noqa: F401
    except ImportError:
        sys.exit(
            "We need both setuptools AND wheel packages installed "
            "for bdist_wheel to work. Try running: pip install wheel"
        )


REQUIRES = ["notion-client>=0.8.0"]

# with open("README_En.md", encoding="utf-8") as handle:
#    readme_rst = handle.read()

setup(
    name="notion-dump-kernel",
    version="0.1.8",
    author="delta1037",
    author_email="geniusrabbit@qq.com",
    url="https://github.com/delta1037/notion-dump-kernel",
    description="Freely available tools for dumping Notion page and database.",
    # long_description=readme_rst,
    project_urls={
        "Documentation": "https://github.com/delta1037/notion-dump-kernel/blob/main/README_En.md",
        "Source": "https://github.com/delta1037/notion-dump-kernel",
        "Tracker": "https://github.com/delta1037/notion-dump-kernel/issues",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Topic :: Text Processing :: Markup",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    packages=find_packages(where='.', exclude=(), include=('*',)),
    include_package_data=True,  # done via MANIFEST.in under setuptools
    install_requires=REQUIRES,
)
# 打包发布
# 1、python setup.py sdist
# 2、twine upload dist/*

