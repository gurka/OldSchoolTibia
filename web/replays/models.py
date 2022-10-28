from django.db import models


class Replay(models.Model):
    filename = models.CharField(max_length=128)
    version = models.IntegerField()
    length_ms = models.IntegerField()

    def __str__(self):
        version_str = str(self.version)
        version_str = version_str[0] + "." + version_str[1:]
        return f"[{version_str}] {self.filename}"

