"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

NOTE: I was having problems running "manage.py test" for this project. Something to do with my virtual environment.
What I did was copy all this test code into another project and ran them there instead

I also played around with Testbed() unit testing, documentation found below:
https://cloud.google.com/appengine/docs/python/tools/localunittesting
"""
import random
import string
from django.test import TestCase
from google.appengine.ext import ndb
from models import Word, UserResults, PractiseSession, Language

def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class WordTestCases(TestCase):
    #Test Word.put()
    def test_insert_entity(self):
        Word().put()
        self.assertEqual(1, len(Word.query().fetch(2)))

    #Test Word filter by language
    def test_filter_by_language(self):
        #Add two words, one French and one Italian
        Word(englishWord='Hi',
             imagePath='hello.jpg',
             languageName='Italian',
             translatedWord='Ciao',
             difficulty=1).put()
        Word(englishWord='Hi',
             imagePath='hello.jpg',
             languageName='French',
             translatedWord='Salut',
             difficulty=1).put()

        #Get french words
        query = Word.query(Word.languageName == 'French')
        results = query.fetch()

        #Check to see if only 1 result was returned
        self.assertEqual(1, len(results))
        #Check if the word is French language
        self.assertEqual('French', results[0].languageName)

    #Test Word filter by language and difficulty
    def test_filter_by_language_and_difficulty(self):
        #Add two words, one French and one Italian
        Word(englishWord='Daughter',
             imagePath='hello.jpg',
             languageName='French',
             translatedWord='Fille',
             difficulty=2).put()
        Word(englishWord='Hi',
             imagePath='hello.jpg',
             languageName='French',
             translatedWord='Salut',
             difficulty=1).put()

        #Get french words
        query = Word.query(Word.languageName == 'French').filter('difficulty=', 2)
        results = query.fetch()

        #Check to see if only 1 result was returned
        self.assertEqual(1, len(results))
        #Check if the word is French language
        self.assertEqual('French', results[0].languageName)
        #Check if the word is of 2 difficulty
        self.assertEqual('2', results[0].difficulty)


#Unit tests for PractiseSession model
class PractiseSessionTestCases(TestCase):
    #Test PractiseSession.put()
    def test_insert_entity(self):
        PractiseSession().put()
        self.assertEqual(1, len(PractiseSession.query().fetch(2)))

    #Test practise session filter by id
    def test_filter_by_id(self):
        word_list = ["word1", "word2", "word3"]
        id1 = id_generator()
        id2 = id_generator()
        PractiseSession(sessionID=id1,
                        difficulty=1,
                        wordStrings=word_list,
                        score=12,
                        currWord="word4Translated",
                        questionNumber=4).put()
        PractiseSession(sessionID=id2,
                        difficulty=1,
                        wordStrings=word_list,
                        score=1,
                        currWord="word5Translated",
                        questionNumber=5).put()
        #Get practise session, filter by id
        query = PractiseSession.query(PractiseSession.sessionID == id1)
        results = query.fetch()

        #Check to see if only 1 result was returned
        self.assertEqual(1, len(results))
        #Check the session id
        self.assertEqual(id1, results[0].sessionID)

    #Test practise session delete by id
    def test_delete_by_id(self):
        word_list = ["word1", "word2", "word3"]
        id1 = id_generator()
        id2 = id_generator()
        PractiseSession(sessionID=id1,
                        difficulty=1,
                        wordStrings=word_list,
                        score=12,
                        currWord="word4Translated",
                        questionNumber=4).put()
        PractiseSession(sessionID=id2,
                        difficulty=1,
                        wordStrings=word_list,
                        score=1,
                        currWord="word5Translated",
                        questionNumber=5).put()
        #Get practise session, filter by id
        query = PractiseSession.query(PractiseSession.sessionID == id1)
        results = query.fetch()

        #Check to see if only 1 result was returned
        self.assertEqual(1, len(results))
        #Check the session id
        self.assertEqual(id1, results[0].sessionID)

        #Delete entry
        query = PractiseSession.query(PractiseSession.sessionID == id1).fetch(keys_only=True)
        ndb.delete_multi(query)

        #Retest to check if it's still there
        #Get practise session, filter by id
        query = PractiseSession.query(PractiseSession.sessionID == id1)
        results = query.fetch()

        #Check to see if none was returned
        self.assertEqual(0, len(results))


#Unit tests for UserResults model
class UserResultsTestCases(TestCase):
    #Test UserResults.put()
    def test_insert_entity(self):
        UserResults().put()
        self.assertEqual(1, len(UserResults.query().fetch(2)))

    #Test User Results filter by id
    def test_filter_by_id(self):
        id1 = id_generator()
        id2 = id_generator()

        UserResults(sessionID=id1,
                    questionNumber=1,
                    word="Hi",
                    userAnswer="Wrong",
                    correctAnswer="Salut").put()

        UserResults(sessionID=id1,
                    questionNumber=2,
                    word="Goodbye",
                    userAnswer="Correct",
                    correctAnswer="Aurvoi").put()

        UserResults(sessionID=id2,
                    questionNumber=2,
                    word="Goodbye",
                    userAnswer="Correct",
                    correctAnswer="Aurvoi").put()

        #Get User Results, filter by id
        query = UserResults.query(UserResults.sessionID == id1)
        results = query.fetch()

        #Check to see if 2 results was returned
        self.assertEqual(2, len(results))
        #Check the session ids
        self.assertEqual(id1, results[0].sessionID)
        self.assertEqual(id1, results[1].sessionID)

    #Test practise session delete by id
    def test_delete_by_id(self):
        id1 = id_generator()
        id2 = id_generator()
        UserResults(sessionID=id1,
                    questionNumber=1,
                    word="Hi",
                    userAnswer="Wrong",
                    correctAnswer="Salut").put()
        UserResults(sessionID=id1,
                    questionNumber=2,
                    word="Goodbye",
                    userAnswer="Correct",
                    correctAnswer="Aurvoi").put()

        #Get User Results, filter by id
        query = UserResults.query(UserResults.sessionID == id1)
        results = query.fetch()

        #Check to see if 2 results was returned
        self.assertEqual(2, len(results))
        #Check the session ids
        self.assertEqual(id1, results[0].sessionID)
        self.assertEqual(id1, results[1].sessionID)

        #Delete entry
        query = UserResults.query(UserResults.sessionID == id1).fetch(keys_only=True)
        ndb.delete_multi(query)

        #Retest to check if it's still there
        #Get User Results, filter by id
        query = UserResults.query(UserResults.sessionID == id1)
        results = query.fetch()

        #Check to see if none was returned
        self.assertEqual(0, len(results))