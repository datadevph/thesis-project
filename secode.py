import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import nltk
from collections import Counter
import requests
import re
import io
import textwrap




st.set_page_config(
    # page_title="SECODE",
    layout="wide",
)


# Define the title with HTML formatting to highlight "SEO" with styles
title_html = """
    <span style="font-weight: bold; font-size: 3em; color: #4CAF50;">S</span>
    <span style="font-weight: bold; font-size: 3em; color: #FF9800;">E</span><span style="font-size: 3em;">C</span>
    <span style="font-weight: bold; font-size: 3em; color: #009688;">O</span><span style="font-size: 3em;">D</span>
    <span style="font-size: 3em;">E</span> <span style="font-size: 1.5em;"><Analyze, Learn & Code/></span>
"""

# Display the title using Markdown
st.markdown(title_html, unsafe_allow_html=True)

# URL input bar
url_input = st.text_input("Enter domain (e.g., synology.com):")

# Preprocess the input URL
if url_input.strip() != "":
    if not re.match(r"^https?://", url_input):
        url_input = "https://" + url_input

if st.button("Analyze"):
    
    # Fetch HTML content from the URL
    response = requests.get(url_input)
    if response.status_code == 200:
        html_content = response.text
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        # Extract HTML, CSS, and JavaScript code
        html_code = soup.prettify()
        css_code = "\n".join([style.string or "" for style in soup.find_all('style')])
        js_code = "\n".join([script.string or "" for script in soup.find_all('script')])
        # Extract domain name
        domain_name = re.search(r"https?://(?:www\.)?(.*?)\.", url_input).group(1)

        about_us = soup.find('meta', attrs={'name': 'description'})
        about_us_content = about_us.get('content') if about_us else None

    else:
        st.error("Failed to fetch content from the provided URL.")
        html_code = css_code = js_code = domain_name = None
else:
    html_code = css_code = js_code = domain_name = None

