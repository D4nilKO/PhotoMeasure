# Area Calculation Tool 
## Описание 
Area Calculation Tool - это приложение на Python с графическим интерфейсом, которое позволяет загружать изображение и рассчитывать площадь объекта на изображении. Приложение также предоставляет возможность настройки порогового значения и размера ядра для обработки изображения.  
## Установка 
Для запуска проекта необходимо установить Python и несколько библиотек. Следуйте инструкциям ниже для установки:  
1. Клонируйте репозиторий:     
```bash
git clone https://github.com/ваш-репозиторий/area-calculation-tool.git
cd area-calculation-tool
``` 
2. Установите необходимые зависимости:     
 ```bash
pip install -r requirements.txt 
``` 
## Запуск 
Для запуска приложения выполните следующую команду:  ```bash python Calculate_Area_New.py

## Использование

### Интерфейс

- **Загрузить изображение**: Нажмите эту кнопку, чтобы выбрать и загрузить изображение.
- **Нарисовать линию**: Нажмите эту кнопку, чтобы нарисовать линию на изображении, которая будет служить эталоном для расчета площади. Теперь укажите последовательно две точки. После ввода второй точки будет проведена красная линия.
- **Рассчитать площадь**: Нажмите эту кнопку, чтобы рассчитать площадь объекта на изображении.
- **Пороговое значение**: Используйте этот слайдер для установки порогового значения при обработке изображения.
- **Размер ядра (нечетное)**: Используйте этот слайдер для установки размера ядра при обработке изображения.
- **Закрасить область** (пока работает некорректно): Установите этот флажок, чтобы закрасить найденную область объекта. 
- **Инвертировать зону**: Нажмите эту кнопку, чтобы инвертировать зону интереса на изображении.

### Пример использования

1. Нажмите кнопку "Загрузить изображение" и выберите изображение.
2. Нажмите кнопку "Нарисовать линию" и нарисуйте эталонную линию на изображении.
3. Укажите длину этой линии и нажмите Enter.
4. Настройте параметры порога и размера ядра с помощью соответствующих слайдеров.
5. Установите или снимите флажок "Закрасить область".
6. Нажмите кнопку "Рассчитать площадь", чтобы получить площадь объекта.

## Библиотеки

- Python 3.x
- Tkinter
- OpenCV
