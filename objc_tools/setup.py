from setuptools import setup, find_packages
 
setup(
    # package name
    name='objc_tools',
    version="0.0.1",
    description="Objc_tools",
    long_description="Objc_tools",
    author='Chloe Surett',
    license='',
    classifiers=[
        "Development Status :: 1 - Planning"
    ],
    # subfolder
    # objc_tools: https://github.com/scj643/objc_tools
    packages=['backports','c','core','foundation','ios10','private','pythonista','scenekit','ui']
)
