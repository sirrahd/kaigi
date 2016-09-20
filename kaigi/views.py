from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from kaigi.authhelper import get_signin_url, get_token_from_code
from kaigi.outlookservice import get_my_messages, get_my_events, get_my_info
from kaigi.models import Person, Meeting, Session, Chat, Rating, MeetingAssoc
from kaigi.names import generate_username
import json
import uuid
import datetime

def auth(request):
    redirect_uri = request.build_absolute_uri(reverse('gettoken'))
    sign_in_url = get_signin_url(redirect_uri)
    return HttpResponseRedirect(sign_in_url)

def gettoken(request):
    auth_code = request.GET['code']
    redirect_uri = request.build_absolute_uri(reverse('gettoken'))
    access_token = get_token_from_code(auth_code, redirect_uri)
    request.session['access_token'] = access_token
    person = get_person_from_access_token(access_token)
    request.session['person_id'] = person.id.hex
    return HttpResponseRedirect(reverse('home'))

def home(request):
    access_token = get_access_token(request)
    if not access_token:
        return HttpResponseRedirect(reverse(auth))
    return render_to_response('kaigi/index.html')

def viewMeeting(request, meeting_id):
    return render_to_response('kaigi/meeting.html', {'meeting_id': meeting_id})

@never_cache
def events(request):
    access_token = get_access_token(request)
    person = get_person_from_access_token(access_token)
    if not person:
        return HttpResponse(status=401)

    events = []
    for event in get_my_events(access_token)['value']:
        meeting = create_meeting(event)
        events.append(meeting.dict())

        try:
            MeetingAssoc.objects.get(person=person, meeting=meeting)
        except:
            MeetingAssoc(person=person, meeting=meeting).save()

    return HttpResponse(json.dumps({
        'person': person.dict(),
        'events': events,
        }, sort_keys=True, indent=4))

@never_cache
def get_cached_meetings(request):
    person = get_person(request)
    if not person:
        return HttpResponse(status=401)

    cached_meetings = Meeting.get_cached_meetings()
    response = []
    for meeting in cached_meetings:
        response.append(meeting.dict())

    return HttpResponse(json.dumps({
        'events': response,
        'person': person.dict(),
    }))


@never_cache
def info(request):
    access_token = request.session['access_token']
    if not access_token:
        return HttpResponseRedirect(reverse('auth'))
    else:
        events = get_my_events(access_token)
        person = get_my_info(access_token)
        return HttpResponse(json.dumps({
            'events': events['value'],
            'person': person,
            'access_token': access_token,
            }))

@csrf_exempt
@never_cache
def reflection(request):
    return HttpResponse(request.body)

# Perform user checks and send meeting info
@never_cache
def meeting(request, meeting_id):
    person = get_person(request)
    if not person:
        return HttpResponseRedirect(reverse('auth'))
    meeting = get_meeting(meeting_id)

    return meeting_update(request, person, meeting)

@csrf_exempt
@never_cache
def chat(request, meeting_id):
    person = get_person(request)
    if not person:
        return HttpResponse("No person specified", status=400)
    meeting = get_meeting(meeting_id)
    session = get_session(person, meeting)

    if 'message' in request.GET:
        newMessage = request.GET['message']
    else:
        newMessage = request.POST['message']

    Chat(
            username=session.username,
            meeting=meeting,
            text=newMessage,
            ).save()

    return meeting_update(request, person, meeting, session)

@csrf_exempt
@never_cache
def rate(request, meeting_id):
    person = get_person(request)
    if not person:
        return HttpResponse("No person specified", status=400)
    meeting = get_meeting(meeting_id)
    session = get_session(person, meeting)

    if 'rating' in request.GET:
        newRating = int(request.GET['rating'])
    else:
        newRating = int(request.POST['rating'])
    if session.rating != newRating and newRating <= 100 and newRating >= 0:
        session.rating = newRating
        session.save()
        Rating(
                rating = meeting.average_rating(),
                meeting = meeting,
                ).save()

    return meeting_update(request, person, meeting, session)

