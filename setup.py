from typing import Dict, Any, cast
from setuptools import setup, find_packages
import pathlib
import os


def get_version(version_file: "os.PathLike[str]") -> str:
    locls: Dict[str, Any] = {}
    exec(open(version_file).read(), {}, locls)
    return cast(str, locls["__version__"])


here = pathlib.Path(__file__).parent.resolve()
readme_file = here / "README.md"
version_file = here / "src" / "kuddl" / "version.py"


setup(
    name="kuddl",
    version=get_version(version_file),
    description="YAML+Python data description language",
    long_description=readme_file.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/ktbarrett/kuddl",
    author="Kaleb Barrett",
    author_email="dev.ktbarrett@gmail.com",
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6, <4",
    install_requires=["pyyaml"],
    entry_points={},
    zip_safe=False,
)
