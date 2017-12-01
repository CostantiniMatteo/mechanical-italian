#! /usr/bin/env python3
import sys, argparse
import tkinter as tk
from os import listdir, rename, makedirs
from os.path import isfile, join, basename, exists
import itertools
from PIL import Image, ImageTk



class Window():
    CANVAS_WIDTH = 500
    CANVAS_HEIGTH = 500
    IMAGE_WITDH = 300
    IMAGE_HEIGTH = 300

    def __init__(self, labels, *, source, dest='.', preload=False, undo_limit=10):
        assert exists(source), "Source directory does not exist!"

        file_list = [f for f in listdir(source) if isfile(join(source, f))]
        assert len(file_list) > 0, "There are no files in the source directory!"

        self.source = source
        self.dest = dest

        self.main = tk.Tk()
        self.main.bind("<Escape>", lambda x: self.main.destroy())
        self.main.bind("<BackSpace>", self.undo_action)

        self.labels = {}
        for key, label in labels:
            self.labels[key] = label

            if not exists(join(dest, label)):
                makedirs(join(dest, label))

            def make_lambda(key):
                return lambda e: self.move_image(key) and self.show_next_image()
            self.main.bind(key, make_lambda(key))

        # The generator is lazy evalued unless preload is True
        images_gen = (self.load_image(f) for f in file_list)
        if preload:
            self.images = iter(list(images_gen))
        else:
            self.images = images_gen
        self.current_image = next(self.images, None)
        self.previous_images = []
        self.undo_limit = int(undo_limit)

        self.build_window()
        self.main.mainloop()

    def load_image(self, file):
        tmp = Image.open(join(self.source, file))
        filename = basename(tmp.filename)

        new_image = ImageTk.PhotoImage(self.resize_image(tmp,
            self.IMAGE_WITDH,
            self.IMAGE_HEIGTH)
        )
        new_image.filename = filename
        return new_image

    def resize_image(self, image, maxWidth, maxHeight):
        ratio = 0
        width = image.width
        height = image.height

        if width > maxWidth:
            ratio = maxWidth / width
            new_width = maxWidth * ratio
            new_height = height / width * new_width
        if height > maxHeight:
            ratio = maxHeight / height
            new_height = height * ratio
            new_width = width / height * new_height

        return image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)


    def build_window(self):
        self.canvas = tk.Canvas(self.main,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGTH
        )
        self.image_on_canvas = self.canvas.create_image(
            self.CANVAS_WIDTH / 2,
            self.CANVAS_WIDTH / 2,
            anchor=tk.CENTER,
            image=self.current_image,
            tags="image_tag"
        )

        self.canvas.pack(fill = tk.BOTH)


    def move_image(self, key):
        try:
            prev_filename = self.current_image.filename
            rename(join(self.source, prev_filename),
                   join(self.dest, self.labels[key], prev_filename))

            self.previous_images.append((self.current_image, key))

            if len(self.previous_images) > self.undo_limit:
                self.previous_images.pop(0)
            return True
        except e:
            print(e.message)
            return False


    def show_next_image(self):
        self.current_image = next(self.images, None)
        if self.current_image:
            self.canvas.itemconfig(self.image_on_canvas,
                                   image=self.current_image)
        else:
            self.main.destroy()


    def undo_action(self, event):
        if self.previous_images:
            image, key = self.previous_images.pop(-1)
            self.images = itertools.chain([image, self.current_image], self.images)

            rename(join(self.dest, self.labels[key], image.filename),
                   join(self.source, image.filename))

            self.show_next_image()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--source', default='.', help="Directory containing the images. Defaults to current directory.")
    parser.add_argument('-d', '--dest', default='.', help="Directory where the images will be saved. Defaults to current directory.")
    parser.add_argument('-l', '--labels', nargs='+', required=True, help='<Required> List of labels and key. label_name:key')
    parser.add_argument('-p', '--preload', action='store_true', help="Preload all images in memory at the beginning, useful when you have really big images and a lot of memory.")
    parser.add_argument('-u', '--undolimit', default='10', help="Maximum number of undo actions. Defaults to 10.")
    args = parser.parse_args()

    if len(args.labels) < 2:
        sys.exit("Error: At least two labels are required")

    labels = []
    for label, key in [s.split(':') for s in args.labels]:
        labels.append((key, label))

    undo_limit = int(args.undolimit)

    Window(labels=labels,
           source=args.source,
           dest=args.dest,
           preload=args.preload,
           undo_limit=undo_limit)

