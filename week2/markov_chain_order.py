import re
import nltk
import string
import operator
import os

# Download Alice's Adventures in Wonderland if it is not yet present
def read_alice_in_wonderland():
    alice_file = 'alice.txt'
    alice_raw = None

    if not os.path.isfile(alice_file):
        from urllib import request
        url = 'http://www.gutenberg.org/cache/epub/19033/pg19033.txt'
        response = request.urlopen(url)
        alice_raw = response.read().decode('utf8')
        with open(alice_file, 'w', encoding='utf8') as f:
            f.write(alice_raw)
    else:
        with open(alice_file, 'r', encoding='utf8') as f:
            alice_raw = f.read()

    # Remove the start and end bloat from Project Gutenberg (this is not exact, but easy).
    pattern = r'\*\*\* START OF THIS PROJECT GUTENBERG EBOOK .+ \*\*\*'
    end = "End of the Project Gutenberg"
    start_match = re.search(pattern, alice_raw)
    if start_match:
        start_index = start_match.span()[1] + 1
    else:
        start_index = 0
    end_index = alice_raw.rfind(end)
    alice = alice_raw[start_index:end_index]

    # And replace more than one subsequent whitespace chars with one space
    raw_text = re.sub(r'\s+', ' ', alice)
    return raw_text

# Use any order markov chain model
def markov_chain(raw_text, order=1):
    # Tokenize the text into sentences.
    sentences = nltk.sent_tokenize(raw_text)

    # Tokenize each sentence to words. Each item in 'words' is a list with
    # tokenized words from that list.
    tokenized_sentences = []
    for s in sentences:
        #    print(s)
        singleWordTokens = nltk.word_tokenize(s)
        tokenized_sentence = []
        for i in range(0, len(singleWordTokens) - order + 1):
            # print(i, w[i])
            counter = 0
            stateElements = []
            for j in range(i, i + order):
                # print(w[j])
                stateElements.append(singleWordTokens[j])
            orderSizeState = ' '.join(stateElements)
            tokenized_sentence.append(orderSizeState)
        tokenized_sentences.append(tokenized_sentence)

    print('States from text:\n', tokenized_sentences)

    transitions = {}
    for eachList in tokenized_sentences:
        for i in range(len(eachList) - 1):
            pred = eachList[i]
            succ = eachList[i + 1].split()[order - 1]
            if pred not in transitions:
                # Predecessor key is not yet in the outer dictionary, so we create
                # a new dictionary for it.
                transitions[pred] = {}

            if succ not in transitions[pred]:
                # Successor key is not yet in the inner dictionary, so we start
                # counting from one.
                transitions[pred][succ] = 1.0
            else:
                # Otherwise we just add one to the existing value.
                transitions[pred][succ] += 1.0

    totals = {}
    for pred, succ_counts in transitions.items():
        totals[pred] = sum(succ_counts.values())

    # Compute the probability for each successor given the predecessor.
    probs = {}
    for pred, succ_counts in transitions.items():
        probs[pred] = {}
        for succ, count in succ_counts.items():
            probs[pred][succ] = count / totals[pred]

    return probs

# Function calls
raw_text = read_alice_in_wonderland()
probabilities_dict=markov_chain(raw_text, 2)
for pred in probabilities_dict:
    sorted_by_values = sorted(probabilities_dict[pred].items(), key=operator.itemgetter(1), reverse=True)
    print(pred, sorted_by_values)