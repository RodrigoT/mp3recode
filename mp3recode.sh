#!/bin/bash

#usage ./mp3recode.sh indir outdir
# reencode media file in input dir (recursive) to output dir (dir tree recreation).
# supports mp3 (reencode/copy), flac (reendocde) and jpg (copy).

shopt -s extglob # extra glob matching

encodeFile () {
    local inF="$1"
    local outF="$2"
    local outDir="$(dirname "$2")"
    local ifname="$(basename -- "$inF")"
    local extension="${ifname##*.}"
    case $extension in
        [mM][pP]3) # maybe reencode mp3
            if [ ! -d "$outDir" ]; then
                mkdir -p "$outDir"
            fi
            bitrate=$(mediainfo "$inF" | grep "Overall bit rate  .*s" | grep -o [0-9]*)
            if ((bitrate<=192)); then # bitrate low enough: just copy
                cp -v "$inF" "$outDir"
            else # hight to low bitrate re-encode
                lame --preset 160 --nohist "$inF" "$outF"
                mid3cp -v "$inF" "$outF"
            fi
            ;;
        [fF][lL][aA][cC]) # reencode FLAC
            if [ ! -d "$outDir" ]; then
                mkdir -p "$outDir"
            fi
            flac -cd "$inF" | lame --preset 160 --nohist - "$outF"
            ./mutagen_FlacTags2id3v2.py "$inF" "$outF"
            ;;
        [jJ][pP]?([eE])[gG]) # copy cover
            if [ ! -d "$outDir" ]; then
                mkdir -p "$outDir"
            fi
            cp -v "$inF" "$outDir"
            ;;
        *)
            echo "SKIP '$inF'"
            ;;
    esac
}

die () {
    echo >&2 "$@"
    exit 1
}

# check and init input args
[ "$#" -eq 2 ] || die "2 or more arguments required, $# provided"
input="$1"
outDir="$2"
[ -d "$outDir" ] || die "Output directory $outDir does not exist"
[ -d "$input" ] || die "Input directory $input does not exist"

# for each file
mkdir -p -v "$outDir/$(basename "$input")"
find "$input" -type f | while read i; do
    #set -x
    ifname="$(basename -- "$i")" # filename only
    extension="${ifname##*.}" # file extension
    filename="${ifname%.*}" # name part of the filename
    ocdir="${outDir}/$(dirname "$(realpath --relative-to="$input/.." "$i")")" # output directory

    ofname="${ocdir}/$filename.mp3" # output filename
    encodeFile "$i" "$ofname" # call conversion: use gnu parallel here
    #set +x
done
