import random

# ================= LIVE STREAMS =================
LIVE_STREAMS = [
    "https://www.youtube.com/watch?v=jfKfPfyJRdk&pp=ygUEMjQvNw%3D%3D",
    "https://www.youtube.com/watch?v=UEyEs8AE1ss&pp=ygUEMjQvNw%3D%3D",
    "https://www.youtube.com/watch?v=vK5VwVyxkbI&pp=ygUMZmFudGFzeSBsaXZl",
    "https://www.youtube.com/watch?v=TfWotiyXGfI&pp=ygUJbG9maSBsaXZl",
    "https://www.youtube.com/watch?v=Y4u7D7xCvtw&pp=ygUMZmFudGFzeSBsaXZl",
]

# ================= PLAYLIST SONG ENTRIES =================
PLAYLIST_SONGS = [
    "https://www.youtube.com/watch?v=E1NXNWHCxhk&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=1",
    "https://www.youtube.com/watch?v=4WIMyqBG9gs&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=2",
    "https://www.youtube.com/watch?v=Cy5b0OiZ6k8&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=3",
    "https://www.youtube.com/watch?v=lmaKCGrNT-o&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=4",
    "https://www.youtube.com/watch?v=WOVD2MLDtrE&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=6",
    "https://www.youtube.com/watch?v=gIJPiuC1o1c&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=7",
    "https://www.youtube.com/watch?v=2Ryn_BnvvRI&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=8",
    "https://www.youtube.com/watch?v=48PxyZtcdDI&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=9",
    "https://www.youtube.com/watch?v=tXVhv_h5-Vc&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=10",
    "https://www.youtube.com/watch?v=rENr1sxQUo8&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=11",
    "https://www.youtube.com/watch?v=0fy4w8T96_A&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=12",
    "https://www.youtube.com/watch?v=hE0Lav4MZDM&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=13",
    "https://www.youtube.com/watch?v=vNdUoxtL1Lk&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=14",
    "https://www.youtube.com/watch?v=me675RmNoOY&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=15",
    "https://www.youtube.com/watch?v=nkWxao_cwy0&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=16",
    "https://www.youtube.com/watch?v=qObvGNVLNfg&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=17",
    "https://www.youtube.com/watch?v=P6ep4duBLFY&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=18",
    "https://www.youtube.com/watch?v=5RRma-0Y8MU&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=19",
    "https://www.youtube.com/watch?v=lrE8fWHHyW4&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=20",
    "https://www.youtube.com/watch?v=pvbX0WOfmlc&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=21",
    "https://www.youtube.com/watch?v=k3WkJq478To&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=22",
    "https://www.youtube.com/watch?v=QYyZjsBOhs&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=23",
    "https://www.youtube.com/watch?v=617L_MOB37k&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=24",
    "https://www.youtube.com/watch?v=mtkKqn3W9sM&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=25",
    "https://www.youtube.com/watch?v=5EC-tYFZAE0&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=26",
    "https://www.youtube.com/watch?v=QL1aEdjAvF8&list=PLy8XVE4f72MpHMhep8YgAcUBg5ZtOYBAH&index=27",
]

# ================= RANDOM SELECTION =================
def get_random_link():
    """
    Probability:
      playlist = 1 / (len(LIVE_STREAMS) + 1)
      live      = len(LIVE_STREAMS) / (len(LIVE_STREAMS) + 1)

    Returns:
        (url, link_type)  where link_type ∈ {"LIVE", "PLAYLIST"}
    """
    total = len(LIVE_STREAMS) + 1
    pick = random.randint(1, total)

    if pick == 1:
        return random.choice(PLAYLIST_SONGS), "PLAYLIST"
    else:
        return random.choice(LIVE_STREAMS), "LIVE"
