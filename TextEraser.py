import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import pytesseract
from pytesseract import Output
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def detect_and_remove_text(image_path, output_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    d = pytesseract.image_to_data(gray, output_type=Output.DICT)
    n_boxes = len(d['level'])
    mask = img.copy()
    
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
    
    img_without_text = cv2.bitwise_and(img, mask)
    cv2.imwrite(output_path, img_without_text)

def process_images_in_folder(input_folder, output_folder, mode):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            print(f"Procesando {filename}...")
            detect_and_remove_text(input_path, output_path)
            print(f"Guardado en {output_path}")

def start_processing():
    input_folder = folder_path.get()
    mode = mode_var.get()
    
    if not input_folder:
        messagebox.showerror("Error", "Por favor selecciona una carpeta de entrada.")
        return
    
    output_folder = os.path.join(input_folder, f'{mode}_processed')
    process_images_in_folder(input_folder, output_folder, mode)
    
    response = messagebox.askyesno("Listo", "Las imágenes han sido procesadas. ¿Quieres procesar más imágenes?")
    
    if not response:
        root.quit()
    else:
        folder_path.set("")

def select_folder():
    folder_selected = filedialog.askdirectory()
    folder_path.set(folder_selected)

root = tk.Tk()
root.title("Eliminador de Texto de Manga y Cómics")

folder_path = tk.StringVar()
mode_var = tk.StringVar(value="manga")

title_label = tk.Label(root, text="Eliminador de Texto de Manga y Cómics", font=("Helvetica", 16))
title_label.pack(pady=10)

folder_button = tk.Button(root, text="Seleccionar Carpeta", command=select_folder)
folder_button.pack(pady=5)

folder_label = tk.Label(root, textvariable=folder_path)
folder_label.pack(pady=5)

mode_frame = tk.Frame(root)
mode_frame.pack(pady=10)

mode_label = tk.Label(mode_frame, text="Selecciona el tipo de imágenes:")
mode_label.pack(side=tk.LEFT)

comic_radio = tk.Radiobutton(mode_frame, text="Cómic", variable=mode_var, value="comic")
comic_radio.pack(side=tk.LEFT, padx=5)

manga_radio = tk.Radiobutton(mode_frame, text="Manga", variable=mode_var, value="manga")
manga_radio.pack(side=tk.LEFT, padx=5)

process_button = tk.Button(root, text="Empezar a Procesar", command=start_processing)
process_button.pack(pady=20)

root.mainloop()
