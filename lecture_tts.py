import customtkinter
import asyncio
import edge_tts
from threading import Thread
from tkinter import filedialog, messagebox
import os
import tempfile
import shutil
import pygame.mixer
import pygame
import time
import datetime
import mutagen.mp3
from PIL import Image
import webbrowser
import sys

# ІМПОРТ VOICES_DATA
try:
    from voices_data import VOICES_DATA
except ImportError:
    messagebox.showerror("Error", "voices_data.py not found! Please ensure 'voices_data.py' is in the same directory.")
    VOICES_DATA = {} # Запасний порожній словник, щоб програма могла запуститися

if getattr(sys, 'frozen', False):
    # Якщо програма запущена як PyInstaller bundle
    # sys._MEIPASS - це тимчасова директорія, куди PyInstaller розпаковує файли
    ICON_PATH = os.path.join(sys._MEIPASS, "app_icon.ico")
else:
    # Якщо програма запущена як звичайний Python-скрипт (для розробки)
    ICON_PATH = "app_icon.ico"


# --- ГЛОБАЛЬНІ СЛОВНИКИ ДЛЯ ЛОКАЛІЗАЦІЇ ІНТЕРФЕЙСУ ---
translations = {
    "uk": {
        "title": "SpeakFlow",
        "text_input_placeholder": "Введіть текст для озвучення тут...",
        "generate_button": "Згенерувати Голос",
        "status_ready": "Готово до генерації...",
        "status_generating": "Генерація аудіо... Будь ласка, зачекайте.",
        "status_success": "Успіх: Аудіо збережено як {filename}",
        "status_error": "Помилка: {error}. Перевірте інтернет або параметри.",
        "status_save_cancelled": "Збереження скасовано.",
        "select_interface_language_label": "Оберіть мову інтерфейсу:",
        "select_language_voice_label": "Оберіть мову голосу:",
        "select_voice_label": "Оберіть голос:",
        "no_voices": "Немає голосів",
        "save_file_dialog_title": "Зберегти аудіофайл як",
        "status_generated_temp": "Аудіо згенеровано: {filename}. Тепер можна прослухати або зберегти.",
        "play_button": "Прослухати ще раз",
        "save_button": "Зберегти файл",
        "pause_button": "Пауза",
        "resume_button": "Відновити",
        "status_playing": "Відтворення аудіо...",
        "status_paused": "Пауза...",
        "status_no_audio_to_play": "Немає аудіо для відтворення.",
        "status_no_audio_to_save": "Немає аудіо для збереження.",
        "status_saved_success": "Файл успішно збережено як {filename}.",
        "status_save_error": "Помилка збереження файлу: {error}.",
        "gender_male": "чоловічий",
        "gender_female": "жіночий",
        "gender_child": "дитячий",
        "gender_neutral": "нейтральний",
        "status_scrubbing": "Перемотування...",
        "about_button": "Про програму",
        "about_title": "Про програму SpeakFlow",
        "about_content_part1": (
            "Ця програма була створена для озвучення тексту за допомогою Edge TTS.\n"
            "Вона дозволяє перетворювати введений текст на аудіофайли високої якості.\n\n"
            "Розробник: Олег Мельницький\n"
            "Контакти: melnitskiy95@gmail.com\n"
            "Версія програми: 1.0.0\n"
        ),
        "telegram_link_intro": "\n\nБільше програм в телеграм каналі: ",
        "telegram_channel_name": "Mlntsk Soft\n",
        "telegram_link_url": "t.me/mlntsksoft",
        "close_button": "Закрити",

        "thanks_message": "Дякуємо, що користуєтесь нашою програмою!", # <-- ДОДАЙТЕ
        "donate_prompt_part1": "Якщо вона була для вас корисною, ви можете ", # <-- ДОДАЙТЕ
        "donate_link_text": "підтримати наш проєкт донатом.", # <-- ДОДАЙТЕ
        "donate_prompt_part2": "Будь-яка сума має значення і допомагає розвивати програму далі.", # <-- ДОДАЙТЕ
        "paypal_link_url": "https://www.paypal.com/donate/?hosted_button_id=WWSDL9ZDYZBCS" # <-- ДОДАЙТЕ
    },
    "en": {
        "title": "SpeakFlow",
        "text_input_placeholder": "Enter text for speech here...",
        "generate_button": "Generate Voice",
        "status_ready": "Ready for generation...",
        "status_generating": "Generating audio... Please wait.",
        "status_success": "Success: Audio saved as {filename}",
        "status_error": "Error: {error}. Check internet or parameters.",
        "status_save_cancelled": "Save cancelled.",
        "select_interface_language_label": "Select interface language:",
        "select_language_voice_label": "Select voice language:",
        "select_voice_label": "Select voice:",
        "no_voices": "No voices",
        "save_file_dialog_title": "Save audio file as",
        "status_generated_temp": "Audio generated: {filename}. You can now play or save it.",
        "play_button": "Play Again",
        "save_button": "Save File",
        "pause_button": "Pause",
        "resume_button": "Resume",
        "status_playing": "Playing audio...",
        "status_paused": "Paused...",
        "status_no_audio_to_play": "No audio to play.",
        "status_no_audio_to_save": "No audio to save.",
        "status_saved_success": "File successfully saved as {filename}.",
        "status_save_error": "File save error: {error}.",
        "gender_male": "male",
        "gender_female": "female",
        "gender_child": "child",
        "gender_neutral": "neutral",
        "status_scrubbing": "Scrubbing...",
        "about_button": "About",
        "about_title": "About SpeakFlow",
        "about_content_part1": ( # Розбито на частини
            "This application was created for text-to-speech conversion using Edge TTS.\n"
            "It allows you to convert entered text into high-quality audio files.\n\n"
            "Developer: Oleg Melnytskyi\n"
            "Contact: melnitskiy95@gmail.com\n"
            "Program Version: 1.0.0\n"
        ),
        "telegram_link_intro": "\n\nMore programs on Telegram channel: ",
        "telegram_channel_name": "Mlntsk Soft",
        "telegram_link_url": "t.me/mlntsksoft",
        "close_button": "Close",
        "thanks_message": "Thank you for using our program!", # <-- ДОДАЙТЕ
        "donate_prompt_part1": "If it was useful to you, you can ", # <-- ДОДАЙТЕ
        "donate_link_text": "support our project with a donation.", # <-- ДОДАЙТЕ
        "donate_prompt_part2": "Any amount matters and helps to develop the program further.", # <-- ДОДАЙТЕ
        "paypal_link_url": "https://www.paypal.com/donate/?hosted_button_id=WWSDL9ZDYZBCS" # <-- ДОДАЙТЕ
    },
    "de": {
        "title": "SpeakFlow",
        "text_input_placeholder": "Geben Sie hier Text zur Sprachausgabe ein...",
        "generate_button": "Stimme generieren",
        "status_ready": "Bereit zur Generierung...",
        "status_generating": "Audio wird generiert... Bitte warten Sie.",
        "status_success": "Erfolg: Audio gespeichert als {filename}",
        "status_error": "Fehler: {error}. Überprüfen Sie Internet oder Parameter.",
        "status_save_cancelled": "Speichern abgebrochen.",
        "select_interface_language_label": "Oberfläche-Sprache wählen:",
        "select_language_voice_label": "Stimme Sprache wählen:",
        "select_voice_label": "Stimme wählen:",
        "no_voices": "Keine Stimmen",
        "save_file_dialog_title": "Audiodatei speichern als",
        "status_generated_temp": "Audio generiert: {filename}. Sie können es jetzt abspielen oder speichern.",
        "play_button": "Nochmal abspielen",
        "save_button": "Datei speichern",
        "pause_button": "Pause",
        "resume_button": "Fortsetzen",
        "status_playing": "Audio wird abgespielt...",
        "status_paused": "Pausiert...",
        "status_no_audio_to_play": "Kein Audio zum Abspielen vorhanden.",
        "status_no_audio_to_save": "Kein Audio zum Speichern vorhanden.",
        "status_saved_success": "Datei erfolgreich gespeichert als {filename}.",
        "status_save_error": "Fehler beim Speichern der Datei: {error}.",
        "gender_male": "männlich",
        "gender_female": "weiblich",
        "gender_child": "Kind",
        "gender_neutral": "neutral",
        "status_scrubbing": "Vorspulen...",
        "about_button": "Über",
        "about_title": "Über SpeakFlow",
        "about_content_part1": ( # Розбито на частини
            "Diese Anwendung wurde zur Text-zu-Sprache-Umwandlung mit Edge TTS erstellt.\n"
            "Sie ermöglicht die Umwandlung von eingegebenem Text in hochwertige Audiodateien.\n\n"
            "Entwickler: Oleg Melnytskyi\n"
            "Kontakt: melnitskiy95@gmail.com\n"
            "Programmversion: 1.0.0\n"
        ),
        "telegram_link_intro": "\n\nWeitere Programme auf Telegram-Kanal: ",
        "telegram_channel_name": "Mlntsk Soft",
        "telegram_link_url": "t.me/mlntsksoft",
        "close_button": "Schließen",
        "thanks_message": "Vielen Dank, dass Sie unser Programm nutzen!", # <-- ДОДАЙТЕ
        "donate_prompt_part1": "Wenn es Ihnen nützlich war, können Sie unser Projekt ", # <-- ДОДАЙТЕ
        "donate_link_text": "mit einer Spende unterstützen.", # <-- ДОДАЙТЕ
        "donate_prompt_part2": "Jeder Betrag zählt und hilft, das Programm weiterzuentwickeln.", # <-- ДОДАЙТЕ
        "paypal_link_url": "https://www.paypal.com/donate/?hosted_button_id=WWSDL9ZDYZBCS" # <-- ДОДАЙТЕ
    }
}

