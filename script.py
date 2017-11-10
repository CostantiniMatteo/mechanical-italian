from os import listdir, rename
from os.path import isfile, join
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

        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.pack(fill = tk.BOTH)

    def on_click(self, event):
        if self.current_image < len(self.images):
            prev = self.images[self.current_image]

            self.current_image += 1
            if self.current_image < len(self.images):

                self.canvas.itemconfig(self.image_on_canvas,
                                       image=self.images[self.current_image])
            else:
                self.canvas.delete('all')

            if event.x < 250:
                rename(join(src_folder, prev.filename),
                       join(dest_folder, "0_" + prev.filename))
            else:
                rename(join(src_folder, prev.filename),
                       join(dest_folder, "1_" + prev.filename))


if __name__ == '__main__':
    # Move files back in the destination folder
    for file in [f for f in listdir(dest_folder) if isfile(join(dest_folder, f))]:
        rename(join(dest_folder, file), join(src_folder, file.split('_')[-1]))

    root = tk.Tk()
    Window(root)
    root.mainloop()
