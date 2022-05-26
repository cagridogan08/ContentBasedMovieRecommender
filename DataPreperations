
import pandas as pd


#movieData = pd.read_csv("../imdb_top_1000.csv")

import nltk
#nltk.download('omw-1.4')


from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

from nltk.corpus import stopwords
#nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

VERB_CODES = {'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}


def plot_process(text):

    text = text.lower()
    temp_sent = []
    words = nltk.word_tokenize(text)
    tags = nltk.pos_tag(words)

    for i, word in enumerate(words):
        if tags[i][1] in VERB_CODES:
            lemmatized = lemmatizer.lemmatize(word,'v')
        else:
            lemmatized = lemmatizer.lemmatize(word)
        if lemmatized not in stop_words and lemmatized.isalpha():
            temp_sent.append(lemmatized)
    finalsent = ' '.join(temp_sent)
    finalsent = finalsent.replace("n't", " not")
    finalsent = finalsent.replace("'m", " am")
    finalsent = finalsent.replace("'s", " is")
    finalsent = finalsent.replace("'re", " are")
    finalsent = finalsent.replace("'ll", " will")
    finalsent = finalsent.replace("'ve", " have")
    finalsent = finalsent.replace("'d", " would")
    return finalsent


#movieData["keywords"] = movieData["Overview"].apply(plot_process)

#print(movieData["keywords"])
print("The Godfather")
aa = 'An organized crime dynastys aging patriarch transfers control of his clandestine empire to his reluctant son.'
print("Befor keyword extraction:\n",aa)
aa = plot_process(aa)
print("After extraction:\n ",aa)
#movieData.to_csv("Extracted1000.csv")
