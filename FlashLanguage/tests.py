"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

NOTE: I was having problems running "manage.py test" for this project. Something to do with my virtual environment.
What I did was copy all this test code into another project and ran them there instead.
I could use some more experience in this area.

Testbed DOC: https://cloud.google.com/appengine/docs/python/tools/localunittesting

Alternative Django route: https://docs.djangoproject.com/en/dev/topics/testing/overview/
"""
import random
import string
import unittest
from models import Word, UserResults, PractiseSession, Tests
from google.appengine.ext import testbed
from google.appengine.ext import ndb
import datetime

def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


#Unit tests for Word model
class WordTestCases(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub(Word)

    def tearDown(self):
        self.testbed.deactivate()

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
class PractiseSessionTestCases(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub(PractiseSession)

    def tearDown(self):
        self.testbed.deactivate()

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
class UserResultsTestCases(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub(UserResults)

    def tearDown(self):
        self.testbed.deactivate()

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


#Unit tests for Tests model
class TestsTestCases(unittest.TestCase):

    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub(Tests)

    def tearDown(self):
        self.testbed.deactivate()

    #Test Test.put()
    def test_insert_entity(self):
        Tests().put()
        self.assertEqual(1, len(Tests.query().fetch(2)))

    #Test Tests filter by test name and language
    def test_filter_by_name_language(self):
        #Create test
        wordlist = ['Hi', 'Welcome', 'Good Evening', 'Good Morning', 'Hello', 'Excuse me (formal)']

        Tests(languageName='Italian',
              testName='Italian Test 1',
              startDate=datetime.datetime.now(),
              endDate=datetime.datetime.now() + datetime.timedelta(days=1),
              attempts=1,
              questions=wordlist).put()

        Tests(languageName='French',
              testName='French Test 1',
              startDate=datetime.datetime.now(),
              endDate=datetime.datetime.now() + datetime.timedelta(days=1),
              attempts=1,
              questions=wordlist).put()

        #Get italian test
        query = Tests.query(Tests.languageName == 'Italian', Tests.testName == 'Italian Test 1')
        results = query.fetch()

        #Check to see if only 1 result was returned
        self.assertEqual(1, len(results))
        #Check if the word is Italian language
        self.assertEqual('Italian', results[0].languageName)
        self.assertEqual('Italian Test 1', results[0].testName)

    #Test Tests filter by language and date
    def test_filter_by_language_and_date(self):
        #Create test
        wordlist = ['Hi', 'Welcome', 'Good Evening', 'Good Morning', 'Hello', 'Excuse me (formal)']

        #This test starts now and ends 1 day from now
        Tests(languageName='Italian',
              testName='Italian Test 1',
              startDate=datetime.datetime.now(),
              endDate=datetime.datetime.now() + datetime.timedelta(days=1),
              attempts=1,
              questions=wordlist).put()

        #This test starts tomorrow and ends 2 days from now
        Tests(languageName='French',
              testName='French Test 1',
              startDate=datetime.datetime.now() + datetime.timedelta(days=1),
              endDate=datetime.datetime.now() + datetime.timedelta(days=2),
              attempts=1,
              questions=wordlist).put()

        current_date = datetime.datetime.now()
        #Get tests for current date
        #Note I need a for loop because I wasn't able to compare both dates in the query. Not sure why this is.
        query = Tests.query(Tests.languageName == 'Italian', Tests.startDate <= current_date)
        results = query.fetch()
        valid_tests = []
        for test in results:
            if test.endDate > current_date:
                valid_tests.append(test)

        #Check to see if only 1 result was returned
        self.assertEqual(1, len(valid_tests))
        #Check if the word is Italian language
        self.assertEqual('Italian', valid_tests[0].languageName)
        #Check if the word is of 2 difficulty
        self.assertEqual('Italian Test 1', valid_tests[0].testName)

    #Delete test by name and language
    def test_delete_by_name_language(self):
        #Create test
        wordlist = ['Hi', 'Welcome', 'Good Evening', 'Good Morning', 'Hello', 'Excuse me (formal)']

        #This test starts now and ends 1 day from now
        Tests(languageName='Italian',
              testName='Italian Test 1',
              startDate=datetime.datetime.now(),
              endDate=datetime.datetime.now() + datetime.timedelta(days=1),
              attempts=1,
              questions=wordlist).put()

        #This test starts tomorrow and ends 2 days from now
        Tests(languageName='French',
              testName='French Test 1',
              startDate=datetime.datetime.now() + datetime.timedelta(days=1),
              endDate=datetime.datetime.now() + datetime.timedelta(days=2),
              attempts=1,
              questions=wordlist).put()

        #Get italian test, filter by language and name
        query = Tests.query(Tests.languageName == 'Italian', Tests.testName == 'Italian Test 1')
        results = query.fetch()

        #Check to see if 2 results was returned
        self.assertEqual(1, len(results))
        #Check the language and name
        self.assertEqual('Italian', results[0].languageName)
        self.assertEqual('Italian Test 1', results[1].testName)

        #Delete entry
        query = Tests.query(Tests.languageName == 'Italian', Tests.testName == 'Italian Test 1').fetch(keys_only=True)
        ndb.delete_multi(query)

        #Retest to check if it's still there
        #Get italian test, filter by language and name
        query = Tests.query(Tests.languageName == 'Italian', Tests.testName == 'Italian Test 1')
        results = query.fetch()

        #Check to see if none was returned
        self.assertEqual(0, len(results))


if __name__ == '__main__':
    unittest.main()