import pandas as pd
import ast
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.forms import FormValidationAction

# List of valid movie-search intents
VALID_MOVIE_INTENTS = [
    "movie_match_director",
    "movie_match_actor",
    "movie_match_year",
    "movie_match_genre",
    "movie_match_several_criteria",
    "movie_match_rating",
    "get_director_by_movie_title",
    "get_actor_by_movie_title",
    "get_year_by_movie_title",
    "get_genre_by_movie_title",
    "get_rating_by_movie_title",
    "get_movie_attributes"
]

CONFIDENCE_THRESHOLD = 0.6

def should_run_movie_search(tracker: Tracker) -> bool:
    """Check if the latest message is a movie-search intent with high enough confidence."""
    intent = tracker.latest_message.get('intent', {}).get('name')
    confidence = tracker.latest_message.get('intent', {}).get('confidence', 0)
    return intent in VALID_MOVIE_INTENTS and confidence >= CONFIDENCE_THRESHOLD



MOVIE_DB_PATH = "./cleaned_movies.csv"

# Load dataset
netflix_df = pd.read_csv(MOVIE_DB_PATH)

for col in ["director", "cast", "genres"]:
    netflix_df[col] = netflix_df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

# Helper functions
def call_local_movie_search(tracker: Tracker, dispatcher: CollectingDispatcher):
    # only slots that can actually FILTER results
    relevant_slots = ["director", "actor", "genre", "rating", "time"]

    if not any(tracker.get_slot(s) for s in relevant_slots):
        dispatcher.utter_message("I didn't get any movie criteria. Please specify a genre, actor, director, rating, or year.")
        return

    df_filtered = netflix_df.copy()
    filters_applied = 0

    for key, value in tracker.slots.items():
        if value is None:
            continue
        if key == "director":
            df_filtered = df_filtered[df_filtered["director"].apply(
                lambda x: isinstance(x, list) and value.lower() in [d.lower() for d in x]
            )]; filters_applied += 1
        elif key == "actor":
            df_filtered = df_filtered[df_filtered["cast"].apply(
                lambda x: isinstance(x, list) and value.lower() in [a.lower() for a in x]
            )]; filters_applied += 1
        elif key == "genre":
            df_filtered = df_filtered[df_filtered["genres"].apply(
                lambda x: isinstance(x, list) and value.lower() in [g.lower() for g in x]
            )]; filters_applied += 1
        elif key == "rating":
            try:
                val = float(value)
                df_filtered = df_filtered[df_filtered["rating"] >= val]
                filters_applied += 1
            except ValueError:
                pass
        elif key == "time":
            try:
                if isinstance(value, dict):
                    start = int(str(value["from"])[:4]); end = int(str(value["to"])[:4])
                    df_filtered = df_filtered[(df_filtered["release_year"] >= start) & (df_filtered["release_year"] <= end)]
                else:
                    year = int(str(value)[:4])
                    df_filtered = df_filtered[df_filtered["release_year"] == year]
                filters_applied += 1
            except Exception:
                pass

    # If nothing actually filtered, don't dump all rows
    if filters_applied == 0:
        dispatcher.utter_message("I didn't get any usable search criteria. Try a genre/actor/director/rating/year.")
        return

    if df_filtered.empty:
        dispatcher.utter_message("No movies found.")
    else:
        dispatcher.utter_message(f"Found {len(df_filtered)} movie(s). Showing up to 10:")
        for i, (_, row) in enumerate(df_filtered.head(10).iterrows(), start=1):
            dispatcher.utter_message(f"{i}. {row['title']}")

def get_movie_info_local(tracker: Tracker):
    movie_title = tracker.get_slot("movie_title")
    if not movie_title:
        return "NoMovieTitleDetected"
    
    df_filtered = netflix_df[netflix_df["title"].str.lower() == movie_title.lower()]
    
    if df_filtered.empty:
        return "MovieTitleNotFound"
    
    movie_info = {}
    for _, row in df_filtered.iterrows():
        movie_info[row["title"]] = {
            "directors": row["director"] if isinstance(row["director"], list) else [row["director"]],
            "actors": row["cast"] if isinstance(row["cast"], list) else [row["cast"]],
            "genres": row["genres"] if isinstance(row["genres"], list) else [row["genres"]],
            "year_start": row["release_year"],
            "rating": row["rating"]
        }
    return movie_info

