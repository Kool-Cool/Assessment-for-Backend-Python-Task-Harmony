from difflib import SequenceMatcher
import re
from collections import defaultdict


class PortResolver:
    def __init__(self, port_data):
        self.ports = port_data

        # build index
        self.name_index = [
            {
                "name": p["name"].lower(),
                "code": p["code"],
                "raw": p["name"]
            }
            for p in port_data
        ]

        ## AUTO-GENERATED ALIASES (no manual mapping)
        self.aliases = self.build_alias_map(port_data)

    # -------------------------
    ## ALIAS BUILDER
    # -------------------------
    def build_alias_map(self, port_data):
        alias_map = defaultdict(set)

        for p in port_data:
            name = p["name"].lower().strip()

            # base name
            alias_map[name].add(name)

            # split variants: "shenzhen / guangzhou"
            parts = re.split(r"\/|,| and ", name)
            for part in parts:
                clean = part.strip()
                if clean:
                    alias_map[clean].add(name)

            # remove ICD suffix
            clean_icd = re.sub(r"\s*icd", "", name).strip()
            alias_map[clean_icd].add(name)

            # remove parentheses
            clean_paren = re.sub(r"\(.*?\)", "", name).strip()
            alias_map[clean_paren].add(name)

        return alias_map

    # -------------------------
    # NORMALIZE TEXT
    # -------------------------
    def normalize(self, text):
        return re.sub(r"[^a-zA-Z ]", "", text.lower()).strip()

    # -------------------------
    # SCORE FUNCTION
    # -------------------------
    def score(self, query, candidate, context_role=None):
        q = self.normalize(query)
        c = candidate["name"]

        # exact match
        if q == c:
            return 100

        # substring match
        if q in c or c in q:
            return 85

        # fuzzy match
        sim = SequenceMatcher(None, q, c).ratio() * 100
        score = sim

        # context boost
        if context_role == "origin" and c.startswith("in"):
            score += 5

        if context_role == "destination" and not c.startswith("in"):
            score += 5

        return score

    # -------------------------
    # RESOLVE WITH ALIASES
    # -------------------------
    def resolve(self, text, context_role=None):
        if not text:
            return None, None

        text_norm = self.normalize(text)

        ## STEP 1: alias expansion
        alias_hits = self.aliases.get(text_norm)

        candidates = []

        if alias_hits:
            # restrict search space (faster + more accurate)
            candidates = [
                p for p in self.name_index
                if p["name"] in alias_hits
            ]
        else:
            candidates = self.name_index

        ## STEP 2: scoring
        best = None
        best_score = -1

        for p in candidates:
            s = self.score(text, p, context_role)
            if s > best_score:
                best_score = s
                best = p

        # safety threshold
        if best_score < 60:
            return None, None

        return best["code"], best["raw"]













# from difflib import SequenceMatcher
# import re
# from collections import defaultdict

# class PortResolver:
#     def __init__(self, port_data):
#         self.ports = port_data

#         # normalize index
#         self.name_index = [
#             {
#                 "name": p["name"].lower(),
#                 "code": p["code"],
#                 "raw": p["name"]
#             }
#             for p in port_data
#         ]

#         # alias map (optional but powerful)
#         self.aliases = {
#             "chennai": "chennai",
#             "madras": "chennai",
#             "nhava sheva": "nhava sheva",
#             "mumbai": "nhava sheva"
#         }


#     def normalize(self, text):
#         return re.sub(r"[^a-zA-Z ]", "", text.lower()).strip()


#     def score(self, query, candidate, context_role=None):
#         q = self.normalize(query)
#         c = candidate["name"]

#         # exact match
#         if q == c:
#             return 100

#         # substring match
#         if q in c or c in q:
#             return 80

#         # fuzzy similarity
#         sim = SequenceMatcher(None, q, c).ratio() * 100

#         score = sim

#         # context boost (VERY IMPORTANT)
#         if context_role == "origin" and "india" in c:
#             score += 5

#         if context_role == "destination" and "india" not in c:
#             score += 5

#         return score


#     def resolve(self, text, context_role=None):
#         if not text:
#             return None, None

#         text = text.lower().strip()

#         best = None
#         best_score = -1

#         for p in self.name_index:
#             s = self.score(text, p, context_role)
#             if s > best_score:
#                 best_score = s
#                 best = p

#         if best_score < 60:
#             return None, None  # safety threshold

#         return best["code"], best["raw"]