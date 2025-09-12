### Preconditions
Preconditions for the chatbot:

- Rasa 3.x
- Streamlit

please use ```pip install rasa streamlit``` to initiate the installation

### Running the chatbot
To run the chatbot:
1. Open three terminal
2. For the first terminal, run ```rasa run actions```
3. For the second terminal, run ```rasa run --enable-api --cors "*"```
4. For the third terminal, run ```streamlit run app.py```
5. This will open a browser with the chatbot interface, you can chat with the chatbot.
6. To stop the chatbot, close all three terminal.

### Note
1. If the model cannot be run, please run ```rasa train``` in any terminal.
2. The datasets is placed in ./datasets/cleaned_movie.csv