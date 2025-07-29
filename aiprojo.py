import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
import datetime
import speech_recognition as sr
import pyttsx3
import os

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)

def speak(text):
    """Converts text to speech."""
    engine.say(text)
    engine.runAndWait()

# Knowledge base of diseases and symptoms
disease_rules = {
    "Common Cold": {
        "symptoms": {"cough", "sneezing", "runny nose"},
        "medication": "Rest, stay hydrated, take vitamin C and antihistamines.",
        "care": "Use humidifiers, drink warm fluids, avoid cold exposure."
    },
    "Flu": {
        "symptoms": {"fever", "headache", "cough", "body ache"},
        "medication": "Antiviral drugs (e.g., Tamiflu), paracetamol for fever.",
        "care": "Bed rest, increase fluid intake, isolate to avoid spreading."
    },
    "Migraine": {
        "symptoms": {"headache", "nausea", "sensitivity to light"},
        "medication": "Pain relievers (ibuprofen), triptans.",
        "care": "Rest in a dark, quiet room, avoid trigger foods."
    },
    "COVID-19": {
        "symptoms": {"fever", "dry cough", "loss of taste", "loss of smell"},
        "medication": "Paracetamol, monitor oxygen levels, consult a doctor.",
        "care": "Isolate, rest, maintain hydration, wear a mask."
    },
    "Malaria": {
        "symptoms": {"fever", "chills", "sweating"},
        "medication": "Antimalarial drugs like chloroquine or artemisinin-based therapy.",
        "care": "Avoid mosquito bites, complete the full medication course."
    }
}

symptom_questions = {
    "fever": "Do you have a fever?",
    "headache": "Do you have a headache?",
    "cough": "Are you coughing?",
    "dry cough": "Do you have a dry cough?",
    "sneezing": "Are you sneezing?",
    "runny nose": "Do you have a runny nose?",
    "body ache": "Do you feel body ache?",
    "nausea": "Do you feel nauseous?",
    "sensitivity to light": "Are you sensitive to light?",
    "loss of taste": "Have you lost your sense of taste?",
    "loss of smell": "Have you lost your sense of smell?",
    "chills": "Are you experiencing chills?",
    "sweating": "Are you sweating excessively?"
}

class MedicalAgentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Medical Diagnostic Agent")
        self.root.geometry("700x550")
        self.root.configure(bg="#e6f2ff")
        self.user_symptoms = set()
        self.symptom_keys = list(symptom_questions.keys())
        self.current_index = 0

        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 14), background="#e6f2ff")
        self.style.configure("TButton", font=("Helvetica", 12), padding=6)

        self.create_widgets()

    def create_widgets(self):
        self.title_label = ttk.Label(self.root, text="AI Medical Diagnostic Agent", font=("Helvetica", 20, "bold"))
        self.title_label.pack(pady=20)

        self.user_label = ttk.Label(self.root, text="Enter your name:")
        self.user_label.pack()

        self.name_entry = ttk.Entry(self.root, font=("Helvetica", 13))
        self.name_entry.pack(pady=8)

        self.start_button = ttk.Button(self.root, text="Start Diagnosis", command=self.start_diagnosis)
        self.start_button.pack(pady=10)

        self.question_label = ttk.Label(self.root, text="", font=("Helvetica", 15), wraplength=600, justify="center")
        self.yes_button = ttk.Button(self.root, text="Yes", command=lambda: self.record_response(True))
        self.no_button = ttk.Button(self.root, text="No", command=lambda: self.record_response(False))
        self.voice_button = ttk.Button(self.root, text="🎤 Answer with Voice", command=self.voice_input)

    def start_diagnosis(self):
        self.user_name = self.name_entry.get().strip()
        if not self.user_name:
            messagebox.showwarning("Input Required", "Please enter your name to begin diagnosis.")
            return
        speak(f"Hello {self.user_name}, let's begin your health check.")
        self.user_label.pack_forget()
        self.name_entry.pack_forget()
        self.start_button.pack_forget()
        self.ask_question()

    def ask_question(self):
        if self.current_index < len(self.symptom_keys):
            key = self.symptom_keys[self.current_index]
            question_text = symptom_questions[key]
            self.question_label.config(text=question_text)
            speak(question_text)
            self.question_label.pack(pady=30)
            self.yes_button.pack(side="left", expand=True, padx=60, pady=20)
            self.no_button.pack(side="right", expand=True, padx=60, pady=20)
            self.voice_button.pack(pady=10)
        else:
            self.show_diagnosis()

    def voice_input(self):
        """Captures voice input and processes it."""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            speak("Please say Yes or No.")
            print("Listening for 'Yes' or 'No'...") # For debugging
            try:
                # Adjust for ambient noise and listen
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=7) # Increased timeout
                text = recognizer.recognize_google(audio).lower()
                print(f"Recognized: {text}") # For debugging

                if "yes" in text:
                    self.record_response(True)
                elif "no" in text:
                    self.record_response(False)
                else:
                    speak("I didn't understand. Please say Yes or No clearly.")
                    messagebox.showwarning("Voice Input", "I didn't understand. Please say 'Yes' or 'No' clearly.")
            except sr.WaitTimeoutError:
                speak("No speech detected. Please try again.")
                messagebox.showwarning("Voice Input", "No speech detected. Please try again.")
            except sr.UnknownValueError:
                speak("Sorry, I could not understand audio. Please try again.")
                messagebox.showwarning("Voice Input", "Sorry, I could not understand audio. Please try again.")
            except sr.RequestError as e:
                speak(f"Could not request results from Google Speech Recognition service; {e}")
                messagebox.showerror("Voice Input Error", f"Could not request results from Google Speech Recognition service; {e}")

    def record_response(self, has_symptom):
        """Records the user's response and moves to the next question."""
        key = self.symptom_keys[self.current_index]
        if has_symptom:
            self.user_symptoms.add(key)
        self.current_index += 1
        self.ask_question()

    def show_diagnosis(self):
        """Displays the diagnosis based on collected symptoms."""
        self.question_label.pack_forget()
        self.yes_button.pack_forget()
        self.no_button.pack_forget()
        self.voice_button.pack_forget()

        diagnosis, match_count = None, 0
        for disease, data in disease_rules.items():
            match = len(data["symptoms"].intersection(self.user_symptoms))
            if match > match_count:
                diagnosis, match_count = disease, match

        self.result_frame = ttk.Frame(self.root)
        self.result_frame.pack(pady=25)

        if diagnosis:
            message = f"{self.user_name}, based on your symptoms, you may have:\n\n"
            message += f"**{diagnosis}**\n\n"
            message += f"**Medication:**\n{disease_rules[diagnosis]['medication']}\n\n"
            message += f"**Care Tips:**\n{disease_rules[diagnosis]['care']}"
            speak(f"{self.user_name}, you may have {diagnosis}. Here is some advice.")
        else:
            message = f"Sorry {self.user_name}, your symptoms don't match a known profile. Please consult a doctor."
            speak("I'm unable to determine a specific illness. Please visit a doctor.")

        self.result_label = ttk.Label(self.result_frame, text=message, wraplength=650, justify="left", font=("Helvetica", 13))
        self.result_label.pack()

        self.export_pdf(diagnosis, message)

    def export_pdf(self, diagnosis, message):
        """Exports the diagnosis report to a PDF file."""
        filename = f"{self.user_name}_diagnosis_report.pdf"
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        save_path = os.path.join(desktop_path, filename)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(0, 10, "AI Medical Diagnostic Report", ln=True, align="C")
        pdf.ln(5)
        pdf.cell(0, 10, f"Name: {self.user_name}", ln=True)
        pdf.cell(0, 10, f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
        pdf.ln(10)

        # Using multi_cell for wrapping text, ensuring robust encoding
        try:
            for line in message.split("\n"):
                pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))
        except Exception as e:
            print(f"Error during PDF content writing: {e}") # Debugging

        try:
            pdf.output(save_path)
            messagebox.showinfo("Success", f"Report saved to your Desktop as {filename}")
            speak("Report saved successfully to your desktop.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {e}")
            speak(f"Failed to save PDF: {e}")

# Run in a GUI-capable environment
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = MedicalAgentApp(root)
        root.mainloop()
    except tk.TclError:
        print("This application requires a GUI environment to run.")