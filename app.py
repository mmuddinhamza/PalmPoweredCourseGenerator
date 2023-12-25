from flask import Flask, render_template, request, session
from flask import render_template_string
import google.generativeai as palm
import markdown
import re
import os

app = Flask(__name__)
app.secret_key = 'aplha-beta-gamma'

def markdown_to_list(markdown_string):
    # Split the string into lines
    lines = markdown_string.split('\n')
    # Use a regular expression to match lines that start with '* '
    list_items = [re.sub(r'\* ', '', line) for line in lines if line.startswith('* ')]
    return list_items



def generate_text(course):
    palm.configure(api_key="YOUR-API-KEY")
    models = [
        m for m in palm.list_models()
        if 'generateText' in m.supported_generation_methods
    ]
    model = models[0].name
    prompts = {
    'approach': f"You are a pedagogy expert and you are designing a learning material for {course} for an undergrad university student. You have to decide the approach to take for learning from this learning material. Please provide a brief description of the approach you would take to study this learning material.",
    'modules': f"You are a pedagogy expert. list the modules you would include in the course {course}. makse sure each module can be explained within 800 characters.",
    }
    completions = {}    
    for key, prompt in prompts.items():
        completion = palm.generate_text(
            model=model,
            prompt=prompt,
            temperature=0.1,
            max_output_tokens=800,
        )
        # Convert the markdown string to a list
        if key == 'modules':
            # Replace bullet points with asterisks
            markdown_string = completion.result.replace('•', '*') if completion.result else ""
            completions[key] = markdown_to_list(markdown_string) if markdown_string else []
        else:
            completions[key] = markdown.markdown(completion.result) if completion.result else ""
    return completions



def generate_module_content(course_name, module_name):
    palm.configure(api_key="AIzaSyAWMEx0ByKdMqvuWQSN4uBGNmvfyX88Fw0")
    models = [
        m for m in palm.list_models()
        if 'generateText' in m.supported_generation_methods
    ]
    model = models[0].name
    module_prompt = f"You are a pedagogy expert and you are designing a learning material for {course_name} for an undergrad university student. You have to decide the content for the module {module_name}. Please provide the content for the module {module_name}."
    module_completion = palm.generate_text(
        model=model,
        prompt=module_prompt,
        temperature=0.1,
        max_output_tokens=800,
    )
    if module_completion.result:
        return markdown.markdown(module_completion.result)
    else:
        return ""



@app.route('/')
def home():
    saved_courses = [filename.replace('_course.html', '') for filename in os.listdir() if filename.endswith('_course.html')]
    return render_template('app.html', saved_courses=saved_courses)



@app.route('/course', methods=['GET', 'POST'])
def course():
    if request.method == 'POST':
        session['course_name'] = request.form['course_name']
        completions = generate_text(session['course_name'])
        rendered = render_template('courses/course1.html', completions=completions)
        with open(f"{session['course_name']}_course.html", 'w') as f:
            f.write(rendered)
        return rendered
    return render_template('courses/course1.html')



@app.route('/module/<module_name>', methods=['GET'])
def module(module_name):
    course_name = session.get('course_name', 'AI course')  # Use 'AI course' as a default value
    content = generate_module_content(course_name, module_name)
    if not content:
        content = "Content for this module is not available"
    return render_template('module.html', content=content, course_name=course_name)



@app.route('/saved_course/<course_name>', methods=['GET'])
def saved_course(course_name):
    try:
        with open(f"{course_name}_course.html", 'r') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "The course content for this course has not been generated yet."



@app.route('/login')
def login():
    return render_template('login.html')



if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
