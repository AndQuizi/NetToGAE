# -*- coding: utf-8 -*-
import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'NetToGAE.settings'
import random
import string
from random import shuffle
from webapp2_extras import sessions
from google.appengine.ext import ndb
import jinja2
import webapp2
from google.appengine.api import users
from django.conf import settings
from FlashLanguage.models import Word, UserResults, PractiseSession, Language, StudentCourses, Tests, TestSession, \
    StudentTests
import datetime
import time

settings._target = None

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Need this for using session keys
# TODO: Change this later
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}



# Accepts string and returns a number representing difficulty
def get_difficulty_rating(diff):
    if diff == "Beginner":
        diff = 1
    elif diff == "Intermediate":
        diff = 2
    else:
        diff = 3
    return diff


#Called on first practise question
#Returns all words to be used in that practise instance
def get_words(language, diff):
    diffNum = get_difficulty_rating(diff)
    #Get words from datastore with chosen language and difficulty
    word_query = Word.query(Word.languageName == language, Word.difficulty == diffNum)
    #TODO: Only fetch about 20 when more words are added to DB
    words = word_query.fetch()
    return words


#Returns a word based on its translation
def get_word_from_translation(translation):
    word_query = Word.query(Word.translatedWord == translation)
    words = word_query.fetch(1)
    return words


#Accepts list of english words
#Returns a list of translated words
def translate_list(wordList, lang):
    returnList = []
    for word in wordList:
        word_query = Word.query(Word.englishWord == word, Word.languageName == lang).fetch().pop()
        returnList.append(word_query.translatedWord)
    return returnList


#Called on first practise question
#Returns words to be used as answer choices
#Does not return the current word
def get_choices(language, diff, currWord):
    diffNum = get_difficulty_rating(diff)
    choice_query = Word.query(Word.languageName == language, Word.difficulty == diffNum,
                              Word.translatedWord != currWord.translatedWord)
    words = choice_query.fetch()
    shuffle(words)
    return words


#Called on first test question
#Returns words to be used as answer choices
#Does not return the current word
def get_test_choices(language, diff, currWord):
    choice_query = Word.query(Word.languageName == language, Word.difficulty == diff,
                              Word.translatedWord != currWord.translatedWord)
    words = choice_query.fetch()
    shuffle(words)
    return words


#http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
#Returns a random string of size 12
#Used to generate a temporary key to identify the current practise session
def id_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


