"""Fetch user-supplied visual references outside the distributed mod."""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import quote
import hashlib

def commons(name):
 h=hashlib.md5(name.encode()).hexdigest()
 return 'https://upload.wikimedia.org/wikipedia/commons/'+h[0]+'/'+h[:2]+'/'+quote(name)

REFERENCES={
 'palazzo_acciaiuoli':'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e7/Palazzo_acciaiuoli_11.JPG/330px-Palazzo_acciaiuoli_11.JPG',
 'mendes_reform':'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRs_Vc0wFYZAsylzdloOUdYXU6iXGqIHL7msjcojqmDsD2pxKW5lQc2eA8&s=10',
 'berenberg_flag':'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSNFjkaP0Q3MWMtswwHYFxwpAOuXn-uxIujvHmjQ34SYg&s=10',
 'mortzenhaus':commons('Mortzenhaus_2.jpg'),
 'banco_del_giro':commons('Pinacoteca_Querini_Stampalia_-_Il_Bancogiro_di_Rialto_-_Gabriele_Bella.jpg'),
 'llotja_de_mar':'https://www.totbarcelona.cat/app/uploads/sites/11/2020/04/llotja-de-barcelona-baldiri-6.jpeg',
 'palazzo_salimbeni':commons('Palazzo_Salimbeni,_Siena,_Headquarters_of_Monte_dei_Paschi_di_Siena,_the_worlds_oldest_surviving_bank.jpg'),
 'palace_saint_george':commons('Palazzo_San_Georgio_Genova_W.jpg'),
}

if __name__=='__main__':
 folder=Path(__file__).resolve().parents[1]/'dist/expanded-bank-references'
 folder.mkdir(parents=True,exist_ok=True)
 for key,url in REFERENCES.items():
  path=folder/(key+'.png')
  try:
   if not path.exists():path.write_bytes(urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40).read())
   print(key,len(path.read_bytes()))
  except Exception as error:print(key,str(error))
