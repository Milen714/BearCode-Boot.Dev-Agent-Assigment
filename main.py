import os
import argparse
import sys
from urllib import response

from dotenv import load_dotenv
from google import genai
from google.genai import types
from promts import system_prompt
from call_function import available_functions, call_function


def main() -> None:

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
    "--working-directory",
    default="./calculator",
    help="Directory the agent is allowed to operate in",
    )
    args = parser.parse_args()
    print("Hello from BearCode!")
    print("Loading environment variables...")
    load_dotenv()
    max_agent_iterations = int(os.environ.get("MAX_AGENT_ITERATIONS", "10"))
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")

    messages: list[types.Content] = [
    types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
    ]

    client = genai.Client(api_key=api_key)
    for i in range(max_agent_iterations):
        done = generate_content(client, messages, verbose=args.verbose, user_prompt=args.user_prompt, working_directory=args.working_directory,)
        if done:
            return
    print("Error: Agent reached maximum iterations without producing a final response.")
    sys.exit(1)
            


def generate_content(client: genai.Client, 
                     messages: list[types.Content], 
                     verbose: bool = False, 
                     user_prompt: str = "",
                     working_directory: str = "./calculator") -> bool:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
            temperature=0),
    )
    if not response.usage_metadata:
        raise RuntimeError("Gemini API response appears to be malformed")

    print("=== Gemini API Response ===")
    if verbose:
        print("User prompt:", user_prompt)
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    print("Response:")
    if response.candidates:
        for candidate in response.candidates:
            messages.append(candidate.content)

    function_results = []
    if response.function_calls:
        for function_call in response.function_calls:
            function_call_result = call_function(function_call, verbose=verbose, working_directory=working_directory)

            if not function_call_result.parts:
                 raise RuntimeError(f"Function call result is empty for function: {function_call.name}")
            
            function_response = function_call_result.parts[0].function_response
            if function_response is None:
                raise RuntimeError(f"Function call result has no function response for function: {function_call.name}")
            
            function_results.append(function_call_result.parts[0])

            if verbose:
                print(f"{function_response.response}")
                
        messages.append(types.Content(role="user", parts=function_results))
        return False
    
    else:
        print(response.text)
        return True

    
if __name__ == "__main__":
    main()