"""Local renderer adapted from the approved facecam/gameplay edit. Cross-platform (macOS, Windows, Linux)."""
import json
import math
import shutil
import subprocess as sp
import sys
import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

W,H,FPS=720,1280,30


def resolve_font():
    bundled = Path(__file__).resolve().parent / 'assets' / 'fonts' / 'default.ttf'
    if bundled.is_file():
        return str(bundled)
    candidates = [
        # macOS
        '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
        '/Library/Fonts/Arial Bold.ttf',
        '/System/Library/Fonts/Helvetica.ttc',
        # Windows
        'C:\\Windows\\Fonts\\arialbd.ttf',
        'C:\\Windows\\Fonts\\arial.ttf',
        'C:\\Windows\\Fonts\\segoeui.ttf',
        'C:\\Windows\\Fonts\\tahoma.ttf',
        # Linux
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
        '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf',
        '/usr/share/fonts/TTF/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf',
    ]
    for c in candidates:
        if Path(c).is_file():
            return c
    return None


def get_font(size):
    font_path = resolve_font()
    if font_path:
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def synthesize_speech(text, base_path, lang='id'):
    base_path = Path(base_path)
    # 1. edge-tts (cross-platform: Windows, Linux, macOS)
    try:
        import asyncio, edge_tts
        voice = 'id-ID-GadisNeural' if lang == 'id' else 'en-US-JennyNeural'
        out = base_path.with_suffix('.mp3')
        async def _run():
            comm = edge_tts.Communicate(text, voice)
            await comm.save(str(out))
        asyncio.run(_run())
        if out.exists() and out.stat().st_size > 0:
            return out
    except Exception:
        pass

    # 2. macOS say command
    if sys.platform == 'darwin' and shutil.which('say'):
        out = base_path.with_suffix('.aiff')
        voice = 'Damayanti' if lang == 'id' else 'Samantha'
        rate = '185' if lang == 'id' else '195'
        r = sp.run(['say', '-v', voice, '-r', rate, '-o', str(out)], input=text.encode(), capture_output=True, timeout=60)
        if r.returncode != 0:
            r = sp.run(['say', '-v', 'Samantha', '-r', '195', '-o', str(out)], input=text.encode(), capture_output=True, timeout=60)
        if r.returncode == 0 and out.exists() and out.stat().st_size > 0:
            return out

    # 3. Windows PowerShell SAPI
    if sys.platform == 'win32' and shutil.which('powershell'):
        out = base_path.with_suffix('.wav')
        script = f"Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.SetOutputToWaveFile('{str(out).replace(chr(39), chr(39)+chr(39))}'); $s.Speak('{text.replace(chr(39), chr(39)+chr(39))}'); $s.Dispose();"
        r = sp.run(['powershell', '-NoProfile', '-Command', script], capture_output=True, timeout=60)
        if r.returncode == 0 and out.exists() and out.stat().st_size > 0:
            return out

    # 4. Linux espeak / espeak-ng
    espeak_bin = shutil.which('espeak-ng') or shutil.which('espeak')
    if espeak_bin:
        out = base_path.with_suffix('.wav')
        r = sp.run([espeak_bin, '-w', str(out), text], capture_output=True, timeout=60)
        if r.returncode == 0 and out.exists() and out.stat().st_size > 0:
            return out

    # 5. Silent audio fallback via ffmpeg (so render never fails if TTS offline)
    out = base_path.with_suffix('.wav')
    sp.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', '1.5', str(out)], capture_output=True, timeout=30)
    return out


def run(args,timeout=120):
    r=sp.run([str(a) for a in args],capture_output=True,timeout=timeout)
    if r.returncode: raise RuntimeError(f'{Path(str(args[0])).name} gagal saat render; periksa audio dan ruang disk.')
    return r.stdout


def duration(path):
    return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',path]).strip())


def draw_text(im,text,y,size=42,color='white',limit=2):
    d=ImageDraw.Draw(im)
    for s in range(size,19,-2):
        font=get_font(s); lines=[]; line=''
        for word in text.split():
            if d.textlength(word,font=font)>640:
                raise ValueError('Kata terlalu panjang untuk caption; pisahkan teks di editor.')
            proposed=(line+' '+word).strip()
            if d.textlength(proposed,font=font)>640 and line: lines.append(line); line=word
            else: line=proposed
        if line: lines.append(line)
        if len(lines)<=limit: break
    if len(lines)>limit: raise ValueError('Teks terlalu panjang; pendekkan judul atau subtitle.')
    for i,line in enumerate(lines):
        d.text((360,y+i*(s+10)),line,anchor='mt',font=font,fill=color,stroke_width=3 if s>24 else 1,stroke_fill='black')


