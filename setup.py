from setuptools import setup

setup(
    name             = 'powerline_awesome_segments',
    description      = 'Powerline segments for the everyday developer',
    version          = '0.1.0a1',
    keywords         = 'powerline segment cwd',
    license          = 'GPLv3',
    author           = 'Will E. Dixon',
    author_email     = 'dixonwille@hotmail.com',
    url              = 'https://github.com/dixonwille/powerline-awesome-segments',
    packages         = ['powerline_awesome_segments'],
    install_requires = ['powerline-status>=2.6', 'pygit2>=0.26.4,<0.27.0'],
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Topic :: Terminals'
    ]
)
