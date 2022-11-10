from pydub import AudioSegment
import glob



path = ''
files = [f for f in glob.glob(path + "**/*.mp3", recursive=True)]

for f in files:
  song_name = f[0:-4]
  print(song_name)

  sound = AudioSegment.from_mp3(song_name+'.mp3')
  sound.export(song_name+'.wav', format="wav")