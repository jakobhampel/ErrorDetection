# ErrorDetection
Python code for the bachelor thesis on error detection within the Tüba-D/Z UD treebank.

Author:  
Jakob Hampel  
3895380  
jakob.hampel@student.uni-tuebingen.de

The idea behind the implementation is the variation n-gram approach for dependency annotation by:   
Boyd, A., Dickinson, M. & Meurers, W.D. On Detecting Errors in Dependency Treebanks. Res on Lang and Comput 6, 113–137 (2008). https://doi.org/10.1007/s11168-008-9051-9


The program can be executed by running [error_detection.py](error_detection.py). This should detect 1 variation nucleus in the example database containing 2 sentences from the Tüba-D/Z treebank, and store them in [data/variationNuclei.json](data/variationNuclei.json).

Please note that, due to copyright reasons, the actual treebank containing more than 100,000 sentences is not uploaded here.  
However, some of the original results are collected in [result_statistics](result_statistics)