# Menu
selected = option_menu(
    menu_title=None,
    options=["Technology", "Analysis", "Learn", "Practice", "Resources"],
    icons=["code-slash", "bar-chart", "lightbulb", "braces", "search"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# Display selected tab content
if selected == "Technology":
    if html_code is not None:
        with st.expander("HTML Structure"):
            st.code(html_code, language='html')
        with st.expander("CSS Styles"):
            st.code(css_code, language='css')
        with st.expander("Javascript Code"):
            st.code(js_code, language='javascript')
    else:
        st.warning("Click Analyze button to fetch content.")




if selected == "Analysis":
    if html_code is not None:
        # Parse HTML content
        soup = BeautifulSoup(html_code, 'html.parser')

        # Find all header tags
        header_tags = soup.find_all(re.compile('^h[1-6]$'))
        # Count occurrences of each header tag
        header_counts = {}
        for tag in header_tags:
            tag_name = tag.name
            if tag_name in header_counts:
                header_counts[tag_name] += 1
            else:
                header_counts[tag_name] = 1

        # Calculate percentage of each technology
        total_length = len(html_code) + len(css_code) + len(js_code)
        html_percent = len(html_code) / total_length * 100
        css_percent = len(css_code) / total_length * 100
        js_percent = len(js_code) / total_length * 100

        # Extract bi-grams
        text = soup.get_text()
        tokens = nltk.word_tokenize(text)
        bi_grams = list(nltk.bigrams(tokens))
        bi_gram_counts = Counter(bi_grams)

        # Extract links with 'https://'
        links_with_https = [link['href'] for link in soup.find_all('a', href=True) if link['href'].startswith('https://')]

        # Limit bi-grams and links to 10
        top_bi_grams = bi_gram_counts.most_common(10)
        top_links = links_with_https[:7]

        # Create a single image containing all the analysis results
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))  # Adjust the figure size here

        # Header tags bar graph
        if header_counts:
            labels = list(header_counts.keys())
            counts = list(header_counts.values())
            axes[0, 0].bar(labels, counts, color='skyblue')
            axes[0, 0].set_xlabel('Header Tags')
            axes[0, 0].set_ylabel('Count')
            axes[0, 0].set_xticklabels(labels, rotation=45)
            axes[0, 0].set_title('Header Tags Analysis')
            axes[0, 0].margins(0.2)  # Add more margin to the graph

        # Technology pie chart
        labels = ['HTML', 'CSS', 'JavaScript']
        sizes = [html_percent, css_percent, js_percent]
        explode = (0.1, 0.1, 0.1)  # explode 1st slice
        axes[0, 1].pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
        axes[0, 1].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        axes[0, 1].set_title('Technology Analysis')
        axes[0, 1].margins(0.2)  # Add more margin to the graph

        # Top bi-grams bar graph
        bi_gram_labels = [str(gram) for gram, count in top_bi_grams]
        bi_gram_counts = [count for gram, count in top_bi_grams]
        axes[1, 0].barh(bi_gram_labels[::-1], bi_gram_counts[::-1], color='lightgreen')  # Reversed to display most common bi-grams at the top
        axes[1, 0].set_xlabel('Count')
        axes[1, 0].set_ylabel('Bi-gram')
        axes[1, 0].set_title('Top Bi-grams')
        axes[1, 0].margins(0.2)  # Add more margin to the graph

        # Top links table
        axes[1, 1].axis('off')  # Hide axes for the table
        table_data = [["Top Links:"]] + [[link] for link in top_links]
        table = axes[1, 1].table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.5]*5)
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(2, 2.1)

        # Extract meta description
        meta_description = soup.find('meta', attrs={'name': 'description'})
        about_us_content = meta_description['content'] if meta_description else None

        # Limit meta description to one sentence
        if about_us_content:
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', about_us_content)
            about_us_content = sentences[0]

        # Add title and paragraph
        plt.figtext(0.02, 0.98, f"SEO Analysis on {url_input}", fontsize=14, fontweight='bold', color='black', ha ='left', va='top', backgroundcolor='white', alpha=0.5)
        plt.figtext(0.02, 0.95, f"About {domain_name.capitalize()}:\n{about_us_content if about_us_content else 'No meta description available.'}", fontsize=10, color='black', ha ='left', va='top', backgroundcolor='white', alpha=0.5)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust the top padding

        # Save the composite image
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)

        # Display the image
        st.image(img_data, use_column_width=True, )

        # Add download button to download the image
        st.download_button(label="Download Image", data=img_data, file_name='analysis_results.png', mime='image/png')

    else:
        st.warning("Click Analyze button for analysis.")







