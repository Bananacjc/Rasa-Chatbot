# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import pandas as pd
import ast

movies_df = pd.read_csv('./datasets/cleaned_movies.csv')

# action_match_director_search_movie
class ActionMatchDirectorSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_director_search_movie"
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        director = tracker.get_slot("director")
        if not director:
            dispatcher.utter_message(text="I need a director name to search.")
            return []
        results = movies_df[movies_df['director'].str.contains(director, case=False, na=False)]
        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find movies by {director}")
        else:
            top_movies = results['title'].head(5).tolist()
            formatted_list = "\n".join(f"- {movie}" for movie in top_movies)
            dispatcher.utter_message(
                text=f"Here are some movies directed by {director}:\n{formatted_list}"
            )
        return []

class ActionMatchActorSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_actor_search_movie"
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        actor = tracker.get_slot("actor")
        if not actor:
            dispatcher.utter_message(text="I need a cast name to search.")
            return []
        results = movies_df[movies_df['cast'].str.contains(actor, case=False, na=False)]
        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find movies with {actor}")
        else:
            top_movies = results['title'].head(5).tolist()
            formatted_list = "\n".join(f"- {movie}" for movie in top_movies)
            dispatcher.utter_message(
                text=f"Here are some movies with {actor}:\n{formatted_list}"
            )
        return []
    
class ActionMatchYearSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_year_search_movie"
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        year = tracker.get_slot("year")
        if not year:
            dispatcher.utter_message(text="I need a cast name to search.")
            return []
        results = movies_df[movies_df['release_year'].astype(str).str.contains(year, case=False, na=False)]
        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find movies in {year}")
        else:
            top_movies = results['title'].head(5).tolist()
            formatted_list = "\n".join(f"- {movie}" for movie in top_movies)
            dispatcher.utter_message(
                text=f"Here are some movies with {year}:\n{formatted_list}"
            )
        return []

class ActionMatchGenreSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_genre_search_movie"
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        genre = tracker.get_slot("genre")
        if not genre:
            dispatcher.utter_message(text="I need a cast name to search.")
            return []
        results = movies_df[movies_df['genres'].str.contains(genre, case=False, na=False)]
        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find {genre} movies")
        else:
            top_movies = results['title'].head(5).tolist()
            formatted_list = "\n".join(f"- {movie}" for movie in top_movies)
            dispatcher.utter_message(
                text=f"Here are some movies with {genre}:\n{formatted_list}"
            )
        return []

class ActionMatchRatingSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_rating_search_movie"
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        top_n = tracker.get_slot("rating")
        
        if not top_n:
            dispatcher.utter_message(text="I need a ranking to search.")
            return []
        if top_n:
            try:
                top_n = int(top_n)
            except ValueError:
                top_n = 5
        else:
            top_n = 5  # default if user didn't specify

        # Sort dataframe by rating (descending)
        results = movies_df.sort_values(by="rating", ascending=False).head(top_n)
        
        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find {top_n} movies")
        else:
            top_movies = results['title'].head(5).tolist()
            formatted_list = "\n".join(f"- {movie}" for movie in top_movies)
            dispatcher.utter_message(
                text=f"Here are the top {top_n} movies:\n{formatted_list}"
            )
        return []

class ActionMatchSeveralCriteriaSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_several_criteria_search_movie"
    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        director = tracker.get_slot("director")
        actor = tracker.get_slot("actor")
        genre = tracker.get_slot("genre")
        year = tracker.get_slot("year")
        rating = tracker.get_slot("rating")
        
        results = movies_df
        
        if director:
            results = results[results['director'].str.contains(director, case=False, na=False)]
        if actor:
            results = results[results['cast'].str.contains(director, case=False, na=False)]
        if genre:
            results = results[results['genres'].str.contains(director, case=False, na=False)]
        if year:
            results = results[results['release_year'].astype(str).str.contains(director, case=False, na=False)]
        if rating:
            results = results[results['rating'] >= float(rating)]
        
        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find movies with those criteria.")
        else:
            top_movies = results['title'].head(5).tolist()
            formatted_list = "\n".join(f"- {movie}" for movie in top_movies)
            dispatcher.utter_message(
                text=f"Here are some movies with {genre}:\n{formatted_list}"
            )
        return []

