# This will be my attempt at creating a GUI for the study guide generator using CustomTkinter

# Import Statements
import customtkinter as ctk
import openai
import re
import time

from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.pagesizes import letter

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.styles import ParagraphStyle


# Ease of use insert Variables
API_KEY = "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"
model_engine = "text-davinci-003"
COLLEGE_DIRECTORY = "Output"
list_of_topics = []

# Functions
def full_monty():
    # use-full monty function processes to update the progress bar for the script
    new_api_key()
    progressBar.set(0.1)


    new_model_name()
    progressBar.set(0.2)

    write_to_classes()
    progressBar.set(0.3)

    new_prompts()
    progressBar.set(0.5)

    main_gpt()
    progressBar.set(0.75)

def new_api_key():
    API_KEY = openaiKEY.get()

def new_model_name():
    model_engine = modelEntry.get()

def write_to_classes():
    # Get the text from the inputBox
    text = inputBox.get("1.0", 'end-1c')  # Gets text from the first character to the last character
    # Split the text into lines
    lines = text.splitlines()
    # Open the file in write mode
    with open('Inputs/course_list.txt', 'w') as file:
        # Process each line
        for line in lines:
            line = line.strip()  # Remove leading/trailing whitespace
            if line:  # Ignore empty lines
                # Write the line to the file
                file.write(line + '\n')  # Add a newline character to end of each line


def topic_generator(subject):
    # Set the API key and model
    openai.api_key = API_KEY
    prompt = "Create a list of class 50 unique topics (1-3 words long) commonly found in a college textbook table of contents for " + subject + " course in a bulleted format. Do not duplicate any topics and make sure they are not similar to each other."
    # Make the request to the API
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        temperature=0,
        max_tokens=1200,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    # Get the generated text
    generated_text = response["choices"][0]["text"]

    topic_pattern = re.compile(("(.)\s?(.+)"))
    topics_found = topic_pattern.finditer(generated_text)
    topics = []
    for topic in topics_found:
        topics.append(topic.group(2).strip())

    return topics

def new_prompts():
    openai.api_key = API_KEY
    temperature = 1
    subjects = open('Inputs/course_list.txt', 'r')
    current_subject = ""
    list_of_topics = []
    current_topic = ""

    for line in subjects.readlines():
        time.sleep(5)
        current_subject = repr(line).replace("\\n", "").replace("'", "")
        generated_topics = topic_generator(current_subject)
        list_of_topics.append(generated_topics)

def generate_pdf(text, subject, topic, prompt_index):
    # Create a new PDF with ReportLab

    document = []
    finaltext = text.encode('utf-8')

    # Title
    style_temp = getSampleStyleSheet()
    title_style = ParagraphStyle('Style1',
                                 fontName="Times-Bold",
                                 fontSize=14,
                                 parent=style_temp['Normal'],
                                 alignment=TA_CENTER,
                                 spaceAfter=30)
    document.append(Paragraph(subject + ": " + topic, title_style))
    document.append(Spacer(1, 5))

    code_mode = False
    for line in finaltext.splitlines():
        decoded_line = line.decode()

        char_array = list(decoded_line)
        num_spaces = 0

        for index, value in enumerate(char_array):
            if value == ' ':
                num_spaces = num_spaces + 1
            else:
                break

        font = ''
        size = 12
        spacer = 5

        if code_mode:
            font = "Courier"
            size = 11
            spacer = 3
        else:
            font = "Times"
            size = 12
            spacer = 9

        paragraph_style = ParagraphStyle('Style1',
                                         fontName=font,
                                         fontSize=size,
                                         leftIndent=12 * num_spaces)

        if decoded_line.lower().__contains__("start of code"):
            code_mode = True
            # do it for the comment as well
            font = "Courier"
            size = 11
            spacer = 3
            paragraph_style = ParagraphStyle('Style1',
                                             fontName=font,
                                             fontSize=size,
                                             leftIndent=12 * num_spaces)

        elif decoded_line.lower().__contains__("end of code"):
            code_mode = False

        document.append(Spacer(1, spacer))

        document.append(Paragraph(decoded_line, paragraph_style))

    SUBFOLDER_DIRECTORY = ""
    DOC_TYPE = ""
    match prompt_index:
        case 0:
            SUBFOLDER_DIRECTORY = "PDFs/Notes"
            DOC_TYPE = "Notes"
        case 1:
            SUBFOLDER_DIRECTORY = "PDFs/PracticeProblems1"
            DOC_TYPE = "PracticeProblems1"
        case 2:
            SUBFOLDER_DIRECTORY = "PDFs/PracticeProblems2"
            DOC_TYPE = "PracticeProblems2"
        case 3:
            SUBFOLDER_DIRECTORY = "PDFs/Summary"
            DOC_TYPE = "Summary"

    SimpleDocTemplate(COLLEGE_DIRECTORY + "/" + SUBFOLDER_DIRECTORY + "/" + subject + " - " + topic + "-" + DOC_TYPE + ".pdf", pagesize=letter, rightMargin=50.5,
                      leftMargin=50.5, topMargin=50.5,
                      bottomMargin=50.5).build(document)