def names(request):
    if 'count' in request.GET:
        count = request.GET['count']
    else:
        count = 1

    names = ""
    for i in range(int(count)):
        names += generate_username() + "\n"

    return HttpResponse('<pre>' + names + '</pre>')

def band(request):
    meeting = get_meeting('e733b84dc40952bd87b23e01bd908a00')
    return HttpResponse(json.dumps({'subject': meeting.subject, 'rating': meeting.band_average_rating()}))

# Helpers

def meeting_update(request, person, meeting, session=None):
    activities = get_last_activities(request)
    last_rating = activities['last_rating']
    last_chat = activities['last_chat']
    ratings = meeting.get_ratings(last_rating)
    rolling_ratings = meeting.rolling_ratings()
    chats = meeting.get_chats(last_chat)
    if not session:
        session = get_session(person, meeting)

    return HttpResponse(json.dumps({
        'person': person.dict(),
        'meeting': meeting.dict(),
        'ratings': ratings,
        'chats': chats,
        'rolling_ratings': rolling_ratings,
        'current_rating': session.rating,
        }, sort_keys=True, indent=4))

def get_person_from_access_token(access_token):
    if not access_token:
        return None

    user_id = get_my_info(access_token)
    if 'Id' not in user_id:
        return None
    user_id = Person.generate_token(user_id['Id'])
    try:
        person = Person.objects.get(id=user_id)
    except Person.DoesNotExist:
        person = Person(id=user_id)
        person.save()

    return person

def anonymous_person():
    person = Person(id=uuid.uuid4())
    person.save()
    return person

def get_access_token(request):
    if 'access_token' in request.session:
        return request.session['access_token']

    return None

def get_person(request):
    if 'person_id' in request.GET:
        person_id = request.GET['person_id']
    elif 'person_id' in request.POST:
        person_id = request.POST['person_id']
    elif 'person_id' in request.session:
        person_id = request.session['person_id']
    else:
        person_id = anonymous_person().id.hex

    request.session['person_id'] = person_id

    return Person.objects.get(id=uuid.UUID(person_id))

def get_meeting(meeting_id):
    meeting = Meeting.objects.get(id=uuid.UUID(meeting_id))

    return meeting

def get_session(person, meeting):
    try:
        session = Session.objects.get(person=person, meeting=meeting)
    except Session.DoesNotExist:
        try:
            session = Session(
                    person=person,
                    meeting=meeting,
                    rating=100,
                    username=generate_username(),
                    )
            session.save()
        except IntegrityError:
            session = Session.objects.get(person=person, meeting=meeting)

    return session

def get_last_activities(request):
    if 'last_chat' in request.GET:
        last_chat = request.GET['last_chat']
    elif 'last_chat' in request.POST:
        last_chat = request.POST['last_chat']
    else:
        last_chat = 0

    if 'last_rating' in request.GET:
        last_rating = request.GET['last_rating']
    elif 'last_rating' in request.POST:
        last_rating = request.POST['last_rating']
    else:
        last_rating = 0

    return {
            'last_chat': last_chat,
            'last_rating': last_rating,
            }

def create_meeting(event):
    meeting_token = Meeting.generate_token(event['iCalUId'])

    try:
        meeting = Meeting.objects.get(id=meeting_token)
    except Meeting.DoesNotExist:
        meeting = Meeting(
                id=meeting_token,
                subject=event['Subject'],
                location=event['Location']['DisplayName'],
                start=datetime.datetime.strptime(event['Start'], '%Y-%m-%dT%H:%M:%SZ'),
                end=datetime.datetime.strptime(event['End'], '%Y-%m-%dT%H:%M:%SZ'),
                organizer_name = event['Organizer']['EmailAddress']['Name'],
                organizer_email = event['Organizer']['EmailAddress']['Address'],
                )
        meeting.save()
        for attendee in event['Attendees']:
            person_id = Person.generate_token(attendee['EmailAddress']['Address'])
            try:
                person = Person.objects.get(id=person_id)
            except:
                person = Person(id=person_id)
                person.save()
            MeetingAssoc(meeting=meeting, person=person).save()

    return meeting
