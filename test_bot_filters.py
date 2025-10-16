"""Тестовый скрипт для проверки фильтров бота"""
from telegram.ext import filters

# Проверяем фильтры
print("VIDEO filter:", filters.VIDEO)
print("VIDEO_NOTE filter:", filters.VIDEO_NOTE)
print("Document.VIDEO filter:", filters.Document.VIDEO)
print("Combined filter:", filters.VIDEO | filters.VIDEO_NOTE | filters.Document.VIDEO)

