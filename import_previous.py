"""Import the user's five previously rendered clips, no API calls."""
import json
import shutil
from pathlib import Path
from app import DATA, archive, probe, frame_jpeg

root=Path('/Users/macbookair/kai-top5.RyaZSp')
ident='previous-kai-top5'
folder=DATA/ident
if folder.exists():
    raise SystemExit('Previous batch already imported; kept unchanged.')
folder.mkdir(mode=0o700)
entries=[('hellcat','Hellcat tidak bisa dicuri',4455,4476),('haircut','Duit potong rambut kurang',5934,5978),('escape','Kabur gagal, kehilangan $527',5240,5282),('dog','Mau elus anjing, ditolak',4483,4512),('book-fixed','Pamer membaca, malah jadi PR',2969,3003)]
job={'id':ident,'title':'Kai Cenat · 5 klip yang sudah dibuat','stage':'done','creator':'Kai Cenat','clips':[],'zip':None,'warnings':['Arsip hasil sesi sebelumnya; bukan analisis AI baru.'],'error':None}
for i,(name,title,start,end) in enumerate(entries):
    filename=f'{i+1:02d}-{name}.mp4'
    shutil.copyfile(root/f'kai-{name}-short.mp4',folder/filename)
    length=probe(folder/filename)
    poster=f'{i+1:02d}.jpg'; (folder/poster).write_bytes(frame_jpeg(folder/filename,min(7,length/2)))
    job['clips'].append({'title':title,'start':start,'end':end,'reason':'Pilihan dari sesi sebelumnya, CTA sudah Kai Cenat.','priority':'high','status':'done','file':filename,'poster':poster,'duration':length})
(folder/'job.json').write_text(json.dumps(job,ensure_ascii=False,indent=2))
archive(job)
print('Imported 5 existing videos; no API calls.')
