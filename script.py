import requests
from bs4 import BeautifulSoup
import collections
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import nltk
import numpy as np
import pandas as pd
import configparser
import openai


nltk.download('stopwords')
