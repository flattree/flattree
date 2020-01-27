from setuptools import setup, find_packages
import flattree

with open("README.rst", "r") as readme_file:
    readme = readme_file.read()

requirements = []

setup(
    name=flattree.__name__,
    version=flattree.__version__,
    author=flattree.__author__,
    author_email=flattree.__author_email__,
    description=flattree.__description__,
    long_description=readme,
    long_description_content_type='text/x-rst',
    python_requires='>=3.6.8',
    license='MIT',
    url="https://github.com/flattree/flattree",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
