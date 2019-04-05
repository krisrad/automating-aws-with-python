from setuptools import setup

setup(
    name='webotron-80',
    version='0.1',
    author='RK Meiappan',
    author_email='RK_meiappan@geniusworld.com',
    description="Webotron-80 is a tool to deploy static websites from s3 buckets to Cloudfront and Route53",
    license='None',
    packages=['webotron'],
    url="https://github.com/krisrad/automating-aws-with-python",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        webotron=webotron.webotron:cli
    '''
)
