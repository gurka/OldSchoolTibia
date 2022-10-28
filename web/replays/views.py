from django.shortcuts import render

from .models import Replay

def versions(request):
    versions = Replay.objects.values_list('version', flat=True).distinct().order_by('version')
    versions_str = []
    for version in versions:
        version_str = str(version)
        versions_str.append(version_str[0] + "." + version_str[1:])
    return render(request, 'versions.html', dict(versions=versions_str))


def version(request, version):
    version_int = int(version.replace('.', ''))
    replays = Replay.objects.values_list('filename', flat=True).filter(version=version_int).order_by('filename')
    return render(request, 'version.html', dict(replays=replays))
