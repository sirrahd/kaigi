from django.db import models
import datetime, uuid

class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)

class Person(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    @staticmethod
    def generate_token(personId):
        return uuid.uuid5(uuid.NAMESPACE_URL, personId.encode('ascii'))

    def dict(self):
        return {
                'id': self.id.hex,
               }

class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    subject = models.CharField(max_length=255)
    location= models.CharField(max_length=255)
    start = models.DateTimeField()
    end = models.DateTimeField()
    organizer_name = models.CharField(max_length=255)
    organizer_email = models.CharField(max_length=255)

    @staticmethod
    def generate_token(meetingId):
        return uuid.uuid5(uuid.NAMESPACE_OID, meetingId.encode('ascii'))

    def dict(self):
        return {
                'id': self.id.hex,
                'subject': self.subject,
                'location': self.location,
                'start': self.start.isoformat(),
                'end': self.end.isoformat(),
                'organizer': { 'name': self.organizer_name, 'email': self.organizer_email },
                }

    def get_ratings(self, start=0):
        ratings = self.rating_set.filter(id__gt=start).order_by('id')
        rating_list = []
        last_id = start
        for rating in ratings:
            rating_list.append(rating.dict())
            last_id = rating.id
        return {
                'last_id': last_id,
                'ratings': rating_list,
                }

    def band_average_rating(self):
        curTime = datetime.datetime.now(tz=UTC())
        startTime = curTime - datetime.timedelta(minutes=15)
        ratings = self.rating_set.filter(time__gte=startTime)
        backup_rating = self.rating_set.last()
        average = 0
        total = len(ratings)
        if total == 0:
            if backup_rating:
                average = backup_rating.rating
                total = 1
            else:
                return 0
        for rating in ratings:
            average += rating.rating
        return average / total

    @staticmethod
    def get_cached_meetings():
        now = datetime.datetime.now(tz=UTC())
        start = now - datetime.timedelta(hours=8)
        end = now + datetime.timedelta(hours=8)
        return Meeting.objects.filter(start__gte=start).filter(start__lte=end)

    def rolling_ratings(self):
        curTime = datetime.datetime.now(tz=UTC())
        startTime = curTime - datetime.timedelta(minutes=5)
        ratings = self.rating_set.filter(time__gte=startTime).order_by('id')
        pre_rating = self.rating_set.filter(time__lt=startTime).last()
        if len(ratings) == 0:
            if pre_rating:
                ratings = [pre_rating]
            else:
                return []
        curIndex = 0
        response = []
        for i in range(60):
            while curIndex < len(ratings) and ratings[curIndex].time - startTime <= datetime.timedelta(seconds=i * 5):
                curIndex += 1
            if curIndex == 0:
                if pre_rating:
                    response.append((i * 5, pre_rating.rating))
                else:
                    response.append((i * 5, 0))
            else:
                response.append((i * 5, ratings[curIndex - 1].rating))

        return response

    def get_chats(self, start=0):
        chats = self.chat_set.filter(id__gt=start).order_by('id')
        chat_list = []
        last_id = start
        for chat in chats:
            chat_list.append(chat.dict())
            last_id = chat.id
        return {
                'last_id': last_id,
                'chats': chat_list,
                }

    def average_rating(self):
        sessions = self.session_set.all()
        average = 0
        count = self.session_set.all().count()
        if count == 0:
            return 0

        for session in sessions:
            average += session.rating

        average /= count
        return average

class Chat(models.Model):
    username = models.CharField(max_length=255, blank=False)
    text = models.CharField(max_length = 255, blank=False)
    meeting = models.ForeignKey('Meeting', blank=False)
    time = models.DateTimeField(auto_now_add=True)

    def dict(self):
        return {
                'id': self.id,
                'time': self.time.isoformat(),
                'name': self.username,
                'message': self.text,
                }

class Rating(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(blank=False)
    meeting = models.ForeignKey('Meeting', blank=False)

    def dict(self):
        return {
                'id': self.id,
                'time': self.time.isoformat(),
                'rating': self.rating,
                }

class Session(models.Model):
    person = models.ForeignKey('Person', blank=False)
    meeting = models.ForeignKey('Meeting', blank=False)
    last_activity = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(blank=False)
    username = models.CharField(max_length=100, blank=False)

    class Meta:
        unique_together = ('person', 'meeting')

class MeetingAssoc(models.Model):
    person = models.ForeignKey('Person', blank=False)
    meeting = models.ForeignKey('Meeting', blank=False)
