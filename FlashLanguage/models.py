# -*- coding: utf-8 -*-
from django.db import models
from google.appengine.api import users
from google.appengine.ext import ndb

#A model used to store user results for practise mode
class UserResults(ndb.Model):
    sessionID = ndb.StringProperty(required=True)
    questionNumber = ndb.IntegerProperty(required=True)
    word = ndb.StringProperty(required=True)
    userAnswer = ndb.StringProperty(required=True)
    correctAnswer = ndb.StringProperty(required=True)




#A model used to keep track of the users current practise session
class PractiseSession(ndb.Model):
    sessionID = ndb.StringProperty(required=True)
    difficulty = ndb.StringProperty(required=True)
    wordStrings = ndb.StringProperty(repeated=True)
    score = ndb.IntegerProperty(required=True)
    currWord = ndb.StringProperty(required=True)
    questionNumber = ndb.IntegerProperty(required=True)


#A model used to keep track of the users current test session
#Almost the same as PractiseSession, just one property difference
class TestSession(ndb.Model):
    sessionID = ndb.StringProperty(required=True)
    totalQuestions = ndb.IntegerProperty(required=True)
    wordStrings = ndb.StringProperty(repeated=True)
    score = ndb.IntegerProperty(required=True)
    currWord = ndb.StringProperty(required=True)
    questionNumber = ndb.IntegerProperty(required=True)

#Language types
class Language(ndb.Model):
    languageName = ndb.StringProperty(required=True)
    courseCode = ndb.StringProperty(required=True)

    def storeInitialLanguage(self):
        Language(languageName='French',
                 courseCode='french123').put()

        Language(languageName='Italian',
                 courseCode='italian123').put()