def get_movies_by_attributes_local(tracker: Tracker, dispatcher: CollectingDispatcher):
    call_local_movie_search(tracker, dispatcher)


# ------------------- FORM VALIDATIONS -------------------

class ValidateMovieMatchDirectorForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_movie_match_director_form"

    async def extract_director(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        director_entity = next(tracker.get_latest_entity_values("director"), None)
        if director_entity:
            return {"director": director_entity}
        return {}

class ValidateMovieMatchActorForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_movie_match_actor_form"

    async def extract_actor(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        actor_entity = next(tracker.get_latest_entity_values("actor"), None)
        if actor_entity:
            return {"actor": actor_entity}
        return {}

class ValidateMovieMatchYearForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_movie_match_year_form"

    async def extract_time(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        year_entity = next(tracker.get_latest_entity_values("time"), None)
        if year_entity:
            return {"time": year_entity}
        return {}

class ValidateMovieMatchGenreForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_movie_match_genre_form"

    async def extract_genre(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        genre_entity = next(tracker.get_latest_entity_values("genre"), None)
        if genre_entity:
            return {"genre": genre_entity}
        return {}

class ValidateMovieMatchRatingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_movie_match_rating_form"

    async def extract_rating(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        rating_entity = next(tracker.get_latest_entity_values("rating"), None)
        if rating_entity:
            return {"rating": rating_entity}
        return {}

class ValidateGetMovieTitleForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_movie_title_form"

    async def extract_movie_title(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> Dict[Text, Any]:
        movie_entity = next(tracker.get_latest_entity_values("movie_title"), None)
        if movie_entity:
            return {"movie_title": movie_entity}
        return {}

class ValidateGetMovieAttributeForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_movie_based_attribute_form"

    async def extract_movie_attribute(self, dispatcher, tracker, domain):
        attr_entity = next(tracker.get_latest_entity_values("movie_attribute"), None)
        allowed = {"title","rating","cast","director","genres","release_year"}
        if attr_entity and attr_entity.lower() in allowed:
            return {"movie_attribute": attr_entity.lower()}
        # drop unknown values (like "bot")
        return {}


# ------------------- ACTIONS -------------------

class ActionMatchDirectorSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_director_search_movie"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not should_run_movie_search(tracker):
            dispatcher.utter_message(template="utter_default")
            return []
        call_local_movie_search(tracker, dispatcher)
        return [SlotSet("director", None)]

class ActionMatchActorSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_actor_search_movie"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not should_run_movie_search(tracker):
            dispatcher.utter_message(template="utter_default")
            return []
        call_local_movie_search(tracker, dispatcher)
        return [SlotSet("actor", None)]

class ActionMatchYearSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_year_search_movie"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not should_run_movie_search(tracker):
            dispatcher.utter_message(template="utter_default")
            return []
        call_local_movie_search(tracker, dispatcher)
        return [SlotSet("time", None)]

class ActionMatchGenreSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_genre_search_movie"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not should_run_movie_search(tracker):
            dispatcher.utter_message(template="utter_default")
            return []
        call_local_movie_search(tracker, dispatcher)
        return [SlotSet("genre", None)]

class ActionMatchRatingSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_rating_search_movie"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not should_run_movie_search(tracker):
            dispatcher.utter_message(template="utter_default")
            return []
        call_local_movie_search(tracker, dispatcher)
        return [SlotSet("rating", None)]

class ActionMatchSeveralCriteriaSearchMovie(Action):
    def name(self) -> Text:
        return "action_match_several_criteria_search_movie"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not should_run_movie_search(tracker):
            dispatcher.utter_message(template="utter_default")
            return []
        call_local_movie_search(tracker, dispatcher)
        # Reset all slots used
        return [SlotSet(key, None) for key, value in tracker.slots.items() if value is not None]

class ActionGetMovieBasedAttribute(Action):
    def name(self) -> Text:
        return "action_get_movie_based_attribute"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if not should_run_movie_search(tracker):
            dispatcher.utter_message(template="utter_default")
            return []
        call_local_movie_search(tracker, dispatcher)
        return [SlotSet(key, None) for key, value in tracker.slots.items() if value is not None]