from os import listdir, rename, path, makedirs
from os.path import isfile, join
import argparse

from PIL import Image, ImageTk
import tkinter as tk

src_folder = "source/"
dest_folder = "dest/"

class Window():
    def __init__(self, main):
        self.canvas = tk.Canvas(main, width=500, height=500)

        self.images = []
        for file in [f for f in listdir(src_folder) if isfile(join(src_folder, f))]:
            tmp = Image.open(join(src_folder, file))
            new_image = ImageTk.PhotoImage(tmp)
            new_image.filename = tmp.filename.split('/')[-1]
            self.images.append(new_image)
        self.current_image = 0

        self.image_on_canvas = self.canvas.create_image(
            250,
            250,
            anchor=tk.CENTER,
            image=self.images[self.current_image],
            tags="image_tag"
        )

        self.canvas.bind('<Button-1>', self.on_click_l)
        self.canvas.bind('<Button-2>', self.on_click_r)
        self.canvas.pack(fill = tk.BOTH)

    def on_click_l(self, event):
        self.on_click(prefix="0_")

    def on_click_r(self, event):
        self.on_click(prefix="1_")

    def on_click(self, prefix="MISSING_"):
        if self.current_image < len(self.images):
            prev = self.images[self.current_image]

            self.current_image += 1
            if self.current_image < len(self.images):

                self.canvas.itemconfig(self.image_on_canvas,
                                       image=self.images[self.current_image])
            else:
                self.canvas.delete('all')

            rename(join(src_folder, prev.filename),
                   join(dest_folder, prefix + prev.filename))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="Directory containing the images. Default source/")
    parser.add_argument("--output", help="Directory where the images will be saved. Default dest/")
    args = parser.parse_args()

    if args.source is not None:
        src_folder = args.source

    if args.output is not None:
        dest_folder = args.output
        if not path.exists(dest_folder):
            makedirs(dest_folder)

    root = tk.Tk()
    Window(root)
    root.mainloop()