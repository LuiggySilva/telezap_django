from emoji_data_python import emoji_data

def get_all_emojis():
    emojis_categories = {
        'Smileys & Emotion':{'icon':'&#128516;', 'emojis':[], 'name':'Emoções'},
        'People & Body':{'icon':'&#128105;', 'emojis':[], 'name':'Pessoas e Corpo'},
        'Skin Tones':{'icon':'&#129335;&#127997;', 'emojis':[], 'name':'Tons de Pele'},
        'Food & Drink':{'icon':'&#127828;', 'emojis':[], 'name':'Comidas e Bebidas'},
        'Animals & Nature':{'icon':'&#128049;', 'emojis':[], 'name':'Animais e Natureza'},
        'Objects':{'icon':'&#128230;', 'emojis':[], 'name':'Objetos'},
        'Activities':{'icon':'&#9917;', 'emojis':[], 'name':'Atividades'},
        'Travel & Places':{'icon':'&#9992;', 'emojis':[], 'name':'Viagens e Lugares'},
        'Flags':{'icon':'&#127987;', 'emojis':[], 'name':'Bandeiras'},
        'Symbols':{'icon':'&#10024;', 'emojis':[], 'name':'Simbolos'}, 
    }

    for emoji in emoji_data:
        emojis_categories[emoji.category]['emojis'].append(emoji.char[0])

    for emoji in emoji_data:
        emojis_categories[emoji.category]['emojis'] = list(set(emojis_categories[emoji.category]['emojis']))

    del emojis_categories['Skin Tones']
    del emojis_categories['Flags']

    return emojis_categories