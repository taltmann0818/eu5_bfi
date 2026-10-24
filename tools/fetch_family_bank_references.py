"""User-supplied architectural and painting references, kept outside runtime."""
from pathlib import Path
from urllib.request import Request,urlopen

REFERENCES={
 'palazzo_busini_bardi':'https://upload.wikimedia.org/wikipedia/commons/6/6c/Palazzo_busini-bardi_11.JPG',
 'fuggerhauser':'https://lh3.googleusercontent.com/gps-cs-s/ANWiy9TclmjtbSXxjsAHSHa6rL7K0G5oQNrYQRbisuDcnF8sm-dkZbPh47oZtMJC9M0eaqsopEfz7I09FFCgsMZwmMbw30AuPwrCkSlJKuHK8JiZYfnq8mjcsV_iWYkVVBpZGuNsdxqr=s680-w680-h510-rw',
 'welserhaus':'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a6/Philippine-Welser-Stra%C3%9Fe_13_Augsburg.JPG/3840px-Philippine-Welser-Stra%C3%9Fe_13_Augsburg.JPG',
 'choice_of_banks':'https://media.licdn.com/dms/image/v2/C4D12AQEYApZpRDjr0A/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1597629430592?e=2147483647&v=beta&t=YZ0NzU_WbnyTGqMFg3--tyWLJaOykPUj4mZ5b51vYY8',
 'palazzo_peruzzi':'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ab/Piazza_dei_peruzzi%2C_Palazzo_Peruzzi-Bourbon_del_Monte_01.jpg/330px-Piazza_dei_peruzzi%2C_Palazzo_Peruzzi-Bourbon_del_Monte_01.jpg',
}

if __name__=='__main__':
 folder=Path(__file__).resolve().parents[1]/'dist/family-bank-references'
 folder.mkdir(parents=True,exist_ok=True)
 for name,url in REFERENCES.items():
  target=folder/(name+'.png')
  try:
   if not target.exists():target.write_bytes(urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read())
   print(name,len(target.read_bytes()))
  except Exception as error:print(name,type(error).__name__,str(error))
