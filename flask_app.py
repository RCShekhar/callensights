from flask import Flask

APP_NAME='Callensights.com'

app = Flask(APP_NAME.split('.')[0])
app.config.from_prefixed_env('CANS')
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024 * 1024
app.config['AUDIO_BUCKET']='callensights-audio'
app.config['FEEDBACK_BUCKET']='callensights-transcript'

app.config['RAW_AUDIO_PATH']=app.config['AUDIO_BUCKET'] + '/raw_audio'
app.config['DENOISED_AUDIO_PATH']=app.config['AUDIO_BUCKET'] + '/denoised_audio'
app.config['TRANSCRIPT_PATH']=app.config['FEEDBACK_BUCKET'] + '/transcript'
app.config['FEEDBACK_PATH']=app.config['FEEDBACK_BUCKET']+ '/feedback'
