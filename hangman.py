# ------------------------- Word of the day - Hangman -------------------------

# Import stuff
import requests
import pygame
import math
import re

# -------------------------------- 1.0 - Get word of the day info from dictionary.com ----------------------------------

# First, get big section containing everything
URL = "https://www.dictionary.com/e/word-of-the-day/"
page = requests.get(URL)
page_text = page.text
big_section_start = page_text.find("otd-item-headword__word")
big_section_end =  page_text.find("otd-item-headword__anchors")
big_search_section = page_text[big_section_start:big_section_end]

# Get wotd
wotd_end = big_search_section.find("</h1>")
wotd_search_section = big_search_section[:wotd_end]
wotd_search_flipped = wotd_search_section[::-1]
wotd_flipped_end = wotd_search_flipped.find(">")
wotd_flipped = wotd_search_flipped[:wotd_flipped_end]
wotd = wotd_flipped[::-1]
# print(wotd)

# Get pronunciation
big_search_section = big_search_section[wotd_end:]
pron_start = big_search_section.find("[")
pron_end = big_search_section.find("]")
pron_search = big_search_section[pron_start:pron_end + 1]
# replace sections in tags with ""
while pron_search.find("<") != -1 or pron_search.find(">") != -1:
    tag_start = pron_search.find("<")
    tag_end = pron_search.find(">")
    tag_section = pron_search[tag_start:tag_end + 1]
    pron_search = pron_search.replace(tag_section,"")
wotd_pron = pron_search
# print(wotd_pron)

# Get word category
big_search_section = big_search_section[pron_end:]
big_search_section = big_search_section[big_search_section.find("otd-item-headword__pos"):]
word_cat_end = big_search_section.find("</span>")
word_cat_search = big_search_section[:word_cat_end]
word_cat_search_flipped = word_cat_search[::-1]
word_cat_search_flipped = word_cat_search_flipped[:word_cat_search_flipped.find(">")]
word_cat = word_cat_search_flipped[::-1]
# print(word_cat)

# Get word definition
big_search_section = big_search_section[word_cat_end:]
word_defn_search = big_search_section[:big_search_section.find("</div>")]
word_defn_search_flipped = word_defn_search[::-1]
word_defn_search_flipped = word_defn_search_flipped.replace(">p/<","")
word_defn_start = word_defn_search_flipped.find(">p<")
word_defn_search_flipped = word_defn_search_flipped[:word_defn_start]
word_defn_search_flipped = word_defn_search_flipped.strip()
word_defn = word_defn_search_flipped[::-1]
# print(word_defn)

# ------------------------------------------ 2.0 - Process Word and Defn -----------------------------------------------

# Test accents
# wotd = "café"

# Acceptable letters
english_alphabet = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

# Split definition in half
defn_list = word_defn.split()
defn_list_half_len = len(defn_list) // 2
defn_list_1st_half = defn_list[:defn_list_half_len]
defn_list_2nd_half = defn_list[defn_list_half_len:]
defn_1st_half = " ".join(defn_list_1st_half)
defn_2nd_half = " ".join(defn_list_2nd_half)

# Get version of word with only letters
letter_only_word = re.sub('[^a-zA-Z]+',"",wotd)

# ---------------------------------------------- 3.0 - Pygame Hangman --------------------------------------------------

# setup display
pygame.init()
WIDTH, HEIGHT = 800, 500
wind = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman - Word of The Day")

# fonts
LETTER_FONT = pygame.font.SysFont("arial", 25)
WORD_FONT = pygame.font.SysFont("arial", 35)
LOSE_FONT = pygame.font.SysFont("arial", 80)
SMALL_FONT = pygame.font.SysFont("arial", 16)

# load images
images = []
for i in range(7):
    image = pygame.image.load("Personal Projects for CV/Hangman/hangman_pic" + str(i) + ".png")
    images.append(image)

# button variables
RADIUS = 20
GAP = 15
letters = []
startx = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)
starty = 390
A = 65
for i in range(26):
    x = startx + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))
    y = starty + ((i // 13) * (GAP + RADIUS * 2))
    letters.append([x, y, chr(A + i), True])

# game variables
hangman_status = 0
word = wotd.upper()
guessed = []
num_to_guess = len(set(list(letter_only_word)))
correctly_guessed = 0

# colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# setup game loop
FPS = 60
clock = pygame.time.Clock()
rungame = True

def draw():
    wind.fill(BLACK)

    # draw word
    display_word = ""
    for letter in word:
        if letter.upper() not in english_alphabet:
            display_word += letter + " "
        elif letter in guessed:
            display_word += letter + " "
        else:
            display_word += "_ "
    bigtext = WORD_FONT.render(display_word, 1, RED)
    wind.blit(bigtext, (400, 200))
    
    # draw buttons
    for letter in letters:
        x, y, ltr, visible = letter
        if visible:
            pygame.draw.circle(wind, RED, (x, y), RADIUS, 3)
            text = LETTER_FONT.render(ltr, 1, RED)
            wind.blit(text, (x - text.get_width() / 2, y - text.get_height() / 2))

    wind.blit(images[hangman_status], (60, 60))
    pygame.display.update()   

while rungame:
    clock.tick(FPS)

    draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rungame = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            m_x, m_y = pygame.mouse.get_pos()
            for letter in letters:
                x, y, ltr, visible = letter
                if visible:
                    dist = math.sqrt((x - m_x) ** 2 + (y - m_y) ** 2)
                    if dist < RADIUS:
                        letter[3] = False
                        guessed.append(ltr)
                        if ltr not in word:
                            hangman_status += 1
                        else:
                            correctly_guessed += 1

    won = True
    for letter in letter_only_word.upper():
        if letter not in guessed:
            won = False
            break

    if won:
        wind.fill(BLACK)
        win_text = WORD_FONT.render("You WON!", 1, WHITE)
        wind.blit(win_text, (WIDTH / 2 - win_text.get_width() / 2, HEIGHT / 8 - win_text.get_height() / 2))
        win_word_text = WORD_FONT.render(wotd.upper(), 1, RED)
        wind.blit(win_word_text, (WIDTH / 2 - win_word_text.get_width() / 2, HEIGHT / 4 - win_word_text.get_height() / 2))
        pron_text = LETTER_FONT.render(wotd_pron, 1, RED)
        wind.blit(pron_text, (WIDTH / 2 - pron_text.get_width() / 2, HEIGHT / 3 - pron_text.get_height() / 2))
        cat_text = LETTER_FONT.render(word_cat, 1, WHITE)
        wind.blit(cat_text, (WIDTH / 2 - cat_text.get_width() / 2, HEIGHT / 2 - cat_text.get_height() / 2 - 40))
        defn_text1 = SMALL_FONT.render(defn_1st_half, 1, RED)
        wind.blit(defn_text1, (WIDTH / 2 - defn_text1.get_width() / 2, HEIGHT / 2 - defn_text1.get_height() / 2))
        defn_text2 = SMALL_FONT.render(defn_2nd_half, 1, RED)
        wind.blit(defn_text2, (WIDTH / 2 - defn_text2.get_width() / 2, HEIGHT / 2 - defn_text2.get_height() / 2 + 40))
        pygame.display.update()
        pygame.time.delay(10000)
        break

    if hangman_status == 6:
        lose_text = LOSE_FONT.render("You Lose!", 1, WHITE)
        wind.blit(lose_text, (WIDTH / 2 - lose_text.get_width() / 2, HEIGHT / 2 - lose_text.get_height() / 2))
        pygame.display.update()
        pygame.time.delay(4000)
        break

pygame.quit()
