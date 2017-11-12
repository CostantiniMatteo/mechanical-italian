#! /usr/bin/env python3
import sys, argparse
import tkinter as tk
from os import listdir, rename, makedirs
from os.path import isfile, join, basename, exists
from PIL import Image, ImageTk


class Window():
    def __init__(self, labels, *, source, dest='.', preload=False):
        assert exists(source), "Source directory does not exist!"
        if not exists(dest):
            makedirs(dest_folder)

        file_list = [f for f in listdir(source) if isfile(join(source, f))]
        assert len(file_list) > 0, "There are no files in the source directory!"

        self.labels = labels
        for label in labels.values():
            if not exists(join(dest, label)):
                makedirs(join(dest, label))

        self.source = source
        self.dest = dest

        self.main = tk.Tk()
        self.main.bind('<Key>', lambda e: self.move_image(e.char) and self.show_next_image())
        self.main.bind("<Button-1>", self.mouse_callback)
        self.main.bind("<Escape>", lambda x: self.main.destroy())

        # The generator is lazy evalued unless preload is True
        images_gen = (self.load_image(f) for f in file_list)
        if preload:
            self.images = iter(list(images_gen))
        else:
            self.images = images_gen
        self.current_image = next(self.images, None)

        self.build_window()
        self.main.mainloop()

    def load_image(self, file):
        tmp = Image.open(join(self.source, file))
        new_image = ImageTk.PhotoImage(tmp)
        new_image.filename = basename(tmp.filename)
        return new_image
        

    def build_window(self):
        self.canvas = tk.Canvas(self.main, width=500, height=500)
        self.image_on_canvas = self.canvas.create_image(
            250,
            250,
            anchor=tk.CENTER,
            image=self.current_image,
            tags="image_tag"
        )
        self.canvas.pack(fill = tk.BOTH)


    def mouse_callback(self, event):
        print('mouse called', event)

    def move_image(self, label):
        print('called', label)
        prev_filename = self.current_image.filename
        rename(join(self.source, prev_filename),
               join(self.dest, self.labels[label], prev_filename))
        return True


    def show_next_image(self):
        self.current_image = next(self.images, None)
        if self.current_image:
            self.canvas.itemconfig(self.image_on_canvas,
                                   image=self.current_image)
        else:
            self.main.destroy()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default='.', help="Directory containing the images. Defaults to current directory.")
    parser.add_argument('-d', '--dest', default='.', help="Directory where the images will be saved. Defaults to current directory.")
    parser.add_argument('-l', '--labels', nargs='+', required=True, help='<Required> List of labels and key. label_name:key')
    parser.add_argument('-p', '--preload', action='store_true', help="Preload all images in memory at the beginning, useful when you have really big images and a lot of memory.")
    args = parser.parse_args()
    
    if len(args.labels) < 2:
        sys.exit("Error: At least two labels are required")

    labels = {}
    for s in args.labels:
        label, key = s.split(':')
        labels[key] = label

    Window(labels, source=args.source, dest=args.dest, preload=args.preload)
    
