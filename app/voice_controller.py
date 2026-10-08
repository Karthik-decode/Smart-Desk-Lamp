import speech_recognition as sr
import re


# ---------------------------------------------------------
# NORMALIZE SPEECH
# ---------------------------------------------------------
def normalize_command(command):
    """
    Cleans speech-recognition output and fixes
    common transcription errors.
    """

    command = command.lower().strip()

    # Remove punctuation
    command = re.sub(r"[^\w\s]", "", command)

    # Fix repeated letters caused by speech recognition
    command = re.sub(r"p{2,}", "p", command)
    command = re.sub(r"f{2,}", "f", command)
    command = re.sub(r"o{2,}", "o", command)
    command = re.sub(r"l{2,}", "l", command)

    # Common recognition mistakes
    corrections = {
        "lamb": "lamp",
        "lam": "lamp",
        "of": "off",

        "brighness": "brightness",
        "brightnes": "brightness",

        "neutrel": "neutral",
        "neuteral": "neutral",
        "neutrul": "neutral",

        "waram": "warm",

        # Cool-light recognition variations
        "coool": "cool",
        "col": "cool",
        "coollite": "cool light",
        "coollite": "cool light",
        "cool lite": "cool light",
        "cool lights": "cool light",
    }

    words = command.split()

    corrected_words = []

    for word in words:
        corrected_words.append(
            corrections.get(word, word)
        )

    command = " ".join(corrected_words)

    # Handle multi-word corrections
    command = command.replace(
        "cool lights",
        "cool light"
    )

    command = command.replace(
        "cool lite",
        "cool light"
    )

    command = command.replace(
        "coollite",
        "cool light"
    )

    # Remove extra spaces
    command = re.sub(r"\s+", " ", command).strip()

    return command


# ---------------------------------------------------------
# VOICE COMMAND LISTENER
# ---------------------------------------------------------
def listen_for_command():

    recognizer = sr.Recognizer()

    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.5

    try:

        with sr.Microphone() as source:

            print("\n🎤 Listening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=5
            )

        print("🔄 Processing...")

        command = recognizer.recognize_google(audio)

        command = normalize_command(command)

        print(f"🗣️ You said: {command}")

        return command

    except sr.WaitTimeoutError:

        print("⏱️ No speech detected.")
        return ""

    except sr.UnknownValueError:

        print("❌ Could not understand the speech.")
        return ""

    except sr.RequestError:

        print("🌐 Speech recognition service unavailable.")
        return ""

    except Exception as e:

        print(f"⚠️ Error: {e}")
        return ""


# ---------------------------------------------------------
# PROCESS POWER COMMAND
# ---------------------------------------------------------
def process_power(command):

    off_commands = [
        "lamp off",
        "light off",
        "turn off",
        "switch off"
    ]

    on_commands = [
        "lamp on",
        "light on",
        "turn on",
        "switch on"
    ]

    # OFF
    for phrase in off_commands:

        if phrase in command:

            print("🌑 POWER: LAMP OFF")
            return "OFF"

    # ON
    for phrase in on_commands:

        if phrase in command:

            print("💡 POWER: LAMP ON")
            return "ON"

    return None


# ---------------------------------------------------------
# PROCESS CCT COMMAND
# ---------------------------------------------------------
def process_cct(command):

    warm_commands = [
        "warm light",
        "warm lights"
    ]

    neutral_commands = [
        "neutral light",
        "neutral lights"
    ]

    cool_commands = [
        "cool light",
        "cool lights",
        "cool lite",
        "coollite"
    ]

    # WARM
    for phrase in warm_commands:

        if phrase in command:

            print("🔥 CCT: WARM WHITE (~3000K)")
            return "WARM"

    # NEUTRAL
    for phrase in neutral_commands:

        if phrase in command:

            print("⚪ CCT: NEUTRAL WHITE (~3500K)")
            return "NEUTRAL"

    # COOL
    for phrase in cool_commands:

        if phrase in command:

            print("❄️ CCT: COOL WHITE (~4000K)")
            return "COOL"

    return None


# ---------------------------------------------------------
# PROCESS BRIGHTNESS COMMAND
# ---------------------------------------------------------
def process_brightness(command):

    brightness_commands = {

        "low brightness": "LOW",

        "medium brightness": "MEDIUM",

        "high brightness": "HIGH"
    }

    for phrase, level in brightness_commands.items():

        if phrase in command:

            if level == "LOW":

                print("🔅 BRIGHTNESS: LOW (~30%)")

            elif level == "MEDIUM":

                print("🔆 BRIGHTNESS: MEDIUM (~60%)")

            elif level == "HIGH":

                print("💡 BRIGHTNESS: HIGH (100%)")

            return level

    return None


# ---------------------------------------------------------
# PROCESS ALL COMMANDS
# ---------------------------------------------------------
def process_command(command):

    if not command:
        return None

    # POWER
    power_result = process_power(command)

    if power_result:
        return power_result

    # CCT
    cct_result = process_cct(command)

    if cct_result:
        return cct_result

    # BRIGHTNESS
    brightness_result = process_brightness(command)

    if brightness_result:
        return brightness_result

    # UNKNOWN
    print("❓ Command not recognized.")

    print("\nSupported commands:")

    print("\n💡 POWER")
    print("   • Lamp on")
    print("   • Light on")
    print("   • Turn on")
    print("   • Switch on")
    print("   • Lamp off")
    print("   • Light off")
    print("   • Turn off")
    print("   • Switch off")

    print("\n🎨 CCT")
    print("   • Warm light")
    print("   • Neutral light")
    print("   • Cool light")

    print("\n🔆 BRIGHTNESS")
    print("   • Low brightness")
    print("   • Medium brightness")
    print("   • High brightness")

    return None


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():

    print("=" * 60)
    print("          SMART DESK LAMP - VOICE CONTROL")
    print("=" * 60)

    print("\n💡 POWER")
    print("   • Lamp on")
    print("   • Light on")
    print("   • Turn on")
    print("   • Switch on")
    print("   • Lamp off")
    print("   • Light off")
    print("   • Turn off")
    print("   • Switch off")

    print("\n🎨 CCT")
    print("   • Warm light     → ~3000K")
    print("   • Neutral light  → ~3500K")
    print("   • Cool light     → ~4000K")

    print("\n🔆 BRIGHTNESS")
    print("   • Low brightness     → ~30%")
    print("   • Medium brightness  → ~60%")
    print("   • High brightness    → 100%")

    print("\nPress Ctrl+C to stop.\n")

    try:

        while True:

            command = listen_for_command()

            if command:

                process_command(command)

    except KeyboardInterrupt:

        print("\n\n🛑 Voice controller stopped.")
        print("Goodbye!")


# ---------------------------------------------------------
# PROGRAM START
# ---------------------------------------------------------
if __name__ == "__main__":
    main()