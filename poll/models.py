from django.db import models
from django.contrib.auth.models import User


class Position(models.Model):
    title = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.title


class Candidate(models.Model):
    name = models.CharField(max_length=50)
    total_vote = models.IntegerField(default=0, editable=False)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    image = models.ImageField(verbose_name="Candidate Pic", upload_to='images/')

    def __str__(self):
        return "{} - {}".format(self.name, self.position.title)


class ControlVote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)
    status = models.BooleanField(default=False)
    #image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
        return "{} - {} - {}".format(self.user, self.position, self.status)


class Captcha(models.Model):
    voter = models.CharField(max_length=50, null=True)
    image = models.BinaryField(null=True)
    share_2 = models.BinaryField(null=True)

    def __str__(self):
        return self.voter
        #return "{}".format(self.user)
