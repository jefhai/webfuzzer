# fuzz

fuzz is an internet vulnerability discoverer for `http` and `https` websites.

## Installation Instructions:
1. Make sure pip is installed: https://pip.pypa.io/en/latest/installing/
2. To install the dependencies, navigate to the fuzz directory and execute the following command:

  `pip install -r dependencies.txt`

   Note: Incase your environment path variables don't include path to pip, execute the following command:

	`python C:\Python27\Lib\site-packages\pip install -r dependencies.txt`


3. Supports Python 2.7.10

## Usage:

To start a site discovery, execute the following command:

`python fuzz.py discover [URL] --common-words ./resources/common_words.txt`

   Note: URL must be in the following format: 'http://127.0.0.1/dvwa/'
   don't forget the trailing slash for urls with a path!

To start a fuzz test, execute the following command:

`python fuzz.py test [URL] --common-words [PATH] --vectors [PATH] --sensitive [PATH]`

   Note: A site discovery is done automatically whenever test is called.

The included common words file contains several of the most common directory
names for websites, which will aid in finding pages that are not linked on public facing webpages. This file can be exchanged with a more substantial
file to increase the number of pages searched.

## Help:

To get help on how to use the fuzzer execute the following command:

`python fuzz.py --help`

Manpage:


    fuzz [discover | test] url OPTIONS

    COMMANDS:
      discover  Output a comprehensive, human-readable list of all discovered inputs to the system. Techniques include both crawling and guessing.
      test      Discover all inputs, then attempt a list of exploit vectors on those inputs. Report potential vulnerabilities.

    OPTIONS:
      --custom-auth=string     Signal that the fuzzer should use hard-coded authentication for a specific application (e.g. dvwa). Optional.

      Discover options:
        --common-words=file    Newline-delimited file of common words to be used in page guessing and input guessing. Required.

      Test options:
        --vectors=file         Newline-delimited file of common exploits to vulnerabilities. Required.
        --sensitive=file       Newline-delimited file data that should never be leaked. It's assumed that this data is in the application's database (e.g. test data), but is not reported in any response. Required.
        --random=[true|false]  When off, try each input to each page systematically.  When on, choose a random page, then a random input field and test all vectors. Default: false.
        --slow=500             Number of milliseconds considered when a response is considered "slow". Default is 500 milliseconds

    Examples:
      # Discover inputs
      python fuzz.py discover http://127.0.0.1/dvwa/ --common-words ./resources/common_words.txt

      # Discover inputs to DVWA using our hard-coded authentication
      python fuzz.py discover http://127.0.0.1/dvwa/ --common-words ./resources/common_words.txt --custom-auth dvwa

      # Discover and Test DVWA with randomness
      python fuzz.py test http://127.0.0.1/dvwa/ --custom-auth dvwa --common-words ./resources/common_words.txt --vectors ./resources/vectors.txt --sensitive ./resources/sensitive.txt --random true


## Credits:

**Jeffrey Haines**
