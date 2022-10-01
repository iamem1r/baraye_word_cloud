import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Union

import arabic_reshaper
import matplotlib.pyplot as plt
from bidi.algorithm import get_display
from hazm import Normalizer, sent_tokenize, word_tokenize
from loguru import logger
from src.data import DATA_DIR
from src.utils.io import read_file, read_json
from wordcloud import STOPWORDS, WordCloud


class ChatStatistics:
    """Generates chat statistics from telegram chat json file
    """
    def __init__(self, chat_json: Union[str, Path]):
        """
        :param chat_json: path to telegram exported json file
        """
        #load chat data
        logger.info(f"Loading chat data from {chat_json}")
        self.chat_data = read_json(DATA_DIR / 'tele_json.json')
        self.normalizer = Normalizer()

        # load stopwords
        logger.info(f"Loading stop words from {DATA_DIR / 'stopwords.txt'}")
        stop_words = set(read_file(DATA_DIR / 'stopwords.txt').split('\n'))
        self.stop_words = list(map(self.normalizer.normalize, stop_words))

    def generate_word_cloud(self, 
        output_dir: Union[str, Path], 
        width: int = 800, height: int = 800,
        max_font_size: int = 250
    ):
        """Generates a word cloud from a telegram chat data

        :param output_dir: path to output directory for word cloud image
        """
        logger.info("Loading text from strings and lists of chat data")
        logger.info("Tokenizing words of text")
        logger.info("Removing stop words from text")
        text_content = ''
        list_content = ''

        for msg in self.chat_data['chats']['list'][0]['messages']:
            if type(msg['text']) is str:
                tokens_str = word_tokenize(msg['text'])
                tokens_str = list(filter(lambda item: item not in self.stop_words, tokens_str))
                
                text_content += f" {' '.join(tokens_str)}"
                
            elif type(msg['text']) is list:
                for i in msg['text']:
                    if type(i) is str:
                        tokens_list = word_tokenize(i)
                        tokens_list = list(filter(lambda item: item not in self.stop_words, tokens_list))
                        
                        list_content += f" {' '.join(tokens_list)}"
        
        # concate, normalize and reshape for final word cloud
        text = text_content + list_content
        text = self.normalizer.normalize(text)
        text = arabic_reshaper.reshape(text)
        text = get_display(text)

        logger.info("Generating word cloud")
        # generate word cloud
        wordcloud = WordCloud(
            width=1200, height=1200, max_font_size=400,
            background_color='white', 
            font_path=str(DATA_DIR / 'IranianSansRegular.ttf')
        ).generate(text)

        logger.info(f"Saving word cloud to {output_dir}")
        wordcloud.to_file(str(Path(output_dir) / 'WordCloud.png'))

    
    def get_top_users(self, top_n: int=10) -> dict:
        """Get top_n users from chat data

        :param top_n: number of users to get, defaults to 10
        :return: dict of top users 
        """
        is_question = defaultdict(bool)

        for msg in self.chat_data['chats']['list'][0]['messages']:
            if not isinstance(msg['text'], str):
                continue
        
        sentences = sent_tokenize(msg['text'])
        for sentence in sentences:
            if ('?' not in sentence) and ('؟' not in sentence):
                continue
            
            is_question[msg['id']] = True
            break

        logger.info("Getting top users...")
        reply_to_questions_users = []   
        for msg in self.chat_data['chats']['list'][0]['messages']:
            if not msg.get('reply_to_message_id'):
                continue
            elif msg.get('from') is None:
                continue
            
            if is_question[msg['reply_to_message_id']] is False:
                continue
                
            reply_to_questions_users.append(msg['from'])
        
        return dict(Counter(reply_to_questions_users).most_common(top_n))

if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json=DATA_DIR / 'online.json')
    chat_stats.generate_word_cloud(output_dir=DATA_DIR)
    top_users = chat_stats.get_top_users(top_n=10)
    print(top_users)

    print("--"*10)
    print("DONE!")
    print("--"*10)

