import setuptools

setuptools.setup(
    setup_requires=['d2to1'],
    d2to1=True,
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'presources = royal.presources:main',
        ],
    },
)