# Початкова мова інтерфейсу
current_language = "en"

# функція для отримання перекладу
def get_translation(key):
    return translations[current_language].get(key, key)

# словник для відображення мов інтерфейсу
translations_language_map = {
    "uk": "Українська",
    "en": "English",
    "de": "Deutsch"
}

def format_time(seconds):
    """Форматує секунди в рядок MM:SS."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:01d}:{seconds:02d}" # :01d для хв 02d для секунд

#перетворення кодів мов у мови озвучення (відображає у Combobox)
language_names = {
    "en": "English", "de": "Deutsch", "uk": "Українська", "ru": "Русский",
    "pl": "Polski", "fr": "Français", "it": "Italiano", "es": "Español",
    "pt": "Português"
}

# Змінна для зберігання шляху до тимч аудіофайлу
temp_audio_filepath = None
# Нова змінна для відстеження стану паузи
is_paused = False
# Відстежує, чи потрібно моніторити закінчення музики
is_music_monitoring_active = False
# Нові змінні для прогрес-бару
audio_duration = 0 # Загальна тривалість аудіофайлу в секундах
playback_update_job = None # Для відстеження циклу оновлення слайдера


current_playback_offset = 0.0 #Відстежує зсув відтворення в секундах


was_playing_before_scrub = False #Відстежує чи грало аудіо до перетягування
all_voices_detailed = {}


#---ФУНКЦІЇ ОБРОБНИКИ ПОДІЙ

def change_interface_language(new_lang_display_name):
    global current_language

    old_placeholder = get_translation("text_input_placeholder")

    for code, name in translations_language_map.items():
        if name == new_lang_display_name:
            current_language = code
            break

    app.title(get_translation("title"))
    interface_language_label.configure(text=get_translation("select_interface_language_label"))
    language_dropdown_label.configure(text=get_translation("select_language_voice_label"))
    voice_combobox_label.configure(text=get_translation("select_voice_label"))
    generate_button.configure(text=get_translation("generate_button"))
    status_label.configure(text=get_translation("status_ready"))

    # ДОДАНО ДЛЯ ПЕРЕКЛАДУ НОВИХ КНОПОК
    play_button.configure(text=get_translation("play_button"))
    save_button.configure(text=get_translation("save_button"))

    # Оновлення тексту кнопки паузи/відновлення
    if is_paused:
        pause_resume_button.configure(text=get_translation("resume_button"))
    else:
        pause_resume_button.configure(text=get_translation("pause_button"))

    current_text_in_field = text_input_field.get("1.0", "end-1c")
    if current_text_in_field == old_placeholder or current_text_in_field.strip() == "":
        text_input_field.delete("1.0", "end")
        text_input_field.insert("1.0", get_translation("text_input_placeholder"))

    current_voice_lang_display = language_dropdown.get()
    on_language_selected(current_voice_lang_display)

    about_button.configure(text=get_translation("about_button")) # Оновлення тексту кнопки "Про програму"


def on_language_selected(choice):
    global all_voices_detailed
    global voice_combobox

    # "English" -> "en"
    selected_lang_code = None
    for code, name in language_names.items():
        if name == choice:
            selected_lang_code = code
            break

    if not selected_lang_code:
        print(f"[ERROR] Не вдалося знайти код мови для '{choice}'")
        voice_combobox.configure(values=[get_translation("no_voices")])
        voice_combobox.set(get_translation("no_voices"))
        return

    all_voices_detailed = {}
    voice_display_names = []

    # голоси вибраної мови з VOICES_DATA
    # get(selected_lang_code, []) щоб уникнути помилки, якщо мови немає
    voices_for_current_lang = VOICES_DATA.get(selected_lang_code, []) # *** ВИПРАВЛЕНО: VOICES_DATA замість voices_data ***

    # Сортування голосів за name_display
    voices_for_current_lang.sort(key=lambda x: x["name_display"])

    for voice in voices_for_current_lang:
        name_display = voice["name_display"]
        voice_id = voice["id"]
        gender = voice.get("gender")
        age = voice.get("age")

        gender_text = ""
        if gender == "Male":
            gender_text = get_translation("gender_male")
        elif gender == "Female":
            gender_text = get_translation("gender_female")
        elif gender == "Neutral":
            gender_text = get_translation("gender_neutral")

        age_text = ""
        if age == "Child":
            age_text = get_translation("gender_child")

        # Форматування назви для відображення
        formatted_name = name_display
        details = []
        if gender_text:
            details.append(gender_text)
        if age_text:
            details.append(age_text)

        if details:
            formatted_name += f" ({', '.join(details)})"

        voice_display_names.append(formatted_name)
        all_voices_detailed[formatted_name] = voice_id

    voice_combobox.configure(values=voice_display_names)
    if voice_display_names:
        voice_combobox.set(voice_display_names[0]) # Перший голос за замовчуванням
    else:
        voice_combobox.set(get_translation("no_voices")) # Якщо голосів немає

# === ФУНКЦІЯ ВІКНА "ПРО ПРОГРАМУ" ===
def open_about_window():
    about_window = customtkinter.CTkToplevel(app)
    about_window.title(get_translation("about_title"))
    about_window.geometry("500x400") # Розмір вікна, як ви вказали
    about_window.resizable(False, False)
    about_window.grab_set()
    about_window.transient(app)

    #  CTkTextbox для можливості вставляти теги та посилання
    about_text_widget = customtkinter.CTkTextbox(
        about_window,
        wrap="word", # Перенос слів
        font=customtkinter.CTkFont(family="Roboto", size=14),
        text_color="white",
        fg_color="#2E2E2E", # Фон, як у головного вікна
        border_width=0,
        padx=20,
        pady=20
    )
    about_text_widget.pack(expand=True, fill="both")

    # Вставляємо основний контент
    about_text_widget.insert("end", get_translation("about_content_part1"))

    # Вставляємо вступний текст для посилання на Telegram
    about_text_widget.insert("end", get_translation("telegram_link_intro"))

    # Вставляємо текст посилання і застосовуємо тег 'link'
    link_text = get_translation("telegram_channel_name")
    about_text_widget.insert("end", link_text, "link")



    about_text_widget.insert("end", "\n")  # Додаємо два нові рядки для відступу
    about_text_widget.insert("end", get_translation("thanks_message"))
    about_text_widget.insert("end", "\n")  # Ще два нові рядки

    about_text_widget.insert("end", get_translation("donate_prompt_part1"))
    donate_link_text = get_translation("donate_link_text")
    about_text_widget.insert("end", donate_link_text, "donate_link")  # Використовуємо новий тег 'donate_link'
    about_text_widget.insert("end", " ")  # Додаємо пробіл після посилання на донат


    about_text_widget.insert("end", "\n")  # Новий рядок
    about_text_widget.insert("end", get_translation("donate_prompt_part2"))

    # Конфігуруємо новий тег 'donate_link' (можна скопіювати з тегу 'link')
    about_text_widget.tag_config("donate_link", foreground="#2196F3", underline=True)
    about_text_widget.tag_bind("donate_link", "<Button-1>",
                               lambda e: open_link_in_browser(get_translation('paypal_link_url')))
    about_text_widget.tag_bind("donate_link", "<Enter>", lambda e: about_text_widget.configure(cursor="hand2"))
    about_text_widget.tag_bind("donate_link", "<Leave>", lambda e: about_text_widget.configure(cursor=""))

    # Конфігур тег 'link' для синього кольору та підкреслення
    about_text_widget.tag_config("link", foreground="#2196F3", underline=True)
    # Прив'язуємо клік до тегу 'link'
    about_text_widget.tag_bind("link", "<Button-1>",
                               lambda e: open_link_in_browser(get_translation('telegram_link_url')))
    about_text_widget.tag_bind("link", "<Enter>", lambda e: about_text_widget.configure(cursor="hand2"))
    about_text_widget.tag_bind("link", "<Leave>", lambda e: about_text_widget.configure(cursor=""))

    # Робимо текстове поле нередагованим
    about_text_widget.configure(state="disabled")

    # Кнопка закриття у вікні "Про програму"
    close_button = customtkinter.CTkButton(
        about_window,
        text=get_translation("close_button"),
        command=about_window.destroy,
        fg_color="#2980B9",
        hover_color="#2471A3",
        text_color="white",
        corner_radius=8
    )
    close_button.pack(pady=10)

    about_window.focus_force()

# Нова функція для відкриття посилань у браузері
def open_link_in_browser(url):
    try:
        # Додаємо "https://" якщо його немає, для коректного відкриття
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webbrowser.open_new_tab(url)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open link: {e}\nPlease check your browser installation.")


async def generate_audio_logic(text_to_speak, selected_voice, output_file_name):
    print(
        f"[DEBUG] generate_audio_logic: Text='{text_to_speak}', Voice='{selected_voice}', Output='{output_file_name}'")
    try:
        if not text_to_speak.strip():
            print("[DEBUG] Text to speak is empty or just whitespace.")
            raise ValueError("Текст для озвучення порожній.")

        communicate = edge_tts.Communicate(text_to_speak, selected_voice, rate="+0%")
        await communicate.save(output_file_name)
        print(f"[DEBUG] Audio saved successfully to {output_file_name}")
        return get_translation("status_generated_temp").format(filename=os.path.basename(output_file_name))
    except Exception as e:
        print(f"[ERROR] Error during audio generation: {e}")
        return get_translation("status_error").format(error=e)


async def update_status_after_generation_for_play(text, voice, output_temp_file):
    print("[DEBUG] update_status_after_generation_for_play started.")
    result_message = await generate_audio_logic(text, voice, output_temp_file)

    app.after(0, lambda: status_label.configure(text=result_message))
    print(f"[DEBUG] Result message: {result_message}")

    expected_prefix = get_translation("status_generated_temp").split("{")[0]
    print(f"[DEBUG] Expected prefix: '{expected_prefix}'")
    print(f"[DEBUG] Result message starts with prefix: {result_message.startswith(expected_prefix)}")

    global audio_duration

    if result_message.startswith(expected_prefix):
        app.after(0, lambda: play_button.configure(state="normal"))
        app.after(0, lambda: save_button.configure(state="normal"))
        app.after(0, lambda: pause_resume_button.configure(state="normal"))
        print("[DEBUG] Buttons enabled.")

        # --- НОВИЙ КОД ДЛЯ ПРОГРЕС-БАРУ ПІСЛЯ ГЕНЕРАЦІЇ ---
        if os.path.exists(output_temp_file):
            try:
                audio = mutagen.mp3.MP3(output_temp_file)
                audio_duration = audio.info.length  # тривалість в секундах
                playback_slider.configure(to=audio_duration)  # максимальне значення слайдера
                playback_slider.set(0)  # Скидаємо слайдер на початок
                current_time_label.configure(text="0:00")  # Скидаємо мітку часу
                total_time_label.configure(text=format_time(audio_duration))  # мітка загального часу
                playback_slider.configure(state="normal")  # Вмик. слайдер
                print(f"[DEBUG] Audio duration: {audio_duration} seconds.")
            except Exception as e:
                print(f"[ERROR] Could not get audio duration or configure slider: {e}")
                audio_duration = 0  # Скидає на 0 якщо є помилки
                playback_slider.configure(state="disabled")  # Викл. слайдер
        else:
            audio_duration = 0
            playback_slider.configure(state="disabled")

        app.after(0, play_audio)
        print("[DEBUG] Attempting to play audio automatically.")
    else:
        app.after(0, lambda: play_button.configure(state="disabled"))
        app.after(0, lambda: save_button.configure(state="disabled"))
        app.after(0, lambda: pause_resume_button.configure(state="disabled"))
        # --- ВИМИКАЄМО ПРОГРЕС-БАР У ВИПАДКУ ПОМИЛКИ ГЕНЕРАЦІЇ ---
        app.after(0, lambda: playback_slider.configure(state="disabled"))
        app.after(0, lambda: current_time_label.configure(text="0:00"))
        app.after(0, lambda: total_time_label.configure(text="0:00"))
        audio_duration = 0
        # --- КІНЕЦЬ ---
        print("[DEBUG] Buttons disabled due to generation error.")


def start_generation_process():
    global temp_audio_filepath, is_paused, is_music_monitoring_active
    print("[DEBUG] start_generation_process called.")


    is_music_monitoring_active = False
    if pygame.mixer.music.get_busy() or is_paused:
        print("[DEBUG] Stopping pygame mixer before new generation.")
        pygame.mixer.music.stop()
        try:
            # вивантажуємо файл з мікшера Pygame
            pygame.mixer.music.unload()
            print("[DEBUG] Pygame mixer unloaded audio.")
        except pygame.error as e:
            # якщо музика не була завантажена
            print(f"[DEBUG] Pygame mixer unload error (likely no audio loaded): {e}")

        is_paused = False
        pause_resume_button.configure(text=get_translation("pause_button"), image=pause_icon_image,
                                      state="disabled")

    play_button.configure(state="disabled")
    save_button.configure(state="disabled")
    pause_resume_button.configure(state="disabled")
    is_paused = False
    pause_resume_button.configure(text=get_translation("pause_button"),
                                  image=pause_icon_image)

    status_label.configure(text=get_translation("status_generating"))
    print("[DEBUG] Status set to 'Generating'.")

    user_text = text_input_field.get("1.0", "end-1c")
    # Перевіряємо, чи текст є стандартним заповнювачем
    if user_text.strip() == get_translation("text_input_placeholder").strip() or not user_text.strip():
        status_label.configure(
            text=get_translation("status_error").format(error="Текст для озвучення порожній або є заповнювачем."))
        print("[ERROR] Generation cancelled: Text input is empty or placeholder.")
        return  # Важливо: вийти з функції, якщо текст недійсний

    chosen_voice = voice_combobox.get()
    chosen_voice_display_name = voice_combobox.get()  # Зберігаємо відображувану назву
    # Отримуємо технічний ID голосу зі словника all_voices_detailed
    # Якщо з якоїсь причини ID не знайдено (хоча не повинно), повертаємо відображувану назву
    # як запасний варіант (хоча це призведе до тієї ж помилки "Invalid voice")
    chosen_voice_id = all_voices_detailed.get(chosen_voice_display_name, chosen_voice_display_name)

    print(
        f"[DEBUG] Chosen voice display name: '{chosen_voice_display_name}', Actual voice ID to use: '{chosen_voice_id}'")
    print(f"[DEBUG] User Text: '{user_text}', Chosen Voice: '{chosen_voice}'")

    # Зберігаємо попередній шлях до файлу для видалення
    old_temp_audio_filepath_for_cleanup = temp_audio_filepath

    # --- ВИПРАВЛЕНО ТУТ: ТЕПЕР ЗАВЖДИ СТВОРЮЄМО УНІКАЛЬНЕ ІМ'Я ---
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    temp_audio_filepath = os.path.join(tempfile.gettempdir(), f"temp_generated_audio_{timestamp}.mp3")  # Це тепер завжди унікальне ім'я
    print(f"[DEBUG] New temp audio filepath set to: {temp_audio_filepath}")

    # Додатковий крок: спробувати видалити попередній тимчасовий файл.
    # Видаляємо затримку, оскільки unload вже має звільнити. Якщо це все ще проблема,
    # можливо, потрібен більший time.sleep після unload() вище.
    if old_temp_audio_filepath_for_cleanup and os.path.exists(old_temp_audio_filepath_for_cleanup):
        try:
            os.remove(old_temp_audio_filepath_for_cleanup)
            print(f"[DEBUG] Deleted old temp file: {old_temp_audio_filepath_for_cleanup}")
        except OSError as e:
            print(
                f"[WARNING] Could not delete old temp file {old_temp_audio_filepath_for_cleanup}: {e}. It might still be in use.")
            pass  # Не перериваємо генерацію, оскільки новий файл має унікальне ім'я

    print("[DEBUG] Starting generation thread.")
    thread = Thread(target=lambda: asyncio.run(
        update_status_after_generation_for_play(user_text, chosen_voice_id, temp_audio_filepath)
        # <--- ТУТ ЗМІНИЛИ chosen_voice НА chosen_voice_id
    ))
    thread.start()


def play_audio():
    global is_paused, is_music_monitoring_active, playback_update_job, current_playback_offset


    if not (temp_audio_filepath and os.path.exists(temp_audio_filepath)):
        status_label.configure(text=get_translation("status_no_audio_to_play"))
        pause_resume_button.configure(state="disabled")
        is_paused = False
        print("[DEBUG] No audio file found for playback.")
        is_music_monitoring_active = False
        playback_slider.configure(state="disabled")
        return

    if is_paused:
        toggle_pause_resume()

        return

    if playback_update_job:
        app.after_cancel(playback_update_job)
        playback_update_job = None
        print("[DEBUG] Cancelled previous playback update job.")

    if pygame.mixer.music.get_busy():
        print("[DEBUG] Audio already playing. Stopping before new playback.")
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.unload()
            print("[DEBUG] Pygame mixer unloaded audio before new playback.")
        except pygame.error as e:
            print(f"[DEBUG] Pygame mixer unload error (likely no audio loaded before new playback): {e}")

    try:
        pygame.mixer.music.load(temp_audio_filepath)
        pygame.mixer.music.play(start=0)
        current_playback_offset = 0.0


        is_paused = False
        status_label.configure(text=get_translation("status_playing"))

        pause_resume_button.configure(
            text=get_translation("pause_button"),
            image=pause_icon_image,
            state="normal"
        )

        playback_slider.configure(state="normal")
        playback_update_job = app.after(100, update_playback_progress)

        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
        if not is_music_monitoring_active:
            is_music_monitoring_active = True
            app.after(100, check_music_end)
            print("[DEBUG] Started music end monitoring loop.")

    except pygame.error as e:
        # обробка помилок
        print(f"[ERROR] Pygame playback error: {e}")



def on_slider_press(event):
    global is_paused, was_playing_before_scrub, playback_update_job
    print("[DEBUG] Slider pressed.")

    if not (temp_audio_filepath and os.path.exists(temp_audio_filepath)):
        print("[DEBUG] No audio file to scrub.")
        return

    # Якщо музика грає, ставимо на паузу і запам'ятовуємо, що грала
    if pygame.mixer.music.get_busy() and not is_paused:
        was_playing_before_scrub = True
        pygame.mixer.music.pause()
        is_paused = True
        pause_resume_button.configure(text=get_translation("resume_button"), image=play_icon_image)
        status_label.configure(text=get_translation("status_scrubbing"))
        if playback_update_job:  # Зупиняємо автоматичне оновлення під час перетягування
            app.after_cancel(playback_update_job)
            playback_update_job = None
        print("[DEBUG] Audio paused for scrubbing.")
    elif is_paused:  # Якщо вже на паузі, просто запам'ятовуємо, що не грало
        was_playing_before_scrub = False
        status_label.configure(text=get_translation("status_scrubbing"))
        if playback_update_job:
            app.after_cancel(playback_update_job)
            playback_update_job = None
        print("[DEBUG] Audio was already paused, now scrubbing.")
    else:  # Якщо взагалі нічого не грає
        was_playing_before_scrub = False
        status_label.configure(text=get_translation("status_scrubbing"))
        if playback_update_job:
            app.after_cancel(playback_update_job)
            playback_update_job = None
        print("[DEBUG] Audio not playing, now scrubbing.")


def on_slider_drag(event):
    # Ця функція просто оновлює мітку часу під час перетягування
    # без фактичної перемотки Pygame
    if not (temp_audio_filepath and os.path.exists(temp_audio_filepath)):
        return

    # Отримуємо значення слайдера, перетворюємо в секунди
    current_scrub_time = playback_slider.get()  # .get() повертає поточне значення слайдера
    current_time_label.configure(text=format_time(current_scrub_time))
    # print(f"[DEBUG] Scrubbing: {format_time(current_scrub_time)}") # Забагато виводу в консоль


def on_slider_release(event):
    global was_playing_before_scrub, current_playback_offset
    print("[DEBUG] Slider released.")

    if not (temp_audio_filepath and os.path.exists(temp_audio_filepath)):
        print("[DEBUG] No audio file to release scrub on.")
        status_label.configure(text=get_translation("status_ready"))
        return

    # Викликаємо основну функцію перемотки з новим значенням
    seek_audio(playback_slider.get())  # Передаємо поточне значення слайдера

    # Після перемотки, якщо відтворення повинно було відновитись
    # Це вже обробляється всередині seek_audio, але тут ми можемо
    # скинути флаг і переконатись в коректному стані статусу
    if was_playing_before_scrub:
        # seek_audio вже запустить play() і оновиться статус
        pass
    else:
        # Якщо до перетягування не грало, то після seek_audio воно залишиться на паузі
        status_label.configure(text=get_translation("status_paused"))
        pause_resume_button.configure(text=get_translation("resume_button"), image=play_icon_image)

    was_playing_before_scrub = False  # Скидаємо прапорець
    print(f"[DEBUG] Slider released. Audio at: {format_time(current_playback_offset)}")


def seek_audio(value):
    global is_paused, is_music_monitoring_active, playback_update_job, current_playback_offset, was_playing_before_scrub
    seek_time = float(value)

    if not (temp_audio_filepath and os.path.exists(temp_audio_filepath)):
        print("[DEBUG] Cannot seek: No audio file.")
        status_label.configure(text=get_translation("status_no_audio_to_play"))
        return

    if pygame.mixer.music.get_busy() or is_paused:
        pygame.mixer.music.stop()
        if playback_update_job:
            app.after_cancel(playback_update_job)
            playback_update_job = None
        is_paused = False
        pause_resume_button.configure(text=get_translation("pause_button"), image=pause_icon_image, state="normal")
        is_music_monitoring_active = False

    try:
        pygame.mixer.music.unload()
        pygame.mixer.music.load(temp_audio_filepath)
        pygame.mixer.music.play(start=seek_time)

        current_playback_offset = seek_time

        status_label.configure(text=get_translation("status_playing"))

        playback_slider.set(seek_time)
        current_time_label.configure(text=format_time(seek_time))

        if not is_music_monitoring_active:
            is_music_monitoring_active = True
            app.after(100, check_music_end)

        if was_playing_before_scrub:
            playback_update_job = app.after(100, update_playback_progress)

        elif is_paused:
            pygame.mixer.music.pause()
            is_paused = True
            status_label.configure(text=get_translation("status_paused"))
            pause_resume_button.configure(text=get_translation("resume_button"), image=play_icon_image)

        else:
            playback_update_job = app.after(100, update_playback_progress)

    except pygame.error as e:
        # ... (існуючий код обробки помилок) ...
        print(f"[ERROR] Pygame seek/playback error: {e}")

def update_playback_progress():
    global playback_update_job, audio_duration, current_playback_offset

    if not is_music_monitoring_active:
        if playback_update_job:
            app.after_cancel(playback_update_job)
            playback_update_job = None
        return

    if pygame.mixer.music.get_busy():
        time_since_last_start_ms = pygame.mixer.music.get_pos()
        current_absolute_seconds = current_playback_offset + (time_since_last_start_ms / 1000.0)

        if current_absolute_seconds > audio_duration:
            current_absolute_seconds = audio_duration

        if audio_duration > 0:
            playback_slider.set(current_absolute_seconds)
            current_time_label.configure(text=format_time(current_absolute_seconds))


    playback_update_job = app.after(100, update_playback_progress)


def toggle_pause_resume():
    global is_paused, is_music_monitoring_active, current_playback_offset, playback_update_job


    if not (temp_audio_filepath and os.path.exists(temp_audio_filepath)):
        print("[DEBUG] No music to pause/resume.")
        return

    if is_paused:

        # Важливо: Зупиняємо поточний стан і перезавантажуємо, щоб скинути get_pos()
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        # Перезавантажуємо файл, оскільки play(start=...) може вимагати цього
        try:
            pygame.mixer.music.unload()
            pygame.mixer.music.load(temp_audio_filepath)
        except pygame.error as e:
            print(f"[ERROR] Error reloading audio for resume: {e}")
            status_label.configure(text=f"Помилка відновлення: {e}")
            return

        # Відтворення з збереженої абсолютної позиції
        pygame.mixer.music.play(start=current_playback_offset)

        is_paused = False
        pause_resume_button.configure(text=get_translation("pause_button"), image=pause_icon_image)
        status_label.configure(text=get_translation("status_playing"))

        # Після play(start=...), get_pos() буде 0.
        # current_playback_offset вже містить правильну абсолютну позицію.
        # update_playback_progress тепер буде коректно додавати get_pos() до current_playback_offset.
        if playback_update_job:
            app.after_cancel(playback_update_job)
        playback_update_job = app.after(100, update_playback_progress)
        print(
            f"[DEBUG] TogglePauseResume End (Resumed by re-play) - is_paused: {is_paused}, current_playback_offset: {current_playback_offset:.2f}")

    else:

        # Зберігаємо поточну абсолютну позицію перед паузою
        current_playback_offset = current_playback_offset + (pygame.mixer.music.get_pos() / 1000.0)

        pygame.mixer.music.pause()
        is_paused = True
        pause_resume_button.configure(text=get_translation("resume_button"), image=play_icon_image)
        status_label.configure(text=get_translation("status_paused"))

        # Зупиняємо автоматичне оновлення слайдера
        if playback_update_job:
            app.after_cancel(playback_update_job)
            playback_update_job = None


    # Цей блок відповідає за моніторинг кінця музики і залишається без змін
    if not is_music_monitoring_active:
        is_music_monitoring_active = True
        app.after(100, check_music_end)


def save_generated_audio():
    global is_paused, is_music_monitoring_active
    print("[DEBUG] save_generated_audio called.")
    if not temp_audio_filepath or not os.path.exists(temp_audio_filepath):
        status_label.configure(text=get_translation("status_no_audio_to_save"))
        print("[DEBUG] No audio file to save.")
        return

    output_file_path = filedialog.asksaveasfilename(
        title=get_translation("save_file_dialog_title"),
        defaultextension=".mp3",
        filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
        initialfile="generated_audio.mp3"
    )

    if not output_file_path:
        status_label.configure(text=get_translation("status_save_cancelled"))
        print("[DEBUG] Save operation cancelled by user.")
        return

    try:
        # Зупиняємо відтворення перед збереженням файлу
        if pygame.mixer.music.get_busy() or is_paused:
            print("[DEBUG] Stopping pygame mixer before saving file.")
            pygame.mixer.music.stop()
            # Обов'язково вивантажуємо файл з мікшера Pygame
            try:
                pygame.mixer.music.unload()
                print("[DEBUG] Pygame mixer unloaded audio before save.")
            except pygame.error as e:
                print(f"[DEBUG] Pygame mixer unload error (likely no audio loaded before save): {e}")

            is_paused = False  # Скидаємо стан паузи після зупинки
            pause_resume_button.configure(text=get_translation("pause_button"), image=pause_icon_image,
                                          state="disabled")
            # Зупиняємо моніторинг, бо музика зупинена
            is_music_monitoring_active = False
            print("[DEBUG] Stopped music end monitoring loop due to save operation.")

        shutil.copy(temp_audio_filepath, output_file_path)
        status_label.configure(
            text=get_translation("status_saved_success").format(filename=os.path.basename(output_file_path)))
        # play_button.configure(state="disabled") # НЕ вимикаємо кнопку "Прослухати ще раз"!
        # save_button.configure(state="disabled") # Можна залишити активованою, якщо можна зберігати повторно
        pause_resume_button.configure(state="disabled")  # Вимикаємо кнопку паузи/відновлення

        # Переконаємося, що кнопка "Прослухати ще раз" активна після збереження,
        # оскільки тимчасовий файл все ще існує для відтворення.
        if temp_audio_filepath and os.path.exists(temp_audio_filepath):
            play_button.configure(state="normal")

        print(f"[DEBUG] File successfully saved to: {output_file_path}")

    except Exception as e:
        status_label.configure(text=get_translation("status_save_error").format(error=e))
        print(f"[ERROR] Error saving file: {e}")

# Функція для перевірки закінчення музики
def check_music_end():
    global is_paused, is_music_monitoring_active, playback_update_job, current_playback_offset  # Додайте current_playback_offset

    if not is_music_monitoring_active:
        if playback_update_job:
            app.after_cancel(playback_update_job)
            playback_update_job = None
        return

    if not pygame.mixer.music.get_busy() and not is_paused:
        print("[DEBUG] Music playback ended or stopped, resetting play/pause state.")

        if temp_audio_filepath and os.path.exists(temp_audio_filepath):
            play_button.configure(state="normal")
        else:
            play_button.configure(state="disabled")

        pause_resume_button.configure(state="disabled")
        status_label.configure(text=get_translation("status_ready"))
        is_paused = False
        pause_resume_button.configure(text=get_translation("pause_button"),
                                      image=pause_icon_image)

        playback_slider.set(0)
        current_time_label.configure(text="0:00")
        current_playback_offset = 0.0  # НОВИЙ РЯДОК: Скидаємо зсув на 0 при завершенні відтворення
        playback_slider.configure(state="normal")  # Залишаємо слайдер активним

        if playback_update_job:
            app.after_cancel(playback_update_job)
            playback_update_job = None

        is_music_monitoring_active = False
        print("[DEBUG] Stopped music end monitoring loop (music finished).")
        return

    app.after(100, check_music_end)


def clear_placeholder(event):
    # Отримуємо поточний текст з поля
    current_text = text_input_field.get("1.0", "end-1c") # "end-1c" щоб не включати символ нового рядка в кінці

    # Перевіряємо, чи поточний текст відповідає плейсхолдеру
    if current_text.strip() == get_translation("text_input_placeholder").strip():
        text_input_field.delete("1.0", "end") # Видаляємо весь текст
        # Змінюємо колір тексту на білий, якщо він був сірим (для плейсхолдера)
        text_input_field.configure(text_color="white") # Важливо, якщо плейсхолдер був іншого кольору


# --- СТВОРЕННЯ ВІКНА ТА ЕЛЕМЕНТІВ ІНТЕРФЕЙСУ ---
customtkinter.set_appearance_mode("dark")  #темний режим
app = customtkinter.CTk()
app.geometry("780x750") # Розмір вікна
app.title("SpeakFlow")
app.configure(fg_color="#1A2D40")

app.iconbitmap(ICON_PATH)

# === СТВОРЕННЯ КНОПКИ "ПРО ПРОГРАМУ" ===
about_button = customtkinter.CTkButton(
    app, # <--- Батьківський елемент - головне вікно "app"
    text=get_translation("about_button"),
    command=open_about_window,
    width=80,
    height=25,
    fg_color="#1A2C3E",     #колір фону #1A2C3E
    hover_color="#2C3E50",  #колір коли наводиться курсор
    text_color="white",
    corner_radius=10,
    font=customtkinter.CTkFont(family="Roboto", size=15, weight="bold")
)
about_button.pack(side="bottom", anchor="ne", padx=20, pady=20)

# Ініціалізація Pygame Mixer (важливо робити до використання)
pygame.mixer.init()

# Завантаження іконок
try:
    generate_icon_image = customtkinter.CTkImage(Image.open(os.path.join("icons", "generate_icon.png")), size=(24, 24))
    play_icon_image = customtkinter.CTkImage(Image.open(os.path.join("icons", "play_icon.png")), size=(24, 24))
    save_icon_image = customtkinter.CTkImage(Image.open(os.path.join("icons", "save_icon.png")), size=(24, 24))
    pause_icon_image = customtkinter.CTkImage(Image.open(os.path.join("icons", "pause_icon.png")), size=(24, 24))
    resume_icon_image = customtkinter.CTkImage(Image.open(os.path.join("icons", "play_icon.png")),
                                               size=(24, 24))  # Можна використовувати ту ж іконку play для resume
except FileNotFoundError:
    print("Помилка: Не знайдено файли іконок в папці 'icons'. Кнопки будуть без іконок.")
    generate_icon_image = None
    play_icon_image = None
    save_icon_image = None
    pause_icon_image = None
    resume_icon_image = None

# Лейбл для вибору мови інтерфейсу
interface_language_label = customtkinter.CTkLabel(app,
                                                  text=get_translation("select_interface_language_label"),
                                                  text_color="white") # <--- ЗМІНА ТУТ
interface_language_label.pack(pady=(10, 0))

# Вибір мови інтерфейсу
interface_language_dropdown = customtkinter.CTkComboBox(
    app,
    values=list(translations_language_map.values()),
    width=200,
    height=35, # ВИСОТА КОМБОБОКС
    command=change_interface_language,
    fg_color="#34495E",
    text_color="white",
    border_width=2,
    border_color="#006080",
    button_color="#006080",
    button_hover_color="#008FD0",
    dropdown_fg_color="#34495E",
    dropdown_hover_color="#283F5B",
    dropdown_text_color="white",
    corner_radius=10,
    font=customtkinter.CTkFont(family="Roboto", size=15) # РОЗМІР ШРИФТУ
)

interface_language_dropdown.set(translations_language_map[current_language])
interface_language_dropdown.pack(pady=(0, 10))

# Текстове поле
text_input_field = customtkinter.CTkTextbox(app,
                                            width=750,
                                            height=300,
                                            fg_color="#34495E",      # <--- КОЛІР ФОНУ: Темно-сірий
                                            text_color="white",      # <--- КОЛІР ТЕКСТУ: Білий
                                            border_width=2,          # <--- ТОВЩИНА РАМКИ
                                            border_color="#006080",
                                            corner_radius=10,        # <--- ЗАОКРУГЛЕННЯ КУТІВ
                                            wrap="word",             # Переносити слова на новий рядок
                                            font=customtkinter.CTkFont(family="Open Sans", size=17)) # <--- НОВИЙ ШРИФТ та РОЗМІР
text_input_field.pack(pady=20)
text_input_field.bind("<Control-v>", lambda event: text_input_field.event_generate("<<Paste>>"))

text_input_field.insert("1.0", get_translation("text_input_placeholder"))
text_input_field.bind("<Button-1>", clear_placeholder)  # Прив'язуємо до натискання лівої кнопки миші
text_input_field.bind("<FocusIn>", clear_placeholder)   # Прив'язуємо до отримання фокуса (наприклад, клавішею Tab)

# Фрейм для розміщення вибору мови та голосу в одному рядку
voice_selection_frame = customtkinter.CTkFrame(app, fg_color="transparent")
voice_selection_frame.pack(pady=10)

# Лейбл для вибору мови голосу (внутри фрейма)
language_dropdown_label = customtkinter.CTkLabel(voice_selection_frame,
                                                 text=get_translation("select_language_voice_label"),
                                                 text_color="white")
language_dropdown_label.pack(side="left", padx=(0, 5))

# Вибір мови озвучення (внутри фрейма)

# Отримуємо коди мов, які мають голоси з VOICES_DATA (наприклад, ['en', 'de', 'uk', ...])
supported_voice_language_codes = list(VOICES_DATA.keys()) # *** ВИПРАВЛЕНО ТУТ ***

# Перетворюємо ці коди мов у зручні для відображення назви (наприклад English,Deutsch, Українська)
display_language_names_for_voice = [language_names[code] for code in supported_voice_language_codes]

language_dropdown = customtkinter.CTkComboBox(voice_selection_frame,
                                              values=display_language_names_for_voice,
                                              width=150,
                                              height=35,
                                              command=on_language_selected,
                                              fg_color="#34495E",
                                              text_color="white",
                                              border_width=2,
                                              border_color="#006080",
                                              button_color="#006080",
                                              button_hover_color="#008FD0",
                                              dropdown_fg_color="#34495E",
                                              dropdown_hover_color="#283F5B",
                                              dropdown_text_color="white",
                                              corner_radius=10,
                                              font=customtkinter.CTkFont(family="Roboto", size=15))

language_dropdown.set(language_names["de"])
# Встановлюємо початкову мову для відображення у дропдауні
initial_voice_language_display = language_names["de"] # Або інша мова, яку ви хочете за замовчуванням
language_dropdown.pack(side="left", padx=(0, 20))

# Лейбл для вибору голосу
voice_combobox_label = customtkinter.CTkLabel(voice_selection_frame,
                                              text=get_translation("select_voice_label"),
                                              text_color="white") # <--- ЗМІНА ТУТ
voice_combobox_label.pack(side="left", padx=(0, 5))



# Вибір голосу

voice_combobox = customtkinter.CTkComboBox(voice_selection_frame,
                                           values=[""],
                                           width=150,
                                           height=35, # <--- ЗБІЛЬШУЄМО ВИСОТУ
                                           fg_color="#34495E",
                                           text_color="white",
                                           border_width=2,
                                           border_color="#006080",
                                           button_color="#006080",
                                           button_hover_color="#008FD0",
                                           dropdown_fg_color="#34495E",
                                           dropdown_hover_color="#283F5B",
                                           dropdown_text_color="white",
                                           corner_radius=10,
                                           font=customtkinter.CTkFont(family="Roboto", size=15)) # <--- ЗБІЛЬШУЄМО РОЗМІР ШРИФТУ
voice_combobox.pack(side="left", padx=(0, 0))

on_language_selected(language_names["de"])

# Фрейм для кнопок в одному рядку
action_buttons_frame = customtkinter.CTkFrame(app, fg_color="transparent")
action_buttons_frame.pack(pady=20)

# Кнопка генерації
generate_button = customtkinter.CTkButton(
    action_buttons_frame,
    text=get_translation("generate_button"),
    command=start_generation_process,
    image=generate_icon_image,
    compound="left",
    width=150,                     # <--- ЗБІЛЬШУЄМО ШИРИНУ
    height=40,                     # <--- ЗБІЛЬШУЄМО ВИСОТУ
    fg_color="#006080",            # <--- КОЛІР КНОПКИ (синій, наприклад, Bootstrap primary)
    hover_color="#218838",         # <--- КОЛІР ПРИ НАВЕДЕННІ
    text_color="white",            # <--- КОЛІР ТЕКСТУ НА КНОПЦІ
    corner_radius=10,              # <--- ЗАОКРУГЛЕННЯ КУТІВ
    font=customtkinter.CTkFont(family="Roboto", size=14, weight="bold") # <--- НОВИЙ ЖИРНИЙ ШРИФТ
)
generate_button.pack(side="left", padx=10)

# Кнопка "Прослухати ще раз"
play_button = customtkinter.CTkButton(
    action_buttons_frame,
    text=get_translation("play_button"),
    command=play_audio,
    state="disabled",
    image=play_icon_image,
    compound="left",
    width=150,                     # <--- ЗБІЛЬШУЄМО ШИРИНУ
    height=40,                     # <--- ЗБІЛЬШУЄМО ВИСОТУ
    fg_color="#006080",            # <--- КОЛІР КНОПКИ (синій, наприклад, Bootstrap primary)
    hover_color="#218838",         # <--- КОЛІР ПРИ НАВЕДЕННІ
    text_color="white",            # <--- КОЛІР ТЕКСТУ
    corner_radius=10,              # <--- ЗАОКРУГЛЕННЯ КУТІВ
    font=customtkinter.CTkFont(family="Roboto", size=14, weight="bold") # <--- НОВИЙ ЖИРНИЙ ШРИФТ
)
play_button.pack(side="left", padx=10)

# НОВА КНОПКА "ПАУЗА/ВІДНОВИТИ"
pause_resume_button = customtkinter.CTkButton(
    action_buttons_frame,
    text=get_translation("pause_button"),
    command=toggle_pause_resume,
    state="disabled",
    image=pause_icon_image,
    compound="left",
    width=150,                     # <--- ЗБІЛЬШУЄМО ШИРИНУ
    height=40,                     # <--- ЗБІЛЬШУЄМО ВИСОТУ
    fg_color="#006080",            # <--- КОЛІР КНОПКИ (синій, наприклад, Bootstrap primary)
    hover_color="#218838",         # <--- КОЛІР ПРИ НАВЕДЕННІ
    text_color="white",            # <--- КОЛІР ТЕКСТУ (чорний, щоб добре читався на жовтому)
    corner_radius=10,              # <--- ЗАОКРУГЛЕННЯ КУТІВ
    font=customtkinter.CTkFont(family="Roboto", size=14, weight="bold") # <--- НОВИЙ ЖИРНИЙ ШРИФТ
)
pause_resume_button.pack(side="left", padx=10)

# Кнопка "Зберегти файл"
save_button = customtkinter.CTkButton(
    action_buttons_frame,
    text=get_translation("save_button"),
    command=save_generated_audio,
    state="disabled",
    image=save_icon_image,
    compound="left",
    width=150,                     # <--- ЗБІЛЬШУЄМО ШИРИНУ
    height=40,                     # <--- ЗБІЛЬШУЄМО ВИСОТУ
    fg_color="#006080",            # <--- КОЛІР КНОПКИ (синій, наприклад, Bootstrap primary)
    hover_color="#218838",         # <--- КОЛІР ПРИ НАВЕДЕННІ
    text_color="white",            # <--- КОЛІР ТЕКСТУ
    corner_radius=10,              # <--- ЗАОКРУГЛЕННЯ КУТІВ
    font=customtkinter.CTkFont(family="Roboto", size=14, weight="bold") # <--- НОВИЙ ЖИРНИЙ ШРИФТ
)
save_button.pack(side="left", padx=10)

# Фрейм для прогрес-бару та часових міток
progress_frame = customtkinter.CTkFrame(app, fg_color="transparent")
progress_frame.pack(pady=(0, 10)) # Невеликий відступ зверху, більший знизу

# Мітка для поточного часу
current_time_label = customtkinter.CTkLabel(progress_frame,
                                            text="0:00",
                                            text_color="white") # <--- ЗМІНА ТУТ
current_time_label.pack(side="left", padx=(0, 5))

# Слайдер прогресу
playback_slider = customtkinter.CTkSlider(
    progress_frame,
    from_=0,
    to=100,
    number_of_steps=1000,
    width=600,                 # <--- ШИРИНА СЛАЙДЕРА (можете коригувати)
    height=15,                 # <--- ВИСОТА/ТОВЩИНА СЛАЙДЕРА
    fg_color="#283F5B",        # <--- КОЛІР ФОНУ СЛАЙДЕРА (темно-сірий, трохи світліший за фон вікна)
    progress_color="#007bff",  # <--- КОЛІР ЗАПОВНЕННЯ/ПРОГРЕСУ (яскравий неоново-зелений)
    button_color="#007bff",    # <--- КОЛІР РУЧКИ СЛАЙДЕРА
    button_hover_color="#0056b3", # <--- КОЛІР РУЧКИ ПРИ НАВЕДЕННІ
    corner_radius=5            # <--- ЗАОКРУГЛЕННЯ КУТІВ
)
playback_slider.set(0)
playback_slider.pack(side="left", fill="x", expand=True, padx=(10, 10))
playback_slider.configure(state="disabled")

# Прив'язки подій для скрубінгу
playback_slider.bind("<ButtonPress-1>", on_slider_press) # Натискання миші
playback_slider.bind("<B1-Motion>", on_slider_drag)     # Перетягування миші
playback_slider.bind("<ButtonRelease-1>", on_slider_release) # Відпускання миші

# Мітка для загального часу
total_time_label = customtkinter.CTkLabel(progress_frame,
                                          text="0:00",
                                          text_color="white") # <--- ЗМІНА ТУТ
total_time_label.pack(side="left", padx=(5, 0))

# Статус-лейбл
status_label = customtkinter.CTkLabel(app,
                                      text=get_translation("status_ready"),
                                      text_color="white") # <--- ЗМІНА ТУТ
status_label.pack(pady=10)

# --- Функція очищення тимчасових файлів при закритті програми ---
def on_closing():
    global temp_audio_filepath
    print("[DEBUG] Application closing. Attempting to clean up temp files.")

    # Зупинити відтворення Pygame, якщо воно активне
    if pygame.mixer.music.get_busy() or is_paused:
        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.unload()
            print("[DEBUG] Pygame mixer unloaded on close.")
        except pygame.error as e:
            print(f"[DEBUG] Pygame mixer unload error on close (likely no audio loaded): {e}")

    # НОВЕ МІСЦЕ ДЛЯ pygame.mixer.quit() - ПЕРЕД ВИДАЛЕННЯМ ФАЙЛІВ
    pygame.mixer.quit()  #вивантажує Pygame mixer, щоб звільнити ресурси
    print("[DEBUG] Pygame mixer quit.")


    # Видалити поточний тимчасовий файл (який міг бути останній згенерований/відтворений)
    if temp_audio_filepath and os.path.exists(temp_audio_filepath):
        try:
            # Даєм системі трохи часу відпустити файл, якщо він щойно використовувався
            time.sleep(0.1)
            os.remove(temp_audio_filepath)
            print(f"[DEBUG] Deleted current temp audio file: {temp_audio_filepath}")
        except OSError as e:
            print(f"[ERROR] Failed to delete current temp audio file on close: {e}")

    # Видалити всі старі тимчасові файли (з timestamp) з системної тимчасової директорії
    temp_dir_for_cleanup = tempfile.gettempdir()
    for file_name in os.listdir(temp_dir_for_cleanup):
        if file_name.startswith("temp_generated_audio_") and file_name.endswith(".mp3"):
            try:
                os.remove(os.path.join(temp_dir_for_cleanup, file_name))
                print(f"[DEBUG] Deleted old temp audio file: {os.path.join(temp_dir_for_cleanup, file_name)}")
            except OSError as e:
                print(f"[ERROR] Failed to delete old temp audio file {file_name} on close: {e}")

    app.destroy()  # Закриває головне вікно програми


# Привязує функцію on_closing до події закриття вікна (наприклад, кнопка X)
app.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()