elif selected == "Learn":
     st.markdown("""
        ## Welcome to the Learn Menu! 🎉
         Expand the tab to start learning.""")
  
     with st.expander("HTML"):
          st.markdown("""
            HTML (Hypertext Markup Language) is the standard markup language for creating web pages and web applications. 
            Here are some basic examples of HTML elements and structures:

            1. **Basic HTML Structure:**
                    This example shows the basic structure of an HTML document, including the `<!DOCTYPE html>` declaration, `<html>`, `<head>`, and `<body>` tags. It also includes a heading (`<h1>`) and a paragraph (`<p>`).
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>My First Web Page</title>
            </head>
            <body>
                <h1>Hello, World!</h1>
                <p>This is a paragraph.</p>
            </body>
            </html>
            ```

            2. **Link with Anchor Tag:**
                    An anchor (`<a>`) tag is used to create hyperlinks. This example demonstrates how to create a link to an external website.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Link Example</title>
            </head>
            <body>
                <a href="https://www.example.com">Visit Example Website</a>
            </body>
            </html>
            ```

            3. **Image Tag:**
                    The image (`<img>`) tag is used to embed images in an HTML document. This example shows how to display an image on a webpage.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Image Example</title>
            </head>
            <body>
                <img src="image.jpg" alt="Image">
            </body>
            </html>
            ```

            4. **Ordered List:**
                    An ordered list (`<ol>`) is used to create a numbered list of items. This example demonstrates how to create a simple ordered list with three items.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Ordered List Example</title>
            </head>
            <body>
                <ol>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </ol>
            </body>
            </html>
            ```

            5. **Form with Input Fields:**
                    Forms are used to collect user input. This example shows how to create a basic form with input fields for the user's first name and last name.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Form Example</title>
            </head>
            <body>
                <form>
                    <label for="fname">First Name:</label><br>
                    <input type="text" id="fname" name="fname"><br>
                    <label for="lname">Last Name:</label><br>
                    <input type="text" id="lname" name="lname"><br><br>
                    <input type="submit" value="Submit">
                </form>
            </body>
            </html>
            ```

            6. **Table Structure:**
                    Tables (`<table>`, `<tr>`, `<th>`, `<td>`) are used to display data in rows and columns. This example demonstrates how to create a simple table with two columns (Name and Age) and two rows of data.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Table Example</title>
            </head>
            <body>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Age</th>
                    </tr>
                    <tr>
                        <td>John</td>
                        <td>25</td>
                    </tr>
                    <tr>
                        <td>Jane</td>
                        <td>30</td>
                    </tr>
                </table>
            </body>
            </html>
            ```

            7. **Division (Div):**
                    Divisions (`<div>`) are used to group elements together for styling or other purposes.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Div Example</title>
            </head>
            <body>
                <div>
                    <p>This paragraph is inside a div.</p>
                    <p>Another paragraph inside the same div.</p>
                </div>
            </body>
            </html>
            ```

            8. **Unordered List:**
                    An unordered list (`<ul>`) is used to create a bulleted list of items.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Unordered List Example</title>
            </head>
            <body>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                    <li>Item 3</li>
                </ul>
            </body>
            </html>
            ```

            9. **Header Tags (h2, h3, etc.):**
                    HTML provides header tags (`<h2>`, `<h3>`, etc.) for creating different levels of headings.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Header Tags Example</title>
            </head>
            <body>
                <h2>Subheading</h2>
                <h3>Sub-subheading</h3>
            </body>
            </html>
            ```

            10. **Bold and Italic Text:**
                    Use `<b>` for bold and `<i>` for italic text.
            ```html
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Bold and Italic Text Example</title>
            </head>
            <body>
                <p>This is <b>bold</b> and this is <i>italic</i>.</p>
            </body>
            </html>
            ```

            HTML provides the structure of a web page, consisting of elements like headings, paragraphs, images, links, forms, etc.
        """)
     with st.expander("CSS"):
         st.markdown("""
            CSS (Cascading Style Sheets) is a style sheet language used for describing the presentation of a document written in HTML. 
            Here are some basic examples of CSS styling:

            1. **Styling Text:**
                CSS can be used to change the appearance of text elements. This example shows how to change the color and font size of an `<h1>` element.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        h1 {
                            color: navy;
                            font-size: 24px;
                        }
                    </style>
                </head>
                <body>
                    <h1>Hello, World!</h1>
                </body>
                </html>
                ```

            2. **Styling Background:**
                Background colors can be applied to the entire webpage or specific elements. This example demonstrates how to set the background color of the `<body>` element.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        body {
                            background-color: lightblue;
                        }
                    </style>
                </head>
                <body>
                    <h1>Hello, World!</h1>
                </body>
                </html>
                ```

            3. **Box Model:**
                The box model is a fundamental concept in CSS that describes how elements are laid out on a webpage. This example demonstrates how to set the width, margin, padding, and border of a container (`<div>`) element.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        .container {
                            width: 80%;
                            margin: 0 auto;
                            padding: 20px;
                            border: 1px solid #ccc;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <p>This is a container with styled box model properties.</p>
                    </div>
                </body>
                </html>
                ```

            4. **Floating Elements:**
                Floating elements (`float: left/right;`) can be used to create layouts where elements appear side by side. This example demonstrates how to float two elements to the left and right within a container.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        .float-left {
                            float: left;
                            width: 50%;
                        }
                        .float-right {
                            float: right;
                            width: 50%;
                        }
                    </style>
                </head>
                <body>
                    <div class="float-left">
                        <p>This element is floated to the left.</p>
                    </div>
                    <div class="float-right">
                        <p>This element is floated to the right.</p>
                    </div>
                </body>
                </html>
                ```

            5. **Responsive Design with Media Queries:**
                Media queries allow you to apply different styles based on the characteristics of the user's device, such as screen size. This example shows how to change the background color of the `<body>` element when the screen width is less than 600 pixels.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        @media screen and (max-width: 600px) {
                            body {
                                background-color: lightpink;
                            }
                        }
                    </style>
                </head>
                <body>
                    <h1>Hello, World!</h1>
                </body>
                </html>
                ```

            6. **Centering Elements:**
                CSS can be used to center elements horizontally or vertically on a webpage. This example demonstrates how to center text horizontally using the `text-align` property.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        .center {
                            text-align: center;
                        }
                    </style>
                </head>
                <body>
                    <div class="center">
                        <p>This text is centered horizontally.</p>
                    </div>
                </body>
                </html>
                ```

            7. **Changing Font Styles:**
                CSS allows you to change font styles such as font family, weight, and style. This example demonstrates how to change the font family and weight of a paragraph (`<p>`) element.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        p {
                            font-family: Arial, sans-serif;
                            font-weight: bold;
                        }
                    </style>
                </head>
                <body>
                    <p>This paragraph has a different font family and weight.</p>
                </body>
                </html>
                ```

            8. **Adding Borders:**
                Borders can be added to elements using CSS. This example shows how to add a border to a `<div>` element.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        .bordered-div {
                            border: 2px solid #000;
                        }
                    </style>
                </head>
                <body>
                    <div class="bordered-div">
                        <p>This div has a border.</p>
                    </div>
                </body>
                </html>
                ```

            9. **Changing Text Color:**
                CSS allows you to change the color of text. This example demonstrates how to change the color of a paragraph (`<p>`) element.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        p {
                            color: green;
                        }
                    </style>
                </head>
                <body>
                    <p>This paragraph has a different text color.</p>
                </body>
                </html>
                ```

            10. **Adding Margins and Padding:**
                Margins and padding can be used to create space around elements. This example demonstrates how to add margins and padding to a `<div>` element.
                ```html
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <style>
                        .styled-div {
                            margin: 20px;
                            padding: 10px;
                            background-color: lightgray;
                        }
                    </style>
                </head>
                <body>
                    <div class="styled-div">
                        <p>This div has margins and padding.</p>
                    </div>
                </body>
                </html>
                ```

            CSS allows you to change the appearance of HTML elements, such as layout, colors, fonts, etc.
        """)
     with st.expander("Javascript"):
         st.markdown("""
            JavaScript is a programming language that enables you to create dynamically updating content, control multimedia, animate images, and much more. 
            Here are some basic examples of JavaScript functionalities:

            1. **Variables and Output:**
                JavaScript uses variables to store data. This example demonstrates how to declare a variable, assign it a value, and display the value.
                ```javascript
                var message = "Hello, JavaScript!";
                console.log(message);
                ```

            2. **User Input and Output:**
                JavaScript can interact with users by getting input and displaying output. This example prompts the user to enter their name and displays a greeting message.
                ```javascript
                var name = prompt("Please enter your name:");
                alert("Hello, " + name + "!");
                ```

            3. **Arithmetic Operators:**
                JavaScript supports arithmetic operators for performing mathematical calculations. This example demonstrates addition, subtraction, multiplication, and division.
                ```javascript
                var x = 5;
                var y = 3;
                console.log("Addition:", x + y);
                console.log("Subtraction:", x - y);
                console.log("Multiplication:", x * y);
                console.log("Division:", x / y);
                ```

            4. **Comparison Operators:**
                JavaScript uses comparison operators to compare values. This example demonstrates equality, inequality, greater than, and less than comparisons.
                ```javascript
                var a = 10;
                var b = 5;
                console.log("Equal:", a === b);
                console.log("Not Equal:", a !== b);
                console.log("Greater Than:", a > b);
                console.log("Less Than:", a < b);
                ```

            5. **Logical Operators:**
                JavaScript uses logical operators to combine conditions. This example demonstrates logical AND, OR, and NOT operations.
                ```javascript
                var p = true;
                var q = false;
                console.log("AND:", p && q);
                console.log("OR:", p || q);
                console.log("NOT:", !p);
                ```

            6. **Conditional Statements:**
                Conditional statements allow JavaScript to make decisions based on conditions. This example demonstrates an if-else statement to check if a number is positive or negative.
                ```javascript
                var number = -10;
                if (number >= 0) {
                    console.log("The number is positive.");
                } else {
                    console.log("The number is negative.");
                }
                ```

            7. **Looping with For Loop:**
                JavaScript provides loops to iterate over a block of code. This example demonstrates a for loop to print numbers from 1 to 5.
                ```javascript
                var result = "";
                for (var i = 1; i <= 5; i++) {
                    result += i + " ";
                }
                console.log(result);
                ```

            8. **Arrays:**
                Arrays allow JavaScript to store multiple values in a single variable. This example demonstrates how to create and access elements of an array.
                ```javascript
                var colors = ["Red", "Green", "Blue"];
                console.log("Second color:", colors[1]);
                ```

            9. **Functions:**
                Functions are blocks of reusable code. This example demonstrates how to define and call a function to calculate the square of a number.
                ```javascript
                function square(x) {
                    return x * x;
                }
                console.log("Square of 5:", square(5));
                ```

            10. **Working with Dates:**
                JavaScript can be used to work with dates and times. This example demonstrates how to display the current date and time.
                ```javascript
                var now = new Date();
                console.log("Current date and time:", now);
                ```

            JavaScript adds interactivity to web pages, allowing you to manipulate HTML content, respond to user actions, and much more.
        """)
     st.markdown("""
        ## Exercises 🧠
         Paste the code exercise to the compiler under the Practice menu.""")
     with st.expander("HTML Excercises"):
       st.markdown("""
        Practice these HTML exercises to get hands-on experience with creating web pages and mastering the basics of HTML. 

        1. **Create a Heading and Paragraph:**
            Create a webpage with a heading displaying "Welcome to My Website" and a paragraph below it saying "This is a basic HTML exercise."
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 1</title>
        </head>
        <body>
            <! –– Your answer ––>
        </body>
        </html>
        ```

        2. **Add an Image:**
            Add an image to your webpage. Display an image of your choice with an appropriate `alt` attribute.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 2</title>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a basic HTML exercise.</p>
             <! –– Your answer ––>
        </body>
        </html>
        ```

        3. **Create an Ordered List:**
            Create an ordered list with three items: "Item 1", "Item 2", "Item 3".
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 3</title>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a basic HTML exercise.</p>
            <! –– Your answer ––>
        </body>
        </html>
        ```

        4. **Create a Form:**
            Create a form with input fields for the user's name and email address.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 4</title>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a basic HTML exercise.</p>
             <! –– Your answer ––>
        </body>
        </html>
        ```

        5. **Create a Table:**
            Create a table with two columns (Name and Age) and two rows of data.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 5</title>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a basic HTML exercise.</p>
             <! –– Your answer ––>
        </body>
        </html>
        ```

        6. **Create a Hyperlink:**
            Create a hyperlink to an external website.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 6</title>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a basic HTML exercise.</p>
             <! –– Your answer ––>
        </body>
        </html>
        ```

        7. **Create a Division (Div):**
            Divisions (`<div>`) are used to group elements together for styling or other purposes.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 7</title>
        </head>
        <body>
            <! –– Your answer ––>
        </body>
        </html>
        ```

        8. **Create an Unordered List:**
            Create an unordered list with three items: "Item 1", "Item 2", "Item 3".
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 8</title>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a basic HTML exercise.</p>
            <! –– Your answer ––>
        </body>
        </html>
        ```

        9. **Use Header Tags (h2, h3, etc.):**
            Use header tags (`<h2>`, `<h3>`, etc.) for creating different levels of headings.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 9</title>
        </head>
        <body>
             <! –– Your answer ––>
        </body>
        </html>
        ```

        10. **Use Bold and Italic Text:**
            Use `<b>` for bold and `<i>` for italic text.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic HTML Exercise 10</title>
        </head>
        <body>
            <! –– Your answer ––>
        </body>
        </html>
        ```

        If you feel lost you can always go back to the tutorial above. 
        """)
     with st.expander("CSS Exercises"):
        st.markdown("""
        Practice these CSS exercises within HTML to enhance your styling skills and make your web pages visually appealing.

        1. **Change Text Color:**
            Change the color of the heading text to red.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 1</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
        </body>
        </html>
        ```

        2. **Change Background Color:**
            Change the background color of the webpage to light blue.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 2</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
        </body>
        </html>
        ```

        3. **Change Font Size:**
            Increase the font size of the paragraph text to 20px.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 3</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a paragraph with increased font size.</p>
        </body>
        </html>
        ```

        4. **Add Padding:**
            Add padding of 10px to all sides of the heading.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 4</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
        </body>
        </html>
        ```

        5. **Add Margin:**
            Add margin of 20px to all sides of the paragraph.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 5</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a paragraph with added margin.</p>
        </body>
        </html>
        ```

        6. **Center Text:**
            Center-align the text of the heading.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 6</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
        </body>
        </html>
        ```

        7. **Change Font Family:**
            Change the font family of the paragraph text to Arial.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 7</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a paragraph with Arial font.</p>
        </body>
        </html>
        ```

        8. **Add Border:**
            Add a border of 1px solid black around the paragraph.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 8</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a paragraph with a border.</p>
        </body>
        </html>
        ```

        9. **Set Text Alignment:**
            Set the text alignment of the paragraph to justify.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 9</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a paragraph with justified text alignment.</p>
        </body>
        </html>
        ```

        10. **Set Text Decoration:**
            Set the text decoration of the paragraph to underline.
        ```html
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Basic CSS Exercise 10</title>
            <style>
                <! –– Your answer ––>
            </style>
        </head>
        <body>
            <h1>Welcome to My Website</h1>
            <p>This is a paragraph with underlined text.</p>
        </body>
        </html>
        ```
         """)
     with st.expander("JavaScript Exercises"):
        st.markdown("""
        Practice these JavaScript exercises to enhance your programming skills and add interactivity to your web pages.

        1. **Variables and Output:**
            Declare a variable named `message` and assign it the value "Hello, JavaScript!". Display the value of the variable using `console.log()`.
            ```javascript
            var message = "Hello, JavaScript!";
            //your answer
            ```

        2. **User Input and Output:**
            Prompt the user to enter their name and store it in a variable named `name`. Display a greeting message using an alert box.
            ```javascript
            var name = prompt("Please enter your name:");
            //your answer
            ```

        3. **Arithmetic Operators:**
            Perform addition, subtraction, multiplication, and division operations and display the results using `console.log()`.
            ```javascript
            var x = 5;
            var y = 3;
            //your answer
            ```

        4. **Comparison Operators:**
            Compare two variables and display the results using `console.log()`.
            ```javascript
            var a = 10;
            var b = 5;
           //your answer
            ```

        5. **Logical Operators:**
            Perform logical AND, OR, and NOT operations and display the results using `console.log()`.
            ```javascript
            var p = true;
            var q = false;
            //your answer
            ```

        6. **Conditional Statements:**
            Use an if-else statement to check if a number is positive or negative and display the result using `console.log()`.
            ```javascript
            var number = -10;
            //your answer
            ```

        7. **Looping with For Loop:**
            Use a for loop to print numbers from 1 to 5 and display the result using `console.log()`.
            ```javascript
            var result = "";
            //your answer
            ```

        8. **Arrays:**
            Create an array of colors and display the second color using `console.log()`.
            ```javascript
            var colors = ["Red", "Green", "Blue"];
            //your answer
            ```

        9. **Functions:**
            Define a function named `square` to calculate the square of a number and display the result using `console.log()`.
            ```javascript
           //your answer
            console.log("Square of 5:", square(5));
            ```

        10. **Working with Dates:**
            Display the current date and time using `console.log()`.
            ```javascript
            var now = new Date();
            //your answer
            ```
        """)


      
         
