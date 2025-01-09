from f5_tts.api import F5TTS
import simpleaudio as sa

# Initializing F5tts class for our trained model
f5tts=F5TTS(ckpt_file=r"./TTS/Model/model_last_smaller.pt", model_type="E2-TTS", vocab_file=r"./TTS/Data/Atlas_pinyin/vocab.txt", device='cuda')

# Path to your wav file
audio_file = ".\Response_Audio\Output.wav"

# Function for creating TTS wav file response
def Speak( txt ):
    #Generating the audio file using F5TTS API
    wav,sr,spect=f5tts.infer(
        ref_file=".\TTS\Data\Atlas_pinyin\wavs\segment_0.wav",
        ref_text="excuse me, sir, but a collision has been detected ahead.",
        gen_text= txt,
        file_wave= audio_file
    )

    # Load the WAV file
    wave_obj = sa.WaveObject.from_wave_file(audio_file)
    play_obj = wave_obj.play()

    # Wait for playback to finish
    play_obj.wait_done()




Speak("i hung out with the geeks and gothics way before carti did.")