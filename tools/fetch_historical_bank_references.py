"""Download the user's visual references for local inspection, not runtime use."""
from pathlib import Path
from urllib.request import Request, urlopen

REFERENCES = {
    'wisselbank': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/2/28/Saenredam_-_Het_oude_stadhuis_te_Amsterdam.jpeg/960px-Saenredam_-_Het_oude_stadhuis_te_Amsterdam.jpeg',
    'amsterdam_flag': 'https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6d/Flag_of_Amsterdam.svg/1280px-Flag_of_Amsterdam.svg.png',
    'riksbank': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJCbaia8ots21yMsTaid-cj1CNNt7gpQi-MEO5qg7nPQ&s=10',
    'riksbank_flag': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZ9kgPVVsFf2tnAIfgVjXCztO3qM6GOPm_h31F6Beok6Qw2lmsso6yq54&s',
    'medici': 'https://www.theflorentine.net/wp-content/uploads/2021/11/Palazzo-Medici-Riccardi5.jpg',
    'boe_logo': 'https://thumb.wikimedia.org/wikipedia/en/thumb/7/72/Bank_of_England_logo.svg/250px-Bank_of_England_logo.svg.png',
}

if __name__ == '__main__':
    folder = Path(__file__).resolve().parents[1]/'dist/historical-bank-references'
    folder.mkdir(parents=True, exist_ok=True)
    for name, url in REFERENCES.items():
        target = folder/(name+'.png')
        if not target.exists():
            try:
                target.write_bytes(urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=40).read())
            except Exception as error:
                print(name, type(error).__name__, str(error)); continue
        print(target)
