from flask import Flask, request, render_template
import re

app = Flask(__name__)

# Mock AI responses (simulating different AIs for code writing)
def mock_ai_1(query):
    """Simulates AI 1's response (e.g., ChatGPT, verbose with error handling)"""
    if "sort" in query.lower():
        return """Here's a Python function for sorting with error handling:
```python
def safe_sort(arr):
    if not arr:
        return []
    if not all(isinstance(x, (int, float)) for x in arr):
        raise ValueError("All elements must be numbers")
    return sorted(arr)
```
This checks for empty lists and invalid types."""
    return "I can help with general queries. Please clarify your request."

def mock_ai_2(query):
    """Simulates AI 2's response (e.g., Gemini, concise and optimized)"""
    if "sort" in query.lower():
        return """Optimized Python sorting function:
```python
def quick_sort(arr):
    return sorted(arr)
```
Uses Python's built-in Timsort for performance."""
    return "Provide more details for a specific answer."

# Router Layer: Decides which AIs to query
def router_layer(query):
    # For simplicity, always query both mock AIs
    return [mock_ai_1, mock_ai_2]

# Fusion Engine: Combines AI responses, optimized for code
def fusion_engine(responses):
    if not responses:
        return "No responses received."
    
    # Extract code blocks and explanations
    code_blocks = []
    explanations = []
    for response in responses:
        # Find code block (between ```python and ```)
        code_match = re.search(r"```python\n(.*?)\n```", response, re.DOTALL)
        if code_match:
            code_blocks.append(code_match.group(1))
        # Extract explanation (non-code text)
        explanation = re.sub(r"```python\n.*?\n```", "", response, flags=re.DOTALL).strip()
        if explanation:
            explanations.append(explanation)
    
    # Fuse code: Prioritize complete, error-handling code
    fused_code = ""
    if code_blocks:
        # Pick the most "complete" code (e.g., with error handling)
        fused_code = max(code_blocks, key=lambda x: len(x) + (100 if "raise" in x else 0))  # Favor error handling
        fused_code = f"```python\n{fused_code}\n```"
    
    # Fuse explanations: Combine unique parts
    unique_explanations = []
    for exp in explanations:
        if exp and exp not in unique_explanations:
            unique_explanations.append(exp)
    fused_explanation = ". ".join(unique_explanations) + ("." if unique_explanations else "")
    
    return f"{fused_code}\n\n{fused_explanation}" if fused_code else fused_explanation or "No valid response."

@app.route("/", methods=["GET", "POST"])
def index():
    response = None
    try:
        if request.method == "POST":
            query = request.form.get("query", "")
            if query:
                # Route query to selected AIs
                ai_functions = router_layer(query)
                # Collect responses
                responses = [ai(query) for ai in ai_functions]
                # Fuse responses
                response = fusion_engine(responses)
            else:
                response = "Please provide a query."
    except Exception as e:
        response = f"Error processing query: {str(e)}"
    return render_template("render.html", response=response)

if __name__ == "__main__":
    app.run(debug=True)