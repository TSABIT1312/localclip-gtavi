"""Offline integration: real FFmpeg/TTS render, scripted AI response (not a live API test)."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import app

SOURCE=Path('/tmp/kai-hellcat-source.bInmMH/hellcat.mp4')
assert SOURCE.is_file(), 'Known local fixture missing'
with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp); folder=root/'smoke'; folder.mkdir()
    app.run(['ffmpeg','-v','error','-n','-ss','5','-i',SOURCE,'-t','9','-c:v','libx264','-preset','fast','-c:a','aac',folder/'source.mp4'])
    (folder/'captions.srt').write_text('1\n00:00:01,000 --> 00:00:04,000\nIt is a Hellcat.\n\n2\n00:00:05,000 --> 00:00:08,000\nHold on.\n')
    job={'id':'smoke','upload':True,'creator':'Kai Cenat','count':1,'stage':'queued','title':'Offline test','clips':[],'warnings':[]}
    replies=[{'clips':[{'start':0,'end':8.8,'title':'A Hellcat appears','hook':'Can he steal it?','narration':'Kai found a Hellcat. Watch what happens.','reason':'Scripted fixture, bukan rekomendasi AI.','priority':'medium'}]}, {'face_box':[0,.4,.204,.206],'zoom_at':5,'captions':[{'start':1,'end':4,'text':'It is a Hellcat.'},{'start':5,'end':8,'text':'Hold on.'}],'warning':'Scripted crop for offline smoke test'}]
    with patch.object(app,'DATA',root), patch.object(app,'ask_ai',side_effect=replies) as ai:
        assert app.BUSY.acquire(blocking=False)
        app.process_job(job,'not-a-real-key','test-model')
        assert job['stage']=='done',job
        assert ai.call_count==2
        assert (folder/job['clips'][0]['file']).is_file()
        assert (folder/'shorts.zip').is_file()
        print(json.dumps({'stage':job['stage'],'clips':len(job['clips']),'ai':'mocked; no external API call','render':'real source, FFmpeg and local TTS'},indent=2))