def main_gpt():
    # Set the API key and model
    openai.api_key = API_KEY


    current_subject = ""
    current_topic = ""

    subject_pattern = re.compile("(.+):")
    topic_pattern = re.compile("(\"|')([\w\s']+),?('|\")")

    for line in subjects.readlines():
        list_of_topics.clear()

        subjects = subject_pattern.finditer(line)
        for subject in subjects:
            current_subject = subject.group(1)

        topics = topic_pattern.finditer(line)
        for topic in topics:
            list_of_topics.append(topic.group(2))

        NUM_OF_PROMPTS = 4

        #Iterate through each topic in a class
        for index, topic in enumerate(list_of_topics):
            current_topic = list_of_topics[index]

            # Iterate through each prompt
            for prompt_index in range(0, NUM_OF_PROMPTS):

                # Determine Prompt List based on Class
                if "CS" or "STA" in current_subject:
                    prompts = [
                        "Act as if you are a student studying for your final exams. Write very detailed lecture notes on " + current_topic + " for the course " + current_subject + ". Please include coding examples (explain them), key concepts, and definitions within the notes. Be descriptive and thorough in your notes. For every coding example, start with a comment saying Start of Code and end it with a comment saying End of Code. Randomize the formatting.",
                        "Imagine you are a student studying for your final exams. Write a long and detailed list of sample computer science exam problems on " + current_topic + " for the course " + current_subject + " with solutions included. Randomize the formatting.",
                        "In the format of a homework sheet with the title 'Extra Practice Problems', Create a long list of problems on " + current_topic + " for the course " + current_subject + " and for each question first explain how you would go about solving the problem, then solve the problem showing your work. Be sure to solve many problems incorrectly, and next to the solution denote whether it is correct or incorrect by writing '[CORRECT]' or '[INCORRECT]'. If it is incorrect, show the correct answer and explain how to get the correct answer. For every coding example, start with a comment saying 'Start of Code' and end it with a comment saying 'End of Code'. Randomize the formatting.",
                        "Imagine you are a student studying for your final exams. Create a sample topic outline that you would find in a syllabus on " + current_topic + " for the course " + current_subject + " and for each subtopic outline the main things to study and really good problem solving strategies to use on the exam. Randomize the formatting."]
                elif "MATH" in current_subject or "PHYS" in current_subject or "CHEM" in current_subject or "CEE" in current_subject or "ECE" in current_subject or "AE" in current_subject or "ME" in current_subject or "MAP" in current_subject:
                    prompts = [
                        "Act as if you are a student studying for your final exams. Write a very detailed study guide on " + current_topic + " for the course " + current_subject + ". Please include relevant equations, key concepts, definitions, and rules when possible. Be descriptive and thorough in your notes. Randomize the formatting.",
                        "Imagine you are a student studying for your final exams. Write a long and detailed list of sample exam problems on " + current_topic + " for the course " + current_subject + " with solutions included. Randomize the formatting.",
                        "In the format of a homework sheet with the title 'Extra Practice Problems', Create a long list of problems on " + current_topic + " for the course " + current_subject + " and for each question first explain how you would go about solving the problem, then solve the problem showing your work. Be sure to solve many problems incorrectly, and next to the solution denote whether it is correct or incorrect by writing '[CORRECT]' or '[INCORRECT]'. If it is incorrect, show the correct answer and explain how to get the correct answer. Randomize the formatting.",
                        "Imagine you are a student studying for your final exams. Create a sample topic outline that you would find in a syllabus on " + current_topic + " for the course " + current_subject + " and for each subtopic outline the main things to study and really good problem solving strategies to use on the exam. Randomize the formatting."]
                else:
                    prompts = [
                        "Act as if you are a student studying for your final exams. Write very detailed lecture notes on " + current_topic + " for the course " + current_subject + ". Please include relevant key concepts, definitions, rules, and examples within the notes. Be descriptive and thorough in your notes. Randomize the formatting.",
                        "Imagine you are a student studying for your final exams. Write a long and detailed list of sample exam problems on " + current_topic + " for the course " + current_subject + " with solutions included. Randomize the formatting.",
                        "In the format of a homework sheet with the title 'Extra Practice Problems', Create a long list of problems on " + current_topic + " for the course " + current_subject + " and for each question first explain how you would go about solving the problem, then solve the problem showing your work. Be sure to solve many problems incorrectly, and next to the solution denote whether it is correct or incorrect by writing '[CORRECT]' or '[INCORRECT]'. If it is incorrect, show the correct answer and explain how to get the correct answer. Randomize the formatting.",
                        "Imagine you are a student studying for your final exams. Create a sample topic outline that you would find in a syllabus on " + current_topic + " for the course " + current_subject + " and for each subtopic outline the main things to study and really good problem solving strategies to use on the exam. Randomize the formatting."]
                prompt = prompts[prompt_index]

                # Determine Model Parameters based on Prompt
                temperatures = [0.3, 0, 0, 0.05]

                response = openai.Completion.create(engine=model_engine, prompt=prompt, temperature=temperatures[prompt_index], max_tokens=3800, top_p=1, frequency_penalty=0, presence_penalty=0.5)

                # Get the generated text
                generated_text = response["choices"][0]["text"]
                #print(generated_text)
                try:
                    generate_pdf(generated_text, current_subject, current_topic, prompt_index)
                    print("Successfully Generated " + current_subject + " - " + current_topic + ".pdf")
                except:
                    print("An error occurred while creating " + current_subject + " - " + current_topic + ".pdf")

                time.sleep(20)



