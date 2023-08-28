from setuptools import setup
setup(name='synapse_selector',
      version='0.0.2',
      description='Small internal package for post-selection of Glutmate/Calcium signal responses.',
      author='Stephan Weissbach',
      author_email='s.weissbach@uni-mainz.de',
      license='MIT',
      packages=['synapse_selector'],
      install_requires=[
          'pyqt6',
          'pyqt6-webengine',
          'numpy',
          'pandas',
          'scipy',
          'plotly'
      ])
