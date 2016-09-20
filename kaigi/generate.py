from __future__ import print_function
from kaigi.models import Person, Meeting
from django.http import HttpRequest
from operator import itemgetter
import kaigi.views
import uuid
import datetime
import sys
import random

class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

def make_person():
    p = Person(id=uuid.uuid4())
    p.save()
    return p

def make_request(person, message=None, rating=None):
    request = HttpRequest()
    request.POST['person_id'] = person.id.hex
    request.POST['message'] = message
    request.POST['rating'] = rating

    return request

def print_status(i):
    status = '-\|/'
    print(status[i % 4], end='\b')
    sys.stdout.flush()

def print_done():
    print('\b...DONE')

random.seed()

print('Generating people', end=' ')
people = []
for i in range (10):
   people.append(make_person())
   print_status(i)
print_done()

print('Joining users to meeting', end=' ')
m_uuid = uuid.uuid4()
meeting = Meeting(
        id = m_uuid,
        subject = 'Test meeting',
        location = 'Anywhere',
        start = datetime.datetime.now(tz=UTC()) - datetime.timedelta(hours = 4),
        end = datetime.datetime.now(tz=UTC()) + datetime.timedelta(hours = 4)
        )
meeting.save()

for person in people:
    kaigi.views.meeting(make_request(person), m_uuid.hex)
    print_status(i)
print_done()

print('Generating activities', end=' ')
for i in range(60*8):
    person = random.choice(people)
    actions = ['chat', 'rate']
    action = random.choice(actions)
    if action == 'chat':
        kaigi.views.chat(
                make_request(
                    person,
                    message='This meeting is {0} minutes too long.'.format(i),
                    ),
                m_uuid.hex
                )
    elif action == 'rate':
        kaigi.views.rate(
            make_request(
                person,
                rating=random.randint(0,100),
                ),
            m_uuid.hex
            )

    print_status(i)
print_done()

print('Adjusting timestamps', end=' ')
chats = meeting.chat_set.all()
ratings = meeting.rating_set.all()

activities = [chat for chat in chats]
activities.extend([rating for rating in ratings])
activities = sorted(activities, key=lambda activity: activity.time)

i = 0
for activity in activities:
    activity.time = meeting.start + datetime.timedelta(minutes=i)
    activity.save()
    print_status(i)
    i += 1
print_done()

print('People:')
for person in people:
    print(person.id.hex)
print('Meeting:\n{0}'.format(m_uuid.hex))
