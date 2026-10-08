# ---------------------------------------------------------
# SMART DESK LAMP - LIGHTING CONTROLLER
# CCT + BRIGHTNESS VOICE CONTROL
# ---------------------------------------------------------

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
    # Examples:
    # brightneess -> brightness (handled below if needed)
    # coolll -> cool
    command = re.sub(r"(.)\1{2,}", r"\1", command)

    # Common speech-recognition mistakes
    corrections = {
        "brighness": "brightness",
        "brightnes": "brightness",
        "brighter": "brightness",
        "brite": "bright",
        "neutrel": "neutral",
        "neuteral": "neutral",
        "neutrul": "neutral",
        "coool": "cool",
        "waram": "warm",
    }

    words = command.split()

    corrected_words = []

    for word in words:
        corrected_words.append(
            corrections.get(word, word)
        )

    command = " ".join(corrected_words)

    # Remove extra spaces
    command = re.sub(r"\s+", " ", command).strip()

    return command


# ---------------------------------------------------------
# LISTEN FOR VOICE COMMAND
# ---------------------------------------------------------
def listen_for_command():

    recognizer = sr.Recognizer()

    # Recognition settings
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.phrase_threshold = 0.3
    recognizer.non_speaking_duration = 0.5

    try:

        with sr.Microphone() as source:

            print("\n🎤 Listening...")

            # Adjust for background noise
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

        # Convert speech to text
        command = recognizer.recognize_google(audio)

        # Normalize command
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
# PROCESS CCT COMMAND
# ---------------------------------------------------------
def process_cct(command):

    cct_commands = {

        "warm light": "WARM",

        "neutral light": "NEUTRAL",

        "cool light": "COOL"
    }

    for phrase, mode in cct_commands.items():

        if phrase in command:

            if mode == "WARM":
                print("🔥 CCT: WARM WHITE (~3000K)")

            elif mode == "NEUTRAL":
                print("⚪ CCT: NEUTRAL WHITE (~3500K)")

            elif mode == "COOL":
                print("❄️ CCT: COOL WHITE (~4000K)")

            return mode

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
# PROCESS LIGHTING COMMAND
# ---------------------------------------------------------
def process_command(command):

    if not command:
        return None

    # Try CCT first
    cct_result = process_cct(command)

    if cct_result:
        return cct_result

    # Try brightness
    brightness_result = process_brightness(command)

    if brightness_result:
        return brightness_result

    # Unknown command
    print("❓ Lighting command not recognized.")

    print("\nUse one of these commands:")

    print("\n🎨 CCT")
    print("   • Warm light")
    print("   • Neutral light")
    print("   • Cool light")

    print("\n💡 BRIGHTNESS")
    print("   • Low brightness")
    print("   • Medium brightness")
    print("   • High brightness")

    return None


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():

    print("=" * 55)
    print("       SMART DESK LAMP - LIGHTING CONTROL")
    print("=" * 55)

    print("\n🎨 CCT COMMANDS")
    print("   • Warm light     → ~3000K")
    print("   • Neutral light  → ~3500K")
    print("   • Cool light     → ~4000K")

    print("\n💡 BRIGHTNESS COMMANDS")
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

        print("\n\n🛑 Lighting controller stopped.")
        print("Goodbye!")


# ---------------------------------------------------------
# PROGRAM START
# ---------------------------------------------------------
if __name__ == "__main__":
    main()