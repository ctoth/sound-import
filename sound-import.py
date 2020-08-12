import sys, os, sox
import tempfile
import ffmpeg

class Sound(object):
 def __init__(self, in_file, out_dir="."):
  self.in_file = in_file
  self.filename = os.path.splitext(os.path.basename(in_file))[0]
  self.out_file = os.path.join(out_dir, self.filename + ".m4a")
  self.out_dir = out_dir
  self.temp_wav = os.path.join(out_dir, self.filename + ".wav")
  self.metadata = ffmpeg.probe(in_file)
  self.temp_filename = ""

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
  if self.temp_filename:
   os.close(self.temp_fd)
   os.remove(self.temp_filename)
   os.remove(self.temp_wav)

 @property
 def get_temp_filename(self):
  if not self.temp_filename:
   (self.temp_fd, self.temp_filename) = tempfile.mkstemp()
  return self.temp_filename

 def convert(self):
  ffmpeg.input(self.in_file).audio.output(self.get_temp_filename, format="wav").overwrite_output().run()
  self.process(self.get_temp_filename)
  ffmpeg.input(self.temp_wav, format="wav").audio.output(self.out_file, format="adts").overwrite_output().run()
  os.close(self.temp_fd)
  os.remove(self.get_temp_filename)
  os.remove(self.temp_wav)

 def process(self, in_file):
  trf = sox.Transformer()
  trf.silence(location=1, buffer_around_silence=True)
  trf.reverse()
  trf.silence(location=1, buffer_around_silence=True)
  trf.reverse()
  trf.norm()
  trf.set_input_format(file_type="wav")
  trf.build(in_file, self.temp_wav)

def convert_sound_file(in_file, out_dir):
 sound = Sound.new_sound(in_file, out_dir)
 if sound:
  sound.convert()
  del sound

def run(*args):
 global in_file
 global out_dir
 check_args(*args)
 convert_sound_file(in_file, out_dir)

def check_args(*args):
 global in_file
 global out_dir
 try:
  in_file = args[1]
  out_dir = args[2]
 except IndexError:
  raise SystemExit(f"Usage: {sys.argv[0]} <in_file> <out_dir>")
 if not os.path.isfile(in_file):
  raise SystemExit(f"Invalid input file {in_file=}")
 if not os.path.isdir(out_dir):
  raise SystemExit(f"Invalid output directory {out_dir=}")
 in_file = os.path.abspath(in_file)
 out_dir = os.path.abspath(out_dir)

if __name__ == "__main__":
 run(*sys.argv)