#Homepage
class MainPage(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/Default.html')
        self.response.write(template.render())


#Italian Page
class Italian(webapp2.RequestHandler):
    #It is my understanding I need this "dispatch" and "session"  functions to use session variables.
    #Removing either of these functions will cause runtime a error
    #I may find an easier way to do this later
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def get(self):
        self.session['Language'] = 'Italian'
        template = JINJA_ENVIRONMENT.get_template('templates/Italian.html')
        self.response.write(template.render())


#French Page
class French(webapp2.RequestHandler):
    #It is my understanding I need this "dispatch" and "session"  functions to use session variables.
    #Removing either of these functions will cause runtime a error
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def get(self):
        self.session['Language'] = 'French'
        template = JINJA_ENVIRONMENT.get_template('templates/French.html')
        self.response.write(template.render())


#About page
class About(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/About.html')
        self.response.write(template.render())


#Contact page
class Contact(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/Contact.html')
        self.response.write(template.render())


#Practise intro page
class PractiseIntro(webapp2.RequestHandler):
    #It is my understanding I need this "dispatch" and "session"  functions to use session variables.
    #Removing either of these functions will cause runtime a error
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def get(self):
        lang = self.session.get('Language')

        #used to identify the current practise session
        #this is a workaround to a problem relating to session keys
        practiseKey = id_generator()
        self.session['practiseKey'] = practiseKey

        template_values = {
            'language': lang,
        }
        template = JINJA_ENVIRONMENT.get_template('templates/PractiseIntro.html')
        self.response.write(template.render(template_values))


#Practise page, includes practise results
#Uses POST
#This class encompasses all of practise mode
#TODO: BUG: There is a .pop() bug where the Practise Session can't get results from the datastore
#TODO: This is due to either form double clicking (this may screw up datastore consistency)
#TODO: Or because I am deleting a Practise Session entity then immediately adding a new one and then reloading the page
#TODO: It is a hard bug to reproduce sometimes. I havn't seen it in a while.
class PractisePage(webapp2.RequestHandler):
    #It is my understanding I need this "dispatch" and "session"  functions to use session variables.
    #Removing either of these functions will cause runtime a error
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def post(self):
        #Language for current practise session
        lang = self.session.get('Language')

        #Session key used to identify practice session
        session_key = self.session.get('practiseKey')

        current_word = None
        score = 0

        #If it's the first question
        #Initializes question queue and displays first question
        if self.request.get('diffChoice'):
            #Delete any previous entries with this key
            prevous_session = UserResults.query(UserResults.sessionID == session_key).fetch(keys_only=True)
            ndb.delete_multi(prevous_session)
            #Difficulty choice
            diff = self.request.get('diffChoice')

            #Get words/questions for chosen difficulty
            words = get_words(lang, diff)
            shuffle(words)

            #Get first word
            current_word = words.pop()

            #Put rest of words/question in list (acts as a Queue)
            word_list = []
            for word in words:
                word_list.append(word.translatedWord)

            #Save current session ID, difficulty, word queue, score, and current question
            PractiseSession(sessionID=session_key,
                            difficulty=diff,
                            wordStrings=word_list,
                            score=0,
                            currWord=current_word.translatedWord,
                            questionNumber=1).put()

            #Get 3 other false answers
            choices = get_choices(lang, diff, current_word)

            #Randomize choices
            choice_list = []
            choice_list.append(choices.pop())
            choice_list.append(choices.pop())
            choice_list.append(choices.pop())
            choice_list.append(current_word)
            shuffle(choice_list)

            #Values for template
            template_values = {
                'currWord': current_word,
                'choice1': choice_list.pop(),
                'choice2': choice_list.pop(),
                'choice3': choice_list.pop(),
                'choice4': choice_list.pop(),
                'score': score,
            }
            template = JINJA_ENVIRONMENT.get_template('templates/PractisePage.html')
            self.response.write(template.render(template_values))

        #If the user clicks end practise button
        #Ends current practise session and displays results
        elif self.request.get('endPractise'):
            #Get information on current session
            practise_query = PractiseSession.query(PractiseSession.sessionID == session_key)
            practise_state = practise_query.fetch()
            if len(practise_state) != 0:
                practise_state = practise_state.pop()
                score = practise_state.score

                #Get user results
                user_result_query = UserResults.query(UserResults.sessionID == session_key).order(
                    UserResults.questionNumber)
                results = user_result_query.fetch()

                #Display results
                template_values = {
                    'results': results,
                    'score': score,
                    'questionNumber': len(results),
                }
                #Delete previous entries of this practise session
                practise_query = PractiseSession.query(PractiseSession.sessionID == session_key).fetch(keys_only=True)
                ndb.delete_multi(practise_query)

                result_query = UserResults.query(UserResults.sessionID == session_key).fetch(keys_only=True)
                ndb.delete_multi(result_query)

                template = JINJA_ENVIRONMENT.get_template('templates/PractiseResults.html')
                self.response.write(template.render(template_values))

            #This only calls when the user refreshes the page on the results screen, or that TODO bug occured
            else:
                template = JINJA_ENVIRONMENT.get_template('templates/Default.html')
                self.response.write(template.render())

        #If the user clicks the Skip button
        #Skips current word and displays new one
        elif self.request.get('skipQuestion'):
            #Get information on current session
            practise_query = PractiseSession.query(PractiseSession.sessionID == session_key)
            practise_state = practise_query.fetch().pop()

            #Get the word that was skipped
            word = practise_state.currWord
            word_list = practise_state.wordStrings

            #Add skipped word back to queue
            word_list.insert(0, word)
            score = practise_state.score

            #Get more information on current session
            diff = practise_state.difficulty
            question_number = practise_state.questionNumber

            #Get a new word for the next question
            current_word = get_word_from_translation(word_list.pop()).pop()
            translation = current_word.translatedWord

            #Delete previous entries of this practise session
            practise_query = PractiseSession.query(PractiseSession.sessionID == session_key).fetch(keys_only=True)
            ndb.delete_multi(practise_query)

            #Save current practise session
            PractiseSession(sessionID=session_key,
                            difficulty=diff,
                            wordStrings=word_list,
                            score=score,
                            currWord=translation,
                            questionNumber=question_number).put()

            #Get 3 other false answers
            choices = get_choices(lang, diff, current_word)

            #Randomize choices
            choice_list = []
            choice_list.append(choices.pop())
            choice_list.append(choices.pop())
            choice_list.append(choices.pop())
            choice_list.append(current_word)
            shuffle(choice_list)

            #Values for template
            template_values = {
                'currWord': current_word,
                'choice1': choice_list.pop(),
                'choice2': choice_list.pop(),
                'choice3': choice_list.pop(),
                'choice4': choice_list.pop(),
                'score': score,
            }
            template = JINJA_ENVIRONMENT.get_template('templates/PractisePage.html')
            self.response.write(template.render(template_values))

        #Called when user clicks an answer
        #Checks answer and displays next question
        elif self.request.get('answerChoice'):
            #The users answer
            choice = self.request.get('answerChoice')


            #Get information on current session
            practise_query = PractiseSession.query(PractiseSession.sessionID == session_key)
            practise_state = practise_query.fetch()
            if len(practise_state) != 0:
                practise_state = practise_state.pop()
                diff = practise_state.difficulty
                prevWord = practise_state.currWord
                question_number = practise_state.questionNumber
                score = practise_state.score

                #If the user is correct, increment score
                if prevWord == choice:
                    score += 1

                last_word = get_word_from_translation(prevWord).pop().englishWord

                #Save user results
                UserResults(sessionID=session_key,
                            questionNumber=question_number,
                            word=last_word,
                            userAnswer=choice,
                            correctAnswer=prevWord).put()

                #Increment question number and get question queue
                question_number += 1
                word_list = practise_state.wordStrings

                #If the question queue is not empty, get next word
                if word_list:
                    #Get next word
                    current_word = get_word_from_translation(word_list.pop()).pop()
                    translation = current_word.translatedWord

                    #Delete previous entries of current session
                    practise_query = PractiseSession.query(PractiseSession.sessionID == session_key).fetch(
                        keys_only=True)
                    ndb.delete_multi(practise_query)

                    #Save new current state of practise session
                    PractiseSession(sessionID=session_key,
                                    difficulty=diff,
                                    wordStrings=word_list,
                                    score=score,
                                    currWord=translation,
                                    questionNumber=question_number).put()

                    #Get 3 other false answers
                    choices = get_choices(lang, diff, current_word)

                    #Randomize choices
                    choice_list = []
                    choice_list.append(choices.pop())
                    choice_list.append(choices.pop())
                    choice_list.append(choices.pop())
                    choice_list.append(current_word)
                    shuffle(choice_list)

                    #Values for template
                    template_values = {
                        'currWord': current_word,
                        'choice1': choice_list.pop(),
                        'choice2': choice_list.pop(),
                        'choice3': choice_list.pop(),
                        'choice4': choice_list.pop(),
                        'score': score,
                    }
                    template = JINJA_ENVIRONMENT.get_template('templates/PractisePage.html')
                    self.response.write(template.render(template_values))

                #If the question queue is empty, display result page
                else:
                    #Get user results, order by question number
                    user_result_query = UserResults.query(UserResults.sessionID == session_key).order(
                        UserResults.questionNumber)
                    results = user_result_query.fetch()

                    #Values for template
                    #NOTICE: The last question answered does not appear in "results" list
                    #To workaround this I manually add the last questions information to template
                    template_values = {
                        'results': results,
                        'score': score,
                        'questionNumber': question_number - 1,
                        'answer': last_word,
                        'choice': choice,
                        'prevWord': prevWord,
                    }
                    #Deletes all practise sessions and user results saved in the datastore
                    practise_query = PractiseSession.query(PractiseSession.sessionID == session_key).fetch(
                        keys_only=True)
                    ndb.delete_multi(practise_query)

                    result_query = UserResults.query(UserResults.sessionID == session_key).fetch(keys_only=True)
                    ndb.delete_multi(result_query)

                    template = JINJA_ENVIRONMENT.get_template('templates/PractiseResults.html')
                    self.response.write(template.render(template_values))
            #This only calls when the user refreshes the page on the results screen, or that TODO bug occured
            else:
                template = JINJA_ENVIRONMENT.get_template('templates/Default.html')
                self.response.write(template.render())


#Test intro page, includes Course Register page
#Checks if user is signed up for course and functions accordingly
class TestIntro(webapp2.RequestHandler):
    #It is my understanding I need this "dispatch" and "session"  functions to use session variables.
    #Removing either of these functions will cause runtime a error
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def get(self):
        lang = self.session.get('Language')
        if lang:
            user = users.get_current_user()
            login_url = users.create_login_url(self.request.path)
            logout_url = users.create_logout_url(self.request.path)
            #If user is signed in
            if user:
                template_values = {
                    'language': lang,
                    'user': user,
                    'login_url': login_url,
                    'logout_url': logout_url,
                }
                query = StudentCourses.query(StudentCourses.studentID == user.user_id()).fetch()

                #The student never signed up for a course before
                if len(query) == 0:
                    template = JINJA_ENVIRONMENT.get_template('templates/CourseRegister.html')
                    self.response.write(template.render(template_values))

                #If the user is signing up for French
                elif lang == "French":
                    #The user is signed up
                    if query[0].french:
                        testKey = id_generator()
                        self.session['testKey'] = testKey

                        #Get current time
                        current_date = datetime.datetime.now()
                        #Query tests, filtering start/end dates and language
                        tests = Tests.query(Tests.languageName == lang, Tests.startDate <= current_date).fetch()

                        #BadRequestError: Only one inequality filter per query is supported.
                        #I can't compare the end date directly in the query, so below is a workaround
                        valid_tests = []
                        for test in tests:
                            if test.endDate > current_date:
                                valid_tests.append(test)

                        no_tests_message = ""
                        if len(valid_tests) == 0:
                            no_tests_message = "There are no tests at this time."

                        curr_attempts = []
                        for test in valid_tests:
                            student_test_query = StudentTests.query(StudentTests.testName == test.testName,
                                                                    StudentTests.studentID == user.user_id(),
                                                                    StudentTests.language == lang).fetch()
                            if len(student_test_query) != 0:
                                student_test = student_test_query.pop()
                                curr_attempts.append(student_test.attempts)
                            else:
                                curr_attempts.append(0)

                        template_values = {
                            'language': lang,
                            'user': user,
                            'login_url': login_url,
                            'logout_url': logout_url,
                            'tests': valid_tests,
                            'message': no_tests_message,
                            'attempts': curr_attempts,
                        }

                        template = JINJA_ENVIRONMENT.get_template('templates/TestIntro.html')
                        self.response.write(template.render(template_values))
                    #The user is not signed up
                    else:
                        template = JINJA_ENVIRONMENT.get_template('templates/CourseRegister.html')
                        self.response.write(template.render(template_values))

                #If the user is signing up for Italian
                else:
                    #The user is signed up
                    if query[0].italian:
                        testKey = id_generator()
                        self.session['testKey'] = testKey

                        #Get current time
                        current_date = datetime.datetime.now()
                        #Query tests, filtering start/end dates and language
                        tests = Tests.query(Tests.languageName == lang, Tests.startDate <= current_date).fetch()

                        #BadRequestError: Only one inequality filter per query is supported.
                        #I can't compare the end date directly in the query, so below is a workaround
                        valid_tests = []
                        for test in tests:
                            if test.endDate > current_date:
                                valid_tests.append(test)

                        no_tests_message = ""
                        if len(valid_tests) == 0:
                            no_tests_message = "There are no tests at this time."

                        curr_attempts = []
                        for test in valid_tests:
                            student_test_query = StudentTests.query(StudentTests.testName == test.testName,
                                                                    StudentTests.studentID == user.user_id(),
                                                                    StudentTests.language == lang).fetch()
                            if len(student_test_query) != 0:
                                student_test = student_test_query.pop()
                                curr_attempts.append(student_test.attempts)
                            else:
                                curr_attempts.append(0)

                        template_values = {
                            'language': lang,
                            'user': user,
                            'login_url': login_url,
                            'logout_url': logout_url,
                            'tests': valid_tests,
                            'message': no_tests_message,
                            'attempts': curr_attempts,
                        }

                        template = JINJA_ENVIRONMENT.get_template('templates/TestIntro.html')
                        self.response.write(template.render(template_values))
                    #The user is not signed up
                    else:
                        template = JINJA_ENVIRONMENT.get_template('templates/CourseRegister.html')
                        self.response.write(template.render(template_values))

            #If user is not signed in
            else:
                template_values = {
                    'language': lang,
                    'login_url': login_url,
                    'logout_url': logout_url,
                }
                template = JINJA_ENVIRONMENT.get_template('templates/TestIntro.html')
                self.response.write(template.render(template_values))

        #User navigated to this page without visiting a language first
        else:
            template = JINJA_ENVIRONMENT.get_template('templates/Default.html')
            self.response.write(template.render())

    #The user submitted a course code to sign up for a course
    def post(self):
        #Current language, user, user inputted course code
        lang = self.session.get('Language')
        user = users.get_current_user()
        login_url = users.create_login_url(self.request.path)
        logout_url = users.create_logout_url(self.request.path)
        code = self.request.get('courseCode')

        #Invalid code message
        message = "Invalid course code."
        template_values = {
            'language': lang,
            'user': user,
            'login_url': login_url,
            'logout_url': logout_url,
            'message': message,
        }
        #Get current student courses
        query = StudentCourses.query(StudentCourses.studentID == user.user_id()).fetch()

        #The student never signed up for a course before
        if len(query) == 0:
            if lang == "French":
                #Get French course code
                course_code = Language.query(Language.languageName == "French").fetch().pop().courseCode

                #If user code is same as real code
                #Signs user up and redirects to test intro page
                if code == course_code:
                    StudentCourses(studentID=user.user_id(),
                                   french=True).put()

                    testKey = id_generator()
                    self.session['testKey'] = testKey

                    #Get current time
                    current_date = datetime.datetime.now()
                    #Query tests, filtering start/end dates and language
                    tests = Tests.query(Tests.languageName == lang, Tests.startDate <= current_date).fetch()

                    #BadRequestError: Only one inequality filter per query is supported.
                    #I can't compare the end date directly in the query, so below is a workaround
                    valid_tests = []
                    for test in tests:
                        if test.endDate > current_date:
                            valid_tests.append(test)

                    no_tests_message = ""
                    if len(valid_tests) == 0:
                        no_tests_message = "There are no tests at this time."

                    curr_attempts = []
                    for test in valid_tests:
                        student_test_query = StudentTests.query(StudentTests.testName == test.testName,
                                                                StudentTests.studentID == user.user_id(),
                                                                StudentTests.language == lang).fetch()
                        if len(student_test_query) != 0:
                            student_test = student_test_query.pop()
                            curr_attempts.append(student_test.attempts)
                        else:
                            curr_attempts.append(0)

                    template_values = {
                        'language': lang,
                        'user': user,
                        'login_url': login_url,
                        'logout_url': logout_url,
                        'tests': valid_tests,
                        'message': no_tests_message,
                        'attempts': curr_attempts,
                    }

                    template = JINJA_ENVIRONMENT.get_template('templates/TestIntro.html')
                    self.response.write(template.render(template_values))

                #Invalid course code
                else:
                    template = JINJA_ENVIRONMENT.get_template('templates/CourseRegister.html')
                    self.response.write(template.render(template_values))

            if lang == "Italian":
                #Get Italian course code
                course_code = Language.query(Language.languageName == "Italian").fetch().pop().courseCode

                #If user code is same as real code
                #Signs user up and redirects to test intro page
                if code == course_code:
                    StudentCourses(studentID=user.user_id(),
                                   italian=True).put()
                    testKey = id_generator()

                    #Get current time
                    current_date = datetime.datetime.now()
                    #Query tests, filtering start/end dates and language
                    tests = Tests.query(Tests.languageName == lang, Tests.startDate <= current_date).fetch()

                    #BadRequestError: Only one inequality filter per query is supported.
                    #I can't compare the end date directly in the query, so below is a workaround
                    valid_tests = []
                    for test in tests:
                        if test.endDate > current_date:
                            valid_tests.append(test)

                    no_tests_message = ""
                    if len(valid_tests) == 0:
                        no_tests_message = "There are no tests at this time."

                    curr_attempts = []
                    for test in valid_tests:
                        student_test_query = StudentTests.query(StudentTests.testName == test.testName,
                                                                StudentTests.studentID == user.user_id(),
                                                                StudentTests.language == lang).fetch()
                        if len(student_test_query) != 0:
                            student_test = student_test_query.pop()
                            curr_attempts.append(student_test.attempts)
                        else:
                            curr_attempts.append(0)

                    template_values = {
                        'language': lang,
                        'user': user,
                        'login_url': login_url,
                        'logout_url': logout_url,
                        'tests': valid_tests,
                        'message': no_tests_message,
                        'attempts': curr_attempts,
                    }

                    template = JINJA_ENVIRONMENT.get_template('templates/TestIntro.html')
                    self.response.write(template.render(template_values))

                #Invalid course code
                else:
                    template = JINJA_ENVIRONMENT.get_template('templates/CourseRegister.html')
                    self.response.write(template.render(template_values))

        #The user has signed up for a class before
        #In this case edit already created StudentCourse entity
        else:
            if lang == "French":
                #Get French course code
                course_code = Language.query(Language.languageName == "French").fetch().pop().courseCode

                #If user code is same as real code
                #Signs user up and redirects to test intro page
                if code == course_code:
                    student_course = StudentCourses.query(StudentCourses.studentID == user.user_id()).fetch().pop()
                    student_course.french = True
                    student_course.put()

                    testKey = id_generator()
                    self.session['testKey'] = testKey
                    #Get current time
                    current_date = datetime.datetime.now()
                    #Query tests, filtering start/end dates and language
                    tests = Tests.query(Tests.languageName == lang, Tests.startDate <= current_date).fetch()

                    #BadRequestError: Only one inequality filter per query is supported.
                    #I can't compare the end date directly in the query, so below is a workaround
                    valid_tests = []
                    for test in tests:
                        if test.endDate > current_date:
                            valid_tests.append(test)

                    no_tests_message = ""
                    if len(valid_tests) == 0:
                        no_tests_message = "There are no tests at this time."

                    curr_attempts = []
                    for test in valid_tests:
                        student_test_query = StudentTests.query(StudentTests.testName == test.testName,
                                                                StudentTests.studentID == user.user_id(),
                                                                StudentTests.language == lang).fetch()
                        if len(student_test_query) != 0:
                            student_test = student_test_query.pop()
                            curr_attempts.append(student_test.attempts)
                        else:
                            curr_attempts.append(0)

                    template_values = {
                        'language': lang,
                        'user': user,
                        'login_url': login_url,
                        'logout_url': logout_url,
                        'tests': valid_tests,
                        'message': no_tests_message,
                        'attempts': curr_attempts,
                    }

                    template = JINJA_ENVIRONMENT.get_template('templates/TestIntro.html')
                    self.response.write(template.render(template_values))

                #Invalid course code
                else:
                    template = JINJA_ENVIRONMENT.get_template('templates/CourseRegister.html')
                    self.response.write(template.render(template_values))

            if lang == "Italian":
                #Get Italian course code
                course_code = Language.query(Language.languageName == "Italian").fetch().pop().courseCode

                #If user code is same as real code
                #Signs user up and redirects to test intro page
                if code == course_code:
                    student_course = StudentCourses.query(StudentCourses.studentID == user.user_id()).fetch().pop()
                    student_course.italian = True
                    student_course.put()

                    testKey = id_generator()
                    self.session['testKey'] = testKey

                    #Get current time
                    current_date = datetime.datetime.now()
                    #Query tests, filtering start/end dates and language
                    tests = Tests.query(Tests.languageName == lang, Tests.startDate <= current_date).fetch()

                    #BadRequestError: Only one inequality filter per query is supported.
                    #I can't compare the end date directly in the query, so below is a workaround
                    valid_tests = []
                    for test in tests:
                        if test.endDate > current_date:
                            valid_tests.append(test)

                    no_tests_message = ""
                    if len(valid_tests) == 0:
                        no_tests_message = "There are no tests at this time."

                    curr_attempts = []
                    for test in valid_tests:
                        student_test_query = StudentTests.query(StudentTests.testName == test.testName,
                                                                StudentTests.studentID == user.user_id(),
                                                                StudentTests.language == lang).fetch()
                        if len(student_test_query) != 0:
                            student_test = student_test_query.pop()
                            curr_attempts.append(student_test.attempts)
                        else:
                            curr_attempts.append(0)

                    template_values = {
                        'language': lang,
                        'user': user,
                        'login_url': login_url,
                        'logout_url': logout_url,
                        'tests': valid_tests,
                        'message': no_tests_message,
                        'attempts': curr_attempts,
                    }

                    template = JINJA_ENVIRONMENT.get_template('templates/TestIntro.html')
                    self.response.write(template.render(template_values))

                #Invalid course code
                else:
                    template = JINJA_ENVIRONMENT.get_template('templates/CourseRegister.html')
                    self.response.write(template.render(template_values))


#Test page, includes test results
#Uses POST
#This class encompasses all of test mode
class TestPage(webapp2.RequestHandler):
    #It is my understanding I need this "dispatch" and "session"  functions to use session variables.
    #Removing either of these functions will cause runtime a error
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

    def post(self):
        #Language for current practise session
        lang = self.session.get('Language')
        user = users.get_current_user()

        current_word = None
        score = 0

        #If it's the first question
        #Initializes question queue and displays first question
        if self.request.get('testChoice'):
            #Delete any old results
            result_query = UserResults.query(UserResults.sessionID == user.user_id()).fetch(keys_only=True)
            ndb.delete_multi(result_query)

            #Test choice
            test_choice = self.request.get('testChoice')
            query = Tests.query(Tests.testName == test_choice, Tests.languageName == lang).fetch().pop()

            #Check is student didn't max their attempts
            student_test_query = StudentTests.query(StudentTests.studentID == user.user_id(),
                                                    StudentTests.testName == test_choice,
                                                    StudentTests.language == lang).fetch()
            can_take = True

            #The student never took this test before
            if len(student_test_query) == 0:
                StudentTests(studentID=user.user_id(),
                             testName=test_choice,
                             language=lang,
                             attempts=1,
                             score=0).put()

            #The student took this test before
            #Check attempts and function accordingly
            else:
                student_test = student_test_query.pop()
                current_attempts = student_test.attempts

                #The user did not max out their attempts
                if current_attempts < query.attempts:
                    student_test.attempts += 1
                    student_test.put()

                #The user maxed out their attempts
                else:
                    can_take = False

            #The user can take the test
            if can_take:
                #Get words/questions for chosen test
                words = query.questions
                shuffle(words)
                question_length = len(words)

                words = translate_list(words, lang)
                #Get first word
                current_word = get_word_from_translation(words.pop()).pop()

                #Save current session ID, difficulty, word queue, score, and current question
                TestSession(sessionID=user.user_id(),
                            totalQuestions=question_length,
                            wordStrings=words,
                            score=0,
                            currWord=current_word.translatedWord,
                            questionNumber=1,
                            testName=test_choice).put()

                #Get 3 other false answers of same difficulty
                choices = get_test_choices(lang, current_word.difficulty, current_word)

                #Randomize choices
                choice_list = []
                choice_list.append(choices.pop())
                choice_list.append(choices.pop())
                choice_list.append(choices.pop())
                choice_list.append(current_word)
                shuffle(choice_list)

                #Values for template
                template_values = {
                    'currWord': current_word,
                    'choice1': choice_list.pop(),
                    'choice2': choice_list.pop(),
                    'choice3': choice_list.pop(),
                    'choice4': choice_list.pop(),
                    'score': score,
                    'max_questions': question_length,
                }
                template = JINJA_ENVIRONMENT.get_template('templates/TestPage.html')
                self.response.write(template.render(template_values))

            #User maxed their attempts
            else:
                self.response.write("Cannot take test. Attempts have been maxed.")

        #If the user clicks the Skip button
        #Skips current word and displays new one
        elif self.request.get('skipQuestion'):
            #Get information on current session
            test_query = TestSession.query(TestSession.sessionID == user.user_id())
            test_state = test_query.fetch().pop()

            #Get the word that was skipped
            word = test_state.currWord
            word_list = test_state.wordStrings

            #Add skipped word back to queue
            word_list.insert(0, word)
            score = test_state.score

            #Get more information on current session
            test_choice = test_state.totalQuestions
            question_number = test_state.questionNumber
            test_name = test_state.testName

            #Get a new word for the next question
            current_word = get_word_from_translation(word_list.pop()).pop()
            translation = current_word.translatedWord

            #Delete previous entries of this practise session
            test_query = TestSession.query(TestSession.sessionID == user.user_id()).fetch(keys_only=True)
            ndb.delete_multi(test_query)

            #Save current practise session
            TestSession(sessionID=user.user_id(),
                        totalQuestions=test_choice,
                        wordStrings=word_list,
                        score=score,
                        currWord=translation,
                        questionNumber=question_number,
                        testName=test_name).put()

            #Get 3 other false answers
            choices = get_test_choices(lang, current_word.difficulty, current_word)

            #Randomize choices
            choice_list = []
            choice_list.append(choices.pop())
            choice_list.append(choices.pop())
            choice_list.append(choices.pop())
            choice_list.append(current_word)
            shuffle(choice_list)

            #Values for template
            template_values = {
                'currWord': current_word,
                'choice1': choice_list.pop(),
                'choice2': choice_list.pop(),
                'choice3': choice_list.pop(),
                'choice4': choice_list.pop(),
                'score': score,
                'max_questions': test_choice,
            }
            template = JINJA_ENVIRONMENT.get_template('templates/TestPage.html')
            self.response.write(template.render(template_values))

        #Called when user clicks an answer
        #Checks answer and displays next question
        elif self.request.get('answerChoice'):
            #The users answer
            choice = self.request.get('answerChoice')

            #Get information on current session
            test_query = TestSession.query(TestSession.sessionID == user.user_id())
            test_state = test_query.fetch()
            if len(test_state) != 0:
                test_state = test_state.pop()
                test_choice = test_state.totalQuestions
                test_name = test_state.testName
                prevWord = test_state.currWord
                question_number = test_state.questionNumber
                score = test_state.score

                #If the user is correct, increment score
                if prevWord == choice:
                    score += 1

                last_word = get_word_from_translation(prevWord).pop().englishWord

                #Save user results
                UserResults(sessionID=user.user_id(),
                            questionNumber=question_number,
                            word=last_word,
                            userAnswer=choice,
                            correctAnswer=prevWord).put()

                #Increment question number and get question queue
                question_number += 1
                word_list = test_state.wordStrings

                #If the question queue is not empty, get next word
                if word_list:
                    #Get next word
                    current_word = get_word_from_translation(word_list.pop()).pop()
                    translation = current_word.translatedWord

                    #Delete previous entries of current session
                    test_query = TestSession.query(TestSession.sessionID == user.user_id()).fetch(keys_only=True)
                    ndb.delete_multi(test_query)

                    #Save new current state of practise session
                    TestSession(sessionID=user.user_id(),
                                totalQuestions=test_choice,
                                wordStrings=word_list,
                                score=score,
                                currWord=translation,
                                questionNumber=question_number,
                                testName=test_name).put()

                    #Get 3 other false answers
                    choices = get_test_choices(lang, current_word.difficulty, current_word)

                    #Randomize choices
                    choice_list = []
                    choice_list.append(choices.pop())
                    choice_list.append(choices.pop())
                    choice_list.append(choices.pop())
                    choice_list.append(current_word)
                    shuffle(choice_list)

                    #Values for template
                    template_values = {
                        'currWord': current_word,
                        'choice1': choice_list.pop(),
                        'choice2': choice_list.pop(),
                        'choice3': choice_list.pop(),
                        'choice4': choice_list.pop(),
                        'score': score,
                        'max_questions': test_choice,
                    }
                    template = JINJA_ENVIRONMENT.get_template('templates/TestPage.html')
                    self.response.write(template.render(template_values))

                #If the question queue is empty, display result page
                else:
                    #Get user results, order by question number
                    user_result_query = UserResults.query(UserResults.sessionID == user.user_id()).order(
                        UserResults.questionNumber)
                    results = user_result_query.fetch()

                    #Values for template
                    #NOTICE: The last question answered does not appear in "results" list
                    #To workaround this I manually add the last questions information to template
                    template_values = {
                        'results': results,
                        'score': score,
                        'questionNumber': question_number - 1,
                        'answer': last_word,
                        'choice': choice,
                        'prevWord': prevWord,
                    }

                    test_query = TestSession.query(TestSession.sessionID == user.user_id())
                    test_state = test_query.fetch().pop()
                    test_name = test_state.testName

                    student_test_query = StudentTests.query(StudentTests.studentID == user.user_id(),
                                                            StudentTests.testName == test_name,
                                                            StudentTests.language == lang).fetch()
                    student_test = student_test_query.pop()
                    student_test.score = score
                    student_test.put()

                    #Deletes all practise sessions and user results saved in the datastore
                    test_query = TestSession.query(TestSession.sessionID == user.user_id()).fetch(keys_only=True)
                    ndb.delete_multi(test_query)

                    result_query = UserResults.query(UserResults.sessionID == user.user_id()).fetch(keys_only=True)
                    ndb.delete_multi(result_query)

                    template = JINJA_ENVIRONMENT.get_template('templates/TestResults.html')
                    self.response.write(template.render(template_values))

            #This only calls when the user refreshes the page on the results screen, or that TODO bug occured
            else:
                template = JINJA_ENVIRONMENT.get_template('templates/Default.html')
                self.response.write(template.render())


application = webapp2.WSGIApplication([
                                          ('/', MainPage),
                                          ('/Italian', Italian),
                                          ('/French', French),
                                          ('/About', About),
                                          ('/Contact', Contact),
                                          ('/PractiseIntro', PractiseIntro),
                                          ('/PractisePage', PractisePage),
                                          ('/TestIntro', TestIntro),
                                          ('/TestPage', TestPage),
                                      ], config=config, debug=True)