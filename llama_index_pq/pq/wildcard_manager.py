
import os
import logging

class WildcardManager:
	def __init__(self, wildcards_dir="wildcards"):
		self.wildcards_dir = wildcards_dir
		self.wildcard_index = {}
		self.wildcard_content_cache = {}
		self.index_wildcards()

	def index_wildcards(self):
		"""Builds an index of all .txt files in the wildcards directory and its subdirectories."""
		self.wildcard_index = {}
		if not os.path.exists(self.wildcards_dir):
			os.makedirs(self.wildcards_dir, exist_ok=True)
			return

		for root, _, files in os.walk(self.wildcards_dir):
			for file in files:
				if file.endswith(".txt"):
					wildcard_name = file[:-4]
					# In case of duplicates, the first one found (or closest to root if we sorted) wins.
					# Current implementation in shared.py also just picks the first one it finds.
					if wildcard_name not in self.wildcard_index:
						self.wildcard_index[wildcard_name] = os.path.join(root, file)

	def get_wildcard_path(self, wildcard_name):
		"""Returns the full path to a wildcard file given its name."""
		return self.wildcard_index.get(wildcard_name)

	def load_wildcard_content(self, wildcard_name, cache=True):
		"""Loads and returns the content of a wildcard file."""
		if cache and wildcard_name in self.wildcard_content_cache:
			return self.wildcard_content_cache[wildcard_name]

		wildcard_file = self.get_wildcard_path(wildcard_name)

		# Fallback to root if not in index (might have been added recently)
		if not wildcard_file:
			 wildcard_file = os.path.join(self.wildcards_dir, f"{wildcard_name}.txt")
			 if not os.path.exists(wildcard_file):
				 return []

		options = []
		try:
			if os.path.exists(wildcard_file):
				with open(wildcard_file, "r", encoding="utf-8") as f:
					options = [line.strip() for line in f if line.strip()]
		except Exception as e:
			logging.error(f"Error loading wildcard {wildcard_name}: {e}")
			return []

		if cache:
			self.wildcard_content_cache[wildcard_name] = options

		return options

	def clear_cache(self):
		self.wildcard_content_cache = {}
