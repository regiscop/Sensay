from datetime import datetime, timedelta
from interaction import Interaction
from question import Question
import linguistics.sentenceanalysis as sa
import linguistics.linguistics as lingua
from wordpresso.main import corpus, corp_scan, corp_get
from constants import *
import requests


# -------------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------
class SendViral(Interaction):  # ok
    def __init__(self, bot, user):
        super().__init__(bot, user)

    def usefulness(self):
        if datetime.now() < datetime.strptime(str(self.user.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=0.1):
            return 0.0
        if self.calls == 0:
            # This interaction never ran before for this user
            return 0.05
        else:
            if self.timesince_last_call() > a_month:  # Every months. I don't want to spam too much my user
                return 0.05
            return 0.0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'start'

        elif self.state == 'start':
            self.time_started = datetime.now()
            self.state = 'wait_a_bit'

        elif self.state == 'wait_a_bit':
            if (datetime.now() - self.time_started).total_seconds() > 5:  # Wait a bit after previous interaction before sending a lot of text
                self.state = 'say'
            
        elif self.state == 'say':
            if self.user.last_channel_per_bot[self.bot.name] != "webchat":
                self.bot.say(self.user, "I would highly appreciate if you recommend me to your friends. Why don't you share/transfer the next text message? So your friends can chat with the Sensay community!!")
                if self.user.last_channel_per_bot[self.bot.name] == "Telegram":
                    self.bot.say(self.user, "Hi my friend, I recommend you to chat with the Sensay Network! It's amazing!: https://t.me/SensayChatBot ")
                elif self.user.last_channel_per_bot[self.bot.name] == "Line":
                    self.bot.say(self.user, "Hi my friend, I recommend you to chat with Sensay Network! It's amazing!: https://line.me/R/ti/p/TBD ")
                elif self.user.last_channel_per_bot[self.bot.name] == "Twilio":
                    self.bot.say(self.user, "Hi my friend, I recommend you to chat with Sensay Network! It's amazing!: here is her phone: +32460TBD")
                elif self.user.last_channel_per_bot[self.bot.name] == "Kik":
                    self.bot.say(self.user, "Hi my friend, I recommend you to chat with Sensay Network! It's amazing!: https://kik.me/TBD")
                elif self.user.last_channel_per_bot[self.bot.name] == "Skype":
                    self.bot.say(self.user, "Hi my friend, I recommend you to chat with Sensay Network! It's amazing!: https://join.skype.com/bot/TBD")
                elif self.user.last_channel_per_bot[self.bot.name] == "Facebook":
                    self.bot.say(self.user, "Hi my friend, I recommend you to chat with Sensay Network! It's amazing!:  http://m.me/SensayChatBot")
                else:
                    self.bot.say(self.user, "Hi my friend, I recommend you to chat with Sensay Network! He is amazing!:  http://m.me/SensayChatBot")
            else:
                self.bot.say(self.user, "I would highly appreciate if you recommend me to your friends. Share the following link with all your friends (http://m.me/SensayChatBot) and maybe, you will meet them @ the activities I organize!!")

            self.state = 'success'
            
        elif self.state == 'success':
            self.bot.launch_interaction(Breath(self.bot, self.user))
            self.state = 'end'
            
        elif self.state == 'failure':
            self.state = 'end'
            
        elif self.state == 'end':
            pass


# ---------------------------------------------------------------------------------------------------------------------
class Breath(Interaction):  # ok
    """ Just wait a bit and slow the discussion a bit to make it more natural when needed"""
    def __init__(self, bot, user):
        super().__init__(bot, user)

    def usefulness(self):
        return 0.0

    def execute(self):
        super().execute()
        if self.state is None:
            self.state = 'start'

        elif self.state == 'start':
            self.start = datetime.now()
            self.state = 'wait_a_bit'

        elif self.state == 'wait_a_bit':
            if (datetime.now() - self.start).total_seconds() < 5:
                return
            else:
                self.state = 'success'
                
        elif self.state == 'success':
            self.bot.remove_possible(self)
            self.state = 'end'
            
        elif self.state == 'end':
            pass


# ---------------------------------------------------------------------------------------------------------------------
class AskQuestion(Interaction):  # ok
    def __init__(self, bot, user):
        super().__init__(bot, user)
        self.time_asked = datetime.now()
        self.time_conf_asked = datetime.now()
        self.query = None
        self.question_local = None

    def usefulness(self):
        return 0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'start'

        elif self.state == 'start':
            self.bot.say(self.user, "Ok, let's start... but first, does your question has to be shared with only your neighbours? (Y = Only locals, N= Skilled community)")
            self.state = 'wait for first answer'
            self.time_asked = datetime.now()
            self.question_local = False

        elif self.state == 'wait for first answer':
            if (datetime.now() - self.time_asked).total_seconds() > 60 * 5:
                self.bot.say(self.user, "Ok, don't hesitate to come back to me later with a question via the menu...")
                self.state = 'failure'
                return

            elif self.bot.inbox[self.user]:

                infos = {}
                for msg in self.bot.inbox[self.user]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))

                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.7:
                        self.bot.say(self.user, lingua.dont_be_so_rude())
                        self.bot.clean_inbox(self.user)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1:
                    self.bot.clean_inbox(self.user)
                    if infos['boolean'] == "true":
                        self.question_local = True
                    self.bot.say(self.user,lingua.ok())
                    if self.user.s_home_location is None:
                        self.bot.launch_interaction(AskLocation(self.bot, self.user))
                        self.state = 'Ask the question after asking location'
                    else:
                        self.bot.say(self.user, "Now, Tell me... What is your question?")
                        self.state = 'wait for answer'
                    return
                else:
                    self.bot.say(self.user, lingua.i_dont_understand_sensay())
                    self.bot.clean_inbox(self.user)
                    return

            if self.bot.inbox[self.user]:
                self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                return
            if self.state == 'wait for first answer' and self.get_state_calls_with_msg() >= 3:
                self.clean_state_calls_with_msg()
                self.state = 'start'
                return
            
        elif self.state == 'Ask the question after asking location':
            self.bot.say(self.user, "Ok,  tell me... What is your question?")
            self.state = 'wait for answer'
            return
            
        elif self.state == 'wait for answer':
            if (datetime.now() - self.time_asked).total_seconds() > 60*5:
                self.bot.say(self.user, "Ok, don't hesitate to come back to me later with a question via the menu...")
                self.state = 'failure'
                return

            elif self.bot.inbox[self.user]:
                infos = {}
                for msg in self.bot.inbox[self.user]:
                    results = corpus.process(msg.text)
                    infos.update({'text': msg.text})
                    infos.update(corp_get(results, 'tone'))

                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.9:
                        self.bot.say(self.user, lingua.dont_be_so_rude())
                        self.bot.clean_inbox(self.user)
                        self.state = 'failure'
                        return

                self.query = Question(infos['text'], self.user)
                self.query.question_local = self.question_local
                if self.query.question_local:
                    self.bot.say(self.user, "The question that will be sent to your neighbours is: " + str(self.query.question) + ". Do you confirm? (y/n)" )
                else:
                    self.bot.say(self.user, "The question that will be sent to the Sensay community is: " + str(self.query.question) + ". Do you confirm? (y/n)")
                self.time_conf_asked = datetime.now()
                self.bot.clean_inbox(self.user)
                self.state = 'wait for confirmation'
                return

            if self.bot.inbox[self.user]:
                self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                return
            if self.state == 'wait for answer' and self.get_state_calls_with_msg() >= 3:
                self.clean_state_calls_with_msg()
                self.state = 'start'
                return
            
        elif self.state == 'wait for confirmation':
            if (datetime.now() - self.time_conf_asked).total_seconds() > wait_for_answer_time:
                self.bot.say(self.user, lingua.you_must_be_busy())
                self.state = 'failure'
                return

            elif self.bot.inbox[self.user]:
                infos = {}
                for msg in self.bot.inbox[self.user]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'tone'))
                if 'tone' in infos:
                    if infos['tone'] == 'rude' and infos['tone_score'] > 0.7:
                        self.bot.say(self.user, lingua.dont_be_so_rude())
                        self.bot.clean_inbox(self.user)
                elif 'boolean' in infos and infos['boolean_score'] > 0.1:
                    self.bot.clean_inbox(self.user)
                    if infos['boolean'] == "true":
                        self.state = 'success'
                        is_not_too_far = lambda u: self.bot.distance(u, self.user, "s_home_location") < 18000.0
                        is_not_the_user = lambda u: u is not self.user
                        users_not_too_far = self.bot.search_if(lambda f: is_not_too_far(f) and is_not_the_user(f))
                        distance = lambda u: self.bot.distance(u, self.user, "s_home_location")
                        ranked = sorted(users_not_too_far, key=distance)
                        if ranked is None or len(ranked) <= 0:
                            self.bot.say(self.user, "Sorry but it seems very few users are currently connected in your area. I will keep you posted when more people are around your place.")
                            self.bot.clean_inbox(self.user)
                            return
                        self.query.to_be_asked = ranked[:10]
                        self.bot.launch_interaction(LoopToAll(self.bot, self.query))
                        self.bot.say(self.user, "Ok, understood! ((( signaling sensay ))) I'm currently looking for a human to help. Stay connected. It might take max 5 minutes...")
                    else:
                        self.state = 'failure'
                        self.bot.say(self.user, "Ok! No probs")
                    self.bot.clean_inbox(self.user)
                    return
                else:
                    self.bot.say(self.user, lingua.i_dont_understand_sensay())
                    self.bot.clean_inbox(self.user)
                    return
            if self.bot.inbox[self.user]:
                self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                return
            if self.state == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                self.state = 'start'
                return
            
        elif self.state == 'success':
            self.bot.launch_interaction(Breath(self.bot, self.user))
            self.state = 'end'
            self.time_asked = datetime.now()
            
        elif self.state == 'failure':
            self.resetting()
            self.state = 'end'
            
        elif self.state == 'end':
            pass


