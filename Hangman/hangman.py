import random
import nltk

from operator import itemgetter

import numpy as np
import sys




def guess(runs, vowels, cons, coocurrence):
	"""
	Use unigram distribution to guess the new char
	"""

	if runs%4 == 2 or runs%4 == 3:
		try:
			char = vowels[0]
			del vowels[0]
		except Exception:
			char = cons[0]
			del cons[0]	
		runs+=1
		return runs,char, vowels, cons
	else:
		char = cons[0]
		del cons[0]
		runs+=1
		return runs, char, vowels, cons
	


def guess_bigrams(state, coocurrence):
	"""
	Use bigrams to guess the new char using co-ocurrence statistics
	"""
	for i in range(len(state)):
		if state[i].isalpha() == True and i == 0:
			alpha = coocurrence[ord(state[i])-97]
			val = chr(np.where(alpha == max(alpha))[0][0]+97)
			coocurrence[ord(state[i])-97][np.where(coocurrence[ord(state[i])-97] == max(alpha))[0][0]] = 0
			return val, coocurrence
		elif state[i].isalpha() == True  and state[i-1].isalpha()==False:
			alpha = coocurrence[:, ord(state[i])-97]
			val =chr(np.where(alpha == max(alpha))[0][0]+97)
			coocurrence[np.where(alpha == max(alpha))[0][0]][ord(state[i])-97] = 0
			return val, coocurrence
		elif state[i].isalpha() == True and i == len(state)-1:
			alpha = coocurrence[:, ord(state[i])-97]
			val =chr(np.where(alpha == max(alpha))[0][0]+97)
			coocurrence[np.where(alpha == max(alpha))[0][0]][ord(state[i])-97] = 0
			return val, coocurrence
		elif state[i].isalpha() == True  and state[i+1].isalpha()==False:
			alpha = coocurrence[ord(state[i])-97]
			val = chr(np.where(alpha == max(alpha))[0][0]+97)
			coocurrence[ord(state[i])-97][np.where(coocurrence[ord(state[i])-97] == max(alpha))[0][0]] = 0
			return val, coocurrence
		

def  preprocessing(words):
	"""
	Get the unigram distribution and co-occurence matric
	"""
	vowels = ['a','e','i','o','u']
	coocurrence = [[0]*26]*26

	freq_dist = []
	vowel = []
	consonants = []

	for word in words:
		freq_dist.extend(word)
	freq_dist = nltk.FreqDist(freq_dist)
	for key in sorted(freq_dist.items(),reverse=True, key = itemgetter(1)):

		if key[0] in vowels:
			vowel.append(key[0])
		else:
			consonants.append(key[0])

	bi_freq_dist = []
	for word in words:
		bi_freq_dist.extend(nltk.bigrams(word))

	bi_freq_dist = nltk.FreqDist(bi_freq_dist)
	for pair in bi_freq_dist:
		coocurrence[ord(pair[0])-97][ord(pair[1])-97] += bi_freq_dist[pair]

	return  vowel, consonants, coocurrence

def hangman(inp_word, dictionary, flag = 0, game = 0):
	"""
	inp_word : the word for which chars are to be guessed

	dictionary : lexicon of words in words.txt

	flag : use bigrams for guessing or not

	game : bool to whether print  the state everytime
	game -> 1 : not print
		 -> 0 : print

	"""
	dictionary = [word for word in dictionary if len(word) == len(inp_word) or len(inp_word) > 7]

	vowel_lst, cons_lst, coocurrence = preprocessing(dictionary)
	coocurrence = np.array(coocurrence)

	word = inp_word
	word_hash = {}

	state = ["_"]*len(word)
	missed_chars = []
	guessed = 0

	for char_ind in range(len(word)):
		if word[char_ind] in word_hash:
			word_hash[word[char_ind]].append(char_ind)
		else:
			word_hash[word[char_ind]]=[char_ind]

	runs = 1
	
	while guessed < len(word) and len(missed_chars) < 6:
		if guessed < 8 or flag == 0:
			runs, char, vowel_lst, cons_lst = guess(runs, vowel_lst, cons_lst, coocurrence)
		else:
			char, coocurrence = guess_bigrams(state, coocurrence)
		if char not in state and char not in missed_chars:
			if game == 0:
				print " ".join(state), " missed:", ",".join(missed_chars)
				print "guess:", char
			guessed, missed_chars, state = check_update(char, guessed, word_hash, missed_chars, state)
	
	if game == 0:
		print " ".join(state), " missed:", ",".join(missed_chars)
	if guessed == len(word):
		return 1
	else:
		return 0

def check_update(char, guessed, word_hash, missed_chars, state):
	"""
	check if the guessed char exists or not in the inp_word
	"""
	if char in word_hash:
		for i in word_hash[char]:
			state[i] = char
			guessed+=1
	else:
		missed_chars.append(char)

	return guessed, missed_chars, state


# read the input word txt lexicon
word_file = open("words.txt","r")
words = [word.strip() for word in word_file.readlines()]
word_file.close()



if sys.argv[1] == "1":
	hangman(sys.argv[2], words)
elif sys.argv[1] == "2":
	hangman(sys.argv[2], words,flag = 1)
else:
	print "Percentage Match :",(sum([hangman(word,words, game =1) for word in words])/float(len(words)))*100,"%"
