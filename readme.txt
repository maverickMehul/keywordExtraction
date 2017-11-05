1. rake.py - Python implementation of Rapid Keyword Extraction Algorithm
2. SmartStoplist.txt - Exhaustive list of common stop words
3. find_keys_linkedin.py - Main script for extracting keywords from linkedin descriptions
4. find_keys.sh - Shell script to initialize keyword extraction via cron

##Cron Specification
#Runs every 10 minutes
*/10 * * * * /home/Desktop/maroon-ai^maroon-ai/Keyword_Extraction/RAKE/find_keys.sh

##Dependencies
sudo pip install nltk pymongo

