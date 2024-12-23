import tkinter as tk
from tkinter import font
from urls import Url


class Browser:
    width = 800
    height = 600

    def __init__(self) -> None:
        self.window = tk.Tk()
        self.window.title("CHANZEN BROWSER")
        self.canvas = tk.Canvas(self.window, width=Browser.width, height=Browser.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.window.bind("<Configure>", self.on_resize)
        self.window.bind("<Down>", self.move_down)
        self.window.bind("<Up>", self.move_up)
        self.scroll = 0
        self.times_font = tk.font.Font(size=13)

    def load(self, response_text):
        self.response_text = response_text
        self.make_display_list()

    def make_display_list(self) -> None:
        """loads the response text into a display list with its coordinates and character content"""
        self.display_list = []

        x_space_delta, y_space_delta = 13, 18
        pos_x, pos_y = x_space_delta, y_space_delta
        for word in self.response_text.split():
            word_x = self.times_font.measure(word) + self.times_font.measure(" ")

            if pos_x + word_x > Browser.width - x_space_delta:  # wrapping line
                pos_y += self.times_font.metrics("linespace") * 1.25  # go to next line
                pos_x = x_space_delta  # reset x to initial
            
            self.display_list.append((pos_x, pos_y, word))
            pos_x += word_x

        return None

    def draw(self) -> None:
        """draws each frame"""
        self.canvas.delete("all")

        for x, y, ch in self.display_list:
            if y > self.scroll + Browser.height:
                continue
            if self.scroll > y:
                continue

            self.canvas.create_text(
                x, y - self.scroll, text=ch,font=self.times_font,anchor="nw"
            )  # y - scroll so the y axis start from y-scroll

    def move_down(self, e) -> None:
        self.scroll += (
            50  # scroll is incremented on down button which creates a scroll effect
        )
        self.draw()

    def move_up(self, e) -> None:
        if self.scroll == 0:
            return
        self.scroll -= 50
        self.draw()

    def on_resize(self, e):
        width = e.width
        height = e.height
        Browser.width = width
        Browser.height = height
        self.make_display_list()
        self.draw()


def request(url) -> str:
    """Makes a request and returns text response"""

    url = Url(url)
    response = url.make_request()

    return response


if __name__ == "__main__":
    response_text = request("https://browser.engineering/text.html")
    browser = Browser()
    browser.load(response_text)
    browser.draw()  # initial draw with scroll 0
    tk.mainloop()
