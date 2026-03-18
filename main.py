#!/usr/bin/env python3

import json
import pathlib
import sys

import pygame as pg

pg.init()


FILES_DIR: pathlib.Path = pathlib.Path(__file__).parent


class Game:
    def __init__(self, files_dir: pathlib.Path) -> None:
        # Files
        self.files: pathlib.Path = files_dir

        # Pygame stuff
        self.screen: pg.Surface = pg.display.set_mode(
            (0, 0), pg.FULLSCREEN | pg.DOUBLEBUF, vsync=1
        )
        self.keys: pg.key.ScancodeWrapper = pg.key.get_just_pressed()
        self.clock = pg.Clock()
        self.mouse: tuple[bool, bool, bool, bool, bool] = pg.mouse.get_just_pressed()
        self.mouse_pos: tuple[int, int] = pg.mouse.get_pos()
        self.font = pg.font.Font(self.files / "fonts" / "familiada.ttf", size=40)

        self.round_info: dict = {}
        self.running: bool = True
        self.state: str = "choose"
        self.round: str = "R1"
        self.question_num: int = 0

        self.presets = self.load_presets()

    def load_presets(self) -> list[dict]:
        presets: list[dict] = []
        for file in (self.files / "presets").glob("*.json"):
            with file.open() as f:
                preset = json.load(f)
                presets.append(preset)
        return presets

    # TODO: Make a `load_preset_info` function that will parse informations such as number of questions per round, and its answers.
    # TODO: Make some new `self.` variables about current round, question and uncovered questions.

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
                    self.state = "normal"

            text = self.font.render(f"{preset["title"]}", True, color)

            self.screen.blit(
                text,
                (rect.center[0] - text.width // 2, rect.center[1] - text.height // 2),
            )

    def events(self) -> None:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False

    def update(self) -> None:
        self.clock.tick(60)

        self.keys = pg.key.get_just_pressed()
        self.mouse = pg.mouse.get_just_pressed()
        self.mouse_pos = pg.mouse.get_pos()

        if self.state == "normal":
            pass

    def draw(self) -> None:
        self.screen.fill("black")
        if self.state == "choose":
            self.choose_preset()

        if self.state == "normal":
            size = self.screen.size
            width = size[0]
            iks_width = width / 12

            answers = []
            for answer in self.preset["questions"][self.question_num]["answers"]:
                answers.append(answer)

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