# ----------------------------------------------------------------------------------------------------------------------


class AskLocation(Interaction):  # ok
                        return
    class WelcomeNewUser(Interaction):
        def __init__(self, bot, user):
            super().__init__(bot, user)
            self.start = None

        def usefulness(self):
            if self.user.s_greeted_by_sensay:
                return 0.0
            else:
                return 3.0

        def execute(self):
            super().execute()

            if self.state is None:
                self.state = 'start'

            elif self.state == 'start':
                self.bot.say(self.user, "Welcome to the Sensay network! An opensource collaborative chatbot.")
                self.bot.say(self.user, "Chat now with a helpful human.")
                self.user.s_greeted_by_sensay = True
                self.user.greeted_date_sensay = datetime.now()
                self.bot.clean_inbox(self.user)
                if self.user.last_channel_per_bot[self.bot.name] == "Facebook":
                    try:
                        r = requests.get("https://graph.facebook.com/v2.8/" + self.user.s_numbers['Facebook'] +"?fields=first_name,last_name,gender,timezone&access_token=" + FB_token)
                        self.user.s_name = r.json()['first_name']
                        self.bot.say(self.user, "recorded info {}".format(self.user.s_name))
                        self.user.s_last_name = r.json()['last_name']
                    except:
                        self.bot.launch_interaction(AskName(self.bot, self.user))
                elif self.user.last_channel_per_bot[self.bot.name] == "Twilio":
                    self.user.gender = 'male' # Make sure we don't spend money on Twilio for messages for useless info
                    self.user.s_name = 'Mister X' # Make sure we don't spend money on Twilio for messages for useless info
                else:
                    self.bot.launch_interaction(AskName(self.bot, self.user))
                self.state = 'wait_a_bit'
                self.start = datetime.now()

            elif self.state == 'wait_a_bit':
                if (datetime.now() - self.start).total_seconds() < 2:
                    return
                else:
                    self.state = 'success'

            elif self.state == 'success':
                self.bot.remove_possible(self)
                self.bot.launch_interaction(Breath(self.bot, self.user))
                self.bot.queue_interaction(AskQuestion(self.bot, self.user))
                self.state = 'end'

            elif self.state == 'end':
                pass
    # -----------------------------------------------------------------------------------------------------------------------


    class AskName(Interaction):  # ok
        def __init__(self, bot, user):
            super().__init__(bot, user)
            self.time_asked = None

        def usefulness(self):
            if self.user.s_name:
                return 0.0
            elif not self.launches:
                # We don't know the name and this interaction never ran before
                return 0.5
            elif self.timesince_last_call() < 60*10.0:
                # We still don't know the name but apparently we already asked without success
                return 0.0
            else:
                return 0.5

        def execute(self):
            super().execute()

            if self.state is None:
                self.state = 'start'

            elif self.state == 'start':
                if self.get_state_calls() <= 1:  # because we have to go thru the state "None" before
                    self.bot.say(self.user, lingua.whats_your_name())
                elif self.get_state_calls() <= 2:  # because we have to go thru the state "Failure" "None" before
                    self.bot.say(self.user, "You haven't told me your name yet?")
                elif self.get_state_calls() <= 3:
                    self.bot.say(self.user, "You still don't want to tell me your name?")
                elif self.get_state_calls() <= 4:
                    self.bot.say(self.user, "I guess I will never get to know your name...")
                    # "Do you have privacy concerns???"
                else:
                    self.bot.say(self.user, "As I don't know your name, I will call you Mr. Pink.")
                    self.user.s_name = 'Mr. Pink'
                    self.state = 'success'

                self.state = 'wait for answer'
                self.time_asked = datetime.now()

            elif self.state == 'wait for answer':
                if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                    self.bot.say(self.user, lingua.you_must_be_busy())
                    self.state = 'failure'
                    return

                elif self.bot.inbox[self.user]:
                    infos = {}
                    for msg in self.bot.inbox[self.user]:
                        results = corpus.process(msg.text)
                        infos.update(corp_get(results, 'someone'))
                        infos.update(corp_get(results, 'tone'))
                        infos.update(corp_get(results, 'logic'))
                        if ' ' not in msg.text:
                            infos.update({'any': msg.text, 'any_score': 1})
                        infos.update(corp_get(results, 'any'))

                    if 'tone' in infos:
                        if infos['tone'] == 'rude' and infos['tone_score'] > 0.4:
                            self.bot.say(self.user, lingua.dont_be_so_rude())
                            self.bot.clean_inbox(self.user)
                    if 'someone' in infos and 'logic' in infos and infos['logic'] == "negative":
                        self.bot.say(self.user, "haha! trying to test me? I'm smarter than you think... So... What's your name then?")
                        self.state = 'wait for answer'
                        self.time_asked = datetime.now()
                        self.bot.clean_inbox(self.user)
                        return
                    if 'someone' in infos or 'any' in infos:
                        answer = sa.get_gender_based_on_name(infos['someone'] if 'someone' in infos else infos['any'])
                        if (infos['someone'] if 'someone' in infos else infos['any']).lower() == "Streets":
                            self.bot.say(self.user, "Really?'{}'!. Just like me?. Are you sure I got it right?".format(
                                infos['someone'] if 'someone' in infos else infos['any']))
                            self.state = 'wait for confirmation'
                            self.time_asked = datetime.now()
                            self.bot.clean_inbox(self.user)
                            self.user.s_name = "Streets"
                            if answer is not None and answer['accuracy'] > 95:
                                self.user.gender = answer['gender']
                            else:
                                self.bot.add_again_possible(AskGender(self.bot, self.user))
                            return
                        if answer and answer['samples'] < 1000:
                            self.bot.say(self.user, "Really?'{}'!. That's unusual. Are you sure I got it right?".format(infos['someone'] if 'someone' in infos else infos['any']))
                            self.state = 'wait for confirmation'
                            self.time_asked = datetime.now()
                            self.bot.clean_inbox(self.user)
                            self.user.s_name = infos['someone'] if 'someone' in infos else infos['any']
                            if answer is not None and answer['accuracy'] > 95:
                                self.user.gender = answer['gender']
                            else:
                                self.bot.add_again_possible(AskGender(self.bot, self.user))
                            return
                        elif ('someone_score' in infos and infos['someone_score'] < 0.00001) or ('any' in infos and infos['any_score'] < 0.00001):
                            self.bot.say(self.user,
                                         "It's the first time I meet someone named '{}'!. Are you sure I got it right?".format(
                                             infos['someone'] if 'someone' in infos else infos['any']))
                            self.state = 'wait for confirmation'
                            self.time_asked = datetime.now()
                            self.bot.clean_inbox(self.user)
                            self.user.s_name = infos['someone'] if 'someone' in infos else infos['any']
                            if answer is not None and answer['accuracy'] > 95:
                                self.user.gender = answer['gender']
                            return
                        self.user.s_name = infos['someone'] if 'someone' in infos else infos['any']
                        self.bot.say(self.user, lingua.ok())
                        self.bot.say(self.user, "Nice to meet you, {}!".format(self.user.s_name))
                        self.bot.clean_inbox(self.user)

                        if answer is not None and answer['accuracy'] > 85:
                            self.user.gender = answer['gender']
                        elif answer is not None and answer['accuracy'] > 70:
                            if answer['gender'] == 'female':
                                self.bot.say(self.user, "I know a few {} named like that, but also a {}.".format("girls", "boy"))
                            else:
                                self.bot.say(self.user, "I know a few {} named like that, but also a {}.".format("boys", "girl"))
                            self.bot.launch_interaction(AskGender(self.bot, self.user))
                        else:
                            self.bot.say(self.user, "mmm... I don't know any people named like that.")
                            if answer is not None and answer['accuracy'] > 95:
                                self.user.gender = answer['gender']
                            else:
                                self.bot.launch_interaction(AskGender(self.bot, self.user))
                        self.state = 'success'
                        return
                if self.bot.inbox[self.user]:
                    self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                    return
                if self.state == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                    self.clean_state_calls_with_msg()
                    self.state = 'start'
                    return

            elif self.state == 'wait for confirmation':
                if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                    self.bot.say(self.user, lingua.you_must_be_busy())
                    self.state = 'failure'
                    return

                elif self.bot.inbox[self.user]:
                    infos = {}
                    for msg in self.bot.inbox[self.user]:
                        results = corpus.process(msg.text)
                        infos.update(corp_get(results, 'boolean'))
                        infos.update(corp_get(results, 'tone'))
                        infos.update(corp_get(results, 'someone'))

                    if 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'true':
                        self.bot.say(self.user, "ok! got it! ... then,  nice to meet you, {}!".format(self.user.s_name))
                        self.bot.add_possible(AskGender(self.bot, self.user))
                        self.bot.clean_inbox(self.user)
                        self.state = 'success'
                        return
                    elif 'someone' in infos and 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'false':
                        self.user.s_name = infos['someone']
                        self.bot.say(self.user, "Ok! Understood! Nice to meet you, {}!".format(self.user.s_name))
                        self.bot.add_possible(AskGender(self.bot, self.user))
                        self.bot.clean_inbox(self.user)
                        self.state = 'success'
                        return
                    elif 'boolean' in infos and infos['boolean_score'] > 0 and infos['boolean'] == 'false':
                        self.bot.say(self.user, "Ok! What's your name then?")
                        self.state = 'wait for answer'
                        self.time_asked = datetime.now()
                        self.bot.clean_inbox(self.user)
                        return
                    else:
                        self.bot.say(self.user, "I'm not sure I get it")
                        self.state = 'wait for confirmation'
                        self.time_asked = datetime.now()
                        self.bot.clean_inbox(self.user)
                        return
                if self.bot.inbox[self.user]:
                    self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                    return
                if self.state == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                    self.bot.say(self.user, " '{}'! Did I understand your name correctly?".format(self.user.s_name))
                    self.time_asked = datetime.now()
                    self.clean_state_calls_with_msg()
                    return

            elif self.state == 'success':
                self.bot.remove_possible(self)
                self.bot.launch_interaction(Breath(self.bot, self.user))
                self.state = 'end'

            elif self.state == 'failure':
                self.state = 'end'

            elif self.state == 'end':
                pass
    # ---------------------------------------------------------------------------------------------------------------------


    class AskGender(Interaction):  # ok
        def __init__(self, bot, user):
            super().__init__(bot, user)
            self.time_asked = None

        def usefulness(self):
            if self.user.gender:
                return 0.0
            else:
                return 0.9

        def execute(self):
            super().execute()

            if self.state is None:
                self.state = 'start'

            elif self.state == 'start':
                self.bot.say(self.user, "Are you a male or female?")
                self.state = 'wait for answer'
                self.time_asked = datetime.now()

            elif self.state == 'wait for answer':
                if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                    self.bot.say(self.user, lingua.you_must_be_busy())
                    self.state = 'failure'
                    return

                elif self.bot.inbox[self.user]:
                    infos = {}
                    for msg in self.bot.inbox[self.user]:
                        results = corpus.process(msg.text)
                        infos.update(corp_get(results, 'gender'))
                        infos.update(corp_get(results, 'tone'))

                    if 'tone' in infos:
                        if infos['tone'] == 'rude' and infos['tone_score'] > 0.0:
                            self.bot.say(self.user, lingua.dont_be_so_rude())
                            self.bot.clean_inbox(self.user)
                    if 'gender' in infos and infos['gender_score'] > 0.0:
                        self.user.gender = infos['gender']
                        self.bot.say(self.user, lingua.ok())
                        self.bot.clean_inbox(self.user)
                        self.state = 'success'

                if self.bot.inbox[self.user]:
                    self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                    return
                if self.state == 'wait for answer' and self.get_state_calls_with_msg() >= 3:
                    self.clean_state_calls_with_msg()
                    self.state = 'ask'
                    return

            elif self.state == 'success':
                self.bot.remove_possible(self)
                self.bot.launch_interaction(Breath(self.bot, self.user))
                self.state = 'end'

            elif self.state == 'failure':
                self.resetting()
                self.state = 'end'

            elif self.state == 'end':
                pass
    # ----------------------------------------------------------------------------------------------------------------------
    def __init__(self, bot, user):
        super().__init__(bot, user)

    def usefulness(self):
        if 's_home_location' in self.user.__dict__:
            # We already know!
            return 0.0
        if self.launches and (self.timesince_last_call() < a_day or datetime.now() < datetime.strptime(str(self.user.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=48)):
            return 0.0
        else:
            try:
                return max(self.user.demand_for_info['s_home_location'] / 100000.0, level_start_ask_about)
            except:
                return 0.0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'start'

        elif self.state == 'start':
            if self.user.last_channel_per_bot[self.bot.name] in ["Facebook"]:
                self.bot.say(self.user, "Give me your home location so I can search for help around your home. Please describe me a postal adress with city and zip code. (for example: Caslestreet, 5 14568 state country).")
            elif self.user.last_channel_per_bot[self.bot.name] in ["Telegram", "Line", "Viber"]:
                self.bot.say(self.user, "Give me your home location so I can search for help around your place. Please point me the precise position of where you live with the 'share location' functionality of your app!")
            else:
                self.bot.say(self.user, "Tell me where your home is located so I can search for help around you. Give me your street address! (it's better if you give me your exact street address so I can search very close to your home)")
            self.state = 'wait for answer'
            self.time_asked = datetime.now()

        elif self.state == 'wait for answer':
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                self.bot.say(self.user, lingua.you_must_be_busy())
                self.state = 'failure'
                return

            elif self.bot.inbox[self.user]:
                infos = {}
                for msg in self.bot.inbox[self.user]:
                    if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                        a = msg.text.split("/../")
                        label = {'street-address': sa.get_address_of_location(a[0][4:], a[1][5:])}
                        infos.update(label)
                        infos.update({"lat": a[0][4:], "lng": a[1][5:]})
                        self.user.s_home_location = infos

                    else:
                        reply = sa.get_info(msg.text, 'street-address')
                        if reply:
                            infos.update(reply)
                        else:
                            self.bot.say(self.user, "I didn't recognize your address, can you retype it please?")
                            self.bot.clean_inbox(self.user)
                            self.time_asked = datetime.now()
                            self.state = 'wait for answer'
                            return
                        self.user.s_home_location = reply

                if 'street-address' in infos and 'geometry' in infos and infos['geometry'] == 'APPROXIMATE':
                    self.bot.say(self.user, "Ok, got it, but this is too vague for a precise search. Can you retype your street address please?")
                    self.bot.clean_inbox(self.user)
                    self.user.general_location = reply
                    self.bot.say(self.user, "Wayd developer: Data recorded:" + str(self.user.general_location))
                    self.time_asked = datetime.now()
                    self.user.s_home_location = None
                    self.state = 'wait_for_answer_bis'
                    return

                if 'street-address' in infos:
                    if self.user.last_channel_per_bot[self.bot.name] in ["Facebook"]:
                        self.bot.say(self.user, "Thanks a lot, {}! I did record this location ({}) as your home location. Feel free to type 'location' any time later... :-)".format(
                            self.user.s_name or ("Miss" if self.user.gender == 'female' else "Mister"), str(self.user.s_home_location) ))

                    else:
                        self.bot.say(self.user, "Thanks a lot, {}! I did record this location as your home location. Feel free to use the 'share a point/location' functionality any time later... :-)".format(self.user.s_name or ("Miss" if self.user.gender == 'female' else "Mister")))
                    self.bot.say(self.user, "Wayd developer: Data recorded:" + str(self.user.s_home_location))
                    self.bot.clean_inbox(self.user)
                    self.state = 'success'

            if self.bot.inbox[self.user]:
                self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                return
            if self.state == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                self.state = 'start'
                return

        elif self.state == 'wait_for_answer_bis':
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                self.bot.say(self.user, lingua.you_must_be_busy())
                self.state = 'failure'
                return

            elif self.bot.inbox[self.user]:
                infos = {}
                for msg in self.bot.inbox[self.user]:
                    if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                        a = msg.text.split("/../")
                        label = {'street-address': sa.get_address_of_location(a[0][4:], a[1][5:])}
                        infos.update(label)
                        infos.update({"lat": a[0][4:], "lng": a[1][5:]})
                        self.user.s_home_location = infos
                    else:
                        reply = sa.get_info(msg.text, 'street-address')
                        if reply:
                            infos.update(reply)
                        else:
                            results = corpus.process(msg.text)
                            infos.update(corp_get(results, 'boolean'))
                            infos.update(corp_get(results, 'tone'))
                            infos.update((corp_get(results, 'concern')))

                            if ('boolean' in infos and infos['boolean'] == False) or 'tone' in infos or 'concern' in infos:
                                self.bot.say(self.user, "Ok, I guess you don't want to give you address! Let's continue the discussion anyway but just be aware that it's going to be more difficult to find something cool around you...")
                                self.bot.clean_inbox(self.user)
                                self.state = 'success'
                                return
                            else:
                                self.bot.say(self.user, "I didn't recognize your address, can you retype it please?")
                                self.bot.clean_inbox(self.user)
                                self.time_asked = datetime.now()
                                self.state = 'wait_for_answer_bis'
                                return
                        self.user.s_home_location = reply

                if 'street-address' in infos and 'geometry' in infos and infos['geometry'] == 'APPROXIMATE':
                    self.bot.say(self.user, "Ok, got it, but this is again too vague. Can you retype your street address?")
                    self.bot.clean_inbox(self.user)
                    self.user.general_location = reply
                    self.bot.say(self.user, "Wayd developer: Data recorded:" + str(self.user.general_location))
                    self.time_asked = datetime.now()
                    self.user.s_home_location = None
                    self.state = 'wait_for_answer_bis'
                    return

                if 'street-address' in infos:
                    self.bot.say(self.user, lingua.thanks())
                    self.bot.say(self.user, "Wayd developer: Data recorded:" + str(self.user.s_home_location))
                    self.bot.clean_inbox(self.user)
                    self.state = 'success'

            if self.bot.inbox[self.user]:
                self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                return
            if self.state == 'wait_for_answer_bis' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                self.state = 'start'
                return

        elif self.state == 'success':
            self.bot.remove_possible(self)
            self.bot.say(self.user, "Type 'discuss' to get help. \n Type 'menu' if you are lost.")

            self.bot.launch_interaction(Breath(self.bot, self.user))
            self.state = 'end'

        elif self.state == 'failure':
            self.resetting()
            self.state = 'end'

        elif self.state == 'end':
            pass


class LoopToAll(Interaction):
    def __init__(self, bot, query):
        super().__init__(bot)
        self.query = query
        self.currently_asked = None
        self.tempuser = None

    def usefulness(self):
        return 0.0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'start'
            
        elif self.state == 'start':
            if self.query.to_be_asked is not None and len(self.query.to_be_asked)>0 and self.query.to_be_asked[0] is self.query.user_asked:
                self.query.to_be_asked.pop(0)
                return
            elif self.query.to_be_asked is not None and len(self.query.to_be_asked)>0 and self.query.to_be_asked[0] is not None:
                if self.tempuser is not self.query.to_be_asked[0]:
                    if self.query.to_be_asked[0] is not self.query.user_asked:
                        self.bot.launch_interaction(AskAnswer(self.bot, self.query.to_be_asked[0], self.query))
                    self.tempuser = self.query.to_be_asked[0]
                    return
                else:
                    return
            else:
                self.state = 'success'
                
        elif self.state == 'success':
            self.bot.remove_possible(self)
            self.state = 'end'
            
        elif self.state == 'failure':
            self.bot.remove_possible(self)
            self.state = 'end'
            
        elif self.state == 'end':
            pass
# -----------------------------------------------------------------------------------------------------------------------


class AskFriendContact(Interaction):  # ok
    def __init__(self, bot, user):
        super().__init__(bot, user)

    def usefulness(self):
        if datetime.now() < datetime.strptime(str(self.user.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=0.1):
            return 0.0
        if self.calls == 0:
            # This interaction never ran before for this user
            return 0.05
        else:
            if self.timesince_last_call() > a_day and datetime.now() < datetime.strptime(str(self.user.s_time_of_last_message), '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=36):
                return 0.05
            else:
                return 0.0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'start'
            
        elif self.state == 'start':
            if self.get_state_calls() <= 1:
                self.bot.say(self.user, "I would highly appreciate if you can send me the contact of a friend who might be interested to discuss with me. Please give me his/her mobile phone number (please use international format +xxxxx) or e-mail address and I'll contact him!")
            else:
                self.bot.say(self.user, "I would highly appreciate if you can send me the contact of another friend who might be interested to discuss with me. Please give me his/her mobile phone number(please use international format +xxxxx) or e-mail address and I'll contact him!")
            self.state = 'wait for answer'
            self.time_asked = datetime.now()
            
        elif self.state == 'wait for answer':
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                self.bot.say(self.user, lingua.you_must_be_busy())
                self.state = 'failure'
                return

            elif self.bot.inbox[self.user]:
                infos = {}
                for msg in self.bot.inbox[self.user]:
                    reply = sa.get_info(msg.text, 'email')
                    if reply != {}:
                        infos.update({'email': reply})
                    reply = sa.get_info(msg.text, 'phone')
                    if reply != {}:
                        infos.update({'phone': reply})
                #self.bot.say(self.user, str(reply))
                #self.bot.say(self.user, "Welcome to the Sensay network! An opensource collaborative chatbot.")
                #self.bot.say(self.user, "Chat now with a helpful human")
                if 'email' in infos:
                    if self.bot.search_contacts('Mail', infos['email']) is None:
                        text = "Hi, \n"
                        text += "I'm currently chatting via " + str(self.user.last_channel_per_bot[self.bot.name]) +" with your friend " + str(self.user.s_name or "Mister X") + ".  \n"
                        if self.user.gender == 'female':
                            text += "She"
                        else:
                            text += "He"
                        text += " probably did tell you about the Sensay network " + "he" if self.user.gender == 'male' else "she" + " is in. \n"
                        text += "\n"
                        text += "You can chat directly with a helpful human. We will chat together and, I'll put you in contact with someone who can help you.  \n"
                        text += "You can also chat with people around you interested in willing to practice a foreing language, someone interested in movies, someone interested in cooking, a neighbour willing to start the vegetable gardens, etc...\n"
                        text += "Be prepared to be change the world with Sensay. \n"
                        text += " \n"
                        text += "Let's chat now on Facebook http://m.me/SensayChatBot \n"
                        text += "but also on:   \n"
                        text += "Slack: Available Soon\n"
                        text += "Telegram: https://t.me/SensayChatBot\n"
                        text += "Kik: https://kik.me/Sensay.Chatbot\n"
                        text += "\n Olivia  Wayd\n"
                        self.bot.postmail(str(infos['email']), text)
                    else:
                        text = "Hi!\n" + str(self.user.s_name or "Mister X")
                        text += " added you as a friend on the Sensay community.\n"
                        text += "I'll inform you when you might do an activity together.\n"
                        text += "\n Olivia"
                        self.bot.postmail(str(infos['email']), text)
                    self.bot.say(self.user, "Thank you! I'll contact him and see if you can do an activity together!")
                    self.bot.clean_inbox(self.user)
                    self.state = 'success'

                if 'phone' in infos:
                    if self.bot.search_contacts('Twilio', infos['phone']) is None:
                        if self.user.last_channel_per_bot[self.bot.name] == "Telegram":
                            text = "Hello! My name is Olivia from Sensay and " + str(self.user.s_name if self.user.s_name else "Mister X") + " told me you might be interested in chatting with a helpful human. Check this out on http://t.me/SensayChatBot   Olivia"
                        else:
                            text = "Hello! My name is Olivia from Sensay and " + str(self.user.s_name if self.user.s_name else "Mister X") + " told me you might be interested in chatting with a helpful human. Check this out on http://m.me/SensayChatBot   Olivia"

                        self.bot.sendsms(str(infos['phone']), text)
                        self.bot.say(self.user, "Thanks! I'll contact him and see if you can do an activity together!")
                    else:
                        self.bot.say(self.user, "Thanks, I got it! Btw, your friend is already a WAYD user.")
                    self.bot.clean_inbox(self.user)
                    self.state = 'success'

            if self.bot.inbox[self.user]:
                self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                return
            if self.state == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                self.state = 'ask'
                return
            
        elif self.state == 'success':
            self.bot.launch_interaction(Breath(self.bot, self.user))
            self.resetting()
            self.state = 'end'
            
        elif self.state == 'failure':
            self.resetting()
            self.state = 'end'
            
        elif self.state == 'end':
            pass
# ---------------------------------------------------------------------------------------------------------------------


class AskAnswer(Interaction):
    def __init__(self, bot, user, query):
        super().__init__(bot, user)
        self.query = query
        self.user = user
        self.time_asked = None
        self.time_conf_asked = None

    def usefulness(self):
        return 0.0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'ask_answer'
            
        elif self.state == 'ask_answer':
            self.bot.say(self.user, "I just received a question from a user named '" + str(self.query.user_asked.s_name) + "': "+ str(self.query.question) + ". Do you know the answer? Yes/No/Start Chatting")
            self.state = 'wait for confirmation'
            self.time_conf_asked = datetime.now()
            
        elif self.state == 'wait for confirmation':
            if (datetime.now() - self.time_conf_asked).total_seconds() > 60*10:
                self.bot.say(self.user, lingua.you_must_be_busy())
                self.state = 'failure'
                return

            elif self.bot.inbox[self.user]:
                infos = {}
                for msg in self.bot.inbox[self.user]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'boolean'))
                    infos.update(corp_get(results, 'chatting'))
                if 'chatting' in infos and infos['chatting_score'] > 0.1:
                    if infos['chatting'] == 'true':
                        if self.user.chatting is not True and self.query.user_asked.chatting is not True:
                            self.user.chatting = True
                            self.query.user_asked.chatting = True
                            self.query.user_reply = self.user
                            self.query.chatting = True
                            self.bot.say(self.user, "You are now chatting with the other neighbour who ask the question, type 'end' to stop the discussion")
                            self.bot.say(self.query.user_asked, "You are now chatting with someone in your area who can help you, type 'end' to stop the discussion")
                            self.bot.launch_interaction(UserChat(self.bot, self.user, self.query.user_asked, self.query))
                            self.bot.launch_interaction(UserChat(self.bot, self.query.user_asked, self.user, self.query))
                            self.state = 'success'
                        else:
                            self.bot.say(self.user, "It seems the user is already chatting with someone else so I assume he found the help he wanted. Thanks anyway.")
                            self.state = 'failure'
                        self.bot.clean_inbox(self.user)
                        return
                if 'boolean' in infos and infos['boolean_score'] > 0.1:
                    if infos['boolean'] == "true":
                        if not self.query.answered:
                            self.state = 'wait for answer'
                            self.time_asked = datetime.now()
                            self.bot.say(self.user, "Ok, What is the response?")
                            self.query.answered = True
                            self.query.user_reply = self.user
                        else:
                            self.state = 'success'
                            self.bot.say(self.user, "Thanks! But " + self.query.user_reply.s_name +" took the job")
                    else:
                        self.state = 'success'
                        self.bot.say(self.user, "Ok! Maybe next time....")
                    self.bot.clean_inbox(self.user)
                    return

            if self.bot.inbox[self.user]:
                self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                return

            if self.state == 'wait for confirmation' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                self.state == 'ask_answer'
                return
            
        elif self.state == 'wait for answer':
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                self.bot.say(self.user, lingua.you_must_be_busy())
                self.state = 'failure'
                return

            elif self.bot.inbox[self.user]:
                infos = {}
                for msg in self.bot.inbox[self.user]:
                  infos.update({'text': msg.text})

                if 'text' in infos:
                    self.bot.say(self.user, lingua.ok())
                    self.bot.say(self.query.user_asked, "Someone has a positive reply to your request: " + str(infos['text']) + ". Don't hesitate to relaunch a question any time.")

                self.bot.clean_inbox(self.user)
                self.state = 'success'
                return

            if self.state == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                self.state == 'ask_answer'
                return
            
        elif self.state == 'success':
            self.bot.remove_possible(self)
            self.query.to_be_asked = None
            self.state = 'end'
            
        elif self.state == 'failure':
            self.bot.remove_possible(self)
            self.query.to_be_asked.pop(0)
            self.state = 'end'
            
        elif self.state == 'end':
            pass
# -----------------------------------------------------------------------------------------------------------------------


class UserChat(Interaction):
    def __init__(self, bot, user, other_user, query):
        super().__init__(bot, user)
        self.other_user = other_user
        self.user = user
        self.query = query
        self.time = None

    def usefulness(self):
        return 0.0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'discussion'
            self.time = datetime.now()
            
        elif self.state == 'discussion':
            if (datetime.now() - self.time).total_seconds() > 60 * 60 * 48 or self.query.chatting is False:
                self.bot.say(self.user, "The discussion will end now. You are back to the main chatbot.")
                self.state = 'success'
                return

            elif self.bot.inbox[self.user]:
                infos = {}
                for msg in self.bot.inbox[self.user]:
                    results = corpus.process(msg.text)
                    infos.update(corp_get(results, 'stopdiscussion'))
                if 'stopdiscussion' in infos and infos['stopdiscussion_score'] > 0.2:
                    if infos['stopdiscussion'] == 'true':
                        self.query.chatting = False
                        self.bot.say(self.user, "Ok, I'll stop the chat with the other human.")
                        self.bot.clean_inbox(self.user)
                        return

            if self.bot.inbox[self.user]:
                for msg in self.bot.inbox[self.user]:
                    if "IMG" in msg.text[:3]:
                        self.bot.say(self.other_user, str(msg.text))
                    else:
                        self.bot.say(self.other_user, ">>>" + str(msg.text))
                self.bot.clean_inbox(self.user)
                return

            if self.state == 'discussion' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                return
            
        elif self.state == 'wait for answer':
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                self.bot.say(self.user, lingua.you_must_be_busy())
                self.state = 'failure'
                return

            elif self.bot.inbox[self.user]:
                infos = {}
                for msg in self.bot.inbox[self.user]:
                    infos.update({'text': msg.text})

                if 'text' in infos:
                    self.bot.say(self.user, lingua.ok())
                    self.bot.say(self.query.user_asked, "Here is what I believe is the answer to your question: " + str(infos['text']))

                self.bot.clean_inbox(self.user)
                self.state = 'success'
                return

            if self.state == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.clean_state_calls_with_msg()
                self.state = 'ask'
                return
            
        elif self.state == 'success':
            self.bot.remove_possible(self)
            self.query.user_asked.chatting = False
            self.query.user_reply.chatting = False
            self.bot.launch_interaction(RateUser(self.bot, self.user, self.other_user, self.query))
            self.query.chatting = False
            self.query.answered = True
            self.state = 'end'
            
        elif self.state == 'end':
            pass
# -----------------------------------------------------------------------------------------------------------------------


class RateUser(Interaction):
    def __init__(self, bot, user, other_user, query):
        super().__init__(bot, user)
        self.other_user = other_user
        self.user = user
        self.query = query
        self.time_asked = None

    def usefulness(self):
        return 0.0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'ask'
            
        elif self.state == 'ask':
            if self.user == self.query.user_asked:
                self.bot.say(self.user, "Could you please rate the reply/interaction you had with " + str(self.other_user.s_name) + " (value between 0-5 stars)?")
            else:
                self.bot.say(self.user, "Could you please rate if the question/discussion you had with " + str(self.other_user.s_name) + " was appropriate (value between 0-5 stars)?")
            self.state = 'wait for answer'
            self.time_asked = datetime.now()
            
        elif self.state == 'wait for answer':
            if (datetime.now() - self.time_asked).total_seconds() > wait_for_answer_time:
                self.bot.say(self.user, lingua.you_must_be_busy())
                self.state = 'success'
                return

            elif self.bot.inbox[self.user]:
                reply = None
                for msg in self.bot.inbox[self.user]:
                    reply = sa.get_info(msg.text, 'number')
                    if reply:
                        if self.user == self.query.user_asked:
                            if self.other_user.rating_reply:
                                self.other_user.rating_reply.append(max(min(int(reply[0]),5),0))
                            else:
                                self.other_user.rating_reply = []
                                self.other_user.rating_reply.append(max(min(int(reply[0]), 5), 0))
                        else:
                            if self.other_user.rating:
                                self.other_user.rating.append(max(min(int(reply[0]),5),0))
                            else:
                                self.other_user.rating = []
                                self.other_user.rating.append(max(min(int(reply[0]), 5), 0))
                if reply is not None:
                    self.bot.say(self.user, lingua.ok() + "  Thanks for the feedback!!")
                    self.bot.clean_inbox(self.user)
                    self.state = 'success'

            if self.bot.inbox[self.user]:
                self.bot.launch_interaction(ProcessSpontaneous(self.bot, self.user))
                return

            if self.state == 'wait for answer' and self.get_state_calls_with_msg() >= 2:
                self.bot.say(self.user, "My dear, could you please rate the interaction with " + str(
                    self.other_user.s_name) + " (value between 0-5)?")
                self.clean_state_calls_with_msg()
                
        elif self.state == 'success':
            self.bot.remove_possible(self)
            self.state = 'end'
            
        elif self.state == 'end':
            pass
# -----------------------------------------------------------------------------------------------------------------------


class TwilioLimit(Interaction):  # ok
    def __init__(self, bot, user):
        super().__init__(bot, user)

    def usefulness(self):
        if self.user.last_channel_per_bot[self.bot.name] == 'Twilio' and self.user.number_of_outgoing_messages and self.user.s_number_of_incoming_messages and self.user.number_of_outgoing_messages + self.user.s_number_of_incoming_messages > 15.0:
            return 10.0
        else:
            return 0.0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'say'
            
        elif self.state == 'say':
            if self.bot.inbox[self.user] and self.user.last_channel_per_bot[self.bot.name] == "Twilio" and self.user.s_number_of_incoming_messages and self.number_of_outgoing_messages and self.user.number_of_outgoing_messages + self.user.s_number_of_incoming_messages > 15.0:
                try:
                    self.bot.say(self.user, "{}, let's discuss rather using facebook, skype, telegram or viber.".format(self.user.s_name if self.user.s_name else "Hey"))
                except:
                    self.bot.say(self.user, "I suggest we discuss rather using http://m.me/SensayChatBot")
                self.bot.clean_inbox(self.user)
                self.state = 'success'
            else:
                self.bot.clean_inbox(self.user)
                self.state = 'success'
            
        elif self.state == 'success':
            # Do not remove the interaction
            self.resetting()
            self.state = 'end'
            
        elif self.state == 'failure':
            self.resetting()
            self.state = 'end'
            
        elif self.state == 'end':
            pass
# -----------------------------------------------------------------------------------------------------------


class ProcessSpontaneous(Interaction):
    def __init__(self, bot, user):
        super().__init__(bot, user)
        self.user = user

    def usefulness(self):
        if self.bot.inbox[self.user]:
            return 2.0
        else:
            return 0.0

    def execute(self):
        super().execute()

        if self.state is None:
            self.state = 'start'

        elif self.state == 'start':
            if self.bot.inbox[self.user] and self.user.s_greeted_by_sensay is True:
                if self.bot.inbox[self.user][-1].text == "poke":
                    pass
                else:
                    infos = {}
                    minsize = 100
                    for msg in self.bot.inbox[self.user]:
                        minsize = min(minsize, len(msg.text))
                        results = corpus.process(msg.text)
                        infos.update(corp_get(results, 'name'))
                        infos.update(corp_get(results, 'activity'))
                        infos.update(corp_get(results, 'help'))
                        infos.update(corp_get(results, 'sentiment'))
                        infos.update(corp_get(results, 'question'))
                        infos.update(corp_get(results, 'gdpr'))
                        infos.update(corp_get(results, 'tone'))
                        if "lat:" in msg.text and "long:" in msg.text and "/../" in msg.text:
                            int = AskLocation(self.bot, self.user)
                            int.state = 'wait for answer'
                            int.time_asked = datetime.now()
                            self.bot.launch_interaction(int)
                            self.state = 'success'
                            return
                        if "Location" == msg.text.capitalize():
                            self.bot.clean_inbox(self.user)
                            self.bot.launch_interaction(AskLocation(self.bot, self.user))
                            self.state = 'success'
                            return

                    if 'tone' in infos:
                        if infos['tone'] == 'rude' and infos['tone_score'] > 0.6:
                            self.bot.say(self.user, lingua.dont_be_so_rude())
                            self.bot.clean_inbox(self.user)
                            self.state = 'success'
                            return

                    if 'gdpr' in infos:
                        if infos['gdpr'] == 'true' and infos['gdpr_score'] > 0.8:
                            self.bot.say(self.user, "Ok, understood.... We will delete all data related to you...")
                            self.bot.clean_inbox(self.user)
                            del self.user
                            self.state = 'success'
                            return

                    if 'question' in infos:
                        if infos['question'] == 'true' and infos['question_score'] > 0.8:
                            if self.user.s_home_location is None:
                                self.bot.say(self.user,
                                             "In order to match with your neighbours, you first have to mention your home location.")
                                self.bot.launch_interaction(AskLocation(self.bot, self.user))
                                self.bot.queue_interaction(AskQuestion(self.bot, self.user))
                            else:
                                self.bot.launch_interaction(AskQuestion(self.bot, self.user))
                            self.bot.clean_inbox(self.user)
                            self.state = 'success'
                            return

                    if 'help' in infos:
                        if infos['help'] == 'true' and infos['help_score'] > 0.8:
                            if self.user.last_channel_per_bot[self.bot.name] == "Facebook":
                                self.bot.say(self.user,
                                             "Type 'Discuss' to get help. \n Type 'Off' to snooze \n Type 'Stop' to cancel. \n You can also update your home location anytime by typing 'Location'.")
                            else:
                                self.bot.say(self.user,
                                             "Type 'Discuss' to get help. \n Type 'Off' to snooze \n Type 'Stop' to cancel. \n You can also update your home location anytime by using the functionality of your app to share a point on a map.")
                            if datetime.now().hour < 12:
                                self.bot.say(self.user,
                                             "For example, you can type 'discuss' and ask stuff like 'who can fix my bike around me?' or 'I need a gift for a geeky friend, any idea?' or 'I need to practice my Spanish, who is willing to chat whith me in Spanish?' :-)")
                            else:
                                self.bot.say(self.user,
                                             "For example, you can type 'discuss' and ask stuff like 'who has a lawnmower to lend around me?' or 'I need a gift for a keeky friend, any idea?' or 'I have too many eggs produced by my chickens, who wants to take some at home?' :-)")
                            self.bot.clean_inbox(self.user)
                            self.state = 'success'
                            return

                    if 'tone' in infos:
                        if infos['tone'] == 'stopspamming' and infos['tone_score'] > 0.8:
                            self.bot.say(self.user, lingua.ok())
                            self.bot.clean_inbox(self.user)
                            # This will have a direct effect on the Silent interaction
                            self.user.s_time_of_last_message = str(datetime.now() - timedelta(hours=48))
                            self.state = 'success'
                            return

                    if 'name' in infos:
                        if infos['name_score'] > 0.99 and minsize > 100:  # 0.4 to too much, do not even recognize "My name is Bob"
                            int = AskName(self.bot, self.user)
                            int.state = 'wait for answer'
                            int.time_asked = datetime.now()
                            self.bot.launch_interaction(int)
                            self.state = 'success'
                            return

                    answer = sa.is_general_question(self.bot.inbox[self.user][-1].text)
                    if answer:
                        self.bot.say(self.user, answer.replace("julia", "Olivia").replace("Julia", "Olivia").replace("Wayd", "Sensay").replace("WAYD", "Sensay"))
                    else:
                        self.bot.say(self.user, lingua.i_dont_understand_sensay())

            elif self.bot.inbox[self.user] and self.user.s_greeted_by_sensay is not True:
                self.bot.queue_interaction(WelcomeNewUser(self.bot, self.user))
            self.bot.clean_inbox(self.user)
            self.state = 'success'

        elif self.state == 'success':
            if self.user.s_greeted_by_sensay is True:
                self.bot.launch_interaction(Breath(self.bot, self.user))
            self.state = 'end'
            self.resetting()

        elif self.state == 'end':
            pass