#A model for holding words, their translation, and difficulty
class Word(ndb.Model):
    englishWord = ndb.StringProperty(required=True)
    imagePath = ndb.StringProperty(required=True)
    languageName = ndb.StringProperty(required=True)
    translatedWord = ndb.StringProperty(required=True)
    difficulty = ndb.IntegerProperty(default=1)

    def store_initial_data_italian(self):
        Word(englishWord='Hi',
             imagePath='hello.jpg',
             languageName='Italian',
             translatedWord='Ciao',
             difficulty=1).put()
        Word(englishWord='Good Evening',
             imagePath='good_evening.jpg',
             languageName='Italian',
             translatedWord='Buonasera',
             difficulty=1).put()
        Word(englishWord='Welcome',
             imagePath='welcome.jpg',
             languageName='Italian',
             translatedWord='Benvenuto',
             difficulty=1).put()
        Word(englishWord='Good Morning',
             imagePath='good_morning.jpg',
             languageName='Italian',
             translatedWord='Buongiorno',
             difficulty=1).put()
        Word(englishWord='Hello',
             imagePath='hello.jpg',
             languageName='Italian',
             translatedWord='Salve',
             difficulty=1).put()
        Word(englishWord='Excuse me (formal)',
             imagePath='excuse_me.jpg',
             languageName='Italian',
             translatedWord='Scusi',
             difficulty=1).put()
        Word(englishWord='My name is',
             imagePath='hello_name.jpg',
             languageName='Italian',
             translatedWord='Mi chiamo',
             difficulty=1).put()
        Word(englishWord='Very please to meet you',
             imagePath='meet_you.jpg',
             languageName='Italian',
             translatedWord='Molto lieto',
             difficulty=1).put()

    def store_data_italian_intermediate(self):
        Word(englishWord='Table',
             imagePath='default.jpg',
             languageName='Italian',
             translatedWord='Tavolo',
             difficulty=2).put()
        Word(englishWord='Chair',
             imagePath='default.jpg',
             languageName='Italian',
             translatedWord='Sedia',
             difficulty=2).put()
        Word(englishWord='Hair',
             imagePath='hair.jpg',
             languageName='Italian',
             translatedWord='Capelli',
             difficulty=2).put()
        Word(englishWord='Easter Monday',
             imagePath='easter.jpg',
             languageName='Italian',
             translatedWord='Pasquetta',
             difficulty=2).put()
        Word(englishWord='Here is...',
             imagePath='default.jpg',
             languageName='Italian',
             translatedWord='Ecco',
             difficulty=2).put()
        Word(englishWord='Goodbye (formal)',
             imagePath='goodbye.jpg',
             languageName='Italian',
             translatedWord='ArrivederLa',
             difficulty=2).put()
        Word(englishWord='See you soon',
             imagePath='see_you_soon.jpg',
             languageName='Italian',
             translatedWord='A Presto',
             difficulty=2).put()
        Word(englishWord='Until next time',
             imagePath='goodbye.jpg',
             languageName='Italian',
             translatedWord='Alla prossima',
             difficulty=2).put()
        Word(englishWord='See you',
             imagePath='goodbye.jpg',
             languageName='Italian',
             translatedWord='Ci vediamo',
             difficulty=2).put()
        Word(englishWord='Farewell',
             imagePath='goodbye.jpg',
             languageName='Italian',
             translatedWord='Addio',
             difficulty=2).put()
        Word(englishWord='Uncle',
             imagePath='uncle.jpg',
             languageName='Italian',
             translatedWord='la zio',
             difficulty=2).put()
        Word(englishWord='Eighty',
             imagePath='eighty.jpg',
             languageName='Italian',
             translatedWord='Ottanta',
             difficulty=2).put()
        Word(englishWord='Blue',
             imagePath='blue.jpg',
             languageName='Italian',
             translatedWord='Azzurro',
             difficulty=2).put()

    def store_data_italian_advanced(self):
        Word(englishWord='Sunday I\'m busy',
             imagePath='relaxing.jpg',
             languageName='Italian',
             translatedWord='Domenica ho da fare',
             difficulty=3).put()
        Word(englishWord='In my opinion',
             imagePath='in-my-opinion.jpg',
             languageName='Italian',
             translatedWord='A mio avviso',
             difficulty=3).put()
        Word(englishWord='I agree wholeheartedly',
             imagePath='agree.jpg',
             languageName='Italian',
             translatedWord='Sono assolutamente d’accordo',
             difficulty=3).put()
        Word(englishWord='To be against',
             imagePath='no_pass.jpg',
             languageName='Italian',
             translatedWord='Essere contro',
             difficulty=3).put()
        Word(englishWord='The opposite is true',
             imagePath='default.jpg',
             languageName='Italian',
             translatedWord='è vero il contrari',
             difficulty=3).put()
        Word(englishWord='To be against a plan',
             imagePath='default.jpg',
             languageName='Italian',
             translatedWord='Osteggiare un progetto',
             difficulty=3).put()
        Word(englishWord='Special delivery',
             imagePath='delivery.jpg',
             languageName='Italian',
             translatedWord='l’espresso',
             difficulty=3).put()

    def store_initial_data_french(self):
        Word(englishWord='Hi',
             imagePath='hello.jpg',
             languageName='French',
             translatedWord='Salut',
             difficulty=1).put()
        Word(englishWord='Good Evening',
             imagePath='good_evening.jpg',
             languageName='French',
             translatedWord='Bonsoir',
             difficulty=1).put()
        Word(englishWord='Welcome',
             imagePath='welcome.jpg',
             languageName='French',
             translatedWord='Accueil',
             difficulty=1).put()
        Word(englishWord='Good Morning',
             imagePath='good_morning.jpg',
             languageName='French',
             translatedWord='Bonjour',
             difficulty=1).put()
        Word(englishWord='Excuse me(formal)',
             imagePath='excuse_me.jpg',
             languageName='French',
             translatedWord='Excuse-moi',
             difficulty=1).put()
        Word(englishWord='My name is',
             imagePath='hello_name.jpg',
             languageName='French',
             translatedWord='J ma\'ppelle',
             difficulty=1).put()
        Word(englishWord='Goodbye (formal)',
             imagePath='goodbye.jpg',
             languageName='French',
             translatedWord='Au revoir',
             difficulty=1).put()
        Word(englishWord='Wife',
             imagePath='wife.jpg',
             languageName='French',
             translatedWord='Femme',
             difficulty=1).put()

    def store_data_french_advanced(self):
        Word(englishWord='Until next time',
             imagePath='goodbye.jpg',
             languageName='French',
             translatedWord='Jusqu\'à la prochaine foisc',
             difficulty=3).put()
        Word(englishWord='In my opinion',
             imagePath='default.jpg',
             languageName='French',
             translatedWord='À mon avis',
             difficulty=3).put()
        Word(englishWord='To be against',
             imagePath='no_pass.jpg',
             languageName='French',
             translatedWord='Pour être contre',
             difficulty=3).put()
        Word(englishWord='Sunday I\'m busy',
             imagePath='default.jpg',
             languageName='French',
             translatedWord='Dimanche je suis occupé',
             difficulty=3).put()
        Word(englishWord='Special delivery',
             imagePath='delivery.jpg',
             languageName='French',
             translatedWord='Livraison spéciale',
             difficulty=3).put()
        Word(englishWord='I agree wholeheartedly',
             imagePath='agree.jpg',
             languageName='French',
             translatedWord='Je suis entièrement d\'accord',
             difficulty=3).put()
        Word(englishWord='The opposite is true',
             imagePath='agree.jpg',
             languageName='French',
             translatedWord='L\'inverse est vrai',
             difficulty=3).put()

    def store_data_french_intermediate(self):
        Word(englishWord='Here is...',
             imagePath='default.jpg',
             languageName='French',
             translatedWord='Voici',
             difficulty=2).put()
        Word(englishWord='See you soon',
             imagePath='see_you_soon.jpg',
             languageName='French',
             translatedWord='À bientôt',
             difficulty=2).put()
        Word(englishWord='See you',
             imagePath='goodbye.jpg',
             languageName='French',
             translatedWord='À plus',
             difficulty=2).put()
        Word(englishWord='Farewell',
             imagePath='goodbye.jpg',
             languageName='French',
             translatedWord='Adieu',
             difficulty=2).put()
        Word(englishWord='Brother',
             imagePath='brother.jpg',
             languageName='French',
             translatedWord='Frère',
             difficulty=2).put()
        Word(englishWord='Brother',
             imagePath='brother.jpg',
             languageName='French',
             translatedWord='Frère',
             difficulty=2).put()
        Word(englishWord='Daughter',
             imagePath='daughter.jpg',
             languageName='French',
             translatedWord='Fille',
             difficulty=2).put()
        Word(englishWord='Aunt',
             imagePath='aunt.jpg',
             languageName='French',
             translatedWord='Tante',
             difficulty=2).put()
        Word(englishWord='Fifty',
             imagePath='fifty.jpg',
             languageName='French',
             translatedWord='Cinquante',
             difficulty=2).put()
        Word(englishWord='Eighty',
             imagePath='eighty.jpg',
             languageName='French',
             translatedWord='Quatre-vingts',
             difficulty=2).put()
        Word(englishWord='Sunday',
             imagePath='Sunday.jpg',
             languageName='French',
             translatedWord='Dimanche',
             difficulty=2).put()


#A model for tracking which student is in which course
class StudentCourses(ndb.Model):
    studentID = ndb.StringProperty(required=True)
    french = ndb.BooleanProperty(default=False)
    italian = ndb.BooleanProperty(default=False)


#Questions used to be a StructuredProperty(word)
#It is easier to just leave it as a string
class Tests(ndb.Model):
    languageName = ndb.StringProperty(required=True)
    testName = ndb.StringProperty(required=True)
    startDate = ndb.DateTimeProperty(required=True)
    endDate = ndb.DateTimeProperty(required=True)
    attempts = ndb.IntegerProperty(default=3)
    questions = ndb.StringProperty(repeated=True)


class StudentTests(ndb.Model):
    studentID = ndb.StringProperty(required=True)
    testName = ndb.StringProperty(required=True)
    language = ndb.StringProperty(required=True)
    attempts = ndb.IntegerProperty(default=0)
    score = ndb.IntegerProperty(default=0)