def frame(source,t):
    raw=run(['ffmpeg','-v','error','-ss',str(t),'-i',source,'-frames:v','1','-vf','scale=960:540','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
    if len(raw)!=960*540*3: raise ValueError('Gagal membaca frame video.')
    return Image.frombytes('RGB',(960,540),raw)


def layout(image,t,phase,clip,creator):
    im=Image.new('RGB',(W,H),'#101014')
    face=clip.get('face_box')
    mode=clip.get('layout_mode','split')

    if not face or mode=='no_face':
        # Gameplay full frame mode
        game=ImageOps.contain(image,(720,720),method=Image.Resampling.LANCZOS)
        if phase!='main': game=ImageEnhance.Brightness(game).enhance(.42)
        y_pos=(H-game.height)//2
        im.paste(game,(0,y_pos))
        ImageDraw.Draw(im).rectangle((0,y_pos-4,720,y_pos),fill='#ffd24a')
        ImageDraw.Draw(im).rectangle((0,y_pos+game.height,720,y_pos+game.height+4),fill='#ffd24a')
        draw_text(im,creator,180,32,'#ffd24a')
        if phase=='intro':
            draw_text(im,clip['title'].upper(),850,42,'#ffd24a')
            draw_text(im,clip['hook'],960,36)
            draw_text(im,'Watch what happens next.',1120,28)
        elif phase=='cta':
            draw_text(im,'MORE GAMING?',850,44,'#ffd24a')
            draw_text(im,'Subscribe to '+creator,960,38)
            draw_text(im,'on YouTube',1050,34)
        else:
            for c in clip.get('captions',[]):
                if c['start']<=t<c['end']:
                    draw_text(im,c['text'],1050,42,'#ffd24a' if clip.get('zoom_at',0)<=t<clip.get('zoom_at',0)+1.6 else 'white')
                    break
        draw_text(im,'Source: '+creator,1235,20,'#b9b9c3',1)
        return im

    # Facecam is present
    x,y,w,h=face
    box=(int(x*960),int(y*540),int((x+w)*960),int((y+h)*540))
    cam=image.crop(box)
    if phase=='main' and clip.get('zoom_at',0)<=t<clip.get('zoom_at',0)+1.6:
        cw,ch=cam.size
        cam=cam.crop((int(cw*.15),int(ch*.1),int(cw*.85),ch))

    if mode=='split':
        # 1. Top Facecam: y = 0..460
        cam_fitted=ImageOps.fit(cam,(720,460),method=Image.Resampling.LANCZOS)
        if phase!='main': cam_fitted=ImageEnhance.Brightness(cam_fitted).enhance(.6)
        im.paste(cam_fitted,(0,0))

        # 2. Middle Banner: y = 460..520 (Height 60px)
        d=ImageDraw.Draw(im)
        d.rectangle((0,460,720,520),fill='#101014')
        d.rectangle((0,460,720,463),fill='#ffd24a')
        d.rectangle((0,517,720,520),fill='#ffd24a')
        banner_title=f"{creator.upper()} / {clip.get('title','SHORT').upper()}"
        font_b=get_font(24)
        if d.textlength(banner_title,font=font_b)>680:
            font_b=get_font(20)
        d.text((360,477),banner_title,anchor='mt',font=font_b,fill='#ffd24a',stroke_width=1,stroke_fill='black')

        # 3. Bottom Gameplay: y = 520..1280 (Height 760px)
        game=ImageOps.fit(image,(720,760),method=Image.Resampling.LANCZOS)
        if phase!='main': game=ImageEnhance.Brightness(game).enhance(.42)
        im.paste(game,(0,520))

        # Text / Subtitles overlay on lower gameplay
        clip_lang = clip.get('lang', 'id')
        watch_next = 'Tonton apa yang terjadi selanjutnya.' if clip_lang == 'id' else 'Watch what happens next.'
        more_gaming = 'MAU NONTON LAGI?' if clip_lang == 'id' else 'MORE GAMING?'
        sub_creator = f'Subscribe ke {creator}' if clip_lang == 'id' else f'Subscribe to {creator}'
        on_platform = 'di YouTube' if clip_lang == 'id' else 'on YouTube'

        if phase=='intro':
            draw_text(im,clip['title'].upper(),680,44,'#ffd24a')
            draw_text(im,clip['hook'],800,38)
            draw_text(im,watch_next,1080,28)
        elif phase=='cta':
            draw_text(im,more_gaming,680,46,'#ffd24a')
            draw_text(im,sub_creator,800,38)
            draw_text(im,on_platform,900,34)
        else:
            for c in clip.get('captions',[]):
                if c['start']<=t<c['end']:
                    is_zoom=clip.get('zoom_at',0)<=t<clip.get('zoom_at',0)+1.6
                    draw_text(im,c['text'],1100,42,'#ffd24a' if is_zoom else 'white')
                    break

    else:
        # mode == 'contained'
        cam_fitted=ImageOps.fit(cam,(720,430),method=Image.Resampling.LANCZOS)
        if phase!='main': cam_fitted=ImageEnhance.Brightness(cam_fitted).enhance(.6)
        im.paste(cam_fitted,(0,0))
        ImageDraw.Draw(im).rectangle((0,430,720,434),fill='#ffd24a')

        game=image.resize((720,405),Image.Resampling.LANCZOS)
        if phase!='main': game=ImageEnhance.Brightness(game).enhance(.42)
        im.paste(game,(0,435))
        ImageDraw.Draw(im).rectangle((0,840,720,844),fill='#ffd24a')

        clip_lang = clip.get('lang', 'id')
        watch_next = 'Tonton apa yang terjadi selanjutnya.' if clip_lang == 'id' else 'Watch what happens next.'
        more_gaming = 'MAU NONTON LAGI?' if clip_lang == 'id' else 'MORE GAMING?'
        sub_creator = f'Subscribe ke {creator}' if clip_lang == 'id' else f'Subscribe to {creator}'
        on_platform = 'di YouTube' if clip_lang == 'id' else 'on YouTube'

        if phase=='intro':
            draw_text(im,clip['title'].upper(),870,42,'#ffd24a')
            draw_text(im,clip['hook'],970,36)
            draw_text(im,watch_next,1120,28)
        elif phase=='cta':
            draw_text(im,more_gaming,870,44,'#ffd24a')
            draw_text(im,sub_creator,970,38)
            draw_text(im,on_platform,1060,34)
        else:
            for c in clip.get('captions',[]):
                if c['start']<=t<c['end']:
                    is_zoom=clip.get('zoom_at',0)<=t<clip.get('zoom_at',0)+1.6
                    draw_text(im,c['text'],950,42,'#ffd24a' if is_zoom else 'white')
                    break

    draw_text(im,'Source: '+creator,1235,20,'#b9b9c3',1)
    return im


def render_clip(source,folder,clip,creator):
    source,folder=Path(source),Path(folder)
    folder.mkdir(exist_ok=True,parents=True)
    revision=uuid.uuid4().hex[:10]
    clip_lang = clip.get('lang', 'id')
    cta_text = f'Subscribe ke {creator} di YouTube untuk tontonan seru lainnya.' if clip_lang == 'id' else ('Subscribe to '+creator+' on YouTube for more gaming.')
    intro_audio = synthesize_speech(clip['narration'], folder / f'intro-{revision}', clip_lang)
    cta_audio = synthesize_speech(cta_text, folder / f'cta-{revision}', clip_lang)
    intro=math.ceil((duration(intro_audio)+.15)*FPS)/FPS
    cta=math.ceil((duration(cta_audio)+.15)*FPS)/FPS
    length=duration(source)
    if not 1<=length<=61: raise ValueError('Renderer dibatasi klip maksimal 60 detik.')
    middle=frame(source,min(length/2,length-.1))
    last=frame(source,max(0,length-.2))
    opening=layout(middle,0,'intro',clip,creator)
    ending=layout(last,length,'cta',clip,creator)
    opening.save(folder/f'opening-{revision}.jpg'); ending.save(folder/f'ending-{revision}.jpg')
    picture=folder/f'picture-{revision}.mp4'
    enc=sp.Popen(['ffmpeg','-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(picture)],stdin=sp.PIPE,stderr=sp.DEVNULL)
    dec=None
    try:
        for _ in range(round(intro*FPS)): enc.stdin.write(opening.tobytes())
        dec=sp.Popen(['ffmpeg','-v','error','-i',str(source),'-vf','scale=960:540,fps=30','-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=sp.PIPE,stderr=sp.DEVNULL)
        n=0; size=960*540*3
        while True:
            raw=bytearray()
            while len(raw)<size:
                part=dec.stdout.read(size-len(raw))
                if not part: break
                raw.extend(part)
            if not raw: break
            if len(raw)!=size: raise ValueError('Frame video tidak lengkap.')
            im=layout(Image.frombytes('RGB',(960,540),bytes(raw)),n/FPS,'main',clip,creator)
            if n==round(clip['zoom_at']*FPS): im.save(folder/f'reaction-{revision}.jpg')
            enc.stdin.write(im.tobytes()); n+=1
        if dec.wait(timeout=30)!=0: raise RuntimeError('Decoder video gagal.')
        if abs(n/FPS-length)>.2: raise RuntimeError('Durasi frame tidak cocok dengan audio sumber.')
        for _ in range(round(cta*FPS)): enc.stdin.write(ending.tobytes())
        enc.stdin.close()
        if enc.wait(timeout=120)!=0: raise RuntimeError('Encoder video gagal.')
    finally:
        for process in (dec,enc):
            if process and process.poll() is None:
                process.kill(); process.wait()
    total=intro+n/FPS+cta
    filters=(f'[0:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{intro},asetpts=PTS-STARTPTS[a];'
             f'[1:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{n/FPS},asetpts=PTS-STARTPTS[b];'
             f'[2:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{cta},asetpts=PTS-STARTPTS[c];'
             '[a][b][c]concat=n=3:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[audio]')
    output=folder/f'short-{revision}.mp4'
    run(['ffmpeg','-v','error','-n','-i',intro_audio,'-i',source,'-i',cta_audio,'-i',picture,'-filter_complex',filters,'-map','3:v','-map','[audio]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(total),'-movflags','+faststart',output],300)
    run(['ffmpeg','-v','error','-i',output,'-f','null','-'],120)
    check=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',output]))
    if abs(float(check['format']['duration'])-total)>.15 or not any(s['codec_type']=='audio' for s in check['streams']):
        raise RuntimeError('Validasi output gagal.')
    picture.unlink()  # only this render's generated intermediate; retain source and older finished revisions
    return str(output)
