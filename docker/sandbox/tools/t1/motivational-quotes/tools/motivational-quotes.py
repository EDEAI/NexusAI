import random
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class MotivationalQuotesTool(Tool):
    def __init__(self):
        super().__init__()
        self.quotes = [
            "The only way to do great work is to love what you do. - Steve Jobs",
            "Believe you can and you're halfway there. - Theodore Roosevelt",
            "It does not matter how slowly you go as long as you do not stop. - Confucius",
            "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. - Winston Churchill",
            "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
            "Hardships often prepare ordinary people for an extraordinary destiny. - C.S. Lewis",
            "It's not whether you get knocked down, it's whether you get up. - Vince Lombardi",
            "The best way to predict the future is to create it. - Peter Drucker",
            "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
            "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
            "Life is 10% what happens to us and 90% how we react to it. - Charles R. Swindoll",
            "You are never too old to set another goal or to dream a new dream. - C.S. Lewis",
            "The secret of getting ahead is getting started. - Mark Twain",
            "The harder you work for something, the greater you'll feel when you achieve it. - Unknown",
            "Do what you can, with what you have, where you are. - Theodore Roosevelt",
            "Quality is not an act, it is a habit. - Aristotle",
            "The best revenge is massive success. - Frank Sinatra",
            "Don't count the days, make the days count. - Muhammad Ali",
            "A person who never made a mistake never tried anything new. - Albert Einstein",
            "The only impossible journey is the one you never begin. - Tony Robbins",
            "Opportunities don't happen. You create them. - Chris Grosser",
            "You miss 100% of the shots you don't take. - Wayne Gretzky",
            "If you want to achieve greatness stop asking for permission. - Unknown",
            "Success is walking from failure to failure with no loss of enthusiasm. - Winston Churchill",
        ]

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        random_quote = random.choice(self.quotes)

        yield self.create_json_message({"result": random_quote})
