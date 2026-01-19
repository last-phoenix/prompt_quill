
import globals
from pathlib import Path
import re
import bisect
import os

class WildcardManager:
    def __init__(self):
        self.g = globals.get_globals()
        # Internal storage for indexes to avoid polluting global settings and serialization issues
        self.index = {} # word -> set(keys)
        self.forward_index = {} # key -> set(words)
        self.sorted_vocab = []

        self.ensure_initialized()

    def ensure_initialized(self):
        if 'wildcard_cache' not in self.g.settings_data:
            self.g.settings_data['wildcard_cache'] = {}
            self.reload_cache_from_disk()

        # If cache exists but index is empty (e.g. restart), rebuild
        if not self.index and self.g.settings_data['wildcard_cache']:
            self.rebuild_index()

    def reload_cache_from_disk(self):
        wildcard_dir = Path("wildcards")
        if not wildcard_dir.exists():
            return

        cache = {}
        for file_path in wildcard_dir.glob("**/*.txt"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                filename = file_path.stem
                wildcard_syntax = f"__{filename}__"
                cache[wildcard_syntax] = content.lower()
            except Exception:
                pass
        self.g.settings_data['wildcard_cache'] = cache
        self.rebuild_index()

    def rebuild_index(self):
        """Builds the inverted index and sorted vocabulary."""
        cache = self.g.settings_data['wildcard_cache']
        self.index = {}
        self.forward_index = {}

        for key, content in cache.items():
            # content is already lower case
            words = set(content.split())
            self.forward_index[key] = words
            for w in words:
                if w not in self.index:
                    self.index[w] = set()
                self.index[w].add(key)

        self.sorted_vocab = sorted(self.index.keys())

    def update_file(self, key, content):
        """Updates cache and index for a single file."""
        content_lower = content.lower()
        self.g.settings_data['wildcard_cache'][key] = content_lower

        # Update indexes
        new_words = set(content_lower.split())

        # Get old words to remove
        old_words = self.forward_index.get(key, set())

        # Words to remove: present in old but not in new
        to_remove = old_words - new_words
        # Words to add: present in new but not in old
        to_add = new_words - old_words

        for w in to_remove:
            if w in self.index:
                self.index[w].discard(key)
                if not self.index[w]:
                    del self.index[w]
                    # Updating sorted vocab is skipped for performance on delete

        for w in to_add:
            if w not in self.index:
                self.index[w] = set()
                self.insert_into_vocab(w)
            self.index[w].add(key)

        self.forward_index[key] = new_words

    def insert_into_vocab(self, word):
        idx = bisect.bisect_left(self.sorted_vocab, word)
        if idx < len(self.sorted_vocab) and self.sorted_vocab[idx] == word:
            return # Already exists
        self.sorted_vocab.insert(idx, word)

    def get_suggestions(self, last_word, last_few_words):
        """
        Returns (last_word_suggestions, last_few_suggestions)
        last_word: single word string
        last_few_words: phrase string
        """

        # 1. Last Word Suggestions (Prefix Match)
        last_word_suggestions = []
        if not last_word:
            # Empty input matches everything
            last_word_suggestions = list(self.g.settings_data['wildcard_cache'].keys())
        else:
            idx = bisect.bisect_left(self.sorted_vocab, last_word)
            matches = set()
            for i in range(idx, len(self.sorted_vocab)):
                word = self.sorted_vocab[i]
                if not word.startswith(last_word):
                    break
                if word in self.index:
                    matches.update(self.index[word])
            last_word_suggestions = list(matches)

        # 2. Last Few Words Suggestions (Phrase Match)
        last_few_suggestions = []
        if not last_few_words:
            last_few_suggestions = list(self.g.settings_data['wildcard_cache'].keys())
        else:
            # Split phrase into words
            words = last_few_words.split()
            if not words:
                last_few_suggestions = list(self.g.settings_data['wildcard_cache'].keys())
            else:
                candidates = None
                for w in words:
                    # Find matches for this word (prefix match)
                    w_matches = set()
                    idx = bisect.bisect_left(self.sorted_vocab, w)
                    for i in range(idx, len(self.sorted_vocab)):
                        vocab_word = self.sorted_vocab[i]
                        if not vocab_word.startswith(w):
                            break
                        if vocab_word in self.index:
                            w_matches.update(self.index[vocab_word])

                    if candidates is None:
                        candidates = w_matches
                    else:
                        candidates &= w_matches

                    if not candidates:
                        break

                if candidates:
                    # Verify phrase match in content
                    cache = self.g.settings_data['wildcard_cache']
                    last_few_suggestions = [key for key in candidates if last_few_words in cache[key]]
                else:
                    last_few_suggestions = []

        return last_word_suggestions, last_few_suggestions
