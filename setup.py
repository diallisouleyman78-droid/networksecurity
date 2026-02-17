from setuptools import find_packages, setup
from typing import List

def get_requirements()->List[str]:

    """
    this function returns list of requirements
    """
    requirement_lst:List[str] = []
    try:
        with open('requirements.txt') as file:
            #read lines from file
            lines = file.readlines()
            ## process lines
            for line in lines:
                #strip whitespace and newline characters
                requirement = line.strip()
                ## ignore empty lines and -e .
                if requirement and requirement != '-e .':
                    requirement_lst.append(requirement)
    except FileNotFoundError:
        print("requirements.txt file not found.")
    return requirement_lst

setup(
    name='NetworkSecurity',
    version='0.0.1',
    description='A package for network security analysis and monitoring.',
    author='Diallo',
    author_email='diallisouleyman78@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements(), ## install libraries from requirements.txt
)










