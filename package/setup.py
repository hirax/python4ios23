from setuptools import setup, find_packages
 
setup(
    # package name
    name='python4ios',
    version="0.0.1",
    description="Python for iOS",
    long_description="Python module for iOS and iPadOS",
    author='Jun Hirabayashi',
    license='MIT',
    classifiers=[
        "Development Status :: 1 - Planning"
    ],
    # subfolder
    # objc_tools: https://github.com/scj643/objc_tools
    packages=['arkit','audiotoolbox','avfaudio','avfoundation','classes','corebluetooth','coreimage','corelocation','coreml','coremotion','defines','objc_util','speech','uikit']
)
