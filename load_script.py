__author__ = 'oleh'

import os
import play_sound
import urllib2
from multiprocessing.dummy import Pool
from filters import run_filters
from BeautifulSoup import BeautifulSoup
from os import listdir
from os.path import isfile, join


# Base web-domain. Scripts works only for freesound.org
SITE = 'https://www.freesound.org'

# Start page to download, then on this page we are looking for next page button
PAGE_GUN = SITE + '/search/?q=gun&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_PISTOL = SITE + '/search/?q=pistol&f=bitdepth%3A16+type%3Awav+duration%3A[1+TO+15]&s=score+desc&advanced=1&g=1'
PAGE_GUN_ALL = SITE + '/search/?q=gun&f=bitdepth%3A16+type%3Awav+duration%3A[2+TO+15]&s=score+desc&advanced=1&g=1'
PAGE_SHOOTING = SITE + '/search/?q=shooting&f=bitdepth%3A16+type%3Awav+duration%3A[2+TO+15]&s=score+desc&advanced=1&g=1'

PAGE_DOG = SITE + '/search/?q=dog&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_BIRD = SITE + '/search/?q=bird&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_SCREAM = SITE + '/search/?q=scream&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_NATURE = SITE + '/search/?q=nature&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_STREET = SITE + '/search/?q=street&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_CAT = SITE + '/search/?q=cat&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_HELICOPTER = SITE + '/search/?q=helicopter&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_SILENCE = SITE + '/search/?q=silence&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_RAIN = SITE + '/search/?q=rain&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_TRAIN = SITE + '/search/?q=train&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'
PAGE_PLANE = SITE + '/search/?q=plane&f=type%3Awav+bitdepth%3A16+duration%3A[1+TO+5]&s=score+desc&advanced=1&g=1'

# Asynchronous processing
POOLS_NUMBER = 4


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                      HTML processing section
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def download_song(url, s):
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'sessionid=8inui5sic60f3052jgfzuc5ga7jz4gpi'))
    r = opener.open(url).read()
    with open(s, 'wb') as f:
        f.write(r)


def download_page(url):
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    return response.read()


def refs_list_of_sounds_from_url(url):
    soup = BeautifulSoup(download_page(url))
    class_sounds = soup.findAll("div", {"class": "sound_filename"})
    return [x.a['href'] for x in class_sounds]


def search_url_to_next_page(url):
    soup = BeautifulSoup(download_page(url))
    divs = soup.findAll("li", {"class": "next-page"})
    if not len(divs):
        raise EOFError('No next url')
    return divs[0].a['href']


def get_download_url_and_name(sound_url):
    soup = BeautifulSoup(download_page(sound_url))
    divs = soup.findAll("div", {"id": "download"})
    ref = divs[0].a['href']
    tmp = ref.rsplit('/')
    return ref, tmp[len(tmp) - 1]


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                       Script-functions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def select_success(dir1, dir2):
    files = sorted([f for f in listdir(dir1) if isfile(join(dir1, f))])
    i = 0
    for FILE in files:
        if process_file(dir1 + '/' + FILE) == 'OK':
            os.rename(dir1 + '/' + FILE, dir2 + '/' + FILE)
        i += 1
        if i % 5 == 0:
            print str(100 * i / len(files)) + '%', 'done'
    play_sound.play()


def load_site(current_page, folder):
    i = 0
    page = 1
    while True:
        for sound_url in refs_list_of_sounds_from_url(current_page):
            down_url, song_name = get_download_url_and_name(SITE + sound_url)
            download_song(SITE + down_url, folder + '/' + song_name)
            print 'downloaded song #' + str(i), SITE + down_url
            i += 1
        print 'Downloaded pages: ' + str(page)

        try:
            current_page = SITE + search_url_to_next_page(current_page)
        except EOFError:
            print 'No more downloads left'
            break
        except:
            pass
        page += 1


def process_file(f):
    try:
        if run_filters(f, watch=False):
            return 'OK'
        return 'NOT'
    except:
        return 'ERROR'


def start_test(folder):
    wavs = sorted([f for f in listdir(folder) if isfile(join(folder, f))])

    pool = Pool(POOLS_NUMBER)
    results = pool.map(process_file, [folder + '/' + x for x in wavs])

    pool.close()
    pool.join()

    f = open(folder + '/' + 'Results.txt', 'wb')
    f.write('-------------------------------------------------------\n')
    f.write('           ' + folder + '\n')
    f.write('-------------------------------------------------------')
    f.write('\n found gunshot(%):   ' + str(100. * results.count('OK') / len(results)))
    f.write('\n not found gunshot(%:' + str(100. * results.count('NOT') / len(results)))
    f.write('\n error caught(%):    ' + str(100. * results.count('ERROR') / len(results)))
    f.write('\n-------------------------------------------------------')
    f.close()
    print 'Results written to', folder + '/' + 'Results.txt'

#########################################################################
#########################################################################


if __name__ == '__main__':
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Developing selection
    # select_success('gun_unsuccess', 'gun_success')
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Full load
    # load_site(page_shooting, 'shooting')

    # run_tests('sounds/bird')
    # run_tests('sounds/cat')
    # run_tests('sounds/dog')
    # run_tests('sounds/helicopter')
    # run_tests('sounds/nature')
    # run_tests('sounds/plane')
    # run_tests('sounds/rain')
    # run_tests('sounds/scream')
    # run_tests('sounds/silence')
    # run_tests('sounds/street')
    start_test('sounds/train')
    # run_tests('sounds/gun')
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #                           Point load
    # run_filters('other_wavs/320851_datruth555_gooo_converted.wav', watch=True)
    # run_filters('res/gunshot2_sim-7.wav', watch=True)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    play_sound.play()