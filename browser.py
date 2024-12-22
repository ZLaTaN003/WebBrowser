import tkinter as tk
from urls import Url

class Browser:
    WIDTH = 800
    HEIGHT = 600
    def __init__(self):
        self.window = tk.Tk()
        self.canvas = tk.Canvas(self.window,width=Browser.WIDTH,height=Browser.HEIGHT)
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>",self.move_down)

    def load(self,response_text):

        x_space_delta,y_space_delta = 13,18
        pos_x,pos_y = x_space_delta,y_space_delta
        for char in response_text:
            pos_y = pos_y - self.scroll #add scrolling
            self.canvas.create_text(pos_x,pos_y,text=char)
            pos_x += x_space_delta

            if pos_x > Browser.WIDTH - x_space_delta: #wrapping line
                pos_y += y_space_delta#go to next line
                pos_x = x_space_delta #reset x to initial
    
    def move_down(self,e):
        self.scroll += 50
        #self.load()
        self.canvas.delete("all") 


def request(url) -> str:
    """Makes a request and returns text response"""

    url = Url(url)
    response = url.make_request()

    return response

if __name__ == "__main__":
    response_text = request("https://browser.engineering/examples/xiyouji.html")
    browser = Browser()
    browser.load(response_text)
    tk.mainloop()