# CTK basic initialization
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.geometry("500x500")

# configure the grid
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)

# Application Title
title = ctk.CTkLabel(master=root, text='Study Guide Generator by APKA', font=("Lato", 25))
title.grid(row=0, column=0, columnspan=2)

# Upper left Settings Frame
settingsFrame = ctk.CTkFrame(master=root)
settingsFrame.grid(column=0, row=1, padx=10, pady=10, sticky='NSEW')

spacer1 = ctk.CTkLabel(master=settingsFrame, text='  ')
spacer1.pack()

apiLabel = ctk.CTkLabel(master=settingsFrame, text="OpenAI API Key:")
apiLabel.pack(padx=10, pady=0, )

openaiKEY = ctk.CTkEntry(master=settingsFrame, placeholder_text='API Key', width=250)
openaiKEY.insert(0,API_KEY)
openaiKEY.pack(padx=10, pady=0, )

spacer = ctk.CTkLabel(master=settingsFrame, text='  ')
spacer.pack()

modelName = ctk.CTkLabel(master=settingsFrame, text="GPT model used")
modelName.pack(padx=10, pady=0, )

modelEntry = ctk.CTkEntry(master=settingsFrame, placeholder_text="enter model")
modelEntry.insert(0, model_engine)
modelEntry.pack(padx=10, pady=0, )


# Upper Right Settings Frame
inputFrame = ctk.CTkFrame(master=root)
inputFrame.grid(column=1, row=1, padx=10, pady=10, sticky='NSEW')

inputLabel = ctk.CTkLabel(master=inputFrame, text='Enter Course List:')
inputLabel.pack(padx=10, pady=0, )

inputBox = ctk.CTkTextbox(master=inputFrame, wrap='none')
inputBox.insert(0.0, "[Course #] [Class Name]")
inputBox.pack(padx=10, pady=0, )

spacer4 = ctk.CTkLabel(master=inputFrame, text='  ')
spacer4.pack()

submitButton = ctk.CTkButton(master=inputFrame, text='Generate', hover_color='#144272', fg_color='#205295', command= full_monty)
submitButton.pack(padx=10, pady=0, )

# Bottom Progress Frame and Submit Button
progressFrame = ctk.CTkFrame(master=root)
progressFrame.grid(column=0, row=2, columnspan=2, padx=10, pady=10, sticky='NSEW')

spacer5 = ctk.CTkLabel(master=progressFrame, text='  ')
spacer5.pack()

progressBar = ctk.CTkProgressBar(master= progressFrame, width= 300, height= 15, orientation="horizontal")
progressBar.pack()
progressBar.set(0) #Set progress bar to specific value (range 0 to 1).

# Final Loop
root.mainloop()
