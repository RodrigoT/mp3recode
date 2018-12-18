#!/usr/bin/env python3

#usage ./mutagen_FlacTags2id3v2.py in.flac out.mp3
#copies FLAC tags to idv3 tags, with tag id conversion, picard/musicbrainz oriented

import sys
import mutagen
import pprint

# tag map FLAC -> id3
tagMapping = {
    "genre"                     : "TCON",
    "composer"                  : "TCOM",
    "title"                     : "TIT2",
    "RELEASECOUNTRY"            : "TXXX=MusicBrainz Album Release Country",
#    "TOTALDISCS": "", # managed by disc/total
    "label"                     : "TPUB",
#    "TOTALTRACKS": "", # managed by ttrack/total
    "musicbrainz_albumartistid" : "TXXX=MusicBrainz Album Artist Id",
    "date"                      : "TDOR",
    "discnumber"                : "TPOS",
#    "tracktotal": "",
    "musicbrainz_releasetrackid": "TXXX=MusicBrainz Release Track Id",
    "asin"                      : "TXXX=ASIN",
    "albumartistsort"           : "TSO2",
    "originaldate"              : "TDRC",
    "script"                    : "TXXX=SCRIPT",
    "musicbrainz_albumid"       : "TXXX=MusicBrainz Album Id",
    "releasestatus"             : "TXXX=MusicBrainz Album Status",
#    "albumartist": "",
    "catalognumber"             : "TXXX=CATALOGNUMBER",
    "album"                     : "TALB",
    "musicbrainz_artistid"      : "TXXX=MusicBrainz Artist Id",
    "media"                     : "TMED",
    "releasetype"               : "TXXX=MusicBrainz Album Type",
    "originalyear"              : "TXXX=originalyear",
    "isrc"                      : "TSRC",
    "musicbrainz_releasegroupid": "TXXX=MusicBrainz Release Group Id",
#    "disctotal": "",
    "artist"                    : "TPE1",
    "barcode"                   : "TXXX=BARCODE",
    "musicbrainz_trackid"       : "UFID=http://musicbrainz.org", # special: to url
    "artistsort"                : "TSO2",
    "artists"                   : "TPE2",
    "tracknumber"               : "TRCK",
    "releasecountry"            : "TXXX=MusicBrainz Album Release Country"
    }

def toTag(tagName, tagValue):
    """Encodes input tag to the correct id3 type"""
    if tagName[:5] == "TXXX=":
        return mutagen.id3.TXXX(encoding=mutagen.id3.Encoding.UTF8, desc=tagName[5:], text=tagValue)
    if tagName[:5] == "UFID=":
        return mutagen.id3.UFID(owner=tagName[5:], data=bytes(tagValue[0], 'utf-8'))
    else:
        return mutagen.id3.Frames[tagName](encoding=mutagen.id3.Encoding.UTF8, text=tagValue)

def counterTag(flacTags, indexTag, totalTag):
    """creates 'X/Y' tags"""
    if indexTag in flacTags and totalTag in flacTags:
        return toTag(tagMapping[indexTag], "%s/%s" % (flacTags[indexTag][0], flacTags[totalTag][0]))

def copyImage(flactTags, mp3Tags):
    """Copy embedded image"""
    for pic in flacTags.pictures: # copy ALL images (artist, album...)
        mp3Tags.add(mutagen.id3.APIC(mutagen.id3.Encoding.UTF8, pic.mime, pic.type, pic.desc, pic.data))

#open flac (in), open mp3 (out)
flacTags = mutagen.File(sys.argv[1])
mp3Tags = mutagen.File(sys.argv[2])
# blank mp3 without tags?
if not mp3Tags.tags:
    mp3Tags.tags = mutagen.id3.ID3()
#for tag in flac: try to copy to an id3 one
for tag, value in flacTags.items():
    newTag = tagMapping.get(tag, None)
    if newTag:
        mp3Tags.tags.add(toTag(newTag, value))
    else:
        print("Skip unsupported tag %s:%s" % (pprint.pformat(tag), pprint.pformat(value)))

# post processing for complex tags: track/total, disc/total
mp3Tags.tags.add(counterTag(flacTags, "tracknumber", "totaltracks"))
mp3Tags.tags.add(counterTag(flacTags, "discnumber", "totaldiscs"))
# Copy images
copyImage(flacTags, mp3Tags.tags)
# and save new tags to mp3 file
mp3Tags.save(sys.argv[2])