class ActionGetDirectorByMovieTitle(Action):
    def name(self) -> Text:
        return "action_get_director_by_movie_title"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        movie_title = tracker.get_slot("movie_title")
        if not movie_title:
            dispatcher.utter_message(text="I need a movie title to search.")
            return []

        results = movies_df[movies_df['title'].str.contains(movie_title, case=False, na=False)]

        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find {movie_title} movies")
        else:
            directors = results["director"].head().tolist()
            formatted_list = "\n".join(f"- {d}" for d in directors)
            dispatcher.utter_message(
                text=f"Director(s) of {movie_title}:\n{formatted_list}"
            )

        return []

class ActionGetActorByMovieTitle(Action):
    def name(self) -> Text:
        return "action_get_actor_by_movie_title"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        movie_title = tracker.get_slot("movie_title")
        if not movie_title:
            dispatcher.utter_message(text="I need a movie title to search.")
            return []

        results = movies_df[movies_df['title'].str.contains(movie_title, case=False, na=False)]

        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find {movie_title} movies")
        else:
            cast = results["cast"].head().tolist()
            formatted_list = "\n".join(f"- {c}" for c in cast)
            dispatcher.utter_message(
                text=f"Cast(s) of {movie_title}:\n{formatted_list}"
            )

        return []
    
class ActionGetYearByMovieTitle(Action):
    def name(self) -> Text:
        return "action_get_year_by_movie_title"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        movie_title = tracker.get_slot("movie_title")
        if not movie_title:
            dispatcher.utter_message(text="I need a movie title to search.")
            return []

        results = movies_df[movies_df['title'].str.contains(movie_title, case=False, na=False)]

        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find {movie_title} movies")
        else:
            year = results["release_year"].head(1).tolist()[0]
            dispatcher.utter_message(
                text=f"{movie_title} was released in: {year}"
            )

        return []



class ActionGetGenreByMovieTitle(Action):
    def name(self) -> Text:
        return "action_get_genre_by_movie_title"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        movie_title = tracker.get_slot("movie_title")
        if not movie_title:
            dispatcher.utter_message(text="I need a movie title to search.")
            return []

        results = movies_df[movies_df['title'].str.contains(movie_title, case=False, na=False)]

        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find {movie_title} movies")
        else:
            # Get the first row
            genre_data = results["genres"].iloc[0]

            # If the genre is a string that looks like a list, convert it
            if isinstance(genre_data, str):
                genre_data = ast.literal_eval(genre_data)

            formatted_list = "\n".join(f"- {g}" for g in genre_data)
            dispatcher.utter_message(
                text=f"Genre(s) of {movie_title}:\n{formatted_list}"
            )

        return []


class ActionGetRatingByMovieTitle(Action):
    def name(self) -> Text:
        return "action_get_rating_by_movie_title"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        movie_title = tracker.get_slot("movie_title")
        if not movie_title:
            dispatcher.utter_message(text="I need a movie title to search.")
            return []

        results = movies_df[movies_df['title'].str.contains(movie_title, case=False, na=False)]

        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find {movie_title} movies")
        else:
            directors = results["rating"].tolist()
            formatted_list = "\n".join(f"- {d}" for d in directors)
            dispatcher.utter_message(
                text=f"Rating of {movie_title}:\n{formatted_list}"
            )

        return []

class ActionGetMovieBasedAttribute(Action):
    def name(self) -> Text:
        return "action_get_movie_based_attribute"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        movie_attribute = tracker.get_slot("movie_attribute")
        genre = tracker.get_slot("genre")
        year = tracker.get_slot("year")

        if not movie_attribute:
            dispatcher.utter_message(text="I need to know what attribute you're looking for.")
            return []

        # Start with all movies
        results = movies_df.copy()

        # Filter by attribute keyword in the features/description column
        results = results[results['features'].str.contains(movie_attribute, case=False, na=False)]

        # Optional: filter by genre
        if genre:
            results = results[results['genre'].str.contains(genre, case=False, na=False)]

        # Optional: filter by year
        if year:
            results = results[results['release_year'].astype(str).str.contains(str(year), case=False, na=False)]

        if results.empty:
            dispatcher.utter_message(text=f"Sorry, I couldn't find movies with '{movie_attribute}'.")
            return []

        # Return top 5 matches
        top_movies = results['title'].head(5).tolist()
        formatted_list = "\n".join(f"- {movie}" for movie in top_movies)
        dispatcher.utter_message(
            text=f"Here are some movies that have '{movie_attribute}':\n{formatted_list}"
        )

        return []
