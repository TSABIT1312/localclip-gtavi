"""Run: .venv/bin/python -m unittest -v test_app.py"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
import app

class Checks(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(app.app)
        self.headers={'X-Local-Token':app.TOKEN}

    def test_urls(self):
        self.assertEqual(app.youtube_url('https://youtu.be/7mjhCbFi9Wk?si=test'),'https://www.youtube.com/watch?v=7mjhCbFi9Wk')
        for u in ['http://youtube.com/watch?v=7mjhCbFi9Wk','https://youtube.com.evil.test/watch?v=7mjhCbFi9Wk','https://127.0.0.1/a','https://user@youtube.com/watch?v=7mjhCbFi9Wk','https://youtube.com/playlist?list=a']:
            with self.assertRaises(ValueError): app.youtube_url(u)

    def test_srt(self):
        rows=app.srt_rows('1\n00:00:01,000 --> 00:00:02,500\nHello\nworld\n\n2\n00:00:03,000 --> 00:00:04,000\nNext\n')
        self.assertEqual(rows[0],{'start':1.,'end':2.5,'text':'Hello world'})
        self.assertEqual(len(rows),2)
        with self.assertRaises(ValueError): app.srt_rows('not subtitles')

    def test_access_boundaries(self):
        self.assertEqual(self.client.post('/api/settings',json={}).status_code,403)
        self.assertEqual(self.client.post('/api/settings',headers={**self.headers,'Origin':'https://evil.test'},json={}).status_code,403)
        self.assertEqual(self.client.get('/api/status',headers={'Host':'evil.test'}).status_code,400)
        self.assertEqual(self.client.get('/media/missing/../../app.py').status_code,404)
        result=self.client.get('/api/status')
        self.assertEqual(result.status_code,200)
        self.assertNotIn('api_key',result.json())

    def test_model_validation(self):
        body=dict(title='A',hook='B',narration='C',creator='Kai',zoom_at=1,captions=[dict(start=0,end=2,text='Hi')])
        self.assertEqual(app.EditClip(**body,face_box=[0,.4,.2,.2],lang='id').creator,'Kai')
        self.assertEqual(app.EditClip(**body,face_box=[0,.4,.2,.2],lang='en').lang,'en')
        self.assertEqual(app.EditClip(**body,start=10.0,end=25.0).start,10.0)
        # Middle cut validation
        clip_with_cut = app.EditClip(**body,start=10.0,end=25.0,cut_start=15.0,cut_end=20.0)
        self.assertEqual(clip_with_cut.cut_start, 15.0)
        self.assertEqual(clip_with_cut.cut_end, 20.0)
        # cut_start without cut_end or vice-versa
        with self.assertRaises(ValueError): app.EditClip(**body,start=10.0,end=25.0,cut_start=15.0)
        with self.assertRaises(ValueError): app.EditClip(**body,start=10.0,end=25.0,cut_end=20.0)
        # cut bounds outside start/end or inverted
        with self.assertRaises(ValueError): app.EditClip(**body,start=10.0,end=25.0,cut_start=20.0,cut_end=15.0)
        with self.assertRaises(ValueError): app.EditClip(**body,start=10.0,end=25.0,cut_start=9.0,cut_end=15.0)
        with self.assertRaises(ValueError): app.EditClip(**body,start=10.0,end=25.0,cut_start=15.0,cut_end=26.0)
        with self.assertRaises(ValueError): app.EditClip(**body,start=10.0,end=25.0,cut_start=10.1,cut_end=20.0) # < 0.2s before cut
        with self.assertRaises(ValueError): app.EditClip(**body,start=25.0,end=10.0)
        with self.assertRaises(ValueError): app.EditClip(**body,start=0.0,end=70.0)
        for box in [[.9,0,.2,.2],[0,0,-.1,.2],[0,0,float('nan'),.2]]:
            with self.assertRaises(ValueError): app.EditClip(**body,face_box=box)
        with self.assertRaises(ValueError): app.Caption(start=3,end=2,text='wrong')

    def test_clip_source_and_render_endpoint(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(app,'DATA',Path(tmp)), patch.object(app,'JOBS',{}):
            folder=Path(tmp)/'testjob'; folder.mkdir()
            (folder/'source.mp4').write_bytes(b'fake')
            clip_dir=folder/'clip-0'; clip_dir.mkdir()
            (clip_dir/'source.mp4').write_bytes(b'fakeclip')
            app.JOBS['testjob']={
                'id':'testjob','title':'Test','upload':True,'duration':120.0,'creator':'Tester',
                'clips':[{'title':'C1','start':10.0,'end':25.0,'duration':15.0,'source_file':'clip-0/source.mp4'}]
            }
            res=self.client.get('/api/jobs/testjob/clips/0/source')
            self.assertEqual(res.status_code,200)
            data=res.json()
            self.assertEqual(data['start'],10.0)
            self.assertEqual(data['end'],25.0)
            self.assertEqual(data['source_start'],0.0)
            self.assertEqual(data['source_end'],120.0)
            self.assertEqual(data['source_file'],'source.mp4')
            self.assertIsNone(data.get('cut_start'))
            self.assertIsNone(data.get('cut_end'))

            app.JOBS['testjob']['clips'][0]['cut_start'] = 14.0
            app.JOBS['testjob']['clips'][0]['cut_end'] = 18.0
            res2=self.client.get('/api/jobs/testjob/clips/0/source')
            self.assertEqual(res2.status_code,200)
            self.assertEqual(res2.json()['cut_start'],14.0)
            self.assertEqual(res2.json()['cut_end'],18.0)

            # Test pre-generated filmstrip & waveform serving
            (clip_dir/'filmstrip.jpg').write_bytes(b'fakejpeg')
            res_film=self.client.get('/api/jobs/testjob/clips/0/filmstrip')
            self.assertEqual(res_film.status_code,200)
            self.assertEqual(res_film.headers['content-type'],'image/jpeg')

            (clip_dir/'waveform.png').write_bytes(b'fakepng')
            res_wave=self.client.get('/api/jobs/testjob/clips/0/waveform')
            self.assertEqual(res_wave.status_code,200)
            self.assertEqual(res_wave.headers['content-type'],'image/png')

    def test_upload_and_missing_key(self):
        with patch.object(app,'KEY',''):
            self.assertEqual(self.client.post('/api/jobs',headers=self.headers,data={'url':'https://youtu.be/7mjhCbFi9Wk','consent':'yes'}).status_code,400)
        with patch.object(app,'KEY','test-not-a-real-key'):
            response=self.client.post('/api/jobs',headers=self.headers,data={'consent':'yes'},files={'video':('x.mp4',b'not video','video/mp4')})
            self.assertEqual(response.status_code,400)

    def test_settings_with_custom_base_url(self):
        s = app.Settings(api_key='sk-test', model='anthropic/claude-3-5-sonnet', base_url='http://localhost:20128/v1/')
        self.assertEqual(s.base_url, 'http://localhost:20128')
        self.assertEqual(s.model, 'anthropic/claude-3-5-sonnet')
        resp = self.client.post('/api/settings', headers=self.headers, json={'api_key': 'sk-test', 'model': 'anthropic/claude-3-5-sonnet', 'base_url': 'http://localhost:20128/v1/'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['base_url'], 'http://localhost:20128')
        self.assertEqual(resp.json()['model'], 'anthropic/claude-3-5-sonnet')

    def test_existing_media_only(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(app,'DATA',Path(tmp)),patch.object(app,'JOBS',{}):
            folder=Path(tmp)/'test';folder.mkdir();(folder/'ok.mp4').write_bytes(b'abc');(folder/'private.json').write_text('secret')
            app.JOBS['test']={'clips':[{'file':'ok.mp4'}],'zip':None}
            self.assertEqual(self.client.get('/media/test/ok.mp4').status_code,200)
            self.assertEqual(self.client.get('/media/test/private.json').status_code,404)

if __name__=='__main__': unittest.main()