elif selected == "Practice":
     st.markdown("""
        ## Welcome to the Practice Menu! 💻""")
     with st.expander("HTML & CSS Compiler"):
         st.markdown("<iframe src='https://www.programiz.com/html/online-compiler/' width='100%' height='600px'></iframe>", unsafe_allow_html=True)
     
     with st.expander("Javascript Compiler"):
         st.markdown("<iframe src='https://www.programiz.com/javascript/online-compiler/' width='100%' height='600px'></iframe>", unsafe_allow_html=True)

elif selected == "Resources":
    st.markdown("""
        ## Welcome to the Resources Menu! 📚""")
    with st.expander("Website"):
          st.markdown("""
        Here are three free websites that offer resources for learning web development:

        1. **MDN Web Docs (Mozilla Developer Network)**
       - **Overview:** MDN Web Docs is a comprehensive resource maintained by Mozilla, offering documentation, tutorials, and references for web technologies including HTML, CSS, and JavaScript. It covers topics ranging from basic concepts to advanced techniques, making it suitable for beginners and experienced developers alike.
       - **Website:** [MDN Web Docs](https://developer.mozilla.org/en-US/)

        2. **W3Schools**
       - **Overview:** W3Schools is a popular online platform that provides tutorials, references, and examples for various web development technologies, including HTML, CSS, JavaScript, and more. It offers interactive code editors and quizzes to facilitate hands-on learning.
       - **Website:** [W3Schools](https://www.w3schools.com/)

        3. **freeCodeCamp**
       - **Overview:** freeCodeCamp is a non-profit organization that offers a vast array of free coding resources, including web development tutorials, coding challenges, and projects. Its curriculum covers HTML, CSS, JavaScript, and other programming languages, and it also provides opportunities to collaborate on real-world projects.
       - **Website:** [freeCodeCamp](https://www.freecodecamp.org/)
        """)
    with st.expander("YouTube"):
        st.markdown("""
        Here are three YouTube channels that provide valuable resources for learning web development:

        1. **Traversy Media**
        - **Overview:** Traversy Media, hosted by Brad Traversy, offers a wide range of tutorials covering web development, programming languages, frameworks, and more. The channel provides clear and concise explanations along with practical examples, making it suitable for beginners and experienced developers alike.
        - **Channel Link:** [Traversy Media](https://www.youtube.com/user/TechGuyWeb)

        2. **The Net Ninja**
        - **Overview:** The Net Ninja, hosted by Shaun Pelling, offers tutorials on web development, including HTML, CSS, JavaScript, and various frameworks such as React, Vue.js, and Node.js. The tutorials are structured into comprehensive playlists and cover both basic and advanced concepts.
        - **Channel Link:** [The Net Ninja](https://www.youtube.com/channel/UCW5YeuERMmlnqo4oq8vwUpg)

        3. **SuperSimpleDev**
        - **Overview:** SuperSimpleDev, hosted by Simon Bao, provides beginner-friendly tutorials on web development, programming languages, and related topics. The channel focuses on simplicity and clarity, making it ideal for those new to coding.
        - **Channel Link:** [SuperSimpleDev](https://www.youtube.com/@SuperSimpleDev)
        """)
