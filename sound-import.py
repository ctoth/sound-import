import sys, os, sox
import tempfile
import ffmpeg

class Sound(object):
 def __init__(self, in_file, out_dir="."):
  self.in_file = in_file
  self.filename = os.path.splitext(os.path.basename(in_file))[0]
  self.out_file = os.path.join(out_dir, self.filename + ".m4a")
  self.out_dir = out_dir
  self.output_wav = os.path.join(out_dir, self.filename + ".wav")
  self.metadata = ffmpeg.probe(in_file)
  self._intermediate_filename = ""
  self._intermediate_fd = 0

 @classmethod
 def new_sound(cls, *args):
  try:
   new_sound = cls(*args)
  except:
   return 0
  for stream in new_sound.metadata['streams']:
   if stream["codec_type"] == "audio":
    return new_sound
  del new_sound
  return 0

 def __dell__(self):
  if self.intermediate_filename:
   os.close(self._intermediate_fd)
   os.remove(self.intermediate_filename)
   os.remove(self.output_wav)

 @property
 def intermediate_filename(self):
  if not self._intermediate_filename:
   self.intermediate_fd, self._intermediate_filename = tempfile.mkstemp(".wav")
  return self._intermediate_filename

 def convert_to_intermediate(self):
  ffmpeg.input(self.in_file).audio.output(self.intermediate_filename, format="wav", acodec='pcm_s24le').overwrite_output().run()
 
 def process_intermediate(self):
  run_import_chain(self.intermediate_filename, self.output_wav)

 def render_output(self):
  ffmpeg.input(self.output_wav, format="wav").audio.output(self.out_file, audio_bitrate=192000).overwrite_output().run()
  os.close(self.intermediate_fd)
  os.remove(self.intermediate_filename)
  os.remove(self.output_wav)

def convert_sound_file(in_file, out_dir):
 out_dir = os.path.dirname(output_filename(in_file, out_dir))
 if not os.path.exists(out_dir):
  os.makedirs(out_dir)
 print(in_file)
 sound = Sound.new_sound(in_file, out_dir)
 if not sound:
   return
 sound.convert_to_intermediate()
 sound.process_intermediate()
 sound.render_output()

def run_import_chain(in_file, out_file):
 trf = sox.Transformer()
 trf.set_input_format(file_type="wav")
 trf = trf.silence(location=1, buffer_around_silence=True)
 trf = trf.reverse()
 trf = trf.silence(location=1, buffer_around_silence=True)
 trf = trf.reverse()
 #trf = trf.norm()
 trf.build(in_file, out_file)

def output_filename(infile, outdir):
 infile = os.path.realpath(infile)
 outdir = os.path.realpath(outdir)
 common = os.path.commonprefix([infile, outdir])
 path = infile[len(common):]
 return os.path.join(outdir, path)


def main():
 out_dir = sys.argv[1]
 files = sys.argv[2:]
 list(map(lambda f: convert_sound_file(f, out_dir), files))

if __name__ == '__main__':
 main()