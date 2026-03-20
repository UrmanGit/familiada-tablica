#!/usr/bin/env python3

import json
import pathlib
import sys
from typing import Literal

import pygame as pg

pg.init()


FILES_DIR: pathlib.Path = pathlib.Path(__file__).parent


class Game:
    def __init__(self, files_dir: pathlib.Path) -> None:
        # Files
        self.files: pathlib.Path = files_dir

        # Pygame stuff
        self.screen: pg.Surface = pg.display.set_mode(
            (1920, 1080), pg.FULLSCREEN | pg.SCALED
        )
        self.keys: pg.key.ScancodeWrapper = pg.key.get_just_pressed()
        self.clock = pg.Clock()
        self.mouse: tuple[bool, bool, bool, bool, bool] = pg.mouse.get_just_pressed()
        self.mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        self.font = pg.font.Font(self.files / "fonts" / "familiada.ttf", size=30)
        self.Xfont = pg.font.Font(self.files / "fonts" / "familiada.ttf", size=200)
        self.asciifont = pg.font.Font(
            self.files / "fonts" / "JetBrainsMonoNerdFont-Regular.ttf", size=14
        )

        self.running: bool = True
        self.state: str = "choose"
        self.round: int = 0
        self.question: int = 0

        self.presets: list[dict] = self.load_presets()

        self.team_iks: tuple[int, int] = (0, 0)
        self.team: Literal[0] | Literal[1] = 0

        self.points: int = 0
        self.team_points: tuple[int, int] = (0, 0)

        self.intro = self.load_anim(self.files / "output.gif")
        self.current_delay = 0
        self.current_frame = 0
        self.current_time = 0

        self.intro_music = pg.mixer.Sound(self.files / "output.mp3")
        self._intro_music = False

        self.correct = pg.mixer.Sound(self.files / "dobra-odpowiedz-familiada.mp3")
        self.bad = pg.mixer.Sound(self.files / "bledna-familiada.mp3")
        self.jingle = pg.mixer.Sound(self.files / "przed-i-po-rundzie-familiada.mp3")
        self.dzwonki = pg.mixer.Sound(self.files / "dzwonki-familiada.mp3")

        self.ascii_art: str = r"""
         /$$$$$$$$ /$$$$$$  /$$      /$$ /$$$$$$ /$$       /$$$$$$  /$$$$$$  /$$$$$$$   /$$$$$$       
        | $$_____//$$__  $$| $$$    /$$$|_  $$_/| $$      |_  $$_/ /$$__  $$| $$__  $$ /$$__  $$      
        | $$     | $$  \ $$| $$$$  /$$$$  | $$  | $$        | $$  | $$  \ $$| $$  \ $$| $$  \ $$      
        | $$$$$  | $$$$$$$$| $$ $$/$$ $$  | $$  | $$        | $$  | $$$$$$$$| $$  | $$| $$$$$$$$      
        | $$__/  | $$__  $$| $$  $$$| $$  | $$  | $$        | $$  | $$__  $$| $$  | $$| $$__  $$      
        | $$     | $$  | $$| $$\  $ | $$  | $$  | $$        | $$  | $$  | $$| $$  | $$| $$  | $$      
        | $$     | $$  | $$| $$ \/  | $$ /$$$$$$| $$$$$$$$ /$$$$$$| $$  | $$| $$$$$$$/| $$  | $$      
        |__/     |__/  |__/|__/     |__/|______/|________/|______/|__/  |__/|_______/ |__/  |__/      
        """

    def load_presets(self) -> list[dict]:
        presets: list[dict] = []
        for file in (self.files / "presets").glob("*.json"):
            with file.open() as f:
                preset = json.load(f)
                presets.append(preset)
        return presets

    def load_preset_info(self) -> list[list[bool]]:
        """
        Loads information from current preset.
        :param questions: It's a list where each entry is the list of bools, where each bool represents if the question is hidden or revealed.
        Number of questions is the length of the list.
        """
        questions: list[list[bool]] = []
        for question in self.preset["questions"]:
            answers: list[bool] = []
            for answer in question["answers"]:
                answers.append(False)
            questions.append(answers)
        return questions

    def choose_preset(self) -> None:
        for i, preset in enumerate(self.presets):
            margin: tuple[int, int] = (160 * 2, 90 * 2)
            size: tuple[int, int] = (
                self.screen.width - 2 * margin[0],
                self.screen.height // len(self.presets) - 2 * margin[1],
            )

            color = "yellow"

            text = self.font.render(f"{preset["title"]}", True, "yellow")

            rect = pg.Rect(
                margin[0], margin[1] + i * (size[1]), text.width, text.height
            )

            if rect.collidepoint(self.mouse_pos):
                color = "orange"
                if self.mouse[0]:
                    self.preset = preset
                    self.state = "intro"
                    self.questions: list[list[bool]] = self.load_preset_info()

            text = self.font.render(f"{preset["title"]}", True, color)

            self.screen.blit(
                text,
                (rect.center[0] - text.width // 2, rect.center[1] - text.height // 2),
            )

    def load_anim(self, path: pathlib.Path) -> list[tuple[pg.Surface, float]]:

        # Loading the animation as normal
        animation: list[tuple[pg.Surface, float]] = pg.image.load_animation(path)

        for i, pair in enumerate(animation):
            # 1. Rip the pair apart
            frame, delay = pair

            # 2. Convert the frame and resize it
            frame = frame.convert()
            frame = pg.transform.scale(frame, self.screen.size)

            # 3. Put everything together like nothing happened
            animation[i] = (frame, delay)

            # 4. Surgery completed successfully
        return animation

    def animate(self, dt: float) -> None:
        self.current_delay: float = self.intro[self.current_frame][1]

        self.animation_frames: int = len(self.intro)

        self.image = self.intro[self.current_frame][0]
        self.current_time += dt
        if self.current_time >= self.current_delay:
            self.current_time = 0
            self.current_frame += 1
            if self.current_frame >= self.animation_frames:
                self.state = "ascii"
                self.current_frame -= 1
            self.image = self.intro[self.current_frame][0]
        self.screen.blit(self.image)

    def events(self) -> None:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False

    def update(self) -> None:
        self.dt = self.clock.tick(60)

        self.keys = pg.key.get_just_pressed()
        self.mouse = pg.mouse.get_just_pressed()
        self.mouse_pos = pg.mouse.get_pos()

        if self.state == "normal":
            # Odkrywanie odpowiedzi i punkty
            for i in range(1, len(self.questions[self.question]) + 1):
                if eval(f"self.keys[pg.K_{i}]"):
                    i = i - 1
                    if self.questions[self.question][i] == False:
                        self.correct.play()
                        self.questions[self.question][i] = True
                        self.points += self.preset["questions"][self.question][
                            "answers"
                        ][i]["points"]
            # Dodawanie iksów
            if self.keys[pg.K_x]:
                if self.team == 1:
                    self.team_iks = (self.team_iks[0], self.team_iks[1] + 1)
                else:
                    self.team_iks = (self.team_iks[0] + 1, self.team_iks[1])
                self.bad.play()
            # Zmienianie aktywnej drużyny
            if self.keys[pg.K_TAB]:
                self.team = 1 if self.team == 0 else 0

            if self.keys[pg.K_r]:
                self.jingle.play()
                self.question += 1
                self.team_iks = (0, 0)

            if self.keys[pg.K_LEFTBRACKET]:
                self.team_points = (
                    self.team_points[0] + self.points,
                    self.team_points[1],
                )
                self.points = 0
                self.dzwonki.play()

            if self.keys[pg.K_RIGHTBRACKET]:
                self.team_points = (
                    self.team_points[0],
                    self.team_points[1] + self.points,
                )
                self.points = 0
                self.dzwonki.play()

            if self.keys[pg.K_f] or self.keys[pg.K_j]:
                self.state = "final"
                self.final_questions = []
                for i in range(len(self.preset["questions"]) - 1, -1, -1):
                    if len(self.final_questions) < 5:
                        self.final_questions.append(self.preset["questions"])
                    else:
                        break

                self.final_answers = [None, None, None, None, None]
                self.final_answers2 = [None, None, None, None, None]

                if self.keys[pg.K_f]:
                    self.final_team = 0
                else:
                    self.final_team = 1

                self.question = 0
                self.jingle.play()

        if self.state == "final":
            dalej = self.keys[pg.K_d]
            blad = self.keys[pg.K_x]
            bylo = self.keys[pg.K_b]

            for i in range(1, len(self.final_questions[self.question]) + 1):
                if eval(f"self.keys[pg.K_{i}]"):
                    i = i - 1


    def draw(self) -> None:
        self.screen.fill("black")
        if self.state == "choose":
            self.choose_preset()

        if self.state == "intro" and not self.keys[pg.K_ESCAPE]:
            self.animate(self.dt)
            if not self._intro_music:
                self.intro_music.play()
                self._intro_music = True
        elif self.keys[pg.K_ESCAPE]:
            self.intro_music.stop()
            self.state = "ascii"

        if self.state == "ascii":
            rtext = self.asciifont.render(self.ascii_art, True, "yellow")
            rtext = pg.transform.scale2x(rtext)
            self.screen.blit(
                rtext,
                (
                    self.screen.width // 2 - rtext.width // 2,
                    self.screen.height // 2 - rtext.height // 2,
                ),
            )

            if self.keys[pg.K_RETURN]:
                self.state = "normal"

        if self.state == "normal":
            size = self.screen.size
            suma = self.font.render(f"SUMA: {self.points}", True, "yellow")
            size = (size[0], size[1] - suma.height - 20)
            width = size[0]
            iks_width = width / 12

            pointsl, pointsr = self.team_points

            pointsl = self.font.render(f"{pointsl}", True, "yellow")
            pointsr = self.font.render(f"{pointsr}", True, "yellow")

            if self.team == 1:
                # Pionowa linia po prawej
                pg.draw.line(
                    self.screen,
                    "yellow",
                    (width - iks_width, 0),
                    (width - iks_width, size[1]),
                    3,
                )

                # Poziome linie po prawej
                for i in range(3):
                    pg.draw.line(
                        self.screen,
                        "yellow",
                        (width - iks_width, size[1] // 3 * i),
                        (width, size[1] // 3 * i),
                        2,
                    )

            else:
                # Pionowa linia po lewej
                pg.draw.line(
                    self.screen, "yellow", (iks_width, 0), (iks_width, size[1]), 3
                )

                # Poziome linie po lewej
                for i in range(3):
                    pg.draw.line(
                        self.screen,
                        "yellow",
                        (0, size[1] // 3 * i),
                        (iks_width, size[1] // 3 * i),
                        2,
                    )

            rtext = self.Xfont.render("X", True, "yellow")
            iks_width_halfx = (iks_width - rtext.width) // 2
            iks_width_halfy = (size[1] // 3 - rtext.height) // 2

            # Iksy po lewej
            for i in range(self.team_iks[0]):
                self.screen.blit(
                    rtext,
                    (
                        iks_width_halfx,
                        (i + 1) * iks_width_halfy
                        + i * (rtext.height + iks_width_halfy),
                    ),
                )

            # Iksy po prawej
            for i in range(self.team_iks[1]):
                self.screen.blit(
                    rtext,
                    (
                        width - iks_width + iks_width_halfx,
                        (i + 1) * iks_width_halfy
                        + i * (rtext.height + iks_width_halfy),
                    ),
                )

            # Pytania
            for i, answer in enumerate(
                self.preset["questions"][self.question]["answers"]
            ):
                question = self.preset["questions"][self.question]
                text = f"{i + 1}. {answer["text"].upper()}"
                text = f"{text.ljust(83, ".")} | {answer["points"]}"

                rtext = self.font.render(
                    f"{i + 1}. {"." * 83} | ??", True, "yellow", None
                )
                if self.questions[self.question][i] == True:
                    rtext = self.font.render(text, True, "yellow", None)

                answers = len(question["answers"])

                integer = size[1] // answers
                half_integer = (integer - rtext.height) // 2

                # Render text
                self.screen.blit(
                    rtext,
                    (
                        iks_width + 20,
                        (i + 1) * half_integer + i * (rtext.height + half_integer),
                    ),
                )

            self.screen.blit(
                suma,
                (
                    self.screen.width // 2 - suma.width // 2,
                    self.screen.height - 10 - suma.height,
                ),
            )
            self.screen.blit(
                pointsl, (iks_width + 20, self.screen.height - pointsl.height - 20)
            )

            self.screen.blit(
                pointsr,
                (width - iks_width - 20, self.screen.height - pointsl.height - 20),
            )

        pg.display.flip()

    def run(self) -> None:
        while self.running:
            self.events()
            self.update()
            self.draw()
        else:
            sys.exit(0)


if __name__ == "__main__":
    game = Game(FILES_DIR)
    game.run()
