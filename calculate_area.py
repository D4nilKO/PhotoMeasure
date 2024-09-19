import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, Label, Button, Scale
import tkinter.simpledialog

class AreaCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Площадь объекта на изображении")

        # Инициализация переменных
        self.image_path = None
        self.image = None
        self.tk_image = None
        self.contours = []
        self.polygon_points = []
        self.line_length_cm = None
        self.original_image = None
        self.threshold_value = 127
        self.kernel_size = 5

        # Кнопки и элементы интерфейса
        self.load_button = Button(root, text="Загрузить изображение", command=self.load_image)
        self.load_button.pack()

        self.draw_button = Button(root, text="Нарисовать линию", command=self.draw_line)
        self.draw_button.pack()

        self.calculate_button = Button(root, text="Рассчитать площадь", command=self.calculate_area)
        self.calculate_button.pack()

        self.result_label = Label(root, text="Площадь объекта: Неизвестно")
        self.result_label.pack()

        self.canvas = tk.Canvas(root, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Слайдеры
        self.threshold_slider = Scale(root, from_=0, to=255, orient=tk.HORIZONTAL, label="Пороговое значение", command=self.update_image)
        self.threshold_slider.set(self.threshold_value)
        self.threshold_slider.pack()

        self.kernel_slider = Scale(root, from_=1, to=15, orient=tk.HORIZONTAL, label="Размер ядра (нечетное)", command=self.update_image)
        self.kernel_slider.set(self.kernel_size)
        self.kernel_slider.pack()

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if self.image_path:
            self.image = cv2.imread(self.image_path)
            self.original_image = self.image.copy()
            self.update_image()

    def update_image(self, *args):
        if self.image is not None:
            self.threshold_value = self.threshold_slider.get()
            self.kernel_size = self.kernel_slider.get()

            # Преобразование изображения в градации серого
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

            # Применение порога
            _, threshold = cv2.threshold(gray, self.threshold_value, 255, cv2.THRESH_BINARY)

            # Применение морфологической операции для удаления шума
            kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
            threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)

            # Поиск контуров
            self.contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if self.contours:
                # Найти наибольший контур по площади
                largest_contour = max(self.contours, key=cv2.contourArea)
                # Рисуем контуры на копии изображения
                display_image = self.original_image.copy()
                cv2.drawContours(display_image, [largest_contour], -1, (0, 255, 0), 2)
            else:
                print("Контуры не найдены.")
                display_image = self.original_image.copy()

            cv_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv_image)
            self.tk_image = ImageTk.PhotoImage(image=pil_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            # Отображение нарисованной линии
            if self.polygon_points:
                if len(self.polygon_points) == 2:
                    self.canvas.create_line(self.polygon_points[0], self.polygon_points[1], fill="red")
                    print(f"Отображаем линию: {self.polygon_points[0]} - {self.polygon_points[1]}")

    def draw_line(self):
        if self.image is not None:
            self.polygon_points = []  # Очищаем список точек
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            self.draw_button.config(state=tk.DISABLED)  # Делаем кнопку недоступной до завершения
            print("Рисование линии активировано.")

    def on_canvas_click(self, event):
        if len(self.polygon_points) < 2:
            self.polygon_points.append((event.x, event.y))
            print(f"Точка добавлена: {event.x}, {event.y}")

            if len(self.polygon_points) == 2:
                self.canvas.create_line(self.polygon_points[0], self.polygon_points[1], fill="red")
                self.canvas.unbind("<Button-1>")
                length = self.calculate_line_length(self.polygon_points[0], self.polygon_points[1])
                length_cm = tk.simpledialog.askfloat("Длина линии", "Введите длину линии (в сантиметрах):",
                                                     initialvalue=length)
                if length_cm is not None:
                    self.line_length_cm = length_cm
                    print(f"Длина линии в сантиметрах: {length_cm}")
                # Список точек оставляем для использования в расчете

    def calculate_line_length(self, point1, point2):
        return np.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

    def calculate_area(self):
        if self.image is None:
            print("Ошибка: Изображение не загружено.")
            self.result_label.config(text="Ошибка: Изображение не загружено.")
            return

        if self.line_length_cm is None:
            print("Ошибка: Длина линии не задана.")
            self.result_label.config(text="Ошибка: Длина линии не задана.")
            return

        if not self.contours:
            print("Ошибка: Контуры не найдены. Пожалуйста, загрузите изображение и нарисуйте линию.")
            self.result_label.config(text="Контуры не найдены. Пожалуйста, загрузите изображение и нарисуйте линию.")
            return

        if len(self.polygon_points) != 2:
            print(self.polygon_points)
            print("Ошибка: Линия не нарисована или длина не задана.")
            self.result_label.config(text="Пожалуйста, нарисуйте линию и укажите ее длину.")
            return

        print(f"Координаты линии: {self.polygon_points[0]} - {self.polygon_points[1]}")

        # Найти наибольший контур по площади
        largest_contour = max(self.contours, key=cv2.contourArea)
        area_in_pixels = cv2.contourArea(largest_contour)
        print(f"Площадь в пикселях: {area_in_pixels}")

        # Рассчет площади одного пикселя в квадратных сантиметрах
        pixel_length_cm = self.line_length_cm / self.calculate_line_length(self.polygon_points[0],
                                                                           self.polygon_points[1])
        print(f"Длина пикселя в см: {pixel_length_cm}")

        pixel_area_cm2 = pixel_length_cm ** 2
        area_in_cm2 = area_in_pixels * pixel_area_cm2
        print(f"Площадь в квадратных сантиметрах: {area_in_cm2}")

        area_in_m2 = area_in_cm2 / 10000  # Перевод в квадратные метры
        print(f"Площадь объекта в квадратных метрах: {area_in_m2:.4f}")

        self.result_label.config(text=f"Площадь объекта: {area_in_m2:.4f} м²")


# Запуск приложения
root = tk.Tk()
app = AreaCalculatorApp(root)
root.mainloop()
