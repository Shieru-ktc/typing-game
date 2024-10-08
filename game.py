from dotenv import load_dotenv

load_dotenv()

import pygame
from romaji import TypingQuestion
from random import shuffle
import time
import argparse
from pygame import mixer

from score import PartialRecordSchema, RecordType, send_record


parser = argparse.ArgumentParser()

parser.add_argument("count", help="出題する問題数。", default=10, type=int)
parser.add_argument(
    "--question",
    "-q",
    help="最初に出題する問題。テキスト:読みの形式で記述。",
    required=False,
)
parser.add_argument(
    "--file",
    "-f",
    help="ファイル名",
    required=False,
)
args = parser.parse_args()

questions = []

with open(args.file or "words.txt") as f:
    for line in f.readlines():
        if line.startswith("#"):
            continue
        full, read = line.split(":")
        questions.append((full, read.removesuffix("\n")))
shuffle(questions)
mixer.init()


def play_audio(filename: str):
    mixer.music.load(filename)
    mixer.music.play()


name = input("おなまえ: ")

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Typing Game")
font_normal = pygame.font.Font("NotoSansJP-Regular.ttf", 36)
font_small = pygame.font.Font("NotoSansJP-Regular.ttf", 24)
font_mono = pygame.font.Font("NotoSansMono-Regular.ttf", 22)


class TypingGame:
    question: TypingQuestion
    score: int = 0
    combo: int = 0
    max_combo: int = 0
    correct: int = 0
    misses: int = 0
    start: float | None = None
    perfect: bool = True
    cleared: int = 0
    kps_record: list[float] = []

    def __init__(self):
        self.running = True
        self.question = None
        self.set_question(*questions.pop(0))

    def on_key_press(self, key):
        if key == "":
            return
        input_char = key

        if not input_char.isalpha() and input_char not in ["-"]:
            return

        if self.start is None:
            self.start = time.time()
        if self.question.press(input_char):
            self.combo += 1
            self.score += 2 * max(1, min(self.combo, 50))
            self.correct += 1
            play_audio("key.mp3")
        else:
            self.misses += 1
            self.combo = 0
            self.perfect = False
            play_audio("miss.mp3")
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        self.update_question()

    def update_question(self):
        kps = (
            (len(self.question.inputted) / (time.time() - self.start))
            if self.start and len(self.question.inputted) >= 2
            else 0
        )
        if self.question.is_completed:
            play_audio("next.mp3")
            self.kps_record.append(kps)
            if 1 < kps:
                bonus = kps * 500
                if self.perfect:
                    bonus *= 1.2
                    bonus += 300
                self.score += round(bonus)
            self.cleared += 1
            if args.count == self.cleared:
                record = send_record(
                    PartialRecordSchema(
                        self.score,
                        name,
                        RecordType.TYPING,
                        {
                            "misses": self.misses,
                            "cleared": self.cleared,
                            "correct": self.correct,
                            "avg_kps": sum(self.kps_record) / len(self.kps_record),
                        },
                    )
                )

                self.running = False
                pygame.quit()
                print("")
                print(f"Thank you for playing!")
                print(f"スコア: {self.score}")
                print(f"順位: {record['rank']}位")
                input(f"Enterキーを押して終了します: ")

                exit()
            else:
                self.new_question()

    def new_question(self):
        question = questions.pop(0)
        self.set_question(*question)

    def set_question(self, full: str, read: str):
        self.question = TypingQuestion(read)
        self.start = None
        self.perfect = True
        self.full_text = full
        self.reading_text = read

    def accuracy(self):
        if self.correct + self.misses == 0:
            return 1
        return self.correct / (self.correct + self.misses)

    def draw(self):
        screen.fill((255, 255, 255))

    def draw_text(self):
        kps = (
            (len(self.question.inputted) / (time.time() - self.start))
            if self.start and len(self.question.inputted) >= 2
            else 0
        )
        full_text_surface = font_normal.render(self.full_text, True, (0, 0, 0))
        reading_text_surface = font_small.render(self.reading_text, True, (0, 0, 0))
        inputted_text_surface = font_normal.render(
            self.question.inputted, True, (0, 0, 0)
        )
        remaining_text_surface = font_normal.render(
            "".join(self.question.romanize_remaining()), True, (0, 0, 0)
        )
        status_text_surface = font_mono.render(
            f"KPS: {round(kps, 2):05.2f} Score: {self.score} Combo: {self.combo}/{self.max_combo} Misses: {self.misses} ({self.accuracy() * 100:.2f}% accuracy)",
            True,
            (0, 0, 0),
        )
        screen.blit(reading_text_surface, (50, 100))
        screen.blit(full_text_surface, (50, 50))

        inputted_text_surface = font_normal.render(
            self.question.inputted,
            True,
            (0, 255, 0),
            (255, 255, 255),
        )
        remaining_text_surface = font_normal.render(
            "".join(self.question.romanize_remaining()),
            True,
            (128, 128, 128),
            (255, 255, 255),
        )
        combined_text_surface = pygame.Surface(
            (
                inputted_text_surface.get_width() + remaining_text_surface.get_width(),
                inputted_text_surface.get_height(),
            )
        )
        combined_text_surface.blit(inputted_text_surface, (0, 0))
        combined_text_surface.blit(
            remaining_text_surface, (inputted_text_surface.get_width(), 0)
        )
        screen.blit(combined_text_surface, (50, 150))
        screen.blit(status_text_surface, (50, 250))
        pygame.display.flip()

    def run(self):
        self.draw()
        self.draw_text()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.on_key_press(event.unicode)
                    self.draw_text()
            self.draw()
        pygame.quit()


game = TypingGame()
game.run()
