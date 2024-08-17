import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def detect_and_remove_text_bubbles(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    
    contours, _ = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        area = cv2.contourArea(contour)

        if area < 500:
            continue
        
        mask = np.zeros_like(image)
        cv2.drawContours(mask, [contour], -1, (255, 255, 255), -1)
        mean_color = cv2.mean(image, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))[:3]
        cv2.drawContours(image, [contour], -1, mean_color, -1)
    
    return image

def process_images_in_folder(input_folder, output_folder, mode, progress_bar, status_label):
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
    images = [f for f in os.listdir(input_folder) if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    total_images = len(images)
    start_time = time.time()
    
    for i, image_name in enumerate(images):
        input_path = os.path.join(input_folder, image_name)
        output_path = os.path.join(output_folder, image_name)
        
        image = cv2.imread(input_path)
        processed_image = detect_and_remove_text_bubbles(image)
        cv2.imwrite(output_path, processed_image)
        
        progress = int((i + 1) / total_images * 100)
        elapsed_time = time.time() - start_time
        estimated_total_time = elapsed_time / (i + 1) * total_images
        remaining_time = estimated_total_time - elapsed_time
        
        progress_bar['value'] = progress
        status_label.config(text=f"Procesando {i + 1}/{total_images} imágenes... (Tiempo restante: {int(remaining_time)}s)")
        root.update_idletasks()
    
    messagebox.showinfo("Completado", "El procesamiento de imágenes ha finalizado.")
    status_label.config(text="Listo.")
    if messagebox.askyesno("Proceso finalizado", "¿Desea procesar más imágenes?"):
        progress_bar['value'] = 0
        status_label.config(text="")
    else:
        root.quit()

def start_processing_thread():
    threading.Thread(target=start_processing).start()

def start_processing():
    input_folder = input_folder_entry.get()
    if not input_folder:
        messagebox.showerror("Error", "Debe seleccionar una carpeta de entrada.")
        return
    
    mode = mode_var.get()
    output_folder = os.path.join(input_folder, 'output')
    
    process_images_in_folder(input_folder, output_folder, mode, progress_bar, status_label)

def select_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(0, folder_selected)

root = tk.Tk()
root.title("Text Bubble Remover")

title_label = tk.Label(root, text="Text Bubble Remover", font=("Helvetica", 16))
title_label.grid(row=0, column=0, columnspan=3, pady=10)

input_folder_label = tk.Label(root, text="Carpeta de entrada:")
input_folder_label.grid(row=1, column=0, padx=10, pady=10)

input_folder_entry = tk.Entry(root, width=40)
input_folder_entry.grid(row=1, column=1, padx=10, pady=10)

browse_button = tk.Button(root, text="Buscar...", command=select_input_folder)
browse_button.grid(row=1, column=2, padx=10, pady=10)

mode_label = tk.Label(root, text="Modo:")
mode_label.grid(row=2, column=0, padx=10, pady=10)

mode_var = tk.StringVar(value="Manga")
mode_options = ["Manga", "Cómic"]
mode_menu = tk.OptionMenu(root, mode_var, *mode_options)
mode_menu.grid(row=2, column=1, padx=10, pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, padx=10, pady=20)

status_label = tk.Label(root, text="")
status_label.grid(row=4, column=0, columnspan=3, pady=10)

start_button = tk.Button(root, text="Iniciar Procesamiento", command=start_processing_thread)
start_button.grid(row=5, column=0, columnspan=3, pady=10)

root.mainloop()
