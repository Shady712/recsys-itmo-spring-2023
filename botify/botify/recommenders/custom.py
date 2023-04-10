import random

from .recommender import Recommender
from .contextual import Contextual


class Custom(Recommender):

    def __init__(self, tracks_redis, artists_redis, catalog, tracks_listened, begin_track):
        self.tracks_redis = tracks_redis
        self.artists_redis = artists_redis
        self.fallback = Contextual(tracks_redis, catalog)
        self.catalog = catalog
        self.tracks_listened = tracks_listened
        self.begin_track = begin_track

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if user not in self.tracks_listened:
            self.tracks_listened[user] = 1
        else:
            self.tracks_listened[user] += 1
        if user not in self.begin_track:
            self.begin_track[user] = prev_track
        if self.tracks_listened[user] > 7 and prev_track_time > 0.9:
            self.tracks_listened[user] = 1
            self.begin_track[user] = prev_track


        begin_track = self.tracks_redis.get(self.begin_track[user])
        if begin_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        track = self.catalog.from_bytes(begin_track)
        recs = track.recommendations
        if not recs:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        shuffled = list(recs)
        random.shuffle(shuffled)
        return shuffled[0]
