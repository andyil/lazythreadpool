from setuptools import setup, find_packages


setup(
    name='lazythreadpool',
    version='0.6',
    license='MIT',
    author="Andy Worms",
    author_email='andyworms@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/andyil/lazythreadpool',
    keywords='lazy thread pool threadpool multithreading thread parallel',
    install_requires=[
      ],

)