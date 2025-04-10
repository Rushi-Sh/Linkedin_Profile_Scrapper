from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

def get_company_insights(company_name: str):
    """
    Extract detailed company insights using Groq LLM and return a structured JSON dictionary.
    """

    # Initialize Groq LLM
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile"
    )

    # Enhanced prompt with clear, user-friendly formatting expectations
    company_prompt = PromptTemplate(
        input_variables=["company_name"],
        template="""
Act like a business intelligence analyst. Provide well-structured and easy-to-read insights about {company_name}.
Use the **exact JSON format** below and fill it with as much detailed, user-understandable information as possible.

Respond ONLY with valid JSON. No markdown, no additional explanations.

{{
  "Company Overview": {{
    "Industry": "e.g., IT Services, Software Development",
    "Size": "e.g., 200-500 employees",
    "Founding Year": "e.g., 2009",
    "Headquarters": "e.g., Ahmedabad, Gujarat, India"
  }},
  "Key Products/Services": "List the company’s major offerings with brief descriptions.",
  "Employee Distribution": "Rough breakdown by departments (e.g., Engineering: 40%, Sales: 20%, HR: 10%, etc.)",
  "Recent Growth Metrics": "Share growth stats from the past 3-4 years like revenue growth, client base increase, etc.",
  "Key Achievements and Market Position": "Mention awards, recognitions, or notable achievements and how the company stands in its domain."
}}
"""
    )

    # Create LLMChain
    chain = LLMChain(llm=llm, prompt=company_prompt)

    try:
        # Use invoke (recommended)
        response = chain.invoke({"company_name": company_name})

        # Clean potential code formatting
        cleaned_response = response['text'].strip().replace("```json", "").replace("```", "")

        # Parse and return JSON
        insights = json.loads(cleaned_response)
        return insights

    except Exception as e:
        return {
            "error": f"Failed to fetch insights: {str(e)}",
            "company": company_name,
            "raw_response": response if 'response' in locals() else "No response"
        }

# Example test
if __name__ == "__main__":
    test_company = "Sapphire Software Solutions"
    insights = get_company_insights(test_company)
    print(json.dumps(insights, indent=2))
