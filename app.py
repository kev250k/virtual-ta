from flask import Flask, request, jsonify
import pandas as pd
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

# Load knowledge base (you'll need to run the scraper first)
try:
    course_content = pd.read_csv('course_content.csv')
    discourse_posts = pd.read_csv('discourse_posts.csv')
except FileNotFoundError:
    course_content = pd.DataFrame()
    discourse_posts = pd.DataFrame()

def find_relevant_answer(question):
    # This is a simplified version - you'd want to use embeddings for real implementation
    relevant_content = []
    
    # Search course content
    for _, row in course_content.iterrows():
        if question.lower() in row['text'].lower():
            relevant_content.append({
                'text': row['text'],
                'source': 'course_content',
                'title': row['title']
            })
    
    # Search discourse posts
    for _, row in discourse_posts.iterrows():
        if question.lower() in row['title'].lower():
            relevant_content.append({
                'text': row['title'],
                'source': 'discourse',
                'url': row['url']
            })
    
    return relevant_content

def generate_answer(question, context):
    if not context:
        return "I couldn't find an answer to your question in the course materials.", []
    
    # Use GPT to generate a coherent answer
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful teaching assistant for the Tools in Data Science course. Answer the student's question based on the provided context."},
                {"role": "user", "content": f"Question: {question}\n\nContext: {str(context)}"}
            ]
        )
        answer = response.choices[0].message.content
        
        # Extract links
        links = []
        for item in context:
            if item['source'] == 'discourse':
                links.append({
                    'url': item['url'],
                    'text': item['text'][:100] + '...' if len(item['text']) > 100 else item['text']
                })
        
        return answer, links
    except Exception as e:
        return f"Error generating answer: {str(e)}", []

@app.route('/api/', methods=['POST'])
def virtual_ta():
    data = request.get_json()
    question = data.get('question', '')
    image = data.get('image', None)
    
    # Find relevant information
    context = find_relevant_answer(question)
    
    # Generate answer
    answer, links = generate_answer(question, context)
    
    response = {
        "answer": answer,
        "links": links
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, port=5000)