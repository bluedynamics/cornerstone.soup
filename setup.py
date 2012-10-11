from setuptools import setup, find_packages
import sys, os

version = "2.4.1.1"
shortdesc ="Container with queryable Records for Zope 2"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read() 
longdesc += open(os.path.join(os.path.dirname(__file__), 'docs', 'CHANGELOG.txt')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'docs', 'LICENSE.txt')).read()

setup(name='cornerstone.soup',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Framework :: Zope2',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules'        
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='container data record catalog txng3',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url='http://dev.plone.org/collective/browser/cornerstone.soup',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['cornerstone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.catalog',
          'uuid',
          'zope.annotation',
          #'ZODB',
          # Zope 2 dependencies are missing, need to add if Zope 2.<12 is no 
          # longer supported
      ],
      extras_require={
          'test': [
              'interlude',
              'zopyx.txng3.core',
          ]
      },
      )
