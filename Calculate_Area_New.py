import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, Label, Button, Scale, Checkbutton, BooleanVar
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
        self.hierarchy = None
        self.polygon_points = []
        self.line_length_cm = None
        self.original_image = None
        self.threshold_value = 127
        self.kernel_size = 5
        self.fill_area_var = BooleanVar()
        self.inverted = False

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

        # Галочка для закрашивания области
        self.fill_area_checkbox = Checkbutton(root, text="Закрасить область", variable=self.fill_area_var, command=self.update_image)
        self.fill_area_checkbox.pack()

        # Кнопка для инверсии зоны
        self.invert_button = Button(root, text="Инвертировать зону", command=self.invert_area)
        self.invert_button.pack()

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
            if self.inverted:
                _, threshold = cv2.threshold(gray, self.threshold_value, 255, cv2.THRESH_BINARY_INV)
            else:
                _, threshold = cv2.threshold(gray, self.threshold_value, 255, cv2.THRESH_BINARY)

            # Применение морфологической операции для удаления шума
            kernel = np.ones((self.kernel_size, self.kernel_size), np.uint8)
            threshold = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernel)

            # Поиск контуров с иерархией
            self.contours, self.hierarchy = cv2.findContours(threshold, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

            display_image = self.original_image.copy()

            if self.contours and self.hierarchy is not None:
                # Закрашивание области, если выбрана галочка
                if self.fill_area_var.get():
                    mask = np.zeros_like(gray)
                    for i, contour in enumerate(self.contours):
                        # Если родительский контур (-1), то это внешний контур
                        if self.hierarchy[0][i][3] == -1:
                            cv2.drawContours(mask, [contour], -1, 255, -1)
                        else:
                            # Внутренние контуры
                            cv2.drawContours(mask, [contour], -1, 0, -1)
                    # Применяем штриховку
                    self.apply_hatching(display_image, mask)

                # Рисуем контуры на изображении (зеленый цвет)
                cv2.drawContours(display_image, self.contours, -1, (0, 255, 0), 2)
            else:
                print("Контуры не найдены.")

            cv_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(cv_image)
            self.tk_image = ImageTk.PhotoImage(image=pil_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            # Отображение нарисованной линии
            if len(self.polygon_points) == 2:
                self.canvas.create_line(self.polygon_points[0], self.polygon_points[1], fill="red", tags="line")
                print(f"Отображаем линию: {self.polygon_points[0]} - {self.polygon_points[1]}")

    def draw_line(self):
        if self.image is not None:
            self.polygon_points = []  # Очищаем список точек
            self.canvas.delete("line")  # Удаляем предыдущую линию
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            print("Рисование линии активировано.")

    def on_canvas_click(self, event):
        if len(self.polygon_points) < 2:
            self.polygon_points.append((event.x, event.y))
            print(f"Точка добавлена: {event.x}, {event.y}")

            if len(self.polygon_points) == 2:
                self.canvas.create_line(self.polygon_points[0], self.polygon_points[1], fill="red", tags="line")
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

        if not self.contours or self.hierarchy is None:
            print("Ошибка: Контуры не найдены. Пожалуйста, загрузите изображение и нарисуйте линию.")
            self.result_label.config(text="Контуры не найдены. Пожалуйста, загрузите изображение и нарисуйте линию.")
            return

        if len(self.polygon_points) != 2:
            print(self.polygon_points)
            print("Ошибка: Линия не нарисована или длина не задана.")
            self.result_label.config(text="Пожалуйста, нарисуйте линию и укажите ее длину.")
            return

        print(f"Координаты линии: {self.polygon_points[0]} - {self.polygon_points[1]}")

        # Расчет площади с учетом внутренних полостей
        area_in_pixels = 0
        for i, contour in enumerate(self.contours):
            contour_area = cv2.contourArea(contour)
            # Если контур внешний, добавляем площадь
            if self.hierarchy[0][i][3] == -1:
                area_in_pixels += contour_area
            else:
                # Внутренний контур, вычитаем площадь
                area_in_pixels -= contour_area

        print(f"Скорректированная площадь в пикселях: {area_in_pixels}")

        # Рассчет площади одного пикселя в квадратных сантиметрах
        pixel_length_cm = self.line_length_cm / self.calculate_line_length(self.polygon_points[0], self.polygon_points[1])
        pixel_area_cm2 = pixel_length_cm ** 2

        total_area_cm2 = area_in_pixels * pixel_area_cm2
        print(f"Рассчитанная площадь: {total_area_cm2:.2f} см^2")
        self.result_label.config(text=f"Площадь объекта: {total_area_cm2:.2f} см^2")

    def apply_hatching(self, image, mask):
        pattern_size = 10  # Размер штриховки
        color = (255, 0, 0)  # Цвет штриховки (синий)
        thickness = 1  # Толщина линии

        # Создание пустого изображения для штриховки
        hatching_image = np.zeros_like(image)

        # Если инверсия включена, применяем штриховку к инвертированной маске
        if self.invert_area:
            mask = ~mask  # Инвертируем маску

        # Найти все контуры
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Нарисовать штриховку для всех контуров
        for contour in contours:
            # Создать маску для текущего контура
            contour_mask = np.zeros_like(mask)
            cv2.drawContours(contour_mask, [contour], -1, 255, thickness=cv2.FILLED)

            # Применить штриховку к маске контура
            for y in range(0, contour_mask.shape[0], pattern_size):
                for x in range(0, contour_mask.shape[1], pattern_size):
                    if contour_mask[y, x] == 255:
                        start_point = (x, y)
                        end_point = (
                        min(x + pattern_size, contour_mask.shape[1]), min(y + pattern_size, contour_mask.shape[0]))
                        cv2.line(hatching_image, start_point, end_point, color, thickness)

        # Объединение исходного изображения с изображением штриховки
        mask = mask.astype(bool)
        image[mask] = np.where(hatching_image[mask] == 0, image[mask], hatching_image[mask])

    def invert_area(self):
        self.inverted = not self.inverted
        print(f"Инверсия зоны: {self.inverted}")
        self.update_image()

# Запуск приложения
root = tk.Tk()
app = AreaCalculatorApp(root)
root.mainloop()
