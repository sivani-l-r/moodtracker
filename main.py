from flask import Flask, render_template, request, jsonify
import plotly.graph_objs as go
import plotly.offline as opy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
app = Flask(__name__)

analyzer = SentimentIntensityAnalyzer()
user_moods = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mood', methods=['POST'])
def get_mood():
    text = request.json['text']
    username = request.json['username']
    mood, date = determine_mood(text, username)
    user_moods.setdefault(username, []).append({'date': date, 'mood': mood})
    return jsonify({'mood': mood})


def determine_mood(text, username):
    sentiment = analyzer.polarity_scores(text)
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if sentiment['compound'] >= 0.05:
        return "happy", date
    elif -0.05 < sentiment['compound'] < 0.05:
        return "neutral", date
    else:
        return "sad", date

@app.route('/moodlog.html', methods=['GET'])
def moodlog():
    return render_template('moodlog.html')

@app.route('/get_mood_history', methods=['GET'])
def get_mood_history():
    username = request.args.get('username', default='')
    moods = user_moods.get(username, [])

    # Create a Plotly graph
    if moods:
        dates = [mood['date'] for mood in moods]
        mood_values = [mood['mood'] for mood in moods]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=mood_values, mode='lines+markers', name='Mood Progress'))

        plot_div = opy.plot(fig, auto_open=False, output_type='div')

        return render_template('moodhistory.html', username=username, moods=moods, plot_div=plot_div)
    else:
        return render_template('moodhistory.html', username=username, moods=moods, plot_div=None)


if __name__ == '__main__':
    app.run(debug=True)
