#!/usr/bin/env python2.7

from setuptools import setup
from pip.req import parse_requirements
from pip.download import PipSession
import os
import sys
import re
import subprocess

install_reqs = parse_requirements('requirements.txt',
                                  session=PipSession())

packages = []

for root, dirs, files in os.walk('mezzapp'):
    if '__init__.py' in files:
        packages.append(re.sub('%[%A-z0-9_]+', '', root.replace('/', '.')))

is_build = len(sys.argv) > 1 and sys.argv[1] == 'sdist'


def get_version():
    # Skip VERSION.txt if building a package.
    if not is_build and os.path.exists("VERSION.txt"):
        with open("VERSION.txt") as ver_file:
            return ver_file.read()
    else:
        # Build version from latest tag.
        raw_git_branch = os.environ.get('GIT_BRANCH', 'localbuild')
        branch_match = re.match('origin\/pull\/(\d+)/(.+)', raw_git_branch)
        if branch_match:
            gitbranch = "pull{}{}".format(branch_match.group(1),
                                          branch_match.group(2))
        else:
            gitbranch = os.path.basename(raw_git_branch)
        gitcommit = os.environ.get('GIT_COMMIT')
        if not gitcommit:
            gitcommit = subprocess.check_output(
                "git rev-parse HEAD", shell=True)
            gitcommit.rstrip()
        gitdescribe = subprocess.check_output(
            "git describe --tags", shell=True)
        gitdescribe.rstrip()
        buildnumber = os.environ.get('BUILD_NUMBER', '0')

        tagsearch = re.search('(.*)-(\d*)-(.*)', gitdescribe)
        if tagsearch:
            return "{}-c{}-build{}-{}-{}".format(
                tagsearch.group(1), tagsearch.group(2), buildnumber,
                gitbranch, gitcommit[0:8])
        else:
            return "{}-build{}-{}-{}".format(
                gitdescribe, buildnumber, gitbranch, gitcommit[0:8])

version = get_version()

# Write out VERSION.txt if building a package.
if is_build:
    with open("VERSION.txt", "w") as ver_txt:
        print "Saving version: %s" % version
        ver_txt.write(version)

job_url = os.environ.get("JOB_URL")
build_number = os.environ.get("BUILD_NUMBER")
if job_url and build_number:
    url = "{}{}/".format(job_url, build_number)
else:
    url = "https://github.com/stormsherpa/openwest2015-mezzapp"

setup(name="Mezzapp",
      version=version,
      url=url,
      description="App for installing mezzanine site",
      author="Shaun Kruger",
      author_email="shaun.kruger@gmail.com",
      include_package_data=True,
      packages=packages,
      install_requires=[str(ir.req) for ir in install_reqs])
