<h1> ВАРКТ 1 курс 1 сем </h1>

Проект по ВАРКТ.

Команда IVALTEK. 

Миссия PRI-MAT 01


<h2> Инструкция: </h2>

Чтобы составить автопилот, загрузите проект и запустите GUI.py

В диалоговом окне выбирите нужную версию автопилота

Введите стартовые параметры соответсвующие выбранной версии автопилота

Нажмите создать автопилот

- Если ничего не произошло, посмотрите отчет об ошибке, вероятнее всего вы составили траекторию которая не приводит к вашей целевой траектории
  - Меняйте стартовые параметры в окне ввода, чтобы ваша траектория соответсвовала целевой траектории. Чтобы понять как именно менять стартовые параметры обратите внимание на сообщение об ошибке, там указана высота апоцентра низкой околоземной орбиты после маневра с вашими данными и целевая высота низкой околоземной орбиты. Меняя стартовые параметры, нужно максимально сбилизить эти высоты.
  - Если вы хотите лететь по любой вашей траектории, то выбирите `свободный режим`.
- Если возникла другая ошибка - изучите сообщение об ошибке

Когда все условия будет выполнены произойдет расчет траектории, построится ее трёхмерная модель и создастся файл автопилота в папке проекта

- Чтобы изменить целевую траекторию измените `PHASE_3_GOAL` в `main_func.py` - высота низкой околоземной орбиты в метрах
- Чтобы изменить точность соответсвия вашей траектории целевой измените `EPSILON` в `main_func.py` - допустимый интервал в метрах

далее перенесите файл автопилота в [KSP DIRECTORY]/Ships/Script/

запустите КСП

Подождите запуска автопилота
