# -*- coding: utf-8 -*-
import re

def removeAcento(text):
  # Cria uma expressão regular a partir de um dicionário de keys

  dict = {
      "á": "a",
      "à": "a",
      "ä": "a",
      "é": "e",
      "è": "e",
      "ë": "e",
      "í": "i",
      "ì": "i",
      "ï": "i",
      "ó": "o",
      "ò": "o",
      "ö": "o",
      "ú": "u",
      "ù": "u",
      "ü": "u",
      "Á": "A",
      "À": "A",
      "Ä": "A",
      "É": "E",
      "È": "E",
      "Ë": "E",
      "Í": "I",
      "Ì": "I",
      "Ï": "I",
      "Ó": "O",
      "Ò": "O",
      "Ö": "O",
      "Ú": "U",
      "Ù": "U",
      "Ü": "Ü",
      "â": "a",
      "ê": "e",
      "î": "i",
      "ô": "o",
      "û": "u",
      "Â": "A",
      "Ê": "E",
      "Î": "I",
      "Ô": "O",
      "Û": "U",
      "ã": "a",
      "õ": "o",
      "Ã": "A",
      "Õ": "O",
      "ç": "c",
      "Ç": "C",
      "*": " ",
      "-": " ",
      "!": ".",
      "?": ".",
      "@": " ",
      "#": " ",
      "$": " ",
      "%": " ",
      "&": " ",
      "(": " ",
      ")": " ",
      "_": " ",
      "+": " ",
      "=": " ",
      "{": " ",
      "}": " ",
      "[": " ",
      "]": " ",
      "ª": " ",
      "º": " ",
      "°": " ",
      "/": " ",
      "'\'": " ",
      ",":".",
      ":": ".",
      ";": ".",
      "¢": "",
      "€": "",
      "§": "",
      "\'": "",
      "\"": "",
      "–": "",
      "|": "",
      "“": " ",
      "”": "",
      "..": ".",
      "...": ".",

  }

  regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))

  # For each match, look-up corresponding value in dictionary
  